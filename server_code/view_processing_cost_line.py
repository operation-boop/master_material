import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:


# Makes it so that this funct "view_processing_cost_line" can act as a link
# to the backend for the front end to view ".client_readable()"
@anvil.server.callable
def view_processing_cost_line():
  return app_tables.tabl_processing_cost_item.client_readable()