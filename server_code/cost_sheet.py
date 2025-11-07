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

@anvil.server.callable
def list_all_cost_sheets():
  return app_tables.cost_sheet.search()

@anvil.server.callable
def list_all_cost_sheet_versions():
  return app_tables.cost_sheet_version.search()

@anvil.server.callable
def list_all_cost_sheets_simple():
  return list(map(lambda cost_sheet_row: {
    "id": cost_sheet_row.get_id(),
    "document_id": cost_sheet_row['document_id']
  }, list_all_cost_sheets()))

@anvil.server.callable
def list_all_cost_sheet_versions_simple():
  return list(map(lambda cost_sheet_version_row: {
    "id": cost_sheet_version_row.get_id(),
    "document_id": cost_sheet_version_row['document_id']
  }, list_all_cost_sheet_versions()))

@anvil.server.callable
def get_cost_sheet_with_id(id):
  return app_tables.cost_sheet.get_by_id(id)

@anvil.server.callable
def get_cost_sheet_version_with_id(id):
  return app_tables.cost_sheet_version.get_by_id(id)

# start with low level thinking
def create_cost_sheet_low_level():
  return app_tables.cost_sheet.add_row(
    created_at = datetime.now()
  )

def create_cost_sheet_version_low_level_ai(document_id, version_number, created_by=None, **kwargs):
  data = {
    'document_id': document_id,
    'version_number': version_number,
    'created_at': datetime.now(),
    'created_by': created_by,
    'status': kwargs.get('status', 'draft'),
    'exchange_rate_used': [],  # Empty list for linked rows
    'processing_cost_items': [],  # Empty list for linked rows
  }

  # Add any additional fields
  data.update(kwargs)

  return app_tables.cost_sheet_version.add_row(**data)

# case 1: create new cost sheet -> version 1
def create_cost_sheet_version_low_level(user_row, draft=True):

  app_tables.tabl_cost_sheet_version.add_row(
    document_id = 0,
    created_at = datetime.now(),
    created_by = user_row,
    approved_at = None,
    approved_by = None,
    submitted_at = None if draft else datetime.now(), # keep DRAFT vs SUBMITTED
    submitted_by = None if draft else user_row,
    change_description = "First version created",
    version_number = 0 if draft else 1,
    status = get_cost_sheet_status('draft') if draft else get_cost_sheet_status('under review'),
    bom_version = 0,
    exchange_rates_used = 0,
    processing_cost_items = 0,
    total_overhead_cost = 0,
    total_material_cost = 0,
    expected_profit_scenarios = 0
  )



# case 2: update cost sheet -> create new verion X

def generate_document_id():
  pass

def get_cost_sheet_status(key): # UNDER CONSTRUCTION
  status = {
    'draft': 'Draft',
    'under review': 'Under review'
  }
  return status.get(key)