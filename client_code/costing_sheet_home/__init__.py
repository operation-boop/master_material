from ._anvil_designer import costing_sheet_homeTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..creating_cost_sheet_page import creating_cost_sheet_page




class costing_sheet_home(costing_sheet_homeTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def button_create_new_sheet_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.card_costing_sheet_home.clear()
    self.card_costing_sheet_home.add_component(creating_cost_sheet_page())
   