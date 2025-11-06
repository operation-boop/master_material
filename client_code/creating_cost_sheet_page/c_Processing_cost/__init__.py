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
  def __init__(self,
               cost_type,
               cost_amount,
               cost_currency,
               status,
               vendor,
               vendor_name,
               description,
               **properties
                ):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.load_view_processing_cost_line()  #activates funct "load_view_processing_cost_line()" when initalizing


    item_list_processing_cost_type = []
    for row in app_tables.list_processing_cost_type.search():
      item_list_processing_cost_type.append((row["type_name"], row))

    item_list_vendor = []
    for row in app_tables.list_vendor.search():
      item_list_vendor.append((row["vendor"], row))

    item_list_processing_cost_status = []
    for row in app_tables.list_processing_cost_status.search():
      item_list_processing_cost_status.append((row["status"], row))

    item_list_currency_types = []
    for row in app_tables.list_currency_types.search():
      item_list_currency_types.append((row["currency_types"], row))

    #   self.drop_down_processing_type = item_list_processing_cost_type
    #   self.drop_down_vendor_list = item_list_vendor
    #  self.drop_down_processing_type = item_list_processing_cost_type
    #  self.drop_down_currency_type = item_list_currency_types

    
  # Create a function that will allow the client side to interact
  # 'In this case, view the table' from the server side
  def load_view_processing_cost_line(self):
    row = anvil.server.call("view_processing_cost_line").search() #'.search()' allows for this function interate or "scan the table for values"

    for view_processing_cost_line in row:
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
      self.processing_cost_info_line.add_component(z)



      

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

  def button_add_click(self, **event_args):
    """This method is called when the button is clicked"""

    cost_type = self.drop_down_processing_type.selected_value
    cost_amount = self.text_box_cost_amount.text
    cost_currency = self.drop_down_currency_type.selected_value
    status = self.drop_down_status.selected_value
    vendor = self.drop_down_vendor_list.selected_value
    vendor_name = self.text_box_vendor_name.text
    description = self.text_area_processing_description.text
    anvil.server.call('add_exchange_rate_data',
                      cost_type,
                      cost_amount,
                      cost_currency,
                      status,
                      vendor,
                      vendor_name,
                      description,
                     )

    def clear_inputs(self):

      self.drop_down_processing_type.selected_value = ""
      self.drop_down_cost_amount.text = ""
      self.drop_down_currency_type.selected_value = ""
      self.drop_down_status.selected_value = ""
      self.drop_down_vendor_list.selected_value = ""
      self.text_box_vendor_name.text = ""
      self.text_area_processing_description = ""





