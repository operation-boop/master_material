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
Cost Sheet Main Module
Handles core cost sheet CRUD operations and versioning.
"""

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

  print(f"[Main] Created cost sheet {document_id} with version 1")
  return cost_sheet


@anvil.server.callable
def get_cost_sheet(cost_sheet_id):
  """
    Get a cost sheet by ID with its current version data.
    Simple retrieval function.
    
    Args:
        cost_sheet_id: ID of the cost sheet
    
    Returns:
        The cost sheet row
    """
  cost_sheet = app_tables.cost_sheets.get_by_id(cost_sheet_id)
  return cost_sheet


# @anvil.server.callable
# def list_all_cost_sheets():
#   """
#     Get all cost sheets in the system.
#     Returns them sorted by creation date (newest first).
    
#     Returns:
#         List of all cost sheets
#     """
#   all_sheets = app_tables.cost_sheets.search()
#   # Sort in Python - newest first
#   sorted_sheets = sorted(all_sheets, key=lambda x: x['created_at'], reverse=True)
#   return sorted_sheets




# ============================================================================
# OVERVIEW FUNCTION - Returns minimal data for ALL cost sheets
# ============================================================================

@anvil.server.callable
def get_all_cost_sheets_with_current_versions():
  """Returns OVERVIEW data only (fast loading)"""
  try:
    all_cost_sheets = list(app_tables.cost_sheets.search())
    if not all_cost_sheets:
      return []

    cost_sheet_data = []

    for cost_sheet in all_cost_sheets:
      # Get all versions for this cost sheet
      versions = list(app_tables.cost_sheet_versions.search(cost_sheet=cost_sheet))

      if not versions:
        continue

        # Sort by version number (highest first) - Python sorting
      versions_sorted = sorted(versions, key=lambda v: v['version_number'] or 0, reverse=True)
      current_version = versions_sorted[0]

      # Build version history
      version_history = []
      for v in versions_sorted:
        version_history.append({
          "version": v['version_number'],
          "updated_at": v['created_at'].strftime('%d/%m/%Y') if v['created_at'] else None,
          "created_by": v['created_by']['name'] if v['created_by'] else None,
          "change_description": v['change_description'],
        })

        # Build overview item (NO bom, processing_costs, etc. - those load on-demand)
      cost_sheet_item = {
        "cost_sheet_id": cost_sheet['document_id'],
        "version_number": str(current_version['version_number'] or "N/A"),
        "updated_at": current_version['created_at'].strftime('%d/%m/%Y') if current_version['created_at'] else "N/A",
        "created_by": current_version['created_by']['name'] if current_version['created_by'] else "Unknown",
        "approval_status": current_version['status'] or "Unknown",
        "master_style": current_version['master_style']['name'] if current_version['master_style'] else "N/A",
        "currency": current_version['cost_currency'],
        "change_description": current_version['change_description'],
        "total_material_cost": float(current_version['total_material_cost'] or 0.0),
        "total_processing_cost": float(current_version['total_processing_cost'] or 0.0),
        "total_overhead_cost": float(current_version['total_overhead_cost'] or 0.0),
        "total_cost": (
          float(current_version['total_material_cost'] or 0.0) +
          float(current_version['total_processing_cost'] or 0.0) +
          float(current_version['total_overhead_cost'] or 0.0)
        ),
        "version_history": version_history,
      }

      cost_sheet_data.append(cost_sheet_item)

    return cost_sheet_data

  except Exception as e:
    print(f"Server error loading cost sheets: {str(e)}")
    raise






"""
WORKING VERSION - get_cost_sheet_details
Copy this into your Anvil.works Server Module

Fixed Issues:
- Removed .get() calls on Data Table Rows (they don't support it!)
- Safe linked row access (check if null before accessing nested properties)
- Added error logging to help with debugging
"""

