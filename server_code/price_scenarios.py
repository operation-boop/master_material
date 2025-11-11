import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# ============================================
# QUOTED PRICE SCENARIOS - CRUD Operations
# ============================================

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
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  # Get all costs (assuming all converted to USD)
  material_cost = cost_sheet_version['total_material_cost'] or 0.0
  processing_cost = cost_sheet_version['total_processing_cost'] or 0.0
  overhead_cost = cost_sheet_version['total_overhead_cost'] or 0.0

  total_cost = material_cost + processing_cost + overhead_cost

  # Convert quoted price to USD if needed
  quoted_price_usd = quoted_price
  if quoted_currency == "VND":
    quoted_price_usd = quoted_price / 25000
  elif quoted_currency == "RMB":
    quoted_price_usd = quoted_price / 7

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

  print(f"Added pricing scenario: ${quoted_price} {quoted_currency} = {gross_margin*100:.1f}% margin")
  return scenario


@anvil.server.callable
def update_quoted_price_scenario(scenario_id, quoted_price, quoted_currency, user_id):
  """
    Update a pricing scenario - recalculates everything.
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
  quoted_price_usd = quoted_price
  if quoted_currency == "VND":
    quoted_price_usd = quoted_price / 25000
  elif quoted_currency == "RMB":
    quoted_price_usd = quoted_price / 7

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

  print("Updated pricing scenario")
  return scenario


@anvil.server.callable
def delete_quoted_price_scenario(scenario_id):
  """
    Remove a pricing scenario.
    """
  scenario = app_tables.quoted_price_scenarios.get_by_id(scenario_id)
  scenario.delete()
  print("Deleted pricing scenario")


@anvil.server.callable
def list_quoted_price_scenarios(cost_sheet_version_id):
  """
    Get all pricing scenarios for a cost sheet version.
    """
  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  scenarios = app_tables.quoted_price_scenarios.search(
    cost_sheet_version=cost_sheet_version
  )

  return list(scenarios)
