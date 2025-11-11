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
# COST SHEET - Main CRUD Operations
# ============================================

@anvil.server.callable
def create_cost_sheet(master_style_id, client_id, document_id, user_id, cost_currency="USD"):
  """
    Creates a new cost sheet with its first version automatically.
    This is the starting point for the entire costing process.
    
    Args:
        master_style_id: ID of the style we're costing
        client_id: Which client is this for
        document_id: Human-readable identifier
        user_id: Who is creating this
        cost_currency: Currency for this cost sheet (USD, VND, or RMB)
    
    Returns:
        The newly created cost_sheet row
    """

  # Step 1: Get the related records from database
  master_style = app_tables.master_styles.get_by_id(master_style_id)
  client = app_tables.clients.get_by_id(client_id)
  user = app_tables.users.get_by_id(user_id)

  # Step 2: Create the main cost sheet record
  cost_sheet = app_tables.cost_sheets.add_row(
    document_id=document_id,
    current_version=1,
    created_at=datetime.now(),
    created_by=user,
    submitted_at=None,
    submitted_by=None
  )

  # Step 3: Automatically create the first version
  cost_sheet_version = app_tables.cost_sheet_versions.add_row(
    cost_sheet=cost_sheet,  # Link back to parent
    document_id=document_id,
    version_number=1,
    change_description="Initial version",
    created_at=datetime.now(),
    created_by=user,
    submitted_at=None,
    submitted_by=None,
    approved_at=None,
    approved_by=None,
    status="Draft",
    cost_currency=cost_currency,
    master_style=master_style,
    client=client,
    bom_version=None,  # Will be set later
    total_material_cost=0.0,
    total_processing_cost=0.0
  )

  print(f"Created cost sheet {document_id} with version 1")
  return cost_sheet, cost_sheet_version


@anvil.server.callable
def get_cost_sheet(cost_sheet_id):
  """
    Get a cost sheet by ID with its current version data.
    Simple retrieval function.
    """
  cost_sheet = app_tables.cost_sheets.get_by_id(cost_sheet_id)
  return cost_sheet


@anvil.server.callable
def list_all_cost_sheets():
  """
    Get all cost sheets in the system.
    Returns them sorted by creation date (newest first).
    """
  all_sheets = app_tables.cost_sheets.search(
    tables.order_by("created_at", ascending=False)
  )
  return list(all_sheets)


@anvil.server.callable
def get_current_version(cost_sheet_id):
  """
    Gets the current active version of a cost sheet.
    """
  cost_sheet = app_tables.cost_sheets.get_by_id(cost_sheet_id)
  current_version_num = cost_sheet['current_version']

  # Find the version with matching number
  current_version = app_tables.cost_sheet_versions.get(
    cost_sheet=cost_sheet,
    version_number=current_version_num
  )

  return current_version


@anvil.server.callable
def create_new_version(cost_sheet_id, change_description, user_id):
  """
    Creates a new version of an existing cost sheet.
    Copies data from current version to new version.
    
    Args:
        cost_sheet_id: Which cost sheet to version
        change_description: Why are we creating a new version?
        user_id: Who is creating this version
    """

  cost_sheet = app_tables.cost_sheets.get_by_id(cost_sheet_id)
  user = app_tables.users.get_by_id(user_id)

  # Get the current version to copy from
  old_version = get_current_version(cost_sheet_id)

  # Calculate new version number
  new_version_number = cost_sheet['current_version'] + 1

  # Create new version, copying most data from old version
  new_version = app_tables.cost_sheet_versions.add_row(
    cost_sheet=cost_sheet,
    document_id=cost_sheet['document_id'],
    version_number=new_version_number,
    change_description=change_description,
    created_at=datetime.now(),
    created_by=user,
    submitted_at=None,
    submitted_by=None,
    approved_at=None,
    approved_by=None,
    status="Draft",
    cost_currency=old_version['cost_currency'],
    master_style=old_version['master_style'],
    client=old_version['client'],
    bom_version=old_version['bom_version'],
    total_material_cost=old_version['total_material_cost'],
    total_processing_cost=old_version['total_processing_cost']
  )

  # Update the cost sheet to point to new version
  cost_sheet['current_version'] = new_version_number

  print(f"Created version {new_version_number} for cost sheet {cost_sheet['document_id']}")
  return new_version


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
  user = app_tables.users.get_by_id(user_id) # Not in use yet for BOM

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


