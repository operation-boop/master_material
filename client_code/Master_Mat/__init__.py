from ._anvil_designer import Master_MatTemplate
import anvil.server
from anvil import alert

class Master_Mat(Master_MatTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.current_material = None
    self.update_status_label()

  def update_status_label(self):
    """Update the status label with current material info"""
    if self.current_material:
      self.lbl_status.text = f"Current: {self.current_material['document_id']} (v{self.current_material['current_version_number']})"
      self.lbl_status.foreground = "theme:Primary"
    else:
      self.lbl_status.text = "No material created yet"
      self.lbl_status.foreground = "theme:Gray"

  def log_output(self, message):
    """Log messages to text area if it exists"""
    if hasattr(self, 'ta_output'):
      self.ta_output.text += f"{message}\n"
    print(message)

  def btn_create_material_click(self, **event_args):
    """Test creating a new master material"""
    try:
      user = "test_user"
      self.current_material = anvil.server.call('create_new_master_material', user)

      alert(f"✅ New Master Material Created!\n"
            f"Document ID: {self.current_material['document_id']}\n"
            f"Version: {self.current_material['current_version_number']}")

      self.log_output(f"CREATED: {self.current_material['document_id']} v{self.current_material['current_version_number']}")
      self.update_status_label()

    except Exception as e:
      alert(f"❌ Error creating material: {str(e)}")
      self.log_output(f"ERROR creating material: {str(e)}")

  def btn_create_version_click(self, **event_args):
    """Test creating a new version for current material"""
    if not self.current_material:
      alert("❌ No current material. Create one first.")
      return

    try:
      user = "test_user"
      new_version = anvil.server.call('create_new_version', 
                                      self.current_material['document_id'], 
                                      user)

      # Refresh current material to get updated version
      self.current_material = anvil.server.call('get_master_material_with_latest_version', 
                                                self.current_material['document_id'])

      alert(f"✅ New Version Created!\n"
            f"New Version: v{self.current_material['current_version_number']}")

      self.log_output(f"NEW VERSION: v{self.current_material['current_version_number']} for {self.current_material['document_id']}")
      self.update_status_label()

    except Exception as e:
      alert(f"❌ Error creating version: {str(e)}")
      self.log_output(f"ERROR creating version: {str(e)}")

  def btn_get_status_click(self, **event_args):
    """Display current material and version info"""
    if not self.current_material:
      alert("❌ No current material selected.")
      return

    try:
      material = anvil.server.call('get_master_material_with_latest_version', 
                                   self.current_material['document_id'])

      versions = anvil.server.call('get_material_versions', 
                                   material['document_id'])

      version_info = "\n".join([f"v{v['ver_num']}: {v['status']}" 
                                for v in versions])

      alert(f"📋 Current Material:\n"
            f"Document ID: {material['document_id']}\n"
            f"Current Version: v{material['current_version_number']}\n"
            f"Created: {material['created_at']}\n\n"
            f"📚 All Versions:\n{version_info}")

      self.log_output(f"STATUS: {material['document_id']} has {len(versions)} versions")

    except Exception as e:
      alert(f"❌ Error getting status: {str(e)}")
      self.log_output(f"ERROR getting status: {str(e)}")

  def btn_submit_version_click(self, **event_args):
    """Test submitting the current version"""
    if not self.current_material:
      alert("❌ No current material selected.")
      return

    try:
      user = "test_user"
      submitted_version = anvil.server.call('submit_master_material_version', 
                                            self.current_material['document_id'], 
                                            user)

      alert(f"✅ Version Submitted!\n"
            f"Version: v{submitted_version['ver_num']}\n"
            f"Status: {submitted_version['status']}")

      self.log_output(f"SUBMITTED: v{submitted_version['ver_num']} of {self.current_material['document_id']}")

    except Exception as e:
      alert(f"❌ Error submitting version: {str(e)}")
      self.log_output(f"ERROR submitting version: {str(e)}")

  def btn_complete_test_click(self, **event_args):
    """Run a complete test sequence"""
    alert("🚀 Starting Complete Test Sequence...")
    self.log_output("=== STARTING COMPLETE TEST ===")

    try:
      # Step 1: Create new material
      user = "test_user"
      self.current_material = anvil.server.call('create_new_master_material', user)
      self.log_output(f"Step 1: Created {self.current_material['document_id']} v{self.current_material['current_version_number']}")
      self.update_status_label()

      # Step 2: Create a new version
      anvil.server.call('create_new_version', self.current_material['document_id'], user)
      self.current_material = anvil.server.call('get_master_material_with_latest_version', self.current_material['document_id'])
      self.log_output(f"Step 2: Created v{self.current_material['current_version_number']}")

      # Step 3: Submit current version
      anvil.server.call('submit_master_material_version', self.current_material['document_id'], user)
      self.log_output(f"Step 3: Submitted v{self.current_material['current_version_number']}")

      # Step 4: Create another version
      anvil.server.call('create_new_version', self.current_material['document_id'], user)
      self.current_material = anvil.server.call('get_master_material_with_latest_version', self.current_material['document_id'])
      self.log_output(f"Step 4: Created v{self.current_material['current_version_number']}")

      # Step 5: Show final status
      versions = anvil.server.call('get_material_versions', self.current_material['document_id'])
      version_info = ", ".join([f"v{v['ver_num']}({v['status']})" for v in versions])

      self.log_output(f"Step 5: Final - {version_info}")
      self.update_status_label()

      alert(f"✅ Complete Test Finished!\n"
            f"Final: {self.current_material['document_id']} v{self.current_material['current_version_number']}\n"
            f"All versions: {version_info}")

      self.log_output("=== COMPLETE TEST FINISHED ===")

    except Exception as e:
      error_msg = f"❌ Test failed: {str(e)}"
      alert(error_msg)
      self.log_output(f"TEST FAILED: {str(e)}")