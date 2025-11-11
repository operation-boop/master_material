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
  cost_sheet_version = app_tables.cost_sheet_version.add_row(
    cost_sheet = cost_sheet,  # Link back to parent
    document_id = document_id,
    version_number = 1,
    change_description = "Initial version",
    created_at = datetime.now(),
    created_by = user,
    submitted_at = None,
    submitted_by = None,
    approved_at = None,
    approved_by = None,
    status = "Draft",
    cost_currency=cost_currency,
    master_style=master_style,
    client=client,
    bom_version=None,  # Will be set later
    total_material_cost=0.0,
    total_processing_cost=0.0
  )

  print(f"Created cost sheet {document_id} with version 1")
  return cost_sheet


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
  current_version = app_tables.cost_sheet_version.get(
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
  new_version = app_tables.cost_sheet_version.add_row(
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
