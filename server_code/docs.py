import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_docs():
    with open(data_files['docs.md']) as f:
        text = f.read()
    return text