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


     # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.label_cost_type.text = cost_type
    self.label_cost_amount.text = cost_amount
    self.label_cost_currency.text = cost_currency
    self.label_status.text = status
    self.label_Vendor.text = vendor
    self.label_cost_in_usd.text = cost_in_usd






