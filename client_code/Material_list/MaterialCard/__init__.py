from ._anvil_designer import MaterialCardTemplate
from anvil import *
import anvil.server
import anvil.users
from ...Material_detail import Material_detail

class MaterialCard(MaterialCardTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.set_verification_status(self.item['verification_status'].lower())
    user = anvil.users.get_user()
    self.verify_status.visible = (user and user['role'] == 'Admin')
    
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
    """Delete material (Admin only)"""
    if not self.item:
      alert("No item data!", title="Error")
      return
    doc_id = self.item['document_id']
    material_name = self.item.get('material_name', 'this material')
    if not doc_id:
      alert("No document ID!", title="Error")
      return
    # Confirm deletion
    if not confirm(
      f"Are you sure you want to DELETE {doc_id} ({material_name})?\n\n"
      "This will permanently delete the material and all its versions. "
      "This action CANNOT be undone!",
      title="⚠️ Confirm Deletion"
    ):
      return
    self.delete_btn.enabled = False
    try:
      result = anvil.server.call('delete_material', doc_id)
      if result and result.get('ok'):  
        Notification(f"Deleted: {result.get('message')}", title="Success", style="success").show()
        # Refresh the list to remove the deleted card
        self.parent.raise_event('x-refresh-list')
      else:
        Notification(f"Delete call completed but returned: {result}", title="Notice", style="warning").show()
    except Exception as e:
      Notification(f"Delete failed: {e}", title="Error", style="danger").show()
      self.delete_btn.enabled = True  # Re-enable if there's an error
    pass
