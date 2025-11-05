from ._anvil_designer import Master_MatTemplate
from anvil import *
from anvil import Notification
import anvil.server

class Master_Mat(Master_MatTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Store the current document_id for testing
    self.current_document_id = None

  def btn_create_material_click(self, **event_args):
    result = anvil.server.call('create_new_master_material', 'test_user@example.com')
    self.current_document_id = result['document_id']
    self.lbl_result.text = f"Created: {result['document_id']}"
    self.lbl_ver.text = f"Version: {result['current_version_number']} | Status: Draft"
    self.update_ui_state()

  def btn_save_draft_click(self, **event_args):
    if not self.current_document_id:
      alert("Please create a material first!")
      return
      result = anvil.server.call('save_draft', self.current_document_id, 'test_user@example.com')

    if result['action'] == "new_version_created":
      self.lbl_ver.text = f"Version: {result['version']['ver_num']} | Status: Draft (NEW VERSION)"
    else:
      self.lbl_ver.text = f"Version: {result['version']['ver_num']} | Status: Draft (UPDATED)"

    self.update_ui_state()
    
  def btn_submit_click(self, **event_args):
    if not self.current_document_id:
      alert("Please create a material first!")
      return

    try:
      result = anvil.server.call('submit_version', self.current_document_id, 'test_user@example.com')
      self.lbl_ver.text = f"Version: {result['ver_num']} | Status: Submitted ✓"
      self.update_ui_state()
    except Exception as e:
      alert(str(e))

  def update_ui_state(self):
    """Enable/disable buttons based on current status"""
    if not self.current_document_id:
      self.btn_save_draft.enabled = False
      self.btn_submit.enabled = False
      return
  
    status = anvil.server.call('get_current_status', self.current_document_id)
    if status:
      self.btn_save_draft.enabled = True
      self.btn_submit.enabled = status['can_submit']