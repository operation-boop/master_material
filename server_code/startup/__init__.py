import anvil.users
import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import api_docs_server

@anvil.server.callable
def server_status_check():
  return "Server is Online and APIs are Registered."