from ._anvil_designer import creating_cost_sheet_pageTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .a_Basic_information_page import a_Basic_information_page
from .b_Bom_page import b_Bom_page
from .c_Processing_cost import c_Processing_cost
from .d_Overhead_cost import d_Overhead_cost
from .e_Profit_scenarios import e_Profit_scenarios



class creating_cost_sheet_page(creating_cost_sheet_pageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def button_cancel_create_cost_sheet_click(self, **event_args):
    """This method is called when the button is clicked"""
    from ..costing_sheet_home import costing_sheet_home
    from ..costing_sheet_base import costing_sheet_base
    base = get_open_form().content_panel.get_components()[0]
    base.card_costing_sheet_base.clear()
    base.card_costing_sheet_base.add_component(costing_sheet_home())












  

  def radio_button_basic_information_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    self.column_panel_information.clear()
    self.column_panel_information.add_component(a_Basic_information_page())

  def radio_button_bill_of_material_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    self.column_panel_information.clear()
    self.column_panel_information.add_component(b_Bom_page())

  def radio_button_processing_cost_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    self.column_panel_information.clear()
    self.column_panel_information.add_component(c_Processing_cost())

  def radio_button_overhead_cost_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    self.column_panel_information.clear()
    self.column_panel_information.add_component(d_Overhead_cost())

  def radio_button_profit_scenario_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    self.column_panel_information.clear()
    self.column_panel_information.add_component(e_Profit_scenarios())

