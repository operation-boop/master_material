from ._anvil_designer import Material_listTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Material_list(Material_listTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.load_materials()
    # Any code you write here will run before the form opens.

  def load_materials(self):
    try:
      materials = anvil.server.call('get_materials')
      self.repeating_panel_1.items = materials
    except Exception as e:
      alert(f"Error loading materials: {e}")

  def view_details_btn_click(self, **event_args):
    selected = None

    for row_form in self.repeating_panel_1.get_components():
      if getattr(row_form, 'select_row', None) and row_form.select_row.checked:
        selected = row_form.item
        break

    if selected:
      open_form('Material_detail', item=selected)
    else:
      alert("Please select a material first.")

  def add_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    
