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
    self.init_components(**properties)
    self.form_show()

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
        title=f"New Material - {document_id}",
        large=True,
        buttons=None 
      )
      self.load_materials()

    except Exception as e:
      alert(f"Error creating material: {str(e)}")

  def form_show(self, **event_args):
    # 1) Pull items from the server
    try:
      materials = anvil.server.call('get_material_cards_for_list')
    except Exception as e:
      Notification(f"Failed to load materials: {e}", style="danger").show()
      materials = []
  
    # 2) Clear and render cards
    self.flow_panel_materials.clear()
    for m in materials:
      from .MaterialCard import MaterialCard
      card = MaterialCard(item=m)   # your card gets the dict
      card.width = "100%"
      self.flow_panel_materials.add_component(card)


