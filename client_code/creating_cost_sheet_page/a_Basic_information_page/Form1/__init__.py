from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    
    item_list_currency_types = []
    for row in app_tables.list_currency_types.search():
     item_list_currency_types.append((row["types"], row))

    item_list_stuff_user = []
    for row in app_tables.tabl_staff_users.search():
      item_list_stuff_user.append((row["staff"], row))

    self.drop_down_from_currency_type.items = item_list_currency_types
    self.drop_down_to_currency_type.items = item_list_currency_types
    self.drop_down_created_by.items = item_list_stuff_user
    # Any code you write here will run before the form opens.

  def button_add_click(self, **event_args):
    """This method is called when the button is clicked"""
    from_currency = self.drop_down_from_currency_type.selected_value
    to_currency = self.drop_down_to_currency_type.selected_value
    rate = self.text_box_rate.text
    date = self.date_picker_currency.date
    created_by = self.drop_down_created_by.selected_value
    anvil.server.call('add_exchange_data',
                      from_currency,
                      to_currency,
                      rate,
                      date,
                      created_by
                      
                      )
    Notification("Added, Thank you").show()

  def clear_inputs(self):

    self.drop_down_from_currency_type.items = ""
    self.drop_down_to_currency_type.items = ""
    self.text_box_rate.text = ""
    self.date_picker_currency.date = ""
    self.drop_down_created_by.items = ""




#class Form1(Form1Template):
#  def __init__(self, **properties):
#    self.init_components(**properties)
#
#    data = anvil.server.call('get_dropdown_lists')
#    self.drop_down_from_currency_type.items = data['currency']
#    self.drop_down_to_currency_type.items = data['currency']
#    self.drop_down_created_by.items = data['staff']