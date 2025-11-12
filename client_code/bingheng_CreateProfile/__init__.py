from ._anvil_designer import bingheng_CreateProfileTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
from datetime import datetime, date

class bingheng_CreateProfile(bingheng_CreateProfileTemplate):
  def __init__(self, **properties):
    """Initialize the form"""
    self.init_components(**properties)

  # -----------------------------
  # Submit Button
  # -----------------------------
  def submit_button1_click(self, **event_args):
    """This method is called when the Submit button is clicked"""

    # Get values from the TextBoxes
    Enter_Your_Name = self.Enter_Your_Name.text.strip()
    Contact_Number = self.Contact_Number.text.strip()
    Email = self.Email.text.strip()
    Address = self.Address.text.strip()

    Notification("Submitted").show()

    # Basic validation BEFORE sending to backend
    if not Enter_Your_Name or not Contact_Number:
      alert("Please fill in both the Client Name and Contact Number.")
      return

    # Now call your server function safely
    try:
      result = anvil.server.call(
        'save_client_info',
        Enter_Your_Name,
        Contact_Number,
        Email,
        Address
      )
      alert(result)

    except Exception as e:
      alert(f"Error: {e}")

  # -----------------------------
  # Navigation Buttons
  # -----------------------------
  def create_button1_click(self, **event_args):
    """Navigate to Create Profile"""
    open_form('bingheng_CreateProfile')

  def update_button1_click(self, **event_args):
    """Navigate to Update Profile"""
    open_form('bingheng_CreateProfile')

  def edit_button1_click(self, **event_args):
    """Navigate to Edit Profile"""
    open_form('bingheng_CreateProfile')

  def home_button1_click(self, **event_args):
    """Navigate to Home"""
    open_form('bingheng_Details_Page')

    # Any code you write here will run before the form opens.
