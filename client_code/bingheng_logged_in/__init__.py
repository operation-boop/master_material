from ._anvil_designer import bingheng_logged_inTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class bingheng_logged_in(bingheng_logged_inTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Store username
    self.username = username or "Guest"

    # Display welcome text and username
    self.label_welcome.text = f"Welcome, {self.username}"
    self.username_label.text = self.username

    # Control access to admin-only features
    self.update_admin_visibility()

  def update_admin_visibility(self):
    """Show or hide admin-only buttons"""
    if hasattr(self, "Style_SKU_button"):
      self.Style_SKU_button.visible = self.username.lower() == "admin"

  def sku(self, **event_args):
    """Handle click for SKU button"""
    if self.username.lower() == "admin":
      alert("Welcome Admin — Access granted to SKU Management.")
      open_form('Style_SKU', username=self.username)
    else:
      alert("Access denied. Only admin can access SKU functions.")

  def edit_button3(self, **event_args):
    """This method is called when the button is clicked"""
    open_form( 'Master_Style.Create_Form')
    pass

  def control_panel_click(self, **event_args):
    """Handle click for control panel button"""
    if self.username.lower() == "admin":
      alert("Welcome Admin — Access granted to Control Panel.")
      open_form('Control_Panel', username=self.username)
    else:
      alert("Access denied. Only admin can access Control Panel.")
    pass
