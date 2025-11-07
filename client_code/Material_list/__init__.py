from ._anvil_designer import Material_listTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Material_input_form import Material_input_form


class Material_list(Material_listTemplate):
  def __init__(self, focus_document_id=None, **properties):
    self.init_components(**properties)
    self.refresh_cards(focus_document_id)

  def add_btn_click(self, **event_args):
    """Creates new material with 'Creating' status"""
    try:
      # Create new material document on server
      result = anvil.server.call('create_new_master_material', 'test_user@example.com')
      document_id = result['document_id']
      # Show notification
      Notification(f"Created new material: {document_id}", style="success", timeout=2).show()
      # Import and create popup WITH document_id
      from ..Material_input_form import Material_input_form
      popup = Material_input_form(current_document_id=document_id)  
      popup.set_event_handler('x-refresh-list', lambda **e: self.refresh_list())
      alert(
        content=popup,
        title=None,
        large=True,
        buttons=None 
      )

    except Exception as e:
      alert(f"Error creating material: {str(e)}")
      
  def refresh_list(self):
    try:
      rows = anvil.server.call('get_material_overview_list')
      self.repeating_panel_cards.items = rows
    except Exception as e:
      Notification(f"Load failed: {e}", style="danger").show()



  


