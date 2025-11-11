import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

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

