import anvil.files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

try:
    from anvil.files import data_files
except ImportError:
    pass


@anvil.server.callable
def get_docs():
    try:
        with open(data_files["docs.md"]) as f:
            text = f.read()
        return text
    except Exception as e:
        return str(e)
