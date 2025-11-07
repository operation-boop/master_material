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

  def form_show(self, **event_args):
  
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
      }
    ]

    for cs in cost_sheet:
      tm = float(cs["total_material_cost"] or 0)
      tp = float(cs["total_processing_cost"] or 0)
      to = float(cs["total_overhead_cost"] or 0)
      cs["total_cost"] = tm + tp + to
  
    self.repeating_panel_cost_sheet.items = cost_sheet