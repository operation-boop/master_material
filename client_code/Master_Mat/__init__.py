from ._anvil_designer import Master_MatTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

class Master_Mat(Master_MatTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.current_doc_id = None

  def button_create_new_click(self, **event_args):
    """Create a brand new master material"""
    try:
      result = anvil.server.call('create_new_master_material')
      self.current_doc_id = result['doc_id']
      self.label_result.text = f"✅ Created NEW: {result['doc_id']} (Version {result['ver_num']})"
      self.button_create_version.enabled = True
      self.button_get_versions.enabled = True
    except Exception as e:
      self.label_result.text = f"❌ Error: {str(e)}"

  def button_create_version_click(self, **event_args):
    """Create a new version of current material"""
    if not self.current_doc_id:
      alert("Please create a new material first!")
      return

    try:
      result = anvil.server.call('create_new_version', self.current_doc_id)
      self.label_result.text = f"✅ Created VERSION: {result['doc_id']} (Version {result['ver_num']})"
    except Exception as e:
      self.label_result.text = f"❌ Error: {str(e)}"

  def button_get_versions_click(self, **event_args):
    """Get all versions of current material"""
    if not self.current_doc_id:
      alert("Please create a new material first!")
      return

    try:
      versions = anvil.server.call('get_material_versions', self.current_doc_id)
      version_list = "\n".join([f"• Version {v['ver_num']} (ID: {v['id']})" for v in versions])
      self.label_result.text = f"📋 Versions of {self.current_doc_id}:\n{version_list}"
    except Exception as e:
      self.label_result.text = f"❌ Error: {str(e)}"

  def button_get_latest_click(self, **event_args):
    """Get latest version of current material"""
    if not self.current_doc_id:
      alert("Please create a new material first!")
      return

    try:
      latest = anvil.server.call('get_latest_version', self.current_doc_id)
      if latest:
        self.label_result.text = f"🎯 LATEST: {latest['doc_id']} (Version {latest['ver_num']})"
      else:
        self.label_result.text = "No versions found!"
    except Exception as e:
      self.label_result.text = f"❌ Error: {str(e)}"

  def button_clear_click(self, **event_args):
    """Clear results and reset"""
    self.current_doc_id = None
    self.label_result.text = "Click buttons to test versioning system"
    self.button_create_version.enabled = False
    self.button_get_versions.enabled = False
