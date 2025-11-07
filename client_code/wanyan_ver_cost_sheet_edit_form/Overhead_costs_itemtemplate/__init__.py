from ._anvil_designer import Overhead_costs_itemtemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Overhead_costs_itemtemplate(Overhead_costs_itemtemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def remove_btn_click(self, **event_args):
    overhead_list = self.parent.items
    overhead_list.remove(self.item)
    self.parent.items = overhead_list
