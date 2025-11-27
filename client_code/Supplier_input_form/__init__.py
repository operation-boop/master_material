from ._anvil_designer import Supplier_input_formTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Supplier_input_form(Supplier_input_formTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.country.items = ['Vietnam', 'China']
    # Any code you write here will run before the form opens.

  def close_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.raise_event("x-close-alert")

  def cancel_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.raise_event("x-close-alert")

  def create_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    supplier_name = self.supplier_name.text
    country = self.country.selected_value
    contact_person = self.contact_person.text
    email = self.email.text

    anvil.server.call(
      'add_supplier',
      supplier_name=supplier_name,
      country=country,
      contact_person=contact_person,
      email=email
    )
    Notification("✅ Supplier added successfully!").show()
    self.raise_event("x-close-alert", value="ok")
