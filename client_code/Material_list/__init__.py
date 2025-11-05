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
    """Creates new material with 'Creating' status"""
    result = anvil.server.call('create_new_master_material', 'test_user@example.com')
    self.current_document_id = result['document_id']
   
    from ..Material_input_form import Material_input_form
    popup = Material_input_form()

    alert(
      content=popup,
      title=None,
      large=True,
      buttons=None 

    )