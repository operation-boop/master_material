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

# Import helper functions
from . import cost_sheet_helpers_module as helpers

"""
Pricing Scenarios Module
Handles all quoted price scenario operations with automatic margin/profit calculations.
"""

@anvil.server.callable
def add_quoted_price_scenario(cost_sheet_version_id, quoted_price, quoted_currency, user_id):
  """
    Add a pricing scenario - calculates margins and profits automatically.
    
    Calculations:
    - Total Cost = Material + Processing + Overhead
    - Gross Profit = Quoted Price - Total Cost
    - Gross Margin = Gross Profit / Quoted Price
    - Net Profit = Gross Profit (for MVP, same as gross)
    - Net Margin = Net Profit / Quoted Price
    
    Args:
        cost_sheet_version_id: Which cost sheet version to add to
        quoted_price: The price to quote to client
        quoted_currency: Currency of the quoted price
        user_id: Who is creating this scenario
    
    Returns:
        The newly created pricing scenario
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  # Get all costs (assuming all converted to USD)
  material_cost = cost_sheet_version['total_material_cost'] or 0.0
  processing_cost = cost_sheet_version['total_processing_cost'] or 0.0
  overhead_cost = cost_sheet_version['total_overhead_cost'] or 0.0

  total_cost = material_cost + processing_cost + overhead_cost

  # Convert quoted price to USD if needed
  quoted_price_usd = helpers.convert_currency_to_usd(quoted_price, quoted_currency)

  # Calculate metrics
  gross_profit = quoted_price_usd - total_cost
  gross_margin = (gross_profit / quoted_price_usd) if quoted_price_usd > 0 else 0.0

  # For MVP, net = gross
  net_profit = gross_profit
  net_margin = gross_margin

  # Create scenario
  scenario = app_tables.quoted_price_scenarios.add_row(
    cost_sheet_version=cost_sheet_version,
    quoted_currency=quoted_currency,
    quoted_price=quoted_price,
    quoted_price_usd=quoted_price_usd,
    total_cost=total_cost,
    expected_gross_margin=gross_margin,
    expected_net_margin=net_margin,
    expected_gross_profit=gross_profit,
    expected_net_profit=net_profit,
    created_at=datetime.now(),
    created_by=user
  )

  print(f"[Pricing] Added pricing scenario: ${quoted_price} {quoted_currency} = {gross_margin*100:.1f}% margin")
  return scenario


@anvil.server.callable
def update_quoted_price_scenario(scenario_id, quoted_price, quoted_currency, user_id):
  """
    Update a pricing scenario - recalculates everything.
    
    Args:
        scenario_id: Which scenario to update
        quoted_price: Updated quoted price
        quoted_currency: Updated currency
        user_id: Who is updating this
    
    Returns:
        The updated pricing scenario
    """

  scenario = app_tables.quoted_price_scenarios.get_by_id(scenario_id)
  cost_sheet_version = scenario['cost_sheet_version']
  user = app_tables.users.get_by_id(user_id)

  # Get costs
  material_cost = cost_sheet_version['total_material_cost'] or 0.0
  processing_cost = cost_sheet_version['total_processing_cost'] or 0.0
  overhead_cost = cost_sheet_version['total_overhead_cost'] or 0.0
  total_cost = material_cost + processing_cost + overhead_cost

  # Convert price
  quoted_price_usd = helpers.convert_currency_to_usd(quoted_price, quoted_currency)

  # Recalculate
  gross_profit = quoted_price_usd - total_cost
  gross_margin = (gross_profit / quoted_price_usd) if quoted_price_usd > 0 else 0.0
  net_profit = gross_profit
  net_margin = gross_margin

  # Update scenario
  scenario['quoted_currency'] = quoted_currency
  scenario['quoted_price'] = quoted_price
  scenario['quoted_price_usd'] = quoted_price_usd
  scenario['total_cost'] = total_cost
  scenario['expected_gross_margin'] = gross_margin
  scenario['expected_net_margin'] = net_margin
  scenario['expected_gross_profit'] = gross_profit
  scenario['expected_net_profit'] = net_profit
  scenario['updated_at'] = datetime.now()
  scenario['updated_by'] = user

  print("[Pricing] Updated pricing scenario")
  return scenario


@anvil.server.callable
def delete_quoted_price_scenario(scenario_id):
  """
    Remove a pricing scenario.
    
    Args:
        scenario_id: Which scenario to delete
    """

  scenario = app_tables.quoted_price_scenarios.get_by_id(scenario_id)
  scenario.delete()
  print("[Pricing] Deleted pricing scenario")


@anvil.server.callable
def list_quoted_price_scenarios(cost_sheet_version_id):
  """
    Get all pricing scenarios for a cost sheet version.
    
    Args:
        cost_sheet_version_id: Which cost sheet version
    
    Returns:
        List of pricing scenarios
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  scenarios = app_tables.quoted_price_scenarios.search(
    cost_sheet_version=cost_sheet_version
  )

  return list(scenarios)


@anvil.server.callable
def recalculate_all_scenarios(cost_sheet_version_id):
  """
    Recalculate all pricing scenarios when costs change.
    Call this after updating BOM, processing costs, or overhead.
    This is a wrapper around the helper function for frontend use.
    
    Args:
        cost_sheet_version_id: Which cost sheet version
    """

  helpers.recalculate_all_scenarios(cost_sheet_version_id)
  print("[Pricing] Recalculated all scenarios")


@anvil.server.callable
def compare_scenarios(cost_sheet_version_id):
  """
    Get all scenarios side-by-side for easy comparison.
    Useful for displaying multiple pricing options to choose from.
    
    Args:
        cost_sheet_version_id: Which cost sheet version
    
    Returns:
        List of scenario comparisons
    """

  scenarios = list_quoted_price_scenarios(cost_sheet_version_id)

  comparison = []
  for scenario in scenarios:
    comparison.append({
      'id': scenario.get_id(),
      'quoted_price': f"${scenario['quoted_price']:.2f} {scenario['quoted_currency']}",
      'quoted_price_usd': f"${scenario['quoted_price_usd']:.2f}",
      'total_cost': f"${scenario['total_cost']:.2f}",
      'gross_profit': f"${scenario['expected_gross_profit']:.2f}",
      'gross_margin': f"{scenario['expected_gross_margin']*100:.1f}%",
      'net_profit': f"${scenario['expected_net_profit']:.2f}",
      'net_margin': f"{scenario['expected_net_margin']*100:.1f}%"
    })

  return comparison
