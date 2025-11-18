from ._anvil_designer import wanyan_ver_costing_sheet_overviewTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class wanyan_ver_costing_sheet_overview(wanyan_ver_costing_sheet_overviewTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.form_show()
    # Any code you write here will run before the form opens.

  def add_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    from ..wanyan_ver_cost_sheet_input_form import wanyan_ver_cost_sheet_input_form

    popup = wanyan_ver_cost_sheet_input_form()

    alert(
      content=popup,
      title=None,
      large=True,
      buttons=None 
    )



  """mock data"""
  
  def form_show(self, **event_args):
    testing =      {
      "cost_sheet_id": "CS-001",
      "version_number": "3",
      "updated_at": "5/11/2025",
      "created_by": "John Doe",
      "approval_status": "Approved",

      "master_style": "MS-003 - Wool Coat",
      "currency": "VND",
      "change_description": "Updated material costs",

      "bom": [
        {"material": "Cotton White", "type": "Fabric", "consumption": 2.5, "unit_cost": 4.50, "total_cost": 11.25},
        {"material": "Polyester Black", "type": "Fabric", "consumption": 1.0, "unit_cost": 3.20, "total_cost": 3.20},
      ],

      "total_material_cost": 14.45,

      "processing_costs": [
        {"type": "Cutting", "vendor": "ABC Factory", "description": "test4", "status":  "Verified", "cost": 1.20},
        {"type": "Sewing", "vendor": "XYZ Factory",  "description": "test5", "status":  "Unverified", "cost": 2.80},
      ],

      "version_history": [
        {"version": 3, "updated_at": "5/11/2025", "created_by": "John Doe", "change_description": "Update processing costs"},
        {"version": 2, "updated_at": "2/11/2025", "created_by": "John Doe", "change_description": "Update BOM materials"},
        {"version": 1, "updated_at": "1/11/2025", "created_by": "John Doe", "change_description": "Update import logistics cost"}
      ],

      "overhead_costs": [
        {"type": 3, "description": "test3", "cost": 4.20, "currency": "VND"},
        {"type": 2, "description": "test2", "cost": 7, "currency": "VND"},
        {"type": 1, "description": "test1", "cost": 2.50, "currency": "VND"},
      ],

      "exchange_rate_record" : [
        {"current_currency": "USD",
         "changed_to_currency": "VND",
         "rate": 24850,
         "exchanged_date": "2025-02-10"}
      ],

      "total_processing_cost": 4.00,


      "import_logistics": 0.50,
      "export_logistics": 0.70,
      "vat": 0.10,
      "total_overhead_cost": 2.00,

      "quoted_price": 22.00, "quoted_currency": "VND", "expected_gross_margin": 20, "expected_gross_income": 4.40, "expected_net_margin": 3, "expected_net_income": 4,
    }
    # --- Mock Data Example ---
    cost_sheet = [
      {
        "cost_sheet_id": "CS-001",
        "version_number": "3",
        "updated_at": "5/11/2025",
        "created_by": "John Doe",
        "approval_status": "Approved",

        "master_style": "MS-003 - Wool Coat",
        "currency": "VND",
        "change_description": "Updated material costs",

        "bom": [
          {"material": "Cotton White", "type": "Fabric", "consumption": 2.5, "unit_cost": 4.50, "total_cost": 11.25},
          {"material": "Polyester Black", "type": "Fabric", "consumption": 1.0, "unit_cost": 3.20, "total_cost": 3.20},
        ],

        "total_material_cost": 14.45,

        "processing_costs": [
          {"type": "Cutting", "vendor": "ABC Factory", "description": "test4", "status":  "Verified", "cost": 1.20},
          {"type": "Sewing", "vendor": "XYZ Factory",  "description": "test5", "status":  "Unverified", "cost": 2.80},
        ],

        "version_history": [
          {"version": 3, "updated_at": "5/11/2025", "created_by": "John Doe", "change_description": "Update processing costs"},
          {"version": 2, "updated_at": "2/11/2025", "created_by": "John Doe", "change_description": "Update BOM materials"},
          {"version": 1, "updated_at": "1/11/2025", "created_by": "John Doe", "change_description": "Update import logistics cost"}
        ],

        "overhead_costs": [
          {"type": 3, "description": "test3", "cost": 4.20, "currency": "VND"},
          {"type": 2, "description": "test2", "cost": 7, "currency": "VND"},
          {"type": 1, "description": "test1", "cost": 2.50, "currency": "VND"},
        ],

        "exchange_rate_record" : [
          {"current_currency": "USD",
           "changed_to_currency": "VND",
           "rate": 24850,
           "exchanged_date": "2025-02-10"}
        ],

        "total_processing_cost": 4.00,


        "import_logistics": 0.50,
        "export_logistics": 0.70,
        "vat": 0.10,
        "total_overhead_cost": 2.00,

        "quoted_price": 22.00, "quoted_currency": "VND", "expected_gross_margin": 20, "expected_gross_income": 4.40, "expected_net_margin": 3, "expected_net_income": 4,
      },
      testing

    ]

    for cs in cost_sheet:
      tm = float(cs["total_material_cost"] or 0)
      tp = float(cs["total_processing_cost"] or 0)
      to = float(cs["total_overhead_cost"] or 0)
      cs["total_cost"] = tm + tp + to

    self.repeating_panel_cost_sheet.items = cost_sheet





  
  # def form_show(self, **event_args):
  #   """This method is called when the form is opened"""

  #   # Clear the repeating panel initially
  #   self.repeating_panel_cost_sheet.items = []

  #   try:
  #     # Step 1: Call server to get all cost sheets from database
  #     all_cost_sheets = anvil.server.call('list_all_cost_sheets')

  #     # Step 2: Check if we have any cost sheets
  #     if not all_cost_sheets or len(all_cost_sheets) == 0:
  #       print("No cost sheets found in database")
  #       self.repeating_panel_cost_sheet.items = []
  #       return

  #       # Step 3: Process each cost sheet
  #     cost_sheet_data = []

  #     for cost_sheet in all_cost_sheets:
  #       # Get the current version for this cost sheet
  #       current_version = anvil.server.call('get_current_version', cost_sheet.get_id())

  #       # If no current version exists, skip this cost sheet
  #       if not current_version:
  #         print(f"Warning: Cost sheet {cost_sheet['document_id']} has no current version - skipping")
  #         continue

  #         # Build simplified data with only 4 essential fields
  #       cost_sheet_item = {
  #           "cost_sheet_id": cost_sheet['document_id'],
  #           "version_number": str(current_version['version_number']),
  #           "updated_at": current_version['created_at'].strftime('%d/%m/%Y') if current_version['created_at'] else "N/A",
  #           "created_by": current_version['created_by']['name'] if current_version['created_by'] else "Unknown",
  #           "approval_status": current_version['status'] if current_version['status'] else "Unknown",

  #           "master_style": current_version['master_style']['name'] if current_version['master_style'] else "N/A",
  #           "currency": current_version['cost_currency'],
  #           "change_description": current_version['change_description'],

  #           # Real calculated costs from summary
  #           "total_material_cost": current_version['total_material_cost'] or 0.0,
  #           "total_processing_cost": current_version['total_processing_cost'] or 0.0,
  #           "total_overhead_cost": current_version['total_overhead_cost'] or 0.0,
  #           "total_cost": ((current_version['total_material_cost'] or 0.0) +
  #                          (current_version['total_processing_cost'] or 0.0) +
  #                          (current_version['total_overhead_cost'] or 0.0)),
  #           "scenarios": []  # Skip for now, or fetch separately later

  #         }

  #       cost_sheet_data.append(cost_sheet_item)

  #       # Step 4: Assign to repeating panel
  #     self.repeating_panel_cost_sheet.items = cost_sheet_data
  #     print(f"✓ Loaded {len(cost_sheet_data)} cost sheets successfully")

  #   except Exception as e:
  #     # Step 5: Handle any errors gracefully
  #     print(f"✗ Error loading cost sheets: {str(e)}")
  #     alert(f"Failed to load cost sheets: {str(e)}", title="Error")
  #     self.repeating_panel_cost_sheet.items = []