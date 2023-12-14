DOCS = """
# Documentation for MyTable, MyRow, and MySearchIterator Classes

## MyTable Class

### Overview
`MyTable` is designed for interacting with Anvil database tables, providing a structured, Pythonic interface for managing database records. It ensures transactional integrity for update-related operations.

### Initialization
```python
# Example: Initializing MyTable for an 'employees' table
my_table = MyTable("employees")
```
- **Parameters:**
  - `name` (str): Name of the Anvil table to be managed.

### Methods

#### `add_row`
- **Purpose:** Adds a new row to the table.
- **Signature:** `add_row(**kwargs) -> Union[MyRow, Row]`
- **Example:**
  ```python
  # Adding a new employee
  new_employee = my_table.add_row(name="Alice", role="Engineer")
  ```
- **Arguments:**
  - `**kwargs`: Keyword arguments where each key is a column name and each value is the corresponding value to be added.

#### `update_row`
- **Purpose:** Updates an existing row in the table.
- **Signature:** `update_row(row, **kwargs) -> None`
- **Example:**
  ```python
  # Updating an employee's role
  employee = my_table.get(name="Alice")
  if employee:
      my_table.update_row(employee, role="Senior Engineer")
  ```
- **Arguments:**
  - `row` (Union[Row, MyRow]): The row object to be updated.
  - `**kwargs`: Key-value pairs for the columns to be updated.

#### `get`
- **Purpose:** Retrieves a single row that matches specified criteria.
- **Signature:** `get(**kwargs) -> Union[MyRow, Row, None]`
- **Example:**
  ```python
  # Retrieving an employee by name
  employee = my_table.get(name="Alice")
  ```
- **Arguments:**
  - `**kwargs`: Criteria for selecting the row, provided as column-value pairs.

#### `get_by_id`
- **Purpose:** Retrieves a row by its unique ID.
- **Signature:** `get_by_id(row_id: str) -> Union[MyRow, Row, None]`
- **Example:**
  ```python
  # Retrieving an employee by their unique ID
  employee = my_table.get_by_id("unique_id_123")
  ```
- **Arguments:**
  - `row_id` (str): The unique identifier of the row.

#### `search`
- **Purpose:** Performs a search query on the table.
- **Signature:** `search(*args, **kwargs) -> Union[SearchIterator, list]`
- **Example:**
  ```python
  # Finding all engineers
  engineers = my_table.search(role="Engineer")
  for engineer in engineers:
      print(engineer)
  ```
- **Arguments:**
  - `*args`: Positional arguments for the search query.
  - `**kwargs`: Keyword arguments representing search criteria.

#### `has_row`
- **Purpose:** Checks if the specified row exists in the table.
- **Signature:** `has_row(row: Union[Row, MyRow]) -> bool`
- **Example:**
  ```python
  # Checking if an employee exists
  exists = my_table.has_row(employee)
  ```
- **Arguments:**
  - `row` (Union[Row, MyRow]): The row object to check.

#### `list_columns`
- **Purpose:** Lists all columns in the table.
- **Signature:** `list_columns() -> list`
- **Example:**
  ```python
  # Listing columns in 'employees' table
  columns = my_table.list_columns()
  print(columns)
  ```

#### `to_csv`
- **Purpose:** Exports table data to a CSV format.
- **Signature:** `to_csv() -> str`
- **Example:**
  ```python
  # Exporting employee data to CSV
  csv_data = my_table.to_csv()
  ```

#### `get_anvil_table`
- **Purpose:** Retrieves the underlying Anvil table object.
- **Signature:** `get_anvil_table()`
- **Example:**
  ```python
  # Accessing the underlying Anvil table
  anvil_table = my_table.get_anvil_table()
  ```

## MyRow Class

### Overview
`MyRow` provides an enhanced interface for manipulating individual rows in an Anvil table. It simplifies data access and manipulation, and also takes care of transaction management for updates.

### Initialization
```python
# Example: Wrapping an existing Anvil Row object
anvil_row = app_tables.employees.get(name="Alice")
my_row = MyRow(anvil_row)
```
- **Parameters:**
  - `row` (Row): An instance of Anvil's `Row` object.

### Methods

#### #### `update`
- **Purpose:** Updates the row with new data.
- **Signature:** `update(**kwargs) -> None`
- **Example:**
  ```python
  # Updating an employee's department
  my_row.update(department="Research and Development")
  ```
- **Arguments:**
  - `**kwargs`: Key-value pairs representing the column names and their new values.

#### `delete`
- **Purpose:** Deletes the row from the table.
- **Signature:** `delete() -> None`
- **Example:**
  ```python
  # Deleting an employee record
  my_row.delete()
  ```

#### `get`
- **Purpose:** Retrieves the value for a specified column.
- **Signature:** `get(key: str, default=None)`
- **Example:**
  ```python
  # Getting the value of the 'department' column
  department = my_row.get("department", default="Unknown")
  ```
- **Arguments:**
  - `key` (str): The column name.
  - `default`: The default value to return if the column does not exist.

#### `add_to_list_column`
- **Purpose:** Adds an item to a list-type column.
- **Signature:** `add_to_list_column(column: str, value)`
- **Example:**
  ```python
  # Adding a skill to an employee's skill list
  my_row.add_to_list_column("skills", "Python")
  ```
- **Arguments:**
  - `column` (str): The name of the list-type column.
  - `value`: The item to add to the list.

#### `remove_from_list_column`
- **Purpose:** Removes an item from a list-type column.
- **Signature:** `remove_from_list_column(column: str, value)`
- **Example:**
  ```python
  # Removing a skill from an employee's skill list
  my_row.remove_from_list_column("skills", "Java")
  ```
- **Arguments:**
  - `column` (str): The name of the list-type column.
  - `value`: The item to remove from the list.

#### `add_to_dict_column`
- **Purpose:** Adds or updates a key-value pair in a dictionary-type column.
- **Signature:** `add_to_dict_column(column: str, key, value)`
- **Example:**
  ```python
  # Adding/updating contact information
  my_row.add_to_dict_column("contact_info", "email", "alice@example.com")
  ```
- **Arguments:**
  - `column` (str): The name of the dictionary-type column.
  - `key`: The key in the dictionary.
  - `value`: The value to be set for the key.

#### `remove_from_dict_column`
- **Purpose:** Removes a key-value pair from a dictionary-type column.
- **Signature:** `remove_from_dict_column(column: str, key)`
- **Example:**
  ```python
  # Removing a key from contact information
  my_row.remove_from_dict_column("contact_info", "phone")
  ```
- **Arguments:**
  - `column` (str): The name of the dictionary-type column.
  - `key`: The key to be removed from the dictionary.

#### `update_simple_object_column`
- **Purpose:** Updates a column containing simple objects (dict or list).
- **Signature:** `update_simple_object_column(column: str, data: Union[dict, list])`
- **Example:**
  ```python
  # Updating a dictionary column
  my_row.update_simple_object_column("contact_info", {"address": "123 Main St"})
  # Updating a list column
  my_row.update_simple_object_column("skills", ["Java", "SQL"])
  ```
- **Arguments:**
  - `column` (str): The name of the column to update.
  - `data` (Union[dict, list]): The new data for the column, which should be a dictionary or list depending on the column's type.

## MySearchIterator Class

### Overview
`MySearchIterator` enhances Anvil's `SearchIterator`, providing a more Pythonic way to iterate over and work with search results from Anvil tables.

### Initialization
```python
# Example: Creating a MySearchIterator from a SearchIterator
search_result = app_tables.employees.search(role="Engineer")
my_search_iterator = MySearchIterator(search_result)
```
- **Parameters:**
  - `search` (SearchIterator): An instance of Anvil's `SearchIterator`.

### Methods

#### `__iter__`
- **Purpose:** Provides an iterator interface for the search results.
- **Example:**
  ```python
  # Iterating over search results
  for employee in my_search_iterator:
      print(employee)
  ```

#### `__next__`
- **Purpose:** Advances to the next item in the iterator.
- **Example:**
  ```python
  # Getting the next item in the iterator
  try:
      next_employee = next(my_search_iterator)
      print(next_employee)
  except StopIteration:
      print("No more items in the iterator")
  ```

#### `__getitem__`
- **Purpose:** Retrieves an item at a specific index from the search results.
- **Signature:** `__getitem__(key: int) -> MyRow`
- **Example:**
  ```python
  # Accessing the third item in the search results
  third_employee = my_search_iterator[2]
  print(third_employee)
  ```
- **Arguments:**
  - `key` (int): The index of the item in the search results.

#### `__len__`
- **Purpose:** Returns the number of items in the search results.
- **Signature:** `__len__() -> int`
- **Example:**
  ```python
  # Getting the number of search results
  number_of_employees = len(my_search_iterator)
  print(f"Found {number_of_employees} employees")
  ```

#### `get_index`
- **Purpose:** Retrieves a row at a specific index.
- **Signature:** `get_index(index: int, return_anvil: bool = False) -> MyRow`
- **Example:**
  ```python
  # Getting the first employee in the search results
  first_employee = my_search_iterator.get_index(0)
  print(first_employee)
  ```
- **Arguments:**
  - `index` (int): The index of the row to retrieve.
  - `return_anvil` (bool): If `True`, returns an Anvil `Row` object; otherwise, returns a `MyRow` object.

#### `get_anvil_search`
- **Purpose:** Returns the underlying Anvil `SearchIterator`.
- **Signature:** `get_anvil_search() -> SearchIterator`
- **Example:**
  ```python
  # Accessing the Anvil SearchIterator
  anvil_search = my_search_iterator.get_anvil_search()
  ```

#### `serialize`
- **Purpose:** Serializes the search results into a list of dictionaries.
- **Signature:** `serialize() -> List[Dict]`
- **Example:**
  ```python
  # Serializing search results
  serialized_results = my_search_iterator.serialize()
  for result in serialized_results:
      print(result)
  ```

These classes (`MyTable`, `MyRow`, and `MySearchIterator`) provide an extended interface for managing database operations in Anvil applications, streamlining the process of interacting with Anvil's built-in database capabilities and enhancing the user experience with Pythonic data manipulation techniques.
"""

def get_docs():
    return DOCS.strip()