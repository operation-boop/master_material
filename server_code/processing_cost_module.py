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
Processing Cost Operations Module
Handles all processing cost CRUD operations (Cut-make, Embroidery, Washing).
"""

@anvil.server.callable
def add_processing_cost(cost_sheet_version_id, cost_type, cost_amount, 
                        cost_currency, vendor_name, description, user_id, 
                        supplier_id=None, status="Draft"):
  """
    Add a processing cost like Cut-make, Embroidery, or Washing.
    
    Args:
        cost_sheet_version_id: Which cost sheet version to add to
        cost_type: "Cut-make", "Embroidery", or "Washing"
        cost_amount: How much it costs
        cost_currency: USD, VND, or RMB
        vendor_name: Name of who does this work
        description: Details about this processing cost
        user_id: Who is adding this
        supplier_id: Optional - if approved vendor
        status: "Draft", "Unverified", or "Verified"
    
    Returns:
        The newly created processing cost item
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

  # Update total processing cost using helper
  helpers.update_processing_cost_total(cost_sheet_version_id)

  print(f"[Processing] Added processing cost: {cost_type} - ${cost_amount}")
  return processing_cost


@anvil.server.callable
def update_processing_cost(processing_cost_id, cost_amount, cost_currency, 
                           vendor_name, description, user_id, status=None):
  """
    Update an existing processing cost.
    
    Args:
        processing_cost_id: Which processing cost to update
        cost_amount: Updated cost amount
        cost_currency: Updated currency
        vendor_name: Updated vendor name
        description: Updated description
        user_id: Who is updating this
        status: Optional - update status if provided
    
    Returns:
        The updated processing cost item
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

    # Update total using helper
  cost_sheet_version_id = processing_cost['cost_sheet_version'].get_id()
  helpers.update_processing_cost_total(cost_sheet_version_id)

  print("[Processing] Updated processing cost")
  return processing_cost


@anvil.server.callable
def delete_processing_cost(processing_cost_id):
  """
    Remove a processing cost.
    
    Args:
        processing_cost_id: Which processing cost to delete
    """

  processing_cost = app_tables.processing_cost_items.get_by_id(processing_cost_id)
  cost_sheet_version_id = processing_cost['cost_sheet_version'].get_id()

  processing_cost.delete()

  # Update total using helper
  helpers.update_processing_cost_total(cost_sheet_version_id)

  print("[Processing] Deleted processing cost")


@anvil.server.callable
def list_processing_costs(cost_sheet_version_id):
  """
    Get all processing costs for a cost sheet version.
    
    Args:
        cost_sheet_version_id: Which cost sheet version
    
    Returns:
        List of processing cost items
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  costs = app_tables.processing_cost_items.search(
    cost_sheet_version=cost_sheet_version
  )

  return list(costs)


@anvil.server.callable
def verify_processing_cost(processing_cost_id, user_id):
  """
    Mark a processing cost as verified by a supervisor.
    
    Args:
        processing_cost_id: Which processing cost to verify
        user_id: Who is verifying (should be supervisor)
    
    Returns:
        The updated processing cost item
    """

  processing_cost = app_tables.processing_cost_items.get_by_id(processing_cost_id)
  user = app_tables.users.get_by_id(user_id)

  processing_cost['status'] = "Verified"
  processing_cost['last_verified_date'] = datetime.now()
  processing_cost['last_verified_by'] = user

  print(f"[Processing] Verified processing cost: {processing_cost['cost_type']}")
  return processing_cost
