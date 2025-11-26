from ._anvil_designer import MaterialCardTemplate
from anvil import *
import anvil.users
import anvil.server
from ...Material_detail import Material_detail

class MaterialCard(MaterialCardTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.set_verification_status(self.item['verification_status'].lower())

    user = anvil.users.get_user()
    is_admin = (user and user['role'] == 'Admin')

    self.verify_status.visible = is_admin 
    self.delete_btn.visible = is_admin

  def view_details_btn_click(self, **event_args):
    """Open material detail view"""
    if not self.item:
      alert("No item data!", title="Error")
      return

    doc_id = self.item.get("document_id")
    if not doc_id:
      alert("No document ID!", title="Error")
      return

    open_form("Material_detail", doc_id=doc_id)

  def verify_status_click(self, **event_args):
    """Verify material (Admin only)"""
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
      result = anvil.server.call('verify_material_version', doc_id)
      if result and result.get('ok'):  
        Notification(f"Verified: {result.get('message')}", title="Success", style="success").show()
        self.parent.raise_event('x-refresh-list')
      else:
        Notification(f"Verify call completed but returned: {result}", title="Notice", style="warning").show()
    except Exception as e:
      Notification(f"Verify failed: {e}", title="Error", style="danger").show()
    finally:
      self.verify_status.enabled = True

  def set_verification_status(self, status_value):
    """
    Sets the background color and text of the verification_status component
    based on the status_value.
    """
    status = (status_value or "").lower()

    if status == "submitted - verified":
      self.verification_status.background = "lightgreen"
      self.verification_status.text = "✓ Verified"
      self.verify_status.visible = False
    elif status == "submitted - unverified":
      self.verification_status.background = "orange"
      self.verification_status.text = "\u2717 Unverified"
      self.verify_status.visible = True
    elif status == "draft":
      self.verification_status.background = "#c7c7c7"
      self.verification_status.text = "📝 Draft"
      self.verify_status.visible = False
    else:
      self.verification_status.background = "#ffffff"
      self.verification_status.text = status.capitalize() if status else "Unknown"
      self.verify_status.visible = False

  def delete_btn_click(self, **event_args):
    doc_id = self.item.get('document_id')
    if not doc_id:
      Notification("Error: No Document ID found on this card.", style="danger").show()
      return

    if not confirm(f"Are you SURE you want to permanently delete {doc_id}?\nThis will remove all history and SKUs."):
      return

    self.delete_btn.enabled = False # Prevent double-clicks

    try:
      result_msg = anvil.server.call('delete_material', doc_id)
      self.remove_from_parent()
      Notification(result_msg, style="success").show()

      Notification(f"Material {doc_id} deleted.", style="success").show()

    except Exception as e:
      alert(f"Deletion failed: {str(e)}")
      self.delete_btn.enabled = True
