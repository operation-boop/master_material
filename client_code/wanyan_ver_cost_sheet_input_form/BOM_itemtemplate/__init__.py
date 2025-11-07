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

    if self.item:
      material_name = self.item["material"]
      percentage = self.item["percentage"]
      self.fabric_composition_item.text = f"{material_name} - {percentage}%"
    # Any code you write here will run before the form opens.

  def remove_btn_click(self, **event_args):
    # Remove this row's item from the repeating panel's items list
    composition_list = self.parent.items
    composition_list.remove(self.item)
    self.parent.items = composition_list
    form = self.item["form"]
    form.update_total_percentage()
