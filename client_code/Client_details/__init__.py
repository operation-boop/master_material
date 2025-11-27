from ._anvil_designer import Client_detailsTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Client_list import Client_list


class Client_details(Client_detailsTemplate):
  def __init__(self, client_data=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item = client_data
    self.show_data()
    self.repeating_panel_contact.items = anvil.server.call('get_contacts')

  def show_data(self):
    self.client_name.text = self.item['client_name']
    self.country.selected_value = self.item['country']
    self.price_category.selected_value = self.item['price_category']

    max_account_value = self.item['max_account_value']
    currency = self.item['currency']
    formatted_value = f"{max_account_value:,.0f} {currency}"
    self.account_value.text = formatted_value
    formatted_max_value = f"{max_account_value:,.0f}"
    self.max_account_value.text = formatted_max_value
    self.currency.selected_value = self.item['currency']

  def refresh_data(self):
    try:
      client_id = self.item.get_id()
      updated_client = anvil.server.call('get_client_by_id', client_id)

      if updated_client:
        self.item = updated_client
        self.show_data()
      else:
        Notification("No data to update!", style="danger").show()
    except Exception as e:
      Notification(f"Error: {e}", style="danger").show()

  def edit_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    from ..Client_edit_form import Client_edit_form
    popup = Client_edit_form(
      client_data=self.item,
      on_saved=self.refresh_data   # callback
    )

    alert(
      content=popup,
      large=True,
      buttons=None
    )

  def return_btn_click(self, **event_args):
    home = get_open_form()   # This is your Home form
    home.content_panel.clear()
    home.content_panel.add_component(Client_list(), full_width_row=True)
