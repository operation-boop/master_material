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
    document_id = None
    # 'self.item' is the card's dict returned by list_material_cards()
    if hasattr(self, "item") and self.item:
      document_id = self.item.get("document_id") or self.item.get("document_id")

    if not document_id:
      Notification("Document id not found.", style="warning").show()
      return
  
    # Create and show the detail form
    detail = Material_detail(document_id=document_id)
    from anvil import alert
    alert(detail, title="Material Details", large=True)

    
