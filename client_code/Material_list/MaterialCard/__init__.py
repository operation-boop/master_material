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

def btn_view_details_click(self, **event_args):
  # get document identifier
  doc_id = self.item.get("document_id") or self.item.get("document_uid")
  ver_num = self.item.get("ver_num")

  if not doc_id or ver_num is None:
    alert("Missing document id or version number for this item.", title="Error")
    return

  # Open DetailsForm and pass identifiers (we will fetch the fresh row inside the DetailsForm)
  open_form(Material_detail(document_id=doc_id, ver_num=ver_num))
    

    
