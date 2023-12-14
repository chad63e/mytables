import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from typing import List, Union

import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil._server import LiveObjectProxy
from anvil.tables import Row, SearchIterator, Table, app_tables


class Serializer:
    def to_anvil(self, data):
        if isinstance(data, MyRow):
            # Convert MyRow to an anvil.tables.Row
            return data.get_anvil_row()
        elif isinstance(data, MySearchIterator):
            # Convert MySearchIterator to an anvil.tables.SearchIterator
            return data.get_anvil_search()
        elif isinstance(data, list):
            # Convert each MyRow in the list
            return [self.to_anvil(row) for row in data]
        elif isinstance(data, dict):
            # Convert each value in the dictionary
            return {key: self.to_anvil(value) for key, value in data.items()}
        else:
            # Handle non-MyRow data
            return data

    def serialize(self, data):
        if isinstance(data, (Row, LiveObjectProxy)):
            # Convert Row to a dictionary, handling nested Row objects recursively
            return {
                key: self.serialize(data[key])
                if isinstance(data[key], (Row, SearchIterator, list))
                else data[key]
                for key in data.keys()
            }
        elif isinstance(data, (SearchIterator, list)):
            # Convert each Row in the SearchIterator or list
            return [self.serialize(row) for row in data]
        elif isinstance(data, (MyRow, MySearchIterator)):
            # Convert MyRow or MySearchIterator to a dictionary
            return self.serialize(data.get_anvil_row())
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

    def _convert_nested_rows(self, row, processed_objects=None):
        if processed_objects is None:
            processed_objects = set()

        # Check for circular references
        row_id = id(row)
        if row_id in processed_objects:
            return row  # Return the original row to avoid infinite recursion
        processed_objects.add(row_id)

        if isinstance(row, (Row, LiveObjectProxy)):
            row_dict = {key: row[key] for key in row.keys()}
        elif isinstance(row, dict):
            row_dict = row
        else:
            return row  # Base case for non-dict and non-Row types

        converted_row = {}
        for key, value in row_dict.items():
            value_id = id(value)
            if value_id not in processed_objects:
                processed_objects.add(value_id)
                converted_value = self._process_value(value, processed_objects)
                if converted_value is not None:
                    converted_row[key] = converted_value

        return converted_row

    def _process_value(self, value, processed_objects):
        if isinstance(value, (MyRow, MySearchIterator)):
            return value
        elif isinstance(value, SearchIterator):
            return MySearchIterator(value)
        elif isinstance(value, list):
            return [
                self._convert_nested_rows(item, processed_objects)
                for item in value
                if id(item) not in processed_objects
            ]
        elif isinstance(value, (Row, LiveObjectProxy)):
            return self._convert_live_object_proxy(value, processed_objects)
        else:
            return value

    def _convert_live_object_proxy(self, value, processed_objects):
        if "<LiveObject: anvil.tables.Row>" in str(value):
            return MyRow(value)
        elif "<LiveObject: anvil.tables.SearchIterator>" in str(value):
            return MySearchIterator(value)
        else:
            return self._convert_nested_rows(value, processed_objects)

    # --- PUBLIC METHODS (in_transaction) ---

    @tables.in_transaction
    def update(self, **kwargs) -> None:
        serializer = Serializer()
        kwargs = serializer.to_anvil(kwargs)

        self.row.update(**kwargs)

    # --- PUBLIC METHODS ---

    def delete(self):
        return self.row.delete()

    def get(self, key: str, default=None):
        try:
            return self.row[key]
        except KeyError:
            return default

    def add_to_list_column(self, column: str, value):
        current_list = self.row[column] or []
        if value not in current_list:
            current_list.append(value)
            self.update(**{column: current_list})

    def remove_from_list_column(self, column: str, value):
        current_list = self.row[column] or []
        if value in current_list:
            current_list.remove(value)
            self.update(**{column: current_list})

    def add_to_dict_column(self, column: str, key, value):
        current_dict = self.row[column] or {}
        current_dict[key] = value
        self.update(**{column: current_dict})

    def remove_from_dict_column(self, column: str, key):
        current_dict = self.row[column] or {}
        if key in current_dict:
            del current_dict[key]
            self.update(**{column: current_dict})

    def update_simple_object_column(self, column: str, data: Union[dict, list]):
        current_column = self.row[column]
        if not current_column:
            if isinstance(data, (dict, list)):
                self.update(column=data)
            else:
                raise TypeError(
                    f"Unsupported data type {type(data)} for column {column}."
                )
        elif isinstance(current_column, type(data)):
            if isinstance(data, dict):
                for key, value in data.items():
                    self.add_to_dict_column(column, key, value)
            elif isinstance(data, list):
                self.add_to_list_column(column, data)
            else:
                raise TypeError(
                    f"Unsupported data type {type(data)} for column {column}."
                )
        else:
            raise TypeError(
                f"Data type mismatch: cannot update column {column} of type {type(current_column)} with value {data} of type {type(data)}."
            )

    def get_anvil_row(self):
        return self.row

    # --- SERIALIZATION ---

    def serialize(self):
        serilizer = Serializer()
        return serilizer.serialize(self.row)


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

    def get_index(self, index: int, return_anvil: bool = False) -> MyRow:
        if index >= len(self.search):
            return None

        if return_anvil:
            return self.search[index]

        return MyRow(self.search[index])

    def get_anvil_search(self):
        return getattr(self, "_anvil_search", [])

    # --- SERIALIZATION ---

    def serialize(self):
        serilizer = Serializer()
        return serilizer.serialize(self.search)


class MyTable:
    def __init__(self, name: str):
        self.name = name
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
    def add_row(self, return_anvil: bool = False, **kwargs) -> Union[MyRow, Row]:
        serializer = Serializer()
        kwargs = serializer.to_anvil(kwargs)

        row = self.table.add_row(**kwargs)
        if return_anvil:
            return row

        return MyRow(row)

    @tables.in_transaction
    def update_row(
        self, row: Union[Row, MyRow], return_anvil: bool = False, **kwargs
    ) -> None:
        if isinstance(row, MyRow):
            row = row.row

        row.update(**kwargs)

    # --- PUBLIC METHODS ---

    def get(self, return_anvil: bool = False, **kwargs) -> Union[MyRow, Row, None]:
        serializer = Serializer()
        kwargs = serializer.to_anvil(kwargs)

        row = self.table.get(**kwargs)
        if not row:
            return None

        if return_anvil:
            return row

        return MyRow(row)

    def get_by_id(
        self, row_id: str, return_anvil: bool = False
    ) -> Union[MyRow, Row, None]:
        row = self.table.get_by_id(row_id)
        if not row:
            return None

        if return_anvil:
            return row

        return MyRow(row)

    def search(
        self, *args, return_anvil: bool = False, convert_limit: int = 100, **kwargs
    ) -> Union[SearchIterator, list]:
        serializer = Serializer()
        args = serializer.to_anvil(args)
        kwargs = serializer.to_anvil(kwargs)

        search = self.table.search(*args, **kwargs) or []
        if return_anvil:
            return search
        elif len(search) > convert_limit:
            print(
                f"WARNING: Search returned more than {convert_limit} results.  Will not convert to MySearchIterator object."
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
