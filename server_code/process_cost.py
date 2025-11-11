import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def list_all_processing_cost():
  processing_cost_item = app_tables.processing_cost_item.search()
  return [dict(processing_cost_item) for processing_cost_item in processing_cost_item]