# ============================================
# STATUS & WORKFLOW Operations
# ============================================

@anvil.server.callable
def submit_cost_sheet_for_review(cost_sheet_version_id, user_id):
  """
    Submit a cost sheet version for supervisor review.
    Changes status from Draft to Under review.
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  cost_sheet_version['status'] = "Under review"
  cost_sheet_version['submitted_at'] = datetime.now()
  cost_sheet_version['submitted_by'] = user

  print(f"Submitted cost sheet version {cost_sheet_version['version_number']} for review")
  return cost_sheet_version


@anvil.server.callable
def approve_cost_sheet(cost_sheet_version_id, user_id):
  """
    Approve a cost sheet version (supervisor action).
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  cost_sheet_version['status'] = "Approved"
  cost_sheet_version['approved_at'] = datetime.now()
  cost_sheet_version['approved_by'] = user

  print(f"Approved cost sheet version {cost_sheet_version['version_number']}")
  return cost_sheet_version


@anvil.server.callable
def reject_cost_sheet(cost_sheet_version_id, user_id):
  """
    Reject a cost sheet version (supervisor action).
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  cost_sheet_version['status'] = "Rejected"
  cost_sheet_version['approved_at'] = datetime.now()
  cost_sheet_version['approved_by'] = user

  print(f"Rejected cost sheet version {cost_sheet_version['version_number']}")
  return cost_sheet_version


# ============================================
# HELPER FUNCTIONS - Utilities
# ============================================

def get_current_material_version(master_material_id):
  """
    Helper: Gets the current version of a master material.
    Used when adding materials to BOM.
    """
  master_material = app_tables.master_materials.get_by_id(master_material_id)
  current_version_num = master_material['current_version']

  material_version = app_tables.master_material_versions.get(
    master_material=master_material,
    version_number=current_version_num
  )

  return material_version


@anvil.server.callable
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
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  # Get costs
  material_cost = cost_sheet_version['total_material_cost'] or 0.0
  processing_cost = cost_sheet_version['total_processing_cost'] or 0.0
  overhead_cost = cost_sheet_version['total_overhead_cost'] or 0.0
  total_cost = material_cost + processing_cost + overhead_cost

  # Get all scenarios
  scenarios = list_quoted_price_scenarios(cost_sheet_version_id)
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


@anvil.server.callable
def recalculate_all_scenarios(cost_sheet_version_id):
  """
    Recalculate all pricing scenarios when costs change.
    Call this after updating BOM, processing costs, or overhead.
    """

  scenarios = list_quoted_price_scenarios(cost_sheet_version_id)

  for scenario in scenarios:
    # Get current price
    quoted_price = scenario['quoted_price']
    quoted_currency = scenario['quoted_currency']

    # Recalculate (reuse the update function)
    update_quoted_price_scenario(
      scenario.get_id(), 
      quoted_price, 
      quoted_currency,
      scenario['created_by'].get_id()
    )

  print(f"Recalculated {len(scenarios)} pricing scenarios")


# ============================================
# EXCHANGE RATE HELPERS
# ============================================

@anvil.server.callable
def create_exchange_rate(date, from_currency, to_currency, rate, user_id):
  """
    Create an exchange rate record.
    This helps track what rates were used for cost calculations.
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

  print(f"Created exchange rate: {from_currency} to {to_currency} = {rate}")
  return exchange_rate


