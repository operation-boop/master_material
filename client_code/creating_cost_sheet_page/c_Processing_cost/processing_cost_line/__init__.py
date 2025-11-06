from ._anvil_designer import processing_cost_lineTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class processing_cost_line(processing_cost_lineTemplate):
  def __init__(self, cost_type, cost_amount, cost_currency, status, vendor, cost_in_usd, **properties):



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



    
     # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.label_cost_type.text = cost_type
    self.label_cost_amount.text = cost_amount
    self.label_cost_currency.text = cost_currency
    self.label_status.text = status
    self.label_Vendor.text = vendor
    self.label_cost_in_usd.text = cost_in_usd






