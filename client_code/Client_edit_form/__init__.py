from ._anvil_designer import Client_edit_formTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Client_edit_form(Client_edit_formTemplate):
  def __init__(self, client_data=None, on_saved=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item = client_data
    self.on_saved = on_saved
    self.country.items = ["UK", "US", "Australia", "Vietnam"]
    self.price_category.items = ["Low", "Medium", "High"]
    self.currency.items = ["USD", "VND", "EUR"]

    self.client_name.text = self.item['client_name']
    self.country.selected_value = self.item['country']
    self.price_category.selected_value = self.item['price_category']
    self.max_account_value.text = str(self.item['max_account_value'] or 0)
    self.currency.selected_value = self.item['currency']

  def edit_btn_click(self, **event_args):
    client_name = self.client_name.text
    country = self.country.selected_value
    price_category = self.price_category.selected_value
    max_account_value = float(self.max_account_value.text or 0)
    currency = self.currency.selected_value

    anvil.server.call(
      'update_client', 
      self.item.get_id(), 
      client_name,
      country,
      price_category,
      max_account_value,
      currency
    )
    if self.on_saved:
      self.on_saved()
    Notification("Update successfully", style="success").show()
    self.raise_event("x-close-alert")

  def cancel_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.raise_event("x-close-alert")

  def close_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.raise_event("x-close-alert")
