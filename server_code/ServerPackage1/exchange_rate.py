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

"""
Exchange Rate Operations Module
Handles exchange rate creation and tracking for cost sheet calculations.
"""

@anvil.server.callable
def create_exchange_rate(date, from_currency, to_currency, rate, user_id):
  """
    Create an exchange rate record.
    This helps track what rates were used for cost calculations.
    
    Args:
        date: Date this exchange rate is effective
        from_currency: "USD", "VND", or "RMB"
        to_currency: "USD", "VND", or "RMB"
        rate: Exchange rate value
        user_id: Who is creating this rate
    
    Returns:
        The newly created exchange rate record
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

  print(f"[Exchange] Created exchange rate: {from_currency} to {to_currency} = {rate}")
  return exchange_rate


@anvil.server.callable
def get_latest_exchange_rate(from_currency, to_currency):
  """
    Get the most recent exchange rate between two currencies.
    
    Args:
        from_currency: Currency to convert from
        to_currency: Currency to convert to
    
    Returns:
        The most recent exchange rate record, or None if not found
    """

  rates = app_tables.exchange_rates.search(
    from_currency=from_currency,
    to_currency=to_currency
  )

  # Sort by date to get most recent
  sorted_rates = sorted(rates, key=lambda x: x['date'], reverse=True)

  if len(sorted_rates) > 0:
    return sorted_rates[0]
  else:
    print(f"[Exchange] No exchange rate found for {from_currency} to {to_currency}")
    return None


@anvil.server.callable
def get_exchange_rate_on_date(from_currency, to_currency, target_date):
  """
    Get the exchange rate that was effective on a specific date.
    Finds the most recent rate before or on the target date.
    
    Args:
        from_currency: Currency to convert from
        to_currency: Currency to convert to
        target_date: The date to look up the rate for
    
    Returns:
        The exchange rate record effective on that date, or None
    """

  rates = app_tables.exchange_rates.search(
    from_currency=from_currency,
    to_currency=to_currency
  )

  # Filter rates that are on or before target date
  valid_rates = [r for r in rates if r['date'] <= target_date]

  if len(valid_rates) == 0:
    print(f"[Exchange] No exchange rate found before {target_date}")
    return None

    # Sort to get most recent before target date
  sorted_rates = sorted(valid_rates, key=lambda x: x['date'], reverse=True)

  return sorted_rates[0]


@anvil.server.callable
def list_all_exchange_rates():
  """
    Get all exchange rates in the system.
    Sorted by date (newest first).
    
    Returns:
        List of all exchange rate records
    """

  rates = app_tables.exchange_rates.search()

  # Sort by date, newest first
  sorted_rates = sorted(rates, key=lambda x: x['date'], reverse=True)

  return sorted_rates


@anvil.server.callable
def update_exchange_rate(exchange_rate_id, rate, user_id):
  """
    Update an existing exchange rate.
    Note: For audit purposes, consider creating a new rate instead of updating.
    
    Args:
        exchange_rate_id: Which exchange rate to update
        rate: New rate value
        user_id: Who is updating this
    
    Returns:
        The updated exchange rate record
    """

  exchange_rate = app_tables.exchange_rates.get_by_id(exchange_rate_id)
  user = app_tables.users.get_by_id(user_id)

  old_rate = exchange_rate['rate']
  exchange_rate['rate'] = rate

  print(f"[Exchange] Updated exchange rate from {old_rate} to {rate}")
  return exchange_rate


@anvil.server.callable
def delete_exchange_rate(exchange_rate_id):
  """
    Delete an exchange rate record.
    Be careful - this should only be done if the rate was entered incorrectly.
    
    Args:
        exchange_rate_id: Which exchange rate to delete
    """

  exchange_rate = app_tables.exchange_rates.get_by_id(exchange_rate_id)
  exchange_rate.delete()

  print("[Exchange] Deleted exchange rate")


@anvil.server.callable
def link_exchange_rates_to_cost_sheet(cost_sheet_version_id, exchange_rate_ids):
  """
    Link exchange rates to a cost sheet version.
    This records what rates were used for this costing.
    
    Args:
        cost_sheet_version_id: Which cost sheet version
        exchange_rate_ids: List of exchange rate IDs to link
    
    Returns:
        The updated cost sheet version
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  # Get exchange rate records
  rates = []
  for rate_id in exchange_rate_ids:
    rate = app_tables.exchange_rates.get_by_id(rate_id)
    rates.append(rate)

    # Store in cost sheet (using simple list column)
  cost_sheet_version['exchange_rates_used'] = rates

  print(f"[Exchange] Linked {len(rates)} exchange rates to cost sheet")
  return cost_sheet_version


@anvil.server.callable
def get_exchange_rates_for_cost_sheet(cost_sheet_version_id):
  """
    Get the exchange rates that were used for a cost sheet.
    
    Args:
        cost_sheet_version_id: Which cost sheet version
    
    Returns:
        List of exchange rates used in this cost sheet
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  rates = cost_sheet_version['exchange_rates_used'] or []

  return list(rates)


@anvil.server.callable
def convert_amount(amount, from_currency, to_currency, use_date=None):
  """
    Convert an amount from one currency to another.
    Uses the most recent exchange rate, or rate on a specific date.
    
    Args:
        amount: Amount to convert
        from_currency: Currency to convert from
        to_currency: Currency to convert to
        use_date: Optional - use rate from specific date
    
    Returns:
        Converted amount
    """

  # If currencies are the same, no conversion needed
  if from_currency == to_currency:
    return amount

    # Get the exchange rate
  if use_date:
    rate_record = get_exchange_rate_on_date(from_currency, to_currency, use_date)
  else:
    rate_record = get_latest_exchange_rate(from_currency, to_currency)

  if rate_record:
    converted = amount * rate_record['rate']
    print(f"[Exchange] Converted {amount} {from_currency} to {converted} {to_currency}")
    return converted
  else:
    # Fallback to simplified conversion if no rate found
    print(f"[Exchange] No rate found, using simplified conversion")
    if from_currency == "VND" and to_currency == "USD":
      return amount / 25000
    elif from_currency == "RMB" and to_currency == "USD":
      return amount / 7
    elif from_currency == "USD" and to_currency == "VND":
      return amount * 25000
    elif from_currency == "USD" and to_currency == "RMB":
      return amount * 7
    else:
      print(f"[Exchange] Cannot convert {from_currency} to {to_currency}")
      return amount
