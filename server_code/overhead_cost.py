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
from . import cost_sheet_helpers as helpers

"""
Overhead Cost Operations Module
Handles all overhead cost CRUD operations (Tier 2 and Tier 3 costs).
"""

@anvil.server.callable
def add_overhead_cost_item(cost_sheet_version_id, name, cost_type, cost_amount, 
                           cost_currency, user_id, material_version_id=None):
  """
    Add an overhead cost item.
    
    Tier 2 (auto-calculated): Import/Export logistics, VAT, Import duty
    Tier 3 (user-added): Material testing, Garment testing, Sampling, MOQ surcharge
    
    Args:
        cost_sheet_version_id: Which cost sheet version to add to
        name: Description of this overhead cost
        cost_type: Type of overhead cost
        cost_amount: Cost value
        cost_currency: USD, VND, or RMB
        user_id: Who is adding this
        material_version_id: Optional - link to specific material if relevant
    
    Returns:
        The newly created overhead cost item
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  material_version = None
  if material_version_id:
    material_version = app_tables.master_material_versions.get_by_id(material_version_id)

  overhead_item = app_tables.overhead_cost_items.add_row(
    cost_sheet_version=cost_sheet_version,
    name=name,
    cost_type=cost_type,
    cost_amount=cost_amount,
    cost_currency=cost_currency,
    material_version=material_version,
    created_at=datetime.now(),
    created_by=user
  )

  # Update total overhead using helper
  helpers.update_overhead_cost_total(cost_sheet_version_id)

  print(f"[Overhead] Added overhead cost: {cost_type} - ${cost_amount}")
  return overhead_item


@anvil.server.callable
def update_overhead_cost_item(overhead_item_id, name, cost_amount, cost_currency, user_id):
  """
    Update an overhead cost item.
    
    Args:
        overhead_item_id: Which overhead item to update
        name: Updated description
        cost_amount: Updated cost amount
        cost_currency: Updated currency
        user_id: Who is updating this
    
    Returns:
        The updated overhead cost item
    """

  overhead_item = app_tables.overhead_cost_items.get_by_id(overhead_item_id)
  user = app_tables.users.get_by_id(user_id)

  overhead_item['name'] = name
  overhead_item['cost_amount'] = cost_amount
  overhead_item['cost_currency'] = cost_currency
  overhead_item['updated_at'] = datetime.now()
  overhead_item['updated_by'] = user

  # Update total using helper
  cost_sheet_version_id = overhead_item['cost_sheet_version'].get_id()
  helpers.update_overhead_cost_total(cost_sheet_version_id)

  print("[Overhead] Updated overhead cost")
  return overhead_item


@anvil.server.callable
def delete_overhead_cost_item(overhead_item_id):
  """
    Remove an overhead cost item.
    
    Args:
        overhead_item_id: Which overhead item to delete
    """

  overhead_item = app_tables.overhead_cost_items.get_by_id(overhead_item_id)
  cost_sheet_version_id = overhead_item['cost_sheet_version'].get_id()

  overhead_item.delete()

  # Update total using helper
  helpers.update_overhead_cost_total(cost_sheet_version_id)

  print("[Overhead] Deleted overhead cost")


@anvil.server.callable
def list_overhead_cost_items(cost_sheet_version_id):
  """
    Get all overhead costs for a cost sheet version.
    
    Args:
        cost_sheet_version_id: Which cost sheet version
    
    Returns:
        List of overhead cost items
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  items = app_tables.overhead_cost_items.search(
    cost_sheet_version=cost_sheet_version
  )

  return list(items)


@anvil.server.callable
def get_overhead_summary_by_type(cost_sheet_version_id):
  """
    Get overhead costs grouped by type.
    Useful for displaying Tier 2 vs Tier 3 costs separately.
    
    Args:
        cost_sheet_version_id: Which cost sheet version
    
    Returns:
        Dictionary with costs grouped by type
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  items = list_overhead_cost_items(cost_sheet_version_id)

  # Tier 2 costs (typically auto-calculated)
  tier2_types = ["Import logistics", "Export logistics", "VAT", "Import duty"]

  # Tier 3 costs (typically user-added)
  tier3_types = ["Material testing", "Garment testing", "Sampling", "MOQ surcharge"]

  tier2_items = []
  tier3_items = []
  tier2_total = 0.0
  tier3_total = 0.0

  for item in items:
    # Convert to USD for totals
    amount_usd = helpers.convert_currency_to_usd(item['cost_amount'], item['cost_currency'])

    if item['cost_type'] in tier2_types:
      tier2_items.append(item)
      tier2_total += amount_usd
    else:
      tier3_items.append(item)
      tier3_total += amount_usd

  summary = {
    'tier2_items': tier2_items,
    'tier2_total': tier2_total,
    'tier3_items': tier3_items,
    'tier3_total': tier3_total,
    'grand_total': tier2_total + tier3_total
  }

  return summary
