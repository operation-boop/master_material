from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables, Row
import anvil.users

from ..Opportunity import Opportunity
from ..Deal import Deal
from ..RFQ import RFQ
from ..RFS import RFS
from ..QMO import QMO
from ..SMO import SMO
from ..Client_list import Client_list
from ..Style_list import Style_list
from ..Material_list import Material_list

class Home(HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # thai 25/10: refactor to set the default link to group

  def link_nav_click(self, **event_args):
    """This method is called when the link is clicked"""
    clicked_link = event_args['sender']
    source = clicked_link.tag
    page_registry = {
      "opportunity_group": Opportunity(),
      "request_group": RFQ(),
      "order_group": QMO(),
      "master_data_group": Client_list(),
      "opportunity": Opportunity(),
      "deal": Deal(),
      "rfq": RFQ(),
      "rfs": RFS(),
      "qmo": QMO(),
      "smo": SMO(),
      "client": Client_list(),
      "style": Style_list(),
      "material": Material_list(),
    }
    page = page_registry.get(source)

    self.format_link_role_to_default()
    self.format_link_role_to_selected(clicked_link)
    self.toggle_group(clicked_link)

    self.content_panel.clear()
    self.content_panel.add_component(page, full_width_row=True)

  def format_link_role_to_default(self):
    self.link_opportunity.role = "<default>"
    self.link_deal.role = "<default>"
    self.link_rfq.role = "<default>"
    self.link_rfs.role = "<default>"
    self.link_qmo.role = "<default>"
    self.link_smo.role = "<default>"
    self.link_client.role = "<default>"
    self.link_style.role = "<default>"
    self.link_material.role = "<default>"


  def format_link_role_to_selected(self, clicked_link):
    group_default_link_registry = {
      "opportunity_group": self.link_opportunity,
      "request_group": self.link_rfq,
      "order_group": self.link_qmo,
      "master_data_group": self.link_client
    }
    default_group_link = group_default_link_registry.get(clicked_link.tag)
    if default_group_link:
      default_group_link.role = "selected"
    else:
      clicked_link.role = "selected"

  def toggle_group(self, clicked_link):
    """
    print(anvil.users.login_with_google())
    print(app_tables.users.Row)
    print(isinstance(anvil.users.get_user(), app_tables.users.Row))
    """
    group_container_registry = {
      "opportunity_group": self.column_panel_group_opporunity,
      "request_group": self.column_panel_group_request,
      "order_group": self.column_panel_group_order,
      "master_data_group": self.column_panel_group_master_data
    }
    group_container = group_container_registry.get(clicked_link.tag)

    if group_container:
      group_container.visible = True if not group_container.visible else False
    else:
      pass
