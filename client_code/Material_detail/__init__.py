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
from ..Material_edit_form import Material_edit_form
from ..Material_sku_input_form import Material_sku_input_form


class Material_detail(Material_detailTemplate):
  def __init__(self, material_data=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item = material_data

    sku_rows = anvil.server.call("get_material_sku")
    self.material_sku_repeating_panel.items = sku_rows

  def back_btn_click(self, **event_args):
    home = get_open_form()   # This is your Home form
    home.content_panel.clear()
    home.content_panel.add_component(Material_list(), full_width_row=True)
    #open_form('Material_list')


  def technical_specs_tab_btn_click(self, **event_args):
    self.technical_specs_panel.visible = True
    self.cost_details_panel.visible = False
    self.version_history_panel.visible = False
    self.material_sku_panel.visible = False

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

  def edit_btn_click(self, **event_args):
    # Get the Home form
    home_form = get_open_form()

    # Clear the content panel and add Material_details
    home_form.content_panel.clear()
    home_form.content_panel.add_component(
      Material_edit_form(material_data=self.item),
      full_width_row=True
    )

  def add_sku_btn_click(self, **event_args):
    # Get the Home form
    home_form = get_open_form()

    # Clear the content panel and add Material_details
    home_form.content_panel.clear()
    home_form.content_panel.add_component(
      Material_sku_input_form(),
      full_width_row=True
    )
