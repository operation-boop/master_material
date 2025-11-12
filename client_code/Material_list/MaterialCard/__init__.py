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
    user = anvil.users.get_user()
    if user and user['role'] == 'Admin':
      self.verify_status.visible = True
    else:
      self.verify_status.visible = False
    

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

  def verify_status_click(self, **event_args):
    if not self.item:
      alert("No item data!", title="Error")
      return
  
    doc_id = self.item['document_id']
    if not doc_id:
      alert("No document ID!", title="Error")
      return
  
    if not confirm(f"Verify material {doc_id}? This action can only be done by admins."):
      return
  
    self.verify_status.enabled = False
    try:
      result = anvil.server.call('verify_material', doc_id)
      if result and result.get('ok'):  
        Notification(f"Verified: {result.get('message')}", title="Success", style="success").show()
        self.parent.raise_event('x-refresh-list')
      else:
        Notification(f"Verify call completed but returned: {result}", title="Notice", style="warning").show()
    except Exception as e:
      Notification(f"Verify failed: {e}", title="Error", style="danger").show()
    finally:
      try:
        self.verify_status.enabled = True
      except Exception:
        pass