@anvil.server.callable
def get_cost_sheet_details(cost_sheet_id):
  """Returns COMPLETE data for ONE cost sheet (called on-demand)"""
  try:
    # Find cost_sheet safely
    css = list(app_tables.cost_sheets.search(document_id=cost_sheet_id))
    if not css:
      print(f"No cost sheet found with document_id: {cost_sheet_id}")
      return None
    cost_sheet = css[0]

    # Get all versions for this cost sheet
    versions = list(app_tables.cost_sheet_versions.search(cost_sheet=cost_sheet))
    if not versions:
      print(f"No versions found for cost sheet: {cost_sheet_id}")
      return None

      # Sort by version_number descending (latest first)
    versions_sorted = sorted(
      versions,
      key=lambda v: v['version_number'] if v['version_number'] is not None else 0,
      reverse=True
    )
    current_version = versions_sorted[0]

    # ---- Query related tables OUTSIDE any loops ----

    # 1) BOM Items
    bom_items = []
    try:
      bom_version = current_version['bom_version'] if current_version['bom_version'] else None
      if bom_version:
        bom_rows = list(app_tables.bom_line_items.search(bom_version=bom_version))
        print(f"Found {len(bom_rows)} BOM items")
        
        for r in bom_rows:
          # Safe access to linked 'material' row
          material_name = "N/A"
          if r['assigned_material']:
            material_name = r['assigned_material']#['name']

          consumption = r['net_buying_consumption'] if r['net_buying_consumption'] is not None else 0
          unit_cost = r['material_cost_in_usd'] if r['material_cost_in_usd'] is not None else 0

          bom_items.append({
            "material_name": material_name,
            "consumption": consumption,
            "unit_cost": unit_cost,
            "total_cost": consumption * unit_cost,
          })

      print(f"Successfully built {len(bom_items)} BOM items")
    except Exception as e:
      print(f"Error loading BOM items: {str(e)}")
      bom_items = []

    # 2) Processing Costs
    processing_costs = []
    try:
      proc_rows = list(app_tables.processing_cost_items.search(cost_sheet_version=current_version))
      print(f"Found {len(proc_rows)} processing cost items")
      
      for r in proc_rows:
        processing_costs.append({
          "process_type": r['cost_type'] if r['cost_type'] else 'N/A',
          "cost_amount": r['cost_amount'] if r['cost_amount'] is not None else 0,
          "cost_currency": r['cost_currency'] if r['cost_currency'] else 'USD',
          "vendor_name": r['vendor_name'] if r['vendor_name'] else 'N/A',
          "description": r['description'] if r['description'] else 'N/A',
        })

        print(f"Successfully built {len(processing_costs)} processing cost items")
    except Exception as e:
      print(f"Error loading processing costs: {str(e)}")

      # Using traceback for easier debugging
      import traceback
      traceback.print_exc()
      
      processing_costs = []

      # 3) Overhead Costs
    overhead_costs = []
    try:
      oh_rows = list(app_tables.overhead_cost_items.search(cost_sheet_version=current_version))
      print(f"Found {len(oh_rows)} overhead cost items")
      
      for r in oh_rows:
        overhead_costs.append({
          "cost_type": r['cost_type'] if r['cost_type'] else 'N/A',
          "cost_amount": r['cost_amount'] if r['cost_amount'] is not None else 0,
          "cost_currency": r['cost_currency'] if r['cost_currency'] else 'USD',
        })
        
        print(f"Successfully built {len(overhead_costs)} overhead cost items")
    except Exception as e:
      print(f"Error loading overhead costs: {str(e)}")
      
      # Using traceback for easier debugging
      import traceback
      traceback.print_exc()
      
      overhead_costs = []

      # 4) Exchange Rates
    exchange_rates = []
    try:
      ex_rows = list(app_tables.exchange_rate_records.search(cost_sheet_version=current_version))
      for r in ex_rows:
        exchange_rates.append({
          "from_currency": r['from_currency'] if r['from_currency'] else 'N/A',
          "to_currency": r['to_currency'] if r['to_currency'] else 'N/A',
          "rate": r['exchange_rate'] if r['exchange_rate'] is not None else 0,
          "date": r['rate_date'],
        })
    except Exception as e:
      print(f"Error loading exchange rates: {str(e)}")

      # Using traceback for easier debugging
      import traceback
      traceback.print_exc()

      exchange_rates = []

      # 5) Quoted Price Scenarios
    scenarios = []
    try:
      sc_rows = list(app_tables.quoted_price_scenarios.search(cost_sheet_version=current_version))
      for r in sc_rows:
        scenarios.append({
          "quoted_price": r['quoted_price'] if r['quoted_price'] is not None else 0,
          "quoted_currency": r['quoted_currency'] if r['quoted_currency'] else 'USD',
          "gross_margin": r['expected_gross_margin'] if r['expected_gross_margin'] is not None else 0,
        })
    except Exception as e:
      print(f"Error loading price scenarios: {str(e)}")
      scenarios = []

      # 6) Version history (summaries)
    version_history = []
    for v in versions_sorted:
      # Safe access to version fields
      version_num = v['version_number']
      created_at_str = "N/A"
      if v['created_at']:
        created_at_str = v['created_at'].strftime('%d/%m/%Y')

      created_by_name = "Unknown"
      if v['created_by']:
        created_by_name = v['created_by']['name']

      version_history.append({
        "version": version_num,
        "updated_at": created_at_str,
        "created_by": created_by_name,
        "change_description": v['change_description'],
      })

      # ---- Safe access to current_version fields ----
    master_style_name = "N/A"
    if current_version['master_style']:
      master_style_name = current_version['master_style']['name']

    created_by_name = "Unknown"
    if current_version['created_by']:
      created_by_name = current_version['created_by']['name']

    updated_at_str = "N/A"
    if current_version['created_at']:
      updated_at_str = current_version['created_at'].strftime('%d/%m/%Y')

    version_num_str = str(current_version['version_number']) if current_version['version_number'] is not None else "N/A"

    # Calculate totals safely
    total_material = float(current_version['total_material_cost'] or 0.0)
    total_processing = float(current_version['total_processing_cost'] or 0.0)
    total_overhead = float(current_version['total_overhead_cost'] or 0.0)

    # ---- Return a plain-dict payload for client ----
    payload = {
      "cost_sheet_id": cost_sheet['document_id'],
      "version_number": version_num_str,
      "updated_at": updated_at_str,
      "created_by": created_by_name,
      "approval_status": current_version['status'],
      "master_style": master_style_name,
      "currency": current_version['cost_currency'],
      "change_description": current_version['change_description'],

      "total_material_cost": total_material,
      "total_processing_cost": total_processing,
      "total_overhead_cost": total_overhead,
      "total_cost": total_material + total_processing + total_overhead,

      # grouped lists for repeating panels
      "bom": bom_items,
      "processing_costs": processing_costs,
      "overhead_costs": overhead_costs,
      "exchange_rate_record": exchange_rates,
      "scenarios": scenarios,
      "version_history": version_history,
    }

    return payload

  except Exception as e:
    print(f"Server error loading cost sheet details: {str(e)}")
    import traceback
    traceback.print_exc()
    raise














