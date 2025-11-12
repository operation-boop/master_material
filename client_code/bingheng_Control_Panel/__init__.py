from ._anvil_designer import bingheng_Control_PanelTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class bingheng_Control_Panel(bingheng_Control_PanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.username = username or "Guest"

    # Access control
    if self.username.lower() != "admin":
      alert("Access denied. Only admin can access Control Panel.")
      open_form('Details_logged', username=self.username)
      return

    # Show admin greeting
    if hasattr(self, "label_admin"):
      self.label_admin.text = f"Admin Control Panel — Welcome, {self.username}"
    else:
      alert(f"Welcome Admin — {self.username}")

  def some_admin_function(self, **event_args):
    """Placeholder for admin-only actions"""
    alert("This is where you can add admin actions later.")

def button_backup_click(self, **event_args):
  """Backup all Data Tables when the backup button is clicked"""
  try:
    confirm_backup = confirm("This will back up all data tables.\nProceed?")
    if not confirm_backup:
      return

    # Call the server to generate the backup ZIP
    backup_zip = anvil.server.call('backup_fullstack')

    # Trigger download
    download(backup_zip)
    alert("✅ Backup completed successfully!\nA ZIP file has been downloaded.")

  except Exception as e:
    alert(f"❌ Backup failed: {e}")
