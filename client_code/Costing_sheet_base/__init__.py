from ._anvil_designer import Costing_sheet_baseTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Costing_sheet_home import Costing_sheet_home


class Costing_sheet_base(Costing_sheet_baseTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.card_costing_sheet_base.add_component(Costing_sheet_home())
    # Any code you write here will run before the form opens.