@anvil.server.callable
def get_current_version(cost_sheet_id):
  """
    Gets the current active version of a cost sheet.
    This is a wrapper around the helper function for frontend use.
    
    Args:
        cost_sheet_id: ID of the cost sheet
    
    Returns:
        The current cost sheet version
    """
  return helpers.get_current_version(cost_sheet_id)


@anvil.server.callable
def create_new_version(cost_sheet_id, change_description, user_id):
  """
    Creates a new version of an existing cost sheet.
    Copies data from current version to new version.
    
    Args:
        cost_sheet_id: Which cost sheet to version
        change_description: Why are we creating a new version?
        user_id: Who is creating this version
    
    Returns:
        The newly created version
    """

  cost_sheet = app_tables.cost_sheets.get_by_id(cost_sheet_id)
  user = app_tables.users.get_by_id(user_id)

  # Get the current version to copy from
  old_version = helpers.get_current_version(cost_sheet_id)

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

  print(f"[Main] Created version {new_version_number} for cost sheet {cost_sheet['document_id']}")
  return new_version


@anvil.server.callable
def get_cost_sheet_summary(cost_sheet_version_id):
  """
    Get a complete summary of a cost sheet version.
    This is a wrapper around the helper function for frontend use.
    
    Args:
        cost_sheet_version_id: ID of the cost sheet version
    
    Returns:
        Dictionary with all cost summary data
    """
  return helpers.get_cost_sheet_summary(cost_sheet_version_id)
