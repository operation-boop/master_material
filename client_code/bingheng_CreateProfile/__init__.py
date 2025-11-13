# from ._anvil_designer import bingheng_CreateProfileTemplate
# from anvil import *
# import anvil.tables as tables
# import anvil.tables.query as q
# from anvil.tables import app_tables
# import anvil.server
# import anvil.google.auth, anvil.google.drive
# from anvil.google.drive import app_files
# import anvil.users
# from datetime import datetime, date

# class bingheng_CreateProfile(bingheng_CreateProfileTemplate):
#   def __init__(self, **properties):
#     """Initialize the form"""
#     self.init_components(**properties)

#   # -----------------------------
#   # Submit Button
#   # -----------------------------
#   def submit_button1(self, **event_args):
#     """This method is called when the Submit button is clicked"""

#     # Get values from the TextBoxes
#     Enter_Your_Name = self.Enter_Your_Name.text.strip()
#     Contact_Number = self.Contact_Number.text.strip()
#     Email = self.Email.text.strip()
#     Address = self.Address.text.strip()

# Notification("Submitted").show()
# result = anvil.server.call('save_client_info', name, contact, email, address)

# alert(f"{result['message']}\nYour unique reference ID is: {result['ref_id']}")


# # Basic validation BEFORE sending to backend
# if not Enter_Your_Name or not Contact_Number:
#   alert("Please fill in both the Client Name and Contact Number.")
#   return

# # Now call your server function safely
# try:
#   result = anvil.server.call(
#     'save_client_info',
#     Enter_Your_Name,
#     Contact_Number,
#     Email,
#     Address
#   )
#   alert(result)

# except Exception as e:
#   alert(f"Error: {e}")

# # -----------------------------
# # Navigation Buttons
# # -----------------------------


# def home_button1(self, **event_args):
#   """Navigate to Home"""
# open_form('bingheng_Details_Page')

# # Any code you write here will run before the form opens.

###################################################
from ._anvil_designer import bingheng_CreateProfileTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
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
  def submit_button1(self, **event_args):
    """Called when the Submit button is clicked"""
    # Get values from the TextBoxes (use hasattr to avoid attribute errors)
    name = self.Enter_Your_Name.text.strip() if hasattr(self, "Enter_Your_Name") else ""
    contact = self.Contact_Number.text.strip() if hasattr(self, "Contact_Number") else ""
    email = self.Email.text.strip() if hasattr(self, "Email") else ""
    address = self.Address.text.strip() if hasattr(self, "Address") else ""

    # Basic validation BEFORE sending to backend
    if not name or not contact:
      alert("Please fill in both the Client Name and Contact Number.")
      return

    # Immediate feedback (Notification may not exist in all contexts)
    try:
      Notification("Submitting...").show()
    except Exception:
      pass

    # Call the server function safely
    try:
      result = anvil.server.call('save_client_info', name, contact, email, address)

      # If server returns a dict with ref_id, show it; otherwise show whatever it returned
      if isinstance(result, dict) and "ref_id" in result:
        alert(f"{result.get('message','Saved successfully')}\nYour unique reference ID is: {result['ref_id']}")
      else:
        alert(result)

      # Optionally clear inputs after successful save
      if hasattr(self, "Enter_Your_Name"):
        self.Enter_Your_Name.text = ""
      if hasattr(self, "Contact_Number"):
        self.Contact_Number.text = ""
      if hasattr(self, "Email"):
        self.Email.text = ""
      if hasattr(self, "Address"):
        self.Address.text = ""

    except Exception as e:
      alert(f"Error: {e}")

  # -----------------------------
  # Navigation Buttons
  # -----------------------------
  def home_button1(self, **event_args):
    """Navigate to Home"""
    open_form('bingheng_Details_Page')

