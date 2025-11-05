from ._anvil_designer import Costing_sheet_baseTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .Costing_sheet_home import Costing_sheet_home


class Costing_sheet_base(Costing_sheet_baseTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.card_costing_sheet_base.clear()
    self.card_costing_sheet_base.add_component(Costing_sheet_home())
    # Any code you write here will run before the form opens.
    
    # Define the function that clears this panel
    def clear_card_costing_sheet_base():
      self.card_costing_sheet_base.clear()

    # Pass that function down to the child
    base = Costing_sheet_base(clear_fn=clear_card_costing_sheet_base)
    self.card_costing_sheet_base.add_component(base)


    def clear_main_card():
      self.main_card.clear()

    base = Costing_sheet_base(clear_fn=clear_main_card)
    self.main_slot.add_component(base)



#    # pass a function that performs the action (clear + optionally show something)
#    def clear_card_costing_sheet_base():
#      self.card_costing_sheet_base.clear()
#    child = Costing_sheet_home(clear_fn=clear_card_costing_sheet_base)
#   self.card_costing_sheet_base.add_component(child)
