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
# OVERHEAD COSTS - CRUD Operations
# ============================================

@anvil.server.callable
def add_overhead_cost_item(cost_sheet_version_id, name, cost_type, cost_amount, 
                           cost_currency, user_id, material_version_id=None):
  """
    Add an overhead cost item.
    
    Tier 2 (auto-calculated): Import/Export logistics, VAT, Import duty
    Tier 3 (user-added): Material testing, Garment testing, Sampling, MOQ surcharge
    
    Args:
        cost_type: Type of overhead cost
        cost_amount: Cost value
        material_version_id: Optional - link to specific material if relevant
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

  # Update total overhead
  update_overhead_cost_total(cost_sheet_version_id)

  print(f"Added overhead cost: {cost_type} - ${cost_amount}")
  return overhead_item


@anvil.server.callable
def update_overhead_cost_item(overhead_item_id, name, cost_amount, cost_currency, user_id):
  """
    Update an overhead cost item.
    """

  overhead_item = app_tables.overhead_cost_items.get_by_id(overhead_item_id)
  user = app_tables.users.get_by_id(user_id)

  overhead_item['name'] = name
  overhead_item['cost_amount'] = cost_amount
  overhead_item['cost_currency'] = cost_currency
  overhead_item['updated_at'] = datetime.now()
  overhead_item['updated_by'] = user

  # Update total
  cost_sheet_version_id = overhead_item['cost_sheet_version'].get_id()
  update_overhead_cost_total(cost_sheet_version_id)

  print("Updated overhead cost")
  return overhead_item


@anvil.server.callable
def delete_overhead_cost_item(overhead_item_id):
  """
    Remove an overhead cost item.
    """
  overhead_item = app_tables.overhead_cost_items.get_by_id(overhead_item_id)
  cost_sheet_version_id = overhead_item['cost_sheet_version'].get_id()

  overhead_item.delete()

  # Update total
  update_overhead_cost_total(cost_sheet_version_id)

  print("Deleted overhead cost")


@anvil.server.callable
def list_overhead_cost_items(cost_sheet_version_id):
  """
    Get all overhead costs for a cost sheet version.
    """
  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  items = app_tables.overhead_cost_items.search(
    cost_sheet_version=cost_sheet_version
  )

  return list(items)


def update_overhead_cost_total(cost_sheet_version_id):
  """
    Helper function: Calculate total overhead costs by type.
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

  print(f"Updated overhead cost total to ${grand_total:.2f}")

