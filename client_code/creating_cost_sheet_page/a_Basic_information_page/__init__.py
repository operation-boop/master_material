from ._anvil_designer import a_Basic_information_pageTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .add_currency_rates_item import add_currency_rates_item

class a_Basic_information_page(a_Basic_information_pageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.load_currency_rate_information()
    self.content
    # Any code you write here will run before the form opens.


    self.load_currency_rate_information()

  def load_currency_rate_information(self):
    currency_information = anvil.server.call("view_exchange_rate_line").search()

    for currency_information in currency_information:
      print(currency_information["date"])