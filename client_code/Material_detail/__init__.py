from ._anvil_designer import Material_detailTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables


class Material_detail(Material_detailTemplate):
  def __init__(self, item=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item = item
    self.current_document_id = None



  def back_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Material_list')

  def technical_specs_tab_btn_click(self, **event_args):
    self.technical_specs_panel.visible = True
    self.cost_details_panel.visible = False
    self.version_history_panel.visible = False

  def cost_details_tab_btn_click(self, **event_args):
    self.cost_details_panel.visible = True
    self.technical_specs_panel.visible = False
    self.version_history_panel.visible = False
    self.material_sku_panel.visible = False

  def version_history_tab_btn_click(self, **event_args):
    self.version_history_panel.visible = True
    self.technical_specs_panel.visible = False
    self.cost_details_panel.visible = False
    self.material_sku_panel.visible = False

  def material_sku_tab_btn_click(self, **event_args):
    self.material_sku_panel.visible = True
    self.version_history_panel.visible = False
    self.technical_specs_panel.visible = False
    self.cost_details_panel.visible = False


  