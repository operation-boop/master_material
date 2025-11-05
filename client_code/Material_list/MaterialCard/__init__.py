from ._anvil_designer import MaterialCardTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class MaterialCard(MaterialCardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Make the card about half the width -> 2 per row
    self.card_1.width = "48%"     # use your Card component name
    self.card_1.margin = "0 1% 8px 0"   # right + bottom spacing
    # Any code you write here will run before the form opens.
