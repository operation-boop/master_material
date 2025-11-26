from ._anvil_designer import Material_listTemplate
from anvil import *
import anvil.users
import anvil.server
from ..Material_input_form import Material_input_form
from .MaterialCard import MaterialCard

class Material_list(Material_listTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    anvil.users.login_with_form()
    self.flow_panel_materials.add_event_handler('x-refresh-list', self.load_material_cards)
    self.material_card = anvil.server.call("list_material_cards")
    self.load_material_cards()


  def form_show(self, **event_args):
    self.load_material_cards()

  def add_btn_click(self, **event_args):
    """Opens the popup for creating new material WITHOUT creating database row yet"""
    try:
      from ..Material_input_form import Material_input_form
      popup = Material_input_form(current_document_id=None, item=None)
      popup.set_event_handler("x-refresh-list", self.load_material_cards)

      result = alert(
        content=popup,
        large=True,
        buttons=None
      )

      if result =="saved":
        self.refresh_data()

    except Exception as e:
      alert(f"Error opening form: {str(e)}")


  def load_material_cards(self, **event_args): ##
    self.flow_panel_materials.clear()      
    for c in self.material_card:
      card = MaterialCard(item=c)
      card.role = "fixed-card"
      # This applies the CSS height from Step 2
      self.flow_panel_materials.add_component(card, width="48%")

  def refresh_data(self):
    self.material_card = anvil.server.call("list_material_cards")
    self.load_material_cards()

  def logout_btn_click(self, **event_args):
    anvil.users.logout()
    open_form('Material_list')
