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

# ============================================
# EXCHANGE RATE HELPERS
# ============================================

@anvil.server.callable
def create_exchange_rate(date, from_currency, to_currency, rate, user_id):
  """
    Create an exchange rate record.
    This helps track what rates were used for cost calculations.
    """

  user = app_tables.users.get_by_id(user_id)

  exchange_rate = app_tables.exchange_rates.add_row(
    date=date,
    from_currency=from_currency,
    to_currency=to_currency,
    rate=rate,
    created_at=datetime.now(),
    created_by=user
  )

  print(f"Created exchange rate: {from_currency} to {to_currency} = {rate}")
  return exchange_rate


@anvil.server.callable
def get_latest_exchange_rate(from_currency, to_currency):
  """
    Get the most recent exchange rate between two currencies.
    """

  rate = app_tables.exchange_rates.search(
    tables.order_by("date", ascending=False),
    from_currency=from_currency,
    to_currency=to_currency,
  )

  if len(rate) > 0:
    return rate[0]
  else:
    return None


@anvil.server.callable
def link_exchange_rates_to_cost_sheet(cost_sheet_version_id, exchange_rate_ids):
  """
    Link exchange rates to a cost sheet version.
    This records what rates were used for this costing.
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  # Get exchange rate records
  rates = []
  for rate_id in exchange_rate_ids:
    rate = app_tables.exchange_rates.get_by_id(rate_id)
    rates.append(rate)

    # Store in cost sheet (using simple list column)
  cost_sheet_version['exchange_rates_used'] = rates

  print(f"Linked {len(rates)} exchange rates to cost sheet")
  return cost_sheet_version

