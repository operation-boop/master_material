import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from ..client_services import Module1
#
#    Module1.say_hello()
#

from ..server_services import auth

def log_in_optional():
  return auth.new_session_optional()

def log_in_forced():
  logged_in_user = auth.new_session_optional()
  return logged_in_user if logged_in_user else log_in_forced()

def log_out():
  auth.delete_session()