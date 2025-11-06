from ._anvil_designer import c_Processing_costTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .processing_cost_line import processing_cost_line

class c_Processing_cost(c_Processing_costTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.load_view_processing_cost_line()  #activates funct "load_view_processing_cost_line()" when initalizing

    
  # Create a function that will allow the client side to interact
  # 'In this case, view the table' from the server side
  def load_view_processing_cost_line(self):
    view_processing_cost_line = anvil.server.call("view_processing_cost_line").search() #'.search()' allows for this function interate or "scan the table for values"

    for view_processing_cost_line in view_processing_cost_line:
      z = processing_cost_line(cost_type=view_processing_cost_line["cost_type"],
                               cost_amount=view_processing_cost_line["cost_amount"],
                               cost_currency=view_processing_cost_line["cost_currency"],
                               status=view_processing_cost_line["status"],
                               vendor=view_processing_cost_line["vendor"],
                               vendor_name=view_processing_cost_line["vendor_name"],
                               description=view_processing_cost_line["description"],
                               cost_in_usd=view_processing_cost_line["cost_in_usd"],
                               button_callback=None
                              )
      




##  def load_currency_rate_information(self):
#    currency_information = anvil.server.call("view_exchange_rate_line").search()
#
#    for currency_information in currency_information:
#      print(currency_information["date"])
#
#  def button_add_exchange_rate_click(self, **event_args):
#    """This method is called when the button is clicked"""
#    v = add_currency_rates_item(from_currency="USD", to_currency="VND", created_by="Jonathan")
#    self.load_currency_rate_information()
#    self.column_panel_currency_rate_line.add_component(v)