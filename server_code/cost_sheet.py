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
def list_all_cost_sheets():
  return app_tables.tabl_cost_sheet.search()

@anvil.server.callable
def list_all_cost_sheet_versions():
  return app_tables.tabl_cost_sheet_version.search()

def list_all_cost_sheets_simple():
  return app_tables.tabl_cost_sheet