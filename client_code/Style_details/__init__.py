from ._anvil_designer import Style_detailsTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Style_list import Style_list
from ..Style_edit_form import Style_edit_form


class Style_details(Style_detailsTemplate):
  def __init__(self, style_data=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item = style_data
    self.load_documents()
    # Any code you write here will run before the form opens.

  def back_btn_click(self, **event_args):
    home = get_open_form()
    home.content_panel.clear()
    home.content_panel.add_component(Style_list(), full_width_row=True)

  def load_documents(self):
    style_id = self.item['id']
    docs = anvil.server.call('get_style_documents', style_id)
    #self.repeating_panel_documents.items = docs 

    # Clear existing cards
    self.flow_panel_documents.clear()

    for doc in docs:
      from .documents_itemtemplate import documents_itemtemplate
      card = documents_itemtemplate(item=doc)
      card.width = "100%"  # for 2 cards per row with wrap=True
      self.flow_panel_documents.add_component(card)


  def sku_btn_click(self, **event_args):
    self.sku_panel.visible = True
    self.rfq_panel.visible = False
    self.cost_sheet_panel.visible = False
    self.bom_panel.visible = False
    self.documents_panel.visible = False

  def rfq_btn_click(self, **event_args):
    self.sku_panel.visible = False
    self.rfq_panel.visible = True
    self.cost_sheet_panel.visible = False
    self.bom_panel.visible = False
    self.documents_panel.visible = False

  def cost_sheet_btn_click(self, **event_args):
    self.sku_panel.visible = False
    self.rfq_panel.visible = False
    self.cost_sheet_panel.visible = True
    self.bom_panel.visible = False
    self.documents_panel.visible = False

  def bom_btn_click(self, **event_args):
    self.sku_panel.visible = False
    self.rfq_panel.visible = False
    self.cost_sheet_panel.visible = False
    self.bom_panel.visible = True
    self.documents_panel.visible = False

  def documents_btn_click(self, **event_args):
    self.sku_panel.visible = False
    self.rfq_panel.visible = False
    self.cost_sheet_panel.visible = False
    self.bom_panel.visible = False
    self.documents_panel.visible = True

  def edit_btn_click(self, **event_args):
    popup = Style_edit_form()

    alert(
      content=popup,
      title=None,
      large=True,
      buttons=None 
    )
