from ._anvil_designer import Material_listTemplate
from anvil import *
import anvil.server
from ..Material_input_form import Material_input_form


class Material_list(Material_listTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    anvil.users.login_with_form()
    self.repeating_panel_materials.add_event_handler('x-refresh-list', self.load_material_cards)
    self.load_material_cards()
  

  def form_show(self, **event_args):
    self.load_material_cards()

  def add_btn_click(self, **event_args):
    """Opens the popup for creating new material WITHOUT creating database row yet"""
    try:
      from ..Material_input_form import Material_input_form
      popup = Material_input_form(current_document_id=None, item=None)
      popup.set_event_handler("x-refresh-list", self.load_material_cards)

      alert(
        content=popup,
        title="Create New Material",
        large=True,
        buttons=None
      )
    except Exception as e:
      alert(f"Error opening form: {str(e)}")

  def load_material_cards(self, **event_args):
    try:
      self.repeating_panel_materials.items = anvil.server.call('list_material_cards')
    except Exception as e:
      alert(f"Could not load material cards: {e}", title="Load error")





  


