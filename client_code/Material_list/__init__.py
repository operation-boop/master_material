from ._anvil_designer import Material_listTemplate
from anvil import *
import anvil.server
from ..Material_input_form import Material_input_form


class Material_list(Material_listTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.load_material_cards()
  

  def form_show(self, **event_args):
    self.load_material_cards()

  def add_btn_click(self, **event_args):
    """Creates new material with 'Creating' status and opens the popup"""
    try:
      result = anvil.server.call('create_new_master_material', 'test_user@example.com')
      # If your server now returns {"document_id": "..."}:
      document_id = result['document_id']
      Notification(f"Created new material: {document_id}", style="success", timeout=2).show()

      from ..Material_input_form import Material_input_form
      popup = Material_input_form(current_document_id=document_id)
      popup.set_event_handler("x-refresh-list", self.load_material_cards)

      alert(
        content=popup,
        title=None,
        large=True,
        buttons=None
      )
    except Exception as e:
      alert(f"Error creating material: {str(e)}")

  def load_material_cards(self, **event_args):
    try:
      self.repeating_panel_materials.items = anvil.server.call('list_material_cards')
    except Exception as e:
      alert(f"Could not load material cards: {e}", title="Load error")





  


