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
    """This method is called when the button is clicked"""
    try:
      # Call the server function to create new master material
      # Replace 'test_user@example.com' with actual user if you have Users service
      result = anvil.server.call('create_new_master_material', 'test_user@example.com')
    
      # Store the document_id for creating versions later
      self.current_document_id = result['document_id']
    
      # Display results
      self.lbl_result.text = f"✓ Created: {result['document_id']}"
      self.lbl_ver.text = f"Version: {result['current_version_number']} | Status: {result['current_version']['status']}"
    
      # Enable the create version button
      self.btn_create_version.enabled = True
    
      Notification("Master material created successfully!", style="success").show()
    
    except Exception as e:
      self.lbl_result.text = f"Error: {str(e)}"
      self.lbl_ver.text = ""
      Notification(f"Error: {str(e)}", style="danger").show()
  
  def btn_create_version_click(self, **event_args):
    """This method is called when the button is clicked"""
    if not self.current_document_id:
      Notification("Please create a material first!", style="warning").show()
      return
  
    try:
      # Call the server function to create new version
      result = anvil.server.call('create_new_version', self.current_document_id, 'test_user@example.com')
  
      # Get updated master material info
      master_material = anvil.server.call('get_master_material_with_latest_version', self.current_document_id)
  
      # Display results
      self.lbl_result.text = f"✓ Document: {self.current_document_id}"
      self.lbl_ver.text = f"Version: {master_material['current_version_number']} | Status: {master_material['current_version']['status']}"
  
      Notification(f"New version {result['ver_num']} created successfully!", style="success").show()
  
    except Exception as e:
      self.lbl_result.text = f"Error: {str(e)}"
      Notification(f"Error: {str(e)}", style="danger").show()