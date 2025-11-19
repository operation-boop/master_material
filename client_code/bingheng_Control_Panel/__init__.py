from ._anvil_designer import bingheng_Control_PanelTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

#Creating a class for this control panel form
class bingheng_Control_Panel(bingheng_Control_PanelTemplate):
  def __init__(self, username=None, **properties):
    self.init_components(**properties)
    self.username = username or "Guest"

    if self.username.lower() != "admin":
      alert("Access denied. Only admin can access Control Panel.")
      open_form('bingheng_logged_in', username=self.username)
      return
      # hasattr = has attributes so if it stores a value in it, it will be true, else false will come back.
    if hasattr(self, "label_admin"):
      self.label_admin.text = f"Admin Control Panel — Welcome, {self.username}"
    else:
      alert(f"Welcome Admin — {self.username}")

  # Adding additional admin functions for future use.
  def some_admin_function(self, **event_args):
    alert("This is where you can add admin actions later.")

  # Make sure this method name matches the button's event in the Designer.
  def button_backup(self, **event_args):
    """Backup all Data Tables when the backup button is clicked"""
    try:
      if not confirm("This will back up all data tables and app files. Proceed?"):
        return

      # Call the server to generate the backup ZIP (server returns anvil.media.Media)
      backup_media = anvil.server.call('backup_fullstack')

      if backup_media is None:
        alert("❌ Backup failed: server returned nothing.")
        return

      # Trigger download in the browser
      download(backup_media)
      alert("✅ Backup completed successfully — a ZIP was downloaded.")
      # Adding an alert
    except Exception as e:
      alert(f"❌ Backup failed: {e}")