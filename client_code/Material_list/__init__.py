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
      alert(
        content=popup,
        title=None,
        large=True,
        buttons=None 
      )

    except Exception as e:
      alert(f"Error creating material: {str(e)}")

  def refresh_cards(self, focus_document_id=None):
    try:
      items = anvil.server.call('list_material_summaries')
      self.repeating_panel_materials.items = items
  
      # Optional: focus/scroll to a specific card after save/submit
      if focus_document_id:
        for it in items:
          if it.get("document_id") == focus_document_id:
            # you can set a label to bold, or flash the card—depends on your template
            break
    except Exception as e:
      Notification(f"Load failed: {e}", style="danger").show()

  


