from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    item_list = []
    for row in app_tables.list_currency_types.search():
     item_list.append((row["types"], row))

    self.drop_down_from_currency_type.items = item_list
    self.drop_down_to_currency_type.items = item_list
    # Any code you write here will run before the form opens.
