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

from anvil.tables import order_by

@anvil.server.callable
def list_all_cost_sheet_versions():
  cost_sheet_version = app_tables.cost_sheet_version.search()
  return [dict(cost_sheet) for cost_sheet in cost_sheet_version]


  
def generate_next_cost_sheet_document_id():
  
    # Generate the next incremental document ID in the format CS-1001, CS-1002, ...

  # Fetch all cost_sheet_version rows
  rows = list(app_tables.cost_sheet_version.search())

  if not rows:
    # No rows exist yet
    next_number = 1001
  else:
    # Extract numeric part from each document_id
    numbers = []
    for r in rows:
      rd = dict(r)
      doc_id = rd.get("document_id")
      if isinstance(doc_id, str) and doc_id.startswith("CS-"):
        try:
          # split and strip to be tolerant of spaces
          num_part = doc_id.split("-", 1)[1].strip()
          num = int(num_part)
          numbers.append(num)
        except (IndexError, ValueError):
          # skip malformed document_id values
          continue

    if numbers:
      next_number = max(numbers) + 1
    else:
      next_number = 1001

    # Return padded document ID
  return f"CS-{next_number}"

  # 2. Add the row
@anvil.server.callable
def create_cost_sheet_version_with_rates(draft=True,):
  """
    Create a new cost sheet version row.
    draft=True -> draft version (submitted_at=None, version_number=0)
    No user tracking required.
    """
  # 1. Generate document ID
  document_id = generate_next_cost_sheet_document_id()

  # 2. Add the new row
  new_version = app_tables.cost_sheet_version.add_row(
    document_id=document_id,
    created_at=datetime.now(),
    created_by=None,
    approved_at=None,
    approved_by=None,
    submitted_at=None if draft else datetime.now(),
    submitted_by=None,
    change_description="First version created",
    version_number=0 if draft else 1,
    status="Draft" if draft else "Under review",
    bom_version=None,
    # exchange_rates_used= None,
    processing_cost_items=None,
    total_overhead_cost=None,
    total_material_cost=None,
    # expected_profit_scenarios=None
  )

  return new_version









# @anvil.server.callable
# def list_all_cost_sheets():
#   return app_tables.cost_sheet.search()

# @anvil.server.callable
# def list_all_cost_sheet_versions():
#   return app_tables.cost_sheet_version.search()

# @anvil.server.callable
# def list_all_cost_sheets_simple():
#   return list(map(lambda cost_sheet_row: {
#     "id": cost_sheet_row.get_id(),
#     "document_id": cost_sheet_row['document_id']
#   }, list_all_cost_sheets()))

# @anvil.server.callable
# def list_all_cost_sheet_versions_simple():
#   return list(map(lambda cost_sheet_version_row: {
#     "id": cost_sheet_version_row.get_id(),
#     "document_id": cost_sheet_version_row['document_id']
#   }, list_all_cost_sheet_versions()))

# @anvil.server.callable
# def get_cost_sheet_with_id(id):
#   return app_tables.cost_sheet.get_by_id(id)

# @anvil.server.callable
# def get_cost_sheet_version_with_id(id):
#   return app_tables.cost_sheet_version.get_by_id(id)

# # start with low level thinking
# def create_cost_sheet_low_level():
#   return app_tables.cost_sheet.add_row(
#     created_at = datetime.now()
#   )

# def create_cost_sheet_version_low_level_ai(document_id, version_number, created_by=None, **kwargs):
#   data = {
#     'document_id': document_id,
#     'version_number': version_number,
#     'created_at': datetime.now(),
#     'created_by': created_by,
#     'status': kwargs.get('status', 'draft'),
#     'exchange_rate_used': [],  # Empty list for linked rows
#     'processing_cost_items': [],  # Empty list for linked rows
#   }

#   # Add any additional fields
#   data.update(kwargs)

#   return app_tables.cost_sheet_version.add_row(**data)

# case 1: create new cost sheet -> version 1


# # case 2: update cost sheet -> create new verion X

# def generate_document_id():
#   pass

# def get_cost_sheet_status(key): # UNDER CONSTRUCTION
#   status = {
#     'draft': 'Draft',
#     'under review': 'Under review'
#   }
#  return status.get(key)