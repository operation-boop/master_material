from ._anvil_designer import Creating_cost_sheet_pageTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .a_Basic_information_page import a_Basic_information_page

#from costing import Costing_sheet_home

class Creating_cost_sheet_page(Creating_cost_sheet_pageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.

  def button_cancel_create_cost_sheet_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.card_costing_sheet_base.clear()
    self.card_costing_sheet_base.add_component(Costing_sheet_base())

  def radio_button_basic_information_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    self.column_panel_information.clear()
    self.column_panel_information.add_component(a_Basic_information_page())

