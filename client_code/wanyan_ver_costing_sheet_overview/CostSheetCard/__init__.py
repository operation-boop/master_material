from ._anvil_designer import CostSheetCardTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...wanyan_ver_cost_sheet_details import wanyan_ver_cost_sheet_details

class CostSheetCard(CostSheetCardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.form_show()


    # Any code you write here will run before the form opens.

  def view_details_btn_click(self, **event_args):
    # Get the Home form
    home_form = get_open_form()

    # Get just the ID from self.item
    cost_sheet_id = self.item['cost_sheet_id']

    print(f"Opening detail form for: {cost_sheet_id}")

    # Clear the content panel and add Material_details
    home_form.content_panel.clear()
    home_form.content_panel.add_component(
      wanyan_ver_cost_sheet_details(
        cost_sheet_data={'cost_sheet_id': cost_sheet_id}  # ← Just pass the ID
      ),
      full_width_row=True
    )



    
    # home_form = get_open_form()

    # # Clear the content panel and add Material_details
    # home_form.content_panel.clear()
    # home_form.content_panel.add_component(
    #   wanyan_ver_cost_sheet_details(cost_sheet_data=self.item),
    #   full_width_row=True
    # )




  
  def form_show(self, **event_args):
    status = self.item["approval_status"]

    if status == "Approved":
      self.approval_status.background = "#C3F7C8"   # light green
      self.approval_status.foreground = "#006400"   # dark green text
      self.approval_status.icon = "fa:check"
    elif status == "Unapproved":
      self.approval_status.background = "#FFB4B4"   # light red
      self.approval_status.foreground = "#7A0000"   # dark red text
    elif status == "Pending":
      self.approval_status.background = "#FFE19E"   # light orange-yellow
      self.approval_status.foreground = "#805400"   # dark golden text

