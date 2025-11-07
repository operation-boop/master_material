from ._anvil_designer import MaterialCardTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Material_detail import Material_detail

class MaterialCard(MaterialCardTemplate):
  def _init_(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def refresh_click(self, **event_args):
    """Handle refresh if needed"""
    self.raise_event('x-refresh-list')

  def view_details_btn_click(self, **event_args):
    open_form('Material_detail')

    
