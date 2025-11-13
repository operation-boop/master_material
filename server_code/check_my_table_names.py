import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


@anvil.server.callable
def check_my_table_names():
  """Check what tables actually exist"""

  results = []
  results.append("Checking your table names...")
  results.append("")

  # List of possible table names (singular and plural)
  tables_to_check = [
    'user', 'users',
    'client', 'clients',
    'master_style', 'master_styles',
    'supplier', 'suppliers',
    'master_material', 'master_materials',
    'master_material_version', 'master_material_versions',
    'cost_sheet', 'cost_sheets',
    'cost_sheet_version', 'cost_sheet_versions',
    'bill_of_material', 'bill_of_materials',
    'bom_version', 'bom_versions',
    'bom_line_item', 'bom_line_items',
    'processing_cost_item', 'processing_cost_items',
    'overhead_cost_item', 'overhead_cost_items',
    'quoted_price_scenario', 'quoted_price_scenarios',
    'exchange_rate', 'exchange_rates'
  ]

  found = []
  not_found = []

  for table_name in tables_to_check:
    try:
      table = getattr(app_tables, table_name)
      found.append(table_name)
      results.append(f"✅ {table_name}")
    except:
      not_found.append(table_name)

  results.append("")
  results.append("=" * 50)
  results.append(f"Found {len(found)} tables")
  results.append(f"Not found: {len(not_found)} names")
  results.append("")
  results.append("Your tables are named:")
  for name in found:
    results.append(f"  - {name}")

  return "\n".join(results)