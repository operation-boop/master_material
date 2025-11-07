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
    cost_sheet = {
      "cost_sheet_id": "CS-001",
      "version_number": "1",
      "updated_at": "1/3/2024",
      "created_by": "John Doe",
      "approv"
      "master_style": "MAT-005",
      "currency": "VND",
      "change_description": "Updated material costs...",

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

      "overhead_costs": {
        "import_logistics": 0.50,
        "export_logistics": 0.70,
        "vat": 0.10,
        "import_duty": 0.15,
        "testing": 0.25,
        "sampling": 0.30,
        "total_overhead_cost": 2.00
      },

      "profit_scenarios": [
        {"quoted_price": 22.00, "margin": 20, "profit": 4.40},
        {"quoted_price": 24.00, "margin": 25, "profit": 6.00},
        {"quoted_price": 26.00, "margin": 30, "profit": 7.80},
      ],

      "total_profit_scenarios_cost": 18.20
    }

    self.
    # --- HEADER ---
    self.lbl_master_style.text = cost_sheet["master_style"]
    self.lbl_currency.text = cost_sheet["currency"]
    self.lbl_change_description.text = cost_sheet["change_description"]
  
    # --- BOM Section ---
    self.repeating_panel_bom.items = cost_sheet["bom"]
    # Example row form fields:
    # lbl_material.text = self.item['material']
    # lbl_consumption.text = self.item['consumption']
    # lbl_unit_cost.text = self.item['unit_cost']
    # lbl_total.text = self.item['total']
  
    # --- Processing Costs ---
    self.repeating_panel_processing.items = cost_sheet["processing_costs"]
    # Row form binds: type, vendor, cost
  
    # --- Overhead Costs ---
    oh = cost_sheet["overhead_costs"]
    self.lbl_import_logistics.text = oh["import_logistics"]
    self.lbl_export_logistics.text = oh["export_logistics"]
    self.lbl_vat.text = oh["vat"]
    self.lbl_import_duty.text = oh["import_duty"]
    self.lbl_testing.text = oh["testing"]
    self.lbl_sampling.text = oh["sampling"]
    self.lbl_total_overhead_cost.text = oh["total_overhead_cost"]
  
    # --- Profit Scenarios ---
    self.repeating_panel_profit_scenarios.items = cost_sheet["profit_scenarios"]
    # Row form binds: quoted_price, margin, profit
  
    # --- Totals Footer ---
    self.lbl_total_profit_scenarios_cost.text = cost_sheet["total_profit_scenarios_cost"]
