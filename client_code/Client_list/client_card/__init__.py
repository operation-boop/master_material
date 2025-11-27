from ._anvil_designer import client_cardTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Client_details import Client_details

class client_card(client_cardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    price_category = self.item['price_category']
    max_account_value = self.item['max_account_value']

    # ---- Định dạng tiền ----
    formatted_value = f"{max_account_value:,.0f}"
    self.max_account_value.text = f"{formatted_value}"

    if price_category == "Low":
      self.price_category.foreground = "#1B5E20"             # green text
      self.price_category.background = "#C8E6C9"             # soft green bg
    elif price_category == "Medium":
      self.price_category.foreground = "#5D4037"             # red text
      self.price_category.background = "#FFE0B2"             # soft red bg
    else:   # pending case (None or "Pending")
      self.price_category.foreground = "#C62828"             # brownish yellow text
      self.price_category.background = "#FFCDD2"             # soft yellow bg

    self.price_category.role = "status-label"
    # Any code you write here will run before the form opens.

  def view_detail_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    home_form = get_open_form()

    # Clear the content panel and add Client_detail
    home_form.content_panel.clear()
    home_form.content_panel.add_component(
      Client_details(client_data=self.item),
      full_width_row=True
    )