from ._anvil_designer import Client_input_formTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Client_input_form(Client_input_formTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.price_category.items = ["Low", "Medium", "High"]
    self.country.items = ["UK", "US", "Australia"]
    self.currency.items = ["USD", "VND"]

    # Any code you write here will run before the form opens.
  def create_btn_click(self, **event_args):
    client_name = self.client_name.text
    country = self.country.selected_value
    price_category = self.price_category.selected_value 
    max_account_value = float(self.max_account_value.text or 0)
    currency = self.currency.selected_value
    anvil.server.call(
      'add_client',
      client_name=client_name,
      price_category=price_category,
      country=country,
      max_account_value=max_account_value,
      currency=currency
    )
    Notification("Client created successfully!").show()
    self.raise_event("x-close-alert", value="ok")

  def cancel_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.raise_event("x-close-alert")

  def close_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.raise_event("x-close-alert")

