import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
@anvil.server.callable

def add_exchange_data(date, from_currency, to_currency, rate, created_by):
  app_tables.tabl_exchange_rate.add_row(date=date, from_currency_1=from_currency, to_currency_1=to_currency,
    rate1=rate,
    created_at=datetime.now(),
    created_by1=created_by,
  )