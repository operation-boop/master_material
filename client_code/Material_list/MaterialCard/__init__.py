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
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    

  def refresh_click(self, **event_args):
    """Handle refresh if needed"""
    self.raise_event('x-refresh-list')

  def view_details_btn_click(self, **event_args):
    if not self.item:
      alert("No item data!", title="Error")
      return
    doc_id = self.item.get("document_id")
    if not doc_id:
      alert("No document ID!", title="Error")
      return
    open_form("Material_detail", doc_id=doc_id)