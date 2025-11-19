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
Cost Sheet Helpers Module
Shared utility functions used across all cost sheet operations.
This module has NO dependencies on other modules.
"""

def get_current_version(cost_sheet_id):
  """
    Gets the current active version of a cost sheet.
    
    Args:
        cost_sheet_id: ID of the cost sheet
    
    Returns:
        The current cost_sheet_version row
    """
  cost_sheet = app_tables.cost_sheets.get_by_id(cost_sheet_id)
  current_version_num = cost_sheet['current_version']

  # Find the version with matching number
  current_version = app_tables.cost_sheet_versions.get(
    cost_sheet=cost_sheet,
    version_number=current_version_num
  )

  return current_version


def get_current_material_version(master_material_id):
  """
    Gets the current version of a master material.
    Used when adding materials to BOM.
    
    Args:
        master_material_id: ID of the master material
    
    Returns:
        The current master_material_version row
    """
  master_material = app_tables.master_materials.get_by_id(master_material_id)
  current_version_num = master_material['current_version']

  material_version = app_tables.master_material_versions.get(
    master_material=master_material,
    version_number=current_version_num
  )

  return material_version


def update_material_cost_total(bom_version_id):
  """
    Calculates total material cost from all BOM line items.
    Updates the cost sheet version with new total.
    
    Called after: add/update/delete BOM line items
    
    Args:
        bom_version_id: ID of the BOM version to recalculate
    """

  bom_version = app_tables.bom_versions.get_by_id(bom_version_id)

  # Get all line items for this BOM
  line_items = app_tables.bom_line_items.search(bom_version=bom_version)

  # Sum up costs
  total = 0.0
  for item in line_items:
    # Cost = net buying consumption * material cost in USD
    item_cost = item['net_buying_consumption'] * item['material_cost_in_usd']
    total += item_cost

    # Find the cost sheet version that uses this BOM
  cost_sheet_version = app_tables.cost_sheet_versions.get(bom_version=bom_version)
  if cost_sheet_version:
    cost_sheet_version['total_material_cost'] = total
    print(f"[Helper] Updated material cost total to ${total:.2f}")


def update_processing_cost_total(cost_sheet_version_id):
  """
    Sum all processing costs and update cost sheet.
    
    Called after: add/update/delete processing cost items
    
    Args:
        cost_sheet_version_id: ID of cost sheet version to recalculate
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  # Get all processing costs
  costs = app_tables.processing_cost_items.search(
    cost_sheet_version=cost_sheet_version
  )

  # Sum up (simplified - assumes all in USD for MVP)
  total = 0.0
  for cost in costs:
    # In real app, convert currencies properly
    if cost['cost_currency'] == "USD":
      total += cost['cost_amount']
    elif cost['cost_currency'] == "VND":
      total += cost['cost_amount'] / 25000
    else:  # RMB
      total += cost['cost_amount'] / 7

  cost_sheet_version['total_processing_cost'] = total
  print(f"[Helper] Updated processing cost total to ${total:.2f}")


