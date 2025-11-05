from ._anvil_designer import Costing_sheet_homeTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .Creating_cost_sheet_page import Creating_cost_sheet_page
from anvil_extras import augment

    
class Costing_sheet_home(Costing_sheet_homeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def button_create_new_sheet_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.card_costing_sheet_home.clear()
    self.card_costing_sheet_home.add_component(Creating_cost_sheet_page())
