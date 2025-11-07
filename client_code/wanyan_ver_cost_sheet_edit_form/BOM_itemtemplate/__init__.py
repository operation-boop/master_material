from ._anvil_designer import BOM_itemtemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class BOM_itemtemplate(BOM_itemtemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.material.text = self.item["material"]
    self.consumption.text = str(self.item["consumption"])
    self.unit_cost.text = str(self.item["unit_cost"])
    self.total.text = str(self.item["total_cost"])
    # Any code you write here will run before the form opens.

  def remove_btn_click(self, **event_args):
    # Remove this row's item from the repeating panel's items list
    bom_list = self.parent.items
    bom_list.remove(self.item)
    self.parent.items = bom_list
