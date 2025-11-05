from ._anvil_designer import Master_MatTemplate
from anvil import *
import anvil.server

class Master_Mat(Master_MatTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.current_document_id = None
    self.update_ui_state()

  def btn_create_material_click(self, **event_args):
    """Creates new material with 'Creating' status"""
    result = anvil.server.call('create_new_master_material', 'test_user@example.com')
    self.current_document_id = result['document_id']
    self.lbl_result.text = f"Created: {result['document_id']}"
    self.lbl_ver.text = f"Version: {result['current_version_number']} | Status: Creating"
    self.update_ui_state()
    # Clear textbox when creating new material
    self.txt_supplier.text = ""

  def btn_save_draft_click(self, **event_args):
    """Changes status to 'Draft' (same version)"""
    if not self.current_document_id:
      alert("Please create a material first!")
      return
    supplier_value = self.txt_supplier.text or ""
    anvil.server.call('update_supplier_field', self.current_document_id, supplier_value)
    result = anvil.server.call('save_as_draft', self.current_document_id, 'test_user@example.com')
    self.lbl_ver.text = f"Version: {result['version']['ver_num']} | Status: Draft"
    self.update_ui_state()

  def btn_edit_draft_click(self, **event_args):
    """Edits current draft (same version) - Supplier optional"""
    if not self.current_document_id:
      alert("Please create a material first!")
      return

    # Save supplier field (even if empty)
    supplier_value = self.txt_supplier.text or ""
    anvil.server.call('update_supplier_field', self.current_document_id, supplier_value)

    result = anvil.server.call('edit_draft', self.current_document_id, 'test_user@example.com')
    alert("Draft updated! (same version) - Supplier field is optional.")
    self.update_ui_state()

  def btn_submit_click(self, **event_args):
    """Submits current version - VALIDATES supplier is required"""
    if not self.current_document_id:
      alert("Please create a material first!")
      return

      # Save supplier field before submitting
    supplier_value = self.txt_supplier.text or ""
    anvil.server.call('update_supplier_field', self.current_document_id, supplier_value)

    try:
      result = anvil.server.call('submit_version', self.current_document_id, 'test_user@example.com')
      self.lbl_ver.text = f"Version: {result['ver_num']} | Status: Submitted ✓"
      alert("Submitted successfully!")
      self.update_ui_state()
    except Exception as e:
      alert(f"❌ Submission failed:\n{str(e)}")

  def btn_edit_submitted_click(self, **event_args):
    """Edits submitted version - creates NEW version"""
    if not self.current_document_id:
      alert("Please create a material first!")
      return

    try:
      result = anvil.server.call('edit_submitted', self.current_document_id, 'test_user@example.com')
      alert(f"New version {result['version']['ver_num']} created!")
      self.lbl_ver.text = f"Version: {result['version']['ver_num']} | Status: Creating"
      self.lbl_result.text = f"Document: {self.current_document_id} - Editing new version"

      # Clear textbox for new version
      self.txt_supplier.text = ""

      self.update_ui_state()
    except Exception as e:
      alert(f"❌ Edit failed:\n{str(e)}")

  def update_ui_state(self):
    """Enable/disable buttons based on current status"""
    if not self.current_document_id:
      self.btn_save_draft.enabled = False
      self.btn_edit_draft.enabled = False
      self.btn_submit.enabled = False
      self.btn_edit_submitted.enabled = False
      self.txt_supplier.enabled = False
      return

    status = anvil.server.call('get_current_status', self.current_document_id)
    if status:
      self.btn_save_draft.enabled = status['can_save_draft']
      self.btn_edit_draft.enabled = status['can_edit_draft']
      self.btn_submit.enabled = status['can_submit']
      self.btn_edit_submitted.enabled = status['can_edit_submitted']
      self.txt_supplier.enabled = True

      # Load current supplier value
      current_supplier = anvil.server.call('get_supplier_field', self.current_document_id)
      self.txt_supplier.text = current_supplier or ""

