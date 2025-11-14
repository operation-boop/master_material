from ._anvil_designer import bingheng_logged_inTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

######################################
class bingheng_logged_in(bingheng_logged_inTemplate):
  def __init__(self, username=None, **properties):
    """Initialize the form and set up user session"""
    # Initialize form properties and components
    self.init_components(**properties)

    # Store username (default to Guest if not provided)
    self.username = username or "Guest"

    # Display welcome text and username
    if hasattr(self, "label_welcome"):
      self.label_welcome.text = f"Welcome, {self.username}"
    if hasattr(self, "username_label"):
      self.username_label.text = self.username

    # Update admin visibility
    self.update_admin_visibility()

  # -----------------------------
  # Admin visibility controller
  # -----------------------------
  def update_admin_visibility(self):
    """Show or hide admin-only buttons"""
    if hasattr(self, "Style_SKU_button"):
      self.Style_SKU_button.visible = (self.username.lower() == "admin")
    if hasattr(self, "control_panel_button"):
      self.control_panel_button.visible = (self.username.lower() == "admin")

  # -----------------------------
  # Button event handlers
  # -----------------------------
  def button_sku(self, **event_args):
    """Handle click for SKU button"""
    if self.username.lower() == "admin":
      alert("Welcome Admin — Access granted to SKU Management.")
      open_form('bingheng_Style_SKU', username=self.username)
    else:
      alert("Access denied. Only admin can access SKU functions.")

  # def edit_button3(self, **event_args):
  #   """Handle click for Create Profile button"""
  #   open_form('bingheng_CreateProfile')

  def control_panel(self, **event_args):
    """Handle click for Control Panel button"""
    if self.username.lower() == "admin":
      alert("Welcome Admin — Access granted to Control Panel.")
      open_form('bingheng_Control_Panel', username=self.username)
    else:
      alert("Access denied. Only admin can access Control Panel.")

#######################################

  def back_button1(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('bingheng_Details_Page')
    pass

 

