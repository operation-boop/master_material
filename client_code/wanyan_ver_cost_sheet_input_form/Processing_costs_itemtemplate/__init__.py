from ._anvil_designer import Processing_costs_itemtemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Processing_costs_itemtemplate(Processing_costs_itemtemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.type.text = self.item["type"]
    self.vendor.text = self.item["vendor"]
    self.cost.text = str(self.item["cost"])
    # Any code you write here will run before the form opens.

  def remove_btn_click(self, **event_args):
    processing_list = self.parent.items
    processing_list.remove(self.item)
    self.parent.items = processing_list
