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
# BILL OF MATERIAL (BOM) - CRUD Operations
# ============================================

@anvil.server.callable
def create_bom_for_cost_sheet(cost_sheet_version_id, user_id):
  """
    Creates a new Bill of Material for a cost sheet version.
    A BOM is where we list all materials needed for the style.
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

  print(f"Created BOM {document_id} for cost sheet version")
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
    """

  bom_version = app_tables.bom_versions.get_by_id(bom_version_id)
  master_material = app_tables.master_materials.get_by_id(master_material_id)
  user = app_tables.users.get_by_id(user_id)

  # Calculate net consumptions
  net_selling = gross_consumption * (1 + selling_tolerance)
  net_buying = gross_consumption * (1 + buying_tolerance)

  # Get material cost from the master material's current version
  material_version = get_current_material_version(master_material_id)
  material_cost_native = material_version['effective_cost_per_unit']
  native_currency = material_version['native_cost_currency']

  # Convert to USD (simplified - in real app, use exchange rate table)
  if native_currency == "USD":
    material_cost_usd = material_cost_native
  elif native_currency == "VND":
    material_cost_usd = material_cost_native / 25000  # Simplified conversion
  else:  # RMB
    material_cost_usd = material_cost_native / 7  # Simplified conversion

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
  update_material_cost_total(bom_version_id)

  print(f"Added material {master_material['name']} to BOM")
  return line_item


@anvil.server.callable
def update_bom_line_item(line_item_id, gross_consumption, selling_tolerance, buying_tolerance):
  """
    Update an existing BOM line item.
    Recalculates all the consumption values.
    """

  line_item = app_tables.bom_line_items.get_by_id(line_item_id)

  # Recalculate
  net_selling = gross_consumption * (1 + selling_tolerance)
  net_buying = gross_consumption * (1 + buying_tolerance)

  # Update the row
  line_item['gross_consumption'] = gross_consumption
  line_item['selling_tolerance'] = selling_tolerance
  line_item['net_selling_consumption'] = net_selling
  line_item['buying_tolerance'] = buying_tolerance
  line_item['net_buying_consumption'] = net_buying

  # Update total
  update_material_cost_total(line_item['bom_version'].get_id())

  print("Updated BOM line item")
  return line_item


@anvil.server.callable
def delete_bom_line_item(line_item_id):
  """
    Remove a material from the BOM.
    """
  line_item = app_tables.bom_line_items.get_by_id(line_item_id)
  bom_version_id = line_item['bom_version'].get_id()

  line_item.delete()

  # Update total
  update_material_cost_total(bom_version_id)

  print("Deleted BOM line item")


@anvil.server.callable
def list_bom_line_items(bom_version_id):
  """
    Get all materials in a BOM.
    """
  bom_version = app_tables.bom_versions.get_by_id(bom_version_id)

  items = app_tables.bom_line_items.search(
    bom_version=bom_version
  )

  return list(items)


def update_material_cost_total(bom_version_id):
  """
    Helper function: Calculates total material cost from all BOM line items.
    Updates the cost sheet version with new total.
    """

  bom_version = app_tables.bom_versions.get_by_id(bom_version_id)

  # Get all line items
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
    print(f"Updated material cost total to ${total:.2f}")

