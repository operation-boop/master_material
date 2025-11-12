from ._anvil_designer import Details_PageTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Details_Page(Details_PageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
   self.clear_inputs()

  def clear_inputs(self):
    """Clear all input fields"""
    self.TextBox_Name.text = ""
    self.TextBox_ID.text = ""

  def submit_button2(self, **event_args):
    """This method is called when the Submit button is clicked"""
    # Get text box values
    client_name = self.TextBox_Name.text.strip()
    ref_id = self.TextBox_ID.text.strip()

    # Basic validation
    if not client_name or not ref_id:
      alert("Please fill in both Client Name and Reference ID.")
      return

    try:
      # Call the server function to verify login
      result = anvil.server.call('verify_client_login', client_name, ref_id)

      if result:
        alert(f"Welcome, {client_name}!")
        open_form('Master_Style.Details_logged', username=client_name)
      else:
        alert("Invalid name or ID. Please try again.")
    except Exception as e:
      alert(f"Login error: {e}")

    # ---- Navigation Buttons ----

  def create_button2(self, **event_args):
    """Go to Create Form"""
    open_form('Master_Style.Create_Form')

    # ---- TextBox Event Handlers (optional) ----
