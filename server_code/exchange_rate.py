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
def add_exchange_data(date, from_currency, to_currency, rate, created_at, created_by):
  # Step 1: Find the current highest server_id
  existing_rows = app_tables.tabl_exchange_rate.search()

  if len(existing_rows) == 0:
    next_id = 1
  else:
    # get max server_id from all rows
    max_row = max(existing_rows, key=lambda r: r['server_id'])
    next_id = max_row['server_id'] + 1

  # Step 2: Add the new record
  new_row = app_tables.tabl_exchange_rate.add_row(
    server_id=next_id,
    date=date.now(),
    from_currency=from_currency,
    to_currency=to_currency,
    rate=rate,
    created_at=datetime.now(),
    created_by=created_by
  )

  return new_row

