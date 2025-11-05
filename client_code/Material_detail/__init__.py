from ._anvil_designer import Material_detailTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Material_list import Material_list


class Material_detail(Material_detailTemplate):
  def __init__(self, item=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item = item

    # Any code you write here will run before the form opens.

  def back_btn_click(self, **event_args):
    home = get_open_form()   # This is your Home form
    home.content_panel.clear()
    home.content_panel.add_component(Material_list(), full_width_row=True)


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
