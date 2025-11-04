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
#    from ..server_services import Module1
#
#    Module1.say_hello()
#

from typing import Literal
from anvil.table import Row

_logged_in_user = None

def reset_password():
  anvil.users.change_password_with_form()

def new_session_optional():
  _logged_in_user = anvil.users.login_with_form(show_signup_option=False, allow_cancel=True)
  return _logged_in_user

def delete_session():
  anvil.users.logout()
  _logged_in_user = None

def get_user() -> Literal[Row, None]:
  global _logged_in_user

  if _logged_in_user:
    return _logged_in_user

  _logged_in_user = new_session_optional()
  return _logged_in_user

anvil.users.get_user()