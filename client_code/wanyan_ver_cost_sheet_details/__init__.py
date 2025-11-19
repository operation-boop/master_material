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
    # cost_sheet_data should be a dict for ONE cost sheet (with keys like 'bom', 'processing_costs' ...)
    self.item = cost_sheet_data
    # don't set repeating panels here to cost_sheet_data (that's a dict)
    # call form_show to populate repeating panels
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
