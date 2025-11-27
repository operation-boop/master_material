from ._anvil_designer import Supplier_edit_formTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Supplier_edit_form(Supplier_edit_formTemplate):
  def __init__(self, supplier_data=None, on_saved=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item = supplier_data
    self.on_saved = on_saved
    self.country.items = ["UK", "US", "Australia", "Vietnam"]

    self.supplier_name.text = self.item['supplier_name']
    self.country.selected_value = self.item['country']
    self.contact_person.text = self.item['contact_person']
    self.email.text = self.item['email']
    # Any code you write here will run before the form opens.

  def update_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    supplier_name = self.supplier_name.text
    country = self.country.selected_value
    contact_person = self.contact_person.text
    email = self.email.text

    anvil.server.call(
      'update_supplier',
      self.item.get_id(),
      supplier_name,
      country,
      contact_person,
      email
    )

    if self.on_saved:
      self.on_saved()

    Notification("Supplier updated successfully", style="success").show()
    self.raise_event("x-close-alert")

  def close_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.raise_event("x-close-alert")

  def cancel_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.raise_event("x-close-alert")
