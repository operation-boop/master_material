from ._anvil_designer import Supplier_detailsTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime
from ..Supplier_list import Supplier_list

class Supplier_details(Supplier_detailsTemplate):
  def __init__(self, supplier_data=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.supplier = supplier_data
    self.form_show()
    self.item = supplier_data
    # Any code you write here will run before the form opens.

  def form_show(self, **event_args):
    supplier = self.supplier

    status = supplier.get('is_approved_vendor')
    approved_date = supplier.get('approved_date')
    approved_by = supplier.get('approved_by')

    if status == "True":

      approved_date_str = None
      if isinstance(approved_date, str):
        # try converting from string like "2024-01-20"
        try:
          approved_date_obj = datetime.strptime(approved_date, "%Y-%m-%d")
          approved_date_str = approved_date_obj.strftime("%B %d, %Y")
        except ValueError:
          approved_date_str = approved_date  # keep as-is if format unknown
      elif approved_date is not None:
        # it's already a date/datetime object
        approved_date_str = approved_date.strftime("%B %d, %Y")
      else:
        approved_date_str = "N/A"


      self.status_description.text = (
        f"Approved Vendor\nThis supplier has been approved as a verified vendor "
        f"on {approved_date_str} by {approved_by}."
      )
      self.status_description.visible = True

    else:
      # If supplier not approved → hide the description
      self.status_description.visible = False

  def materials_btn_click(self, **event_args):
    self.materials_panel.visible = True
    self.orders_panel.visible = False
    self.activity_panel.visible = False

  def orders_btn_click(self, **event_args):
    self.materials_panel.visible = False
    self.orders_panel.visible = True
    self.activity_panel.visible = False

  def activity_btn_click(self, **event_args):
    self.materials_panel.visible = False
    self.orders_panel.visible = False
    self.activity_panel.visible = True

  def edit_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    from ..Supplier_edit_form import Supplier_edit_form

    popup = Supplier_edit_form()

    alert(
      content=popup,
      title=None,
      large=True,
      buttons=None 
    )

  def return_btn_click(self, **event_args):
    home = get_open_form()   # This is your Home form
    home.content_panel.clear()
    home.content_panel.add_component(Supplier_list(), full_width_row=True)