def update_overhead_cost_total(cost_sheet_version_id):
  """
    Calculate total overhead costs by type.
    
    Called after: add/update/delete overhead cost items
    
    Args:
        cost_sheet_version_id: ID of cost sheet version to recalculate
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  # Get all overhead items
  items = app_tables.overhead_cost_items.search(
    cost_sheet_version=cost_sheet_version
  )

  # Initialize totals by type
  totals = {
    'import_logistics': 0.0,
    'export_logistics': 0.0,
    'vat': 0.0,
    'import_duty': 0.0,
    'material_testing': 0.0,
    'garment_testing': 0.0,
    'sampling': 0.0,
    'moq_surcharge': 0.0
  }

  # Sum by type
  for item in items:
    amount_usd = item['cost_amount']

    # Convert to USD (simplified)
    if item['cost_currency'] == "VND":
      amount_usd = amount_usd / 25000
    elif item['cost_currency'] == "RMB":
      amount_usd = amount_usd / 7

      # Add to appropriate category
    cost_type = item['cost_type'].lower().replace(' ', '_')
    if cost_type in totals:
      totals[cost_type] += amount_usd

    # Calculate grand total
  grand_total = sum(totals.values())

  # Store in cost sheet version (using simple columns for MVP)
  cost_sheet_version['total_overhead_cost'] = grand_total
  cost_sheet_version['overhead_import_logistics'] = totals['import_logistics']
  cost_sheet_version['overhead_export_logistics'] = totals['export_logistics']
  cost_sheet_version['overhead_vat'] = totals['vat']
  cost_sheet_version['overhead_import_duty'] = totals['import_duty']
  cost_sheet_version['overhead_material_testing'] = totals['material_testing']
  cost_sheet_version['overhead_garment_testing'] = totals['garment_testing']
  cost_sheet_version['overhead_sampling'] = totals['sampling']
  cost_sheet_version['overhead_moq_surcharge'] = totals['moq_surcharge']

  print(f"[Helper] Updated overhead cost total to ${grand_total:.2f}")


def get_cost_sheet_summary(cost_sheet_version_id):
  """
    Get a complete summary of a cost sheet version.
    Returns all the key numbers in one call - useful for displaying on UI.
    
    Returns dict with:
    - Material cost
    - Processing cost
    - Overhead cost
    - Total cost
    - All pricing scenarios
    
    Args:
        cost_sheet_version_id: ID of the cost sheet version
    
    Returns:
        Dictionary with all cost summary data
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  # Get costs
  material_cost = cost_sheet_version['total_material_cost'] or 0.0
  processing_cost = cost_sheet_version['total_processing_cost'] or 0.0
  overhead_cost = cost_sheet_version['total_overhead_cost'] or 0.0
  total_cost = material_cost + processing_cost + overhead_cost

  # Get all scenarios
  scenarios = app_tables.quoted_price_scenarios.search(
    cost_sheet_version=cost_sheet_version
  )

  scenario_list = []
  for s in scenarios:
    scenario_list.append({
      'id': s.get_id(),
      'quoted_price': s['quoted_price'],
      'currency': s['quoted_currency'],
      'gross_margin': s['expected_gross_margin'],
      'net_margin': s['expected_net_margin'],
      'gross_profit': s['expected_gross_profit'],
      'net_profit': s['expected_net_profit']
    })

  summary = {
    'material_cost': material_cost,
    'processing_cost': processing_cost,
    'overhead_cost': overhead_cost,
    'total_cost': total_cost,
    'status': cost_sheet_version['status'],
    'version_number': cost_sheet_version['version_number'],
    'scenarios': scenario_list
  }

  return summary


def recalculate_all_scenarios(cost_sheet_version_id):
  """
    Recalculate all pricing scenarios when costs change.
    Call this after updating BOM, processing costs, or overhead.
    
    Args:
        cost_sheet_version_id: ID of cost sheet version
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  # Get all scenarios
  scenarios = app_tables.quoted_price_scenarios.search(
    cost_sheet_version=cost_sheet_version
  )

  # Get updated costs
  material_cost = cost_sheet_version['total_material_cost'] or 0.0
  processing_cost = cost_sheet_version['total_processing_cost'] or 0.0
  overhead_cost = cost_sheet_version['total_overhead_cost'] or 0.0
  total_cost = material_cost + processing_cost + overhead_cost

  # Recalculate each scenario
  for scenario in scenarios:
    quoted_price = scenario['quoted_price']
    quoted_currency = scenario['quoted_currency']

    # Convert price to USD
    quoted_price_usd = quoted_price
    if quoted_currency == "VND":
      quoted_price_usd = quoted_price / 25000
    elif quoted_currency == "RMB":
      quoted_price_usd = quoted_price / 7

      # Recalculate metrics
    gross_profit = quoted_price_usd - total_cost
    gross_margin = (gross_profit / quoted_price_usd) if quoted_price_usd > 0 else 0.0
    net_profit = gross_profit
    net_margin = gross_margin

    # Update scenario
    scenario['quoted_price_usd'] = quoted_price_usd
    scenario['total_cost'] = total_cost
    scenario['expected_gross_margin'] = gross_margin
    scenario['expected_net_margin'] = net_margin
    scenario['expected_gross_profit'] = gross_profit
    scenario['expected_net_profit'] = net_profit

  print(f"[Helper] Recalculated {len(list(scenarios))} pricing scenarios")


def convert_currency_to_usd(amount, currency):
  """
    Simple currency conversion helper.
    For MVP, uses hardcoded rates. Later, use exchange_rates table.
    
    Args:
        amount: Amount to convert
        currency: "USD", "VND", or "RMB"
    
    Returns:
        Amount in USD
    """

  if currency == "USD":
    return amount
  elif currency == "VND":
    return amount / 25000  # Simplified rate
  elif currency == "RMB":
    return amount / 7  # Simplified rate
  else:
    print(f"[Helper] Unknown currency: {currency}, returning original amount")
    return amount

