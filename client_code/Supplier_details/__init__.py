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
    self.item = supplier_data
    self.show_data()

    for panel in [self.supplier_information_panel, self.approval_information_panel]:
      panel.border = "2px solid #000000"
      panel.background = "secondary-700"         
      panel.border_radius = 8

  def show_data(self, **event_args):
    supplier = self.item
    self.supplier_id.text = supplier['supplier_id']
    self.supplier_name.text = supplier['supplier_name']
    self.country.text = supplier['country']
    self.contact_person.text = supplier['contact_person']
    self.email.text = supplier['email']
    approved_date = str(supplier['approved_date'])
    approved_by = supplier['approved_by']

    status = supplier['status']
    print(status)
    if status is True:
      self.verify_btn.visible = False
      self.status.text = "\u2714  Approved"   # check mark unicode also ok
      self.status.foreground = "#0B7D07"             # green text
      self.status.background = "#DFF8E1"             # soft green bg
    else:
      self.status.text = "\u2716  Not Approved"
      self.status.foreground = "#9B0A0A"             # red text
      self.status.background = "#F9D6D6" 

    if isinstance(approved_date, datetime):
      self.approved_date.text = approved_date.strftime("%B %d, %Y")
    elif isinstance(approved_date, str) and approved_date.strip():
      # cố gắng parse chuỗi sang datetime
      try:
        date_obj = datetime.strptime(approved_date, "%Y-%m-%d")
        self.approved_date.text = date_obj.strftime("%B %d, %Y")
      except ValueError:
        self.approved_date.text = approved_date  # giữ nguyên nếu format lạ
    else:
      self.approved_date.text = "N/A"

    if approved_by:
      self.approved_by.text = approved_by['email']
    else:
      self.approved_by.text = "N/A"

  def refresh_data(self):
    try:
      supplier_id = self.item.get_id() 
      updated_supplier = anvil.server.call('get_supplier_by_id', supplier_id)

      if updated_supplier:
        self.item = updated_supplier
        self.show_data()

    except Exception as e:
      Notification(f"Error: {e}", style="danger").show()

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
    popup = Supplier_edit_form(
      supplier_data=self.item,
      on_saved=self.refresh_data
    )

    alert(
      content=popup,
      large=True,
      buttons=None 
    )

  def return_btn_click(self, **event_args):
    home = get_open_form()   # This is your Home form
    home.content_panel.clear()
    home.content_panel.add_component(Supplier_list(), full_width_row=True)

  def verify_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    supplier = self.item
    confirm_result = confirm(
      "Are you sure you want to verify this supplier?",
      title="Confirm Verification",
      buttons=[("Confirm", True), ("Cancel", False)]
    )
    if not confirm_result:
      return

    result = anvil.server.call('verify_supplier', supplier['supplier_id'])

    if result['success']:
      self.status.text = "✔ Approved"
      self.status.foreground = "#0B7D07"
      self.status.background = "#DFF8E1"
      self.verify_btn.visible = False
      # self.approved_by.text = result['approved_by']
      self.approved_date.text = result['approved_date'].strftime("%d/%m/%Y")
      Notification("✅ Supplier successfully verified!").show()
    else:
      Notification(f"⚠ {result['msg']}").show()


