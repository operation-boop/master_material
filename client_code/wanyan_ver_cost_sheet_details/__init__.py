from ._anvil_designer import wanyan_ver_cost_sheet_detailsTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..wanyan_ver_costing_sheet_overview import wanyan_ver_costing_sheet_overview


class wanyan_ver_cost_sheet_details(wanyan_ver_cost_sheet_detailsTemplate):
  def __init__(self, cost_sheet_data=None, **properties):
    self.init_components(**properties)

    print("=" * 50)
    print("DETAILS INIT — type of cost_sheet_data:", type(cost_sheet_data))
    print("Keys received:", list(cost_sheet_data.keys()) if cost_sheet_data else None)
    print(f"Has BOM?                {'bom' in cost_sheet_data if cost_sheet_data else 'N/A'}")
    print(
      f"Has processing_costs?   {'processing_costs' in cost_sheet_data if cost_sheet_data  else 'N/A'}"
    )
    print(
      f"Has version_history?    {'version_history' in cost_sheet_data if cost_sheet_data else 'N/A'}"
    )

    if not cost_sheet_data:
      alert("No cost sheet data provided")
      return

      # ⭐ NEW CODE - Check if we need to load full details
    if 'bom' not in cost_sheet_data:
      print("⚠️ BOM NOT FOUND - Loading full details from server...")
      cost_sheet_id = cost_sheet_data.get('cost_sheet_id')
      print(f"Calling get_cost_sheet_details with ID: {cost_sheet_id}")

      with Notification("Loading cost sheet details..."):
        full_data = anvil.server.call('get_cost_sheet_details', cost_sheet_id)

      print(f"Server returned: {type(full_data)}")
      if full_data:
        print(f"Keys in full_data: {list(full_data.keys())}")
        print(f"Has BOM now? {'bom' in full_data}")
        print(f"BOM length: {len(full_data.get('bom', []))}")
        self.item = full_data
      else:
        print("ERROR: Server returned None!")
        alert("Failed to load cost sheet details")
        return
    else:
      print("✓ BOM FOUND - Using provided data directly")
      self.item = cost_sheet_data

    print(f"Final self.item keys: {list(self.item.keys()) if self.item else 'None'}")
    print("=" * 50)

    # Call form_show to populate repeating panels
    self.form_show()

  def back_btn_click(self, **event_args):
    home = get_open_form()   # This is your Home form
    home.content_panel.clear()
    home.content_panel.add_component(wanyan_ver_costing_sheet_overview(), full_width_row=True)


  def cost_breakdown_tab_btn_click(self, **event_args):
    self.cost_details_panel.visible = True
    self.version_history_panel.visible = False
    self.exchange_rates_panel.visible = False

  def version_history_tab_btn_click(self, **event_args):
    self.version_history_panel.visible = True
    self.cost_details_panel.visible = False
    self.exchange_rates_panel.visible = False

  def exchange_rates_tab_btn_click(self, **event_args):
    self.version_history_panel.visible = False
    self.cost_details_panel.visible = False
    self.exchange_rates_panel.visible = True

  def form_show(self, **event_args):
    if not self.item:
      self.repeating_panel_bom.items = []
      self.repeating_panel_processing_costs.items = []
      self.repeating_panel_version_history.items = []
      self.repeating_panel_overhead_costs.items = []
      self.repeating_panel_exchange_rates.items = []
      return

    # Defensive: use .get but remember self.item is a dict returned by server
    self.repeating_panel_bom.items = list(self.item.get("bom") or [])
    self.repeating_panel_processing_costs.items = list(self.item.get("processing_costs") or [])
    self.repeating_panel_version_history.items = list(self.item.get("version_history") or [])
    self.repeating_panel_overhead_costs.items = list(self.item.get("overhead_costs") or [])
    self.repeating_panel_exchange_rates.items = list(self.item.get("exchange_rate_record") or [])
    

  def edit_btn_click(self, **event_args):
    from ..wanyan_ver_cost_sheet_edit_form import wanyan_ver_cost_sheet_edit_form

    popup = wanyan_ver_cost_sheet_edit_form(cost_sheet=self.item)

    alert(
      content=popup,
      title=None,
      large=True,
      buttons=None 
    )
