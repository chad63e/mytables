import time
from typing import List, Union

import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import Row, SearchIterator, Table, app_tables


class Serializer:
    def to_dict(self, data):
        if isinstance(data, Row):
            # Convert Row to a dictionary, handling nested Row objects recursively
            return {
                key: self.to_dict(data[key])
                if isinstance(data[key], (Row, SearchIterator, list))
                else data[key]
                for key in data.keys()
            }
        elif isinstance(data, (SearchIterator, list)):
            # Convert each Row in the SearchIterator or list
            return [self.to_dict(row) for row in data]
        elif isinstance(data, (MyRow, MySearchIterator)):
            # Convert MyRow or MySearchIterator to a dictionary
            return self.to_dict(data.get_anvil_row())
        else:
            # Handle non-Row data
            return data


class MyRow:
    def __init__(self, row: Row):
        self.row = row

    # --- PROPERTIES ---

    @property
    def row(self) -> Row:
        return self._row

    @row.setter
    def row(self, value: Row):
        self._row = value
        self._converted_row = self._convert_nested_rows(value)

    # --- MAGIC METHODS ---

    def __repr__(self):
        row_str = str(self.row)
        if "<LiveObject: anvil.tables.Row>" in row_str:
            items = list(dict(self.row).items())
            repr_items = []

            for key, value in items:
                if isinstance(value, (str, int, float, bool)):
                    repr_items.append(f"{key}: {value}")
                if len(repr_items) == 2:
                    break

            repr_str = ", ".join(repr_items)
            if len(items) > 2:
                repr_str += f", plus {len(items) - 2} more columns"
        else:
            repr_str = row_str.replace("<anvil.tables.Row: ", "").replace(">", "")

        return f"<MyRow: {repr_str}>"

    def __setitem__(self, key, value):
        self.update(**{key: value})

    def __getitem__(self, key):
        try:
            return self._converted_row[key]
        except Exception:
            return self.row[key]

    # --- PRIVATE METHODS ---

    def _convert_nested_rows(self, row):
        converted_row = {}
        try:
            items = row.items()
        except AttributeError:
            row = dict(row)
            items = row.items()

        for key, value in items:
            if isinstance(value, (SearchIterator)):
                converted_row[key] = MySearchIterator(value)
            elif isinstance(value, (list)):
                converted_row[key] = [MyRow(item) for item in value]
            elif isinstance(value, (Row)):
                converted_row[key] = MyRow(value)
            else:
                converted_row[key] = value

        return converted_row

    # --- PUBLIC METHODS (in_transaction) ---

    @tables.in_transaction
    def update(self, **kwargs):
        return self.row.update(**kwargs)

    # --- PUBLIC METHODS ---

    def delete(self):
        return self.row.delete()

    def get_anvil_row(self):
        return self.row

    # --- SERIALIZATION ---

    def to_dict(self):
        serilizer = Serializer()
        return serilizer.to_dict(self.row)


class MySearchIterator:
    def __init__(self, search: SearchIterator):
        self.search = search

    # --- PROPERTIES ---

    @property
    def search(self) -> SearchIterator:
        return self._search

    @search.setter
    def search(self, value: SearchIterator):
        self._anvil_search = value
        self._search = self._convert_rows(value)

    # --- MAGIC METHODS ---

    def __repr__(self):
        return f"<MySearchIterator: {self.search}>"

    def __iter__(self):
        return self.search.__iter__()

    def __next__(self):
        return self.search.__next__()

    def __getitem__(self, key):
        return self.search[key]

    def __len__(self):
        return self.search.__len__()

    # --- PRIVATE METHODS ---

    def _convert_rows(self, search: SearchIterator) -> List[MyRow]:
        converted_rows = [MyRow(row) for row in search]
        return converted_rows

    # --- PUBLIC METHODS ---

    def get_anvil_search(self):
        return getattr(self, "_anvil_search", [])

    # --- SERIALIZATION ---

    def to_dict(self):
        serilizer = Serializer()
        return serilizer.to_dict(self.search)


class MyTable:
    def __init__(
        self, name: str, convert_search: bool = True, convert_limit: int = 100
    ):
        self.name = name
        self.convert_search = convert_search
        self.convert_limit = convert_limit
        self.table = self._initialize_table(name)

    # --- PROPERTIES ---

    @property
    def table(self) -> Table:
        return self._table

    @table.setter
    def table(self, value: Table):
        self._table = value

    # --- MAGIC METHODS ---

    def __repr__(self):
        return f"<MyTable: {self.name} columns: {self.list_columns()}>"

    # --- PRIVATE METHODS ---

    def _initialize_table(self, name: str) -> Table:
        if not hasattr(app_tables, name.lower()):
            raise AttributeError("The table {} does not exist in your app".format(name))

        try:
            return app_tables[name]
        except Exception:
            return getattr(app_tables, name)

    # --- PUBLIC METHODS (in_transaction) ---

    @tables.in_transaction
    def add_row(self, **kwargs) -> Row:
        return self.table.add_row(**kwargs)

    @tables.in_transaction
    def update_row(self, row: Union[Row, MyRow], **kwargs) -> Union[Row, MyRow]:
        if isinstance(row, MyRow):
            row = row.row
        return row.update(**kwargs)

    # --- PUBLIC METHODS ---

    def get(self, **kwargs) -> Union[Row, None]:
        row = self.table.get(**kwargs)
        if row:
            return MyRow(row)

    def get_by_id(self, row_id: str) -> Union[Row, None]:
        row = self.table.get_by_id(row_id)
        if row:
            return MyRow(row)

    def search(self, *args, **kwargs) -> Union[SearchIterator, list]:
        search = self.table.search(*args, **kwargs) or []
        if not self.convert_search:
            return search
        elif len(search) > self.convert_limit:
            print(
                f"WARNING: Search returned more than {self.convert_limit} results.  Will not convert to MySearchIterator object."
            )
            return search

        return MySearchIterator(search)

    def has_row(self, row: Union[Row, MyRow]) -> bool:
        if isinstance(row, MyRow):
            row = row.row
        return self.table.has_row(row)

    def list_columns(self) -> list:
        return self.table.list_columns() or []

    def to_csv(self) -> str:
        return self.table.to_csv()

    def get_anvil_table(self):
        return self.table