@anvil.server.callable
def get_latest_exchange_rate(from_currency, to_currency):
  """
    Get the most recent exchange rate between two currencies.
    """

  rate = app_tables.exchange_rates.search(
    tables.order_by("date", ascending=False),
    from_currency=from_currency,
    to_currency=to_currency,
  )

  if len(rate) > 0:
    return rate[0]
  else:
    return None


@anvil.server.callable
def link_exchange_rates_to_cost_sheet(cost_sheet_version_id, exchange_rate_ids):
  """
    Link exchange rates to a cost sheet version.
    This records what rates were used for this costing.
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)

  # Get exchange rate records
  rates = []
  for rate_id in exchange_rate_ids:
    rate = app_tables.exchange_rates.get_by_id(rate_id)
    rates.append(rate)

    # Store in cost sheet (using simple list column)
  cost_sheet_version['exchange_rates_used'] = rates

  print(f"Linked {len(rates)} exchange rates to cost sheet")
  return cost_sheet_version


# ============================================
# COMPLETE WORKFLOW EXAMPLE
# ============================================

@anvil.server.callable
def create_complete_cost_sheet_example(master_style_id, client_id, user_id):
  """
    This is an example function showing the complete workflow.
    You can use this to understand how all the pieces fit together.
    
    This creates a cost sheet with:
    - Basic info
    - BOM with 2 materials
    - Processing costs
    - Overhead costs
    - Pricing scenario
    """

  # Step 1: Create cost sheet
  print("Step 1: Creating cost sheet...")
  cost_sheet = create_cost_sheet(
    master_style_id=master_style_id,
    client_id=client_id,
    document_id=f"CS-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    user_id=user_id,
    cost_currency="USD"
  )

  # Get the version
  version = get_current_version(cost_sheet.get_id())
  version_id = version.get_id()

  # Step 2: Create BOM
  print("Step 2: Creating BOM...")
  bom = create_bom_for_cost_sheet(version_id, user_id)
  bom_version = app_tables.bom_versions.get(bill_of_material=bom)

  # Step 3: Add materials to BOM (example with mock material IDs)
  print("Step 3: Adding materials to BOM...")
  # You would replace these with real material IDs from your database
  # add_bom_line_item(
  #     bom_version_id=bom_version.get_id(),
  #     master_material_id="material_123",
  #     gross_consumption=2.5,  # 2.5 meters
  #     selling_tolerance=0.05,  # 5%
  #     buying_tolerance=0.10,   # 10%
  #     user_id=user_id
  # )

  # Step 4: Add processing costs
  print("Step 4: Adding processing costs...")
  add_processing_cost(
    cost_sheet_version_id=version_id,
    cost_type="Cut-make",
    cost_amount=5.50,
    cost_currency="USD",
    vendor_name="ABC Factory",
    description="Standard cut and sew",
    user_id=user_id,
    status="Draft"
  )

  # Step 5: Add overhead costs
  print("Step 5: Adding overhead costs...")
  add_overhead_cost_item(
    cost_sheet_version_id=version_id,
    name="Import logistics",
    cost_type="Import logistics",
    cost_amount=0.75,
    cost_currency="USD",
    user_id=user_id
  )

  add_overhead_cost_item(
    cost_sheet_version_id=version_id,
    name="Material testing",
    cost_type="Material testing",
    cost_amount=50.0,
    cost_currency="USD",
    user_id=user_id
  )

  # Step 6: Add pricing scenario
  print("Step 6: Adding pricing scenario...")
  add_quoted_price_scenario(
    cost_sheet_version_id=version_id,
    quoted_price=25.00,
    quoted_currency="USD",
    user_id=user_id
  )

  # Step 7: Get summary
  print("Step 7: Getting summary...")
  summary = get_cost_sheet_summary(version_id)

  print("=" * 50)
  print("COST SHEET CREATED SUCCESSFULLY!")
  print(f"Document ID: {cost_sheet['document_id']}")
  print(f"Total Cost: ${summary['total_cost']:.2f}")
  print(f"Status: {summary['status']}")
  print("=" * 50)

  return {
    'cost_sheet': cost_sheet,
    'summary': summary
  }