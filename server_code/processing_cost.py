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

# @anvil.server.callable
# def list_all_processing_cost():
#   processing_cost_item = app_tables.processing_cost_item.search()
#   return [dict(processing_cost_item) for processing_cost_item in processing_cost_item]


# ============================================
# PROCESSING COSTS - CRUD Operations
# ============================================

@anvil.server.callable
def add_processing_cost(cost_sheet_version_id, cost_type, cost_amount, 
                        cost_currency, vendor_name, description, user_id, 
                        supplier_id=None, status="Draft"):
  """
    Add a processing cost like Cut-make, Embroidery, or Washing.
    
    Args:
        cost_type: "Cut-make", "Embroidery", or "Washing"
        cost_amount: How much it costs
        cost_currency: USD, VND, or RMB
        vendor_name: Name of who does this work
        supplier_id: Optional - if approved vendor
        status: "Draft", "Unverified", or "Verified"
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  supplier = None
  if supplier_id:
    supplier = app_tables.suppliers.get_by_id(supplier_id)

  processing_cost = app_tables.processing_cost_items.add_row(
    cost_sheet_version=cost_sheet_version,
    cost_type=cost_type,
    cost_amount=cost_amount,
    cost_currency=cost_currency,
    status=status,
    vendor=supplier,
    vendor_name=vendor_name,
    description=description,
    created_at=datetime.now(),
    created_by=user,
    updated_at=datetime.now(),
    updated_by=user,
    last_verified_date=None,
    last_verified_by=None
  )

  # Update total processing cost
  update_processing_cost_total(cost_sheet_version_id)

  print(f"Added processing cost: {cost_type} - ${cost_amount}")
  return processing_cost


@anvil.server.callable
def update_processing_cost(processing_cost_id, cost_amount, cost_currency, 
                           vendor_name, description, user_id, status=None):
  """
    Update an existing processing cost.
    """

  processing_cost = app_tables.processing_cost_items.get_by_id(processing_cost_id)
  user = app_tables.users.get_by_id(user_id)

  processing_cost['cost_amount'] = cost_amount
  processing_cost['cost_currency'] = cost_currency
  processing_cost['vendor_name'] = vendor_name
  processing_cost['description'] = description
  processing_cost['updated_at'] = datetime.now()
  processing_cost['updated_by'] = user

  if status:
    processing_cost['status'] = status

    # Update total
  cost_sheet_version_id = processing_cost['cost_sheet_version'].get_id()
  update_processing_cost_total(cost_sheet_version_id)

  print("Updated processing cost")
  return processing_cost


@anvil.server.callable
def delete_processing_cost(processing_cost_id):
  """
    Remove a processing cost.
    """
  processing_cost = app_tables.processing_cost_items.get_by_id(processing_cost_id)
  cost_sheet_version_id = processing_cost['cost_sheet_version'].get_id()

  processing_cost.delete()

  # Update total
  update_processing_cost_total(cost_sheet_version_id)

  print("Deleted processing cost")


@anvil.server.callable
def list_processing_costs(cost_sheet_version_id):
  """
    Get all processing costs for a cost sheet version.
    """
  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  costs = app_tables.processing_cost_items.search(
    cost_sheet_version=cost_sheet_version
  )

  return list(costs)


def update_processing_cost_total(cost_sheet_version_id):
  """
    Helper function: Sum all processing costs and update cost sheet.
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
  print(f"Updated processing cost total to ${total:.2f}")

