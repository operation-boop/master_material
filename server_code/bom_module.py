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

# Import helper functions from the helpers module
from . import cost_sheet_helpers as helpers

"""
BOM Operations Module
Handles all Bill of Material CRUD operations.
"""

@anvil.server.callable
def create_bom_for_cost_sheet(cost_sheet_version_id, user_id):
  """
    Creates a new Bill of Material for a cost sheet version.
    A BOM is where we list all materials needed for the style.
    
    Args:
        cost_sheet_version_id: Which cost sheet version to create BOM for
        user_id: Who is creating this
    
    Returns:
        The newly created BOM row
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  # Generate a document ID for the BOM
  document_id = f"BOM-{cost_sheet_version['document_id']}"

  # Create the BOM
  bom = app_tables.bill_of_materials.add_row(
    document_id=document_id,
    current_version=1,
    created_at=datetime.now(),
    created_by=user,
    submitted_at=None,
    submitted_by=None
  )

  # Create first BOM version
  bom_version = app_tables.bom_versions.add_row(
    bill_of_material=bom,
    document_id=document_id,
    version_number=1,
    change_description="Initial BOM",
    created_at=datetime.now(),
    created_by=user
  )

  # Link BOM version to cost sheet version
  cost_sheet_version['bom_version'] = bom_version

  print(f"[BOM] Created BOM {document_id} for cost sheet version")
  return bom


@anvil.server.callable
def add_bom_line_item(bom_version_id, master_material_id, gross_consumption, 
                      selling_tolerance, buying_tolerance, user_id):
  """
    Adds a material to the Bill of Material.
    
    Args:
        bom_version_id: Which BOM version to add to
        master_material_id: Which material to add
        gross_consumption: How much material needed (meters or pieces)
        selling_tolerance: Extra % for selling (0.05 = 5%)
        buying_tolerance: Extra % for buying (0.10 = 10%)
        user_id: Who is adding this
    
    Returns:
        The newly created BOM line item
    """

  bom_version = app_tables.bom_versions.get_by_id(bom_version_id)
  master_material = app_tables.master_materials.get_by_id(master_material_id)
  user = app_tables.users.get_by_id(user_id)

  # Calculate net consumptions
  net_selling = gross_consumption * (1 + selling_tolerance)
  net_buying = gross_consumption * (1 + buying_tolerance)

  # Get material cost from the master material's current version
  # Using helper function from cost_sheet_helpers
  material_version = helpers.get_current_material_version(master_material_id)
  material_cost_native = material_version['effective_cost_per_unit']
  native_currency = material_version['native_cost_currency']

  # Convert to USD using helper function
  material_cost_usd = helpers.convert_currency_to_usd(material_cost_native, native_currency)

  # Create the line item
  line_item = app_tables.bom_line_items.add_row(
    bom_version=bom_version,
    assigned_material=master_material,
    assigned_sku=None,  # Optional for MVP
    gross_consumption=gross_consumption,
    selling_tolerance=selling_tolerance,
    net_selling_consumption=net_selling,
    buying_tolerance=buying_tolerance,
    net_buying_consumption=net_buying,
    material_cost_in_native_currency=material_cost_native,
    native_currency=native_currency,
    material_cost_in_usd=material_cost_usd
  )

  # Update total material cost in cost sheet version
  # Using helper function from cost_sheet_helpers
  helpers.update_material_cost_total(bom_version_id)

  print(f"[BOM] Added material {master_material['name']} to BOM")
  return line_item


@anvil.server.callable
def update_bom_line_item(line_item_id, gross_consumption, selling_tolerance, buying_tolerance):
  """
    Update an existing BOM line item.
    Recalculates all the consumption values.
    
    Args:
        line_item_id: Which line item to update
        gross_consumption: Updated consumption amount
        selling_tolerance: Updated selling tolerance
        buying_tolerance: Updated buying tolerance
    
    Returns:
        The updated line item
    """

  line_item = app_tables.bom_line_items.get_by_id(line_item_id)

  # Recalculate net consumptions
  net_selling = gross_consumption * (1 + selling_tolerance)
  net_buying = gross_consumption * (1 + buying_tolerance)

  # Update the row
  line_item['gross_consumption'] = gross_consumption
  line_item['selling_tolerance'] = selling_tolerance
  line_item['net_selling_consumption'] = net_selling
  line_item['buying_tolerance'] = buying_tolerance
  line_item['net_buying_consumption'] = net_buying

  # Update total using helper function
  helpers.update_material_cost_total(line_item['bom_version'].get_id())

  print(f"[BOM] Updated BOM line item")
  return line_item


@anvil.server.callable
def delete_bom_line_item(line_item_id):
  """
    Remove a material from the BOM.
    
    Args:
        line_item_id: Which line item to delete
    """

  line_item = app_tables.bom_line_items.get_by_id(line_item_id)
  bom_version_id = line_item['bom_version'].get_id()

  # Delete the line item
  line_item.delete()

  # Update total using helper function
  helpers.update_material_cost_total(bom_version_id)

  print("[BOM] Deleted BOM line item")


@anvil.server.callable
def list_bom_line_items(bom_version_id):
  """
    Get all materials in a BOM.
    
    Args:
        bom_version_id: Which BOM version to list items for
    
    Returns:
        List of BOM line items
    """

  bom_version = app_tables.bom_versions.get_by_id(bom_version_id)

  items = app_tables.bom_line_items.search(
    bom_version=bom_version
  )

  return list(items)


@anvil.server.callable
def get_bom_summary(bom_version_id):
  """
    Get a summary of the BOM with total material cost.
    Useful for displaying BOM info on UI.
    
    Args:
        bom_version_id: Which BOM version
    
    Returns:
        Dictionary with BOM summary data
    """

  bom_version = app_tables.bom_versions.get_by_id(bom_version_id)
  line_items = list_bom_line_items(bom_version_id)

  # Calculate totals
  total_cost = 0.0
  total_consumption = 0.0
  material_count = len(line_items)

  for item in line_items:
    item_cost = item['net_buying_consumption'] * item['material_cost_in_usd']
    total_cost += item_cost
    total_consumption += item['net_buying_consumption']

  summary = {
    'bom_version': bom_version,
    'document_id': bom_version['document_id'],
    'version_number': bom_version['version_number'],
    'material_count': material_count,
    'total_cost': total_cost,
    'total_consumption': total_consumption,
    'line_items': line_items
  }

  return summary
