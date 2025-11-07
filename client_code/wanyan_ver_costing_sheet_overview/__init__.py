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
        "version_number": "1",
        "updated_at": "1/3/2024",
        "created_by": "John Doe",
        "approval_status": "Approved",
        
        "master_style": "MAT-005",
        "currency": "VND",
        "change_description": "Updated material costs",
  
        "bom": [
          {"material": "Cotton White", "consumption": 2.5, "unit_cost": 4.50, "total": 11.25},
          {"material": "Polyester Black", "consumption": 1.0, "unit_cost": 3.20, "total": 3.20},
        ],
  
        "total_material_cost": 14.45,
  
        "processing_costs": [
          {"type": "Cutting", "vendor": "ABC Factory", "cost": 1.20},
          {"type": "Sewing", "vendor": "XYZ Factory", "cost": 2.80},
        ],
  
        "total_processing_cost": 4.00,
  
        "overhead_costs": [
          {"import_logistics": 0.50,
          "export_logistics": 0.70,
          "vat": 0.10,
          "import_duty": 0.15,
          "testing": 0.25,
          "sampling": 0.30}
        ],

        "total_overhead_cost": 2.00,
  
        "profit_scenarios": [
          {"quoted_price": 22.00, "margin": 20, "profit": 4.40},
          {"quoted_price": 24.00, "margin": 25, "profit": 6.00},
          {"quoted_price": 26.00, "margin": 30, "profit": 7.80},
        ],
  
        "total_profit_scenarios_cost": 18.20
      }
    ]

    for cs in cost_sheet:
      tm = float(cs["total_material_cost"] or 0)
      tp = float(cs["total_processing_cost"] or 0)
      to = float(cs["total_overhead_cost"] or 0)
      cs["total_cost"] = tm + tp + to
  
    self.repeating_panel_cost_sheet.items = cost_sheet