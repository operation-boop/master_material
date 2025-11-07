from ._anvil_designer import wanyan_ver_cost_sheet_detailsTemplate
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


class wanyan_ver_cost_sheet_details(wanyan_ver_cost_sheet_detailsTemplate):
  def __init__(self, material_data=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item = material_data
    # Any code you write here will run before the form opens.

  def back_btn_click(self, **event_args):
    home = get_open_form()   # This is your Home form
    home.content_panel.clear()
    home.content_panel.add_component(Material_list(), full_width_row=True)
    #open_form('Material_list')


  def cost_breakdown_tab_btn_click(self, **event_args):
    self.cost_details_panel.visible = True
    self.version_history_panel.visible = False
    self.exchange_rates_panel.visible = False

  def version_history_tab_btn_click(self, **event_args):
    self.version_history_panel.visible = True
    self.cost_details_panel.visible = False
    self.exchange_rates_panel.visible = False

  def exchange_rates_tab_btn_click(self, **event_args):
    self.version_history_panel.visible = False
    self.cost_details_panel.visible = False
    self.exchange_rates_panel.visible = True

  def edit_btn_click(self, **event_args):
    # Get the Home form
    home_form = get_open_form()

    # Clear the content panel and add Material_details
    home_form.content_panel.clear()
    home_form.content_panel.add_component(
      Material_edit_form(material_data=self.item),
      full_width_row=True
    )
