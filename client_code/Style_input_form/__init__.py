from ._anvil_designer import Style_input_formTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Style_input_form(Style_input_formTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.color_list = []   # store colors temporarily
    self.size_list = []    # store sizes
    self.repeating_panel_colors.items = self.color_list
    self.repeating_panel_sizes.items = self.size_list

    # Listen for remove request
    self.set_event_handler('x-remove-color', self.remove_color)
    self.set_event_handler('x-remove-size', self.remove_size)
    # Any code you write here will run before the form opens.

  # ---- COLOR ADD ----
  def add_color_btn_click(self, **event_args):
    color = (self.color.text or "").strip()
    if color and color not in self.color_list:
      self.color_list.append(color)
      self.repeating_panel_colors.items = self.color_list[:]   # refresh
    self.color.text = ""

  def remove_color(self, value, **event_args):
    if value in self.color_list:
      self.color_list.remove(value)
      self.repeating_panel_colors.items = self.color_list[:]

  # ---- SIZE ADD ----
  def add_size_btn_click(self, **event_args):
    size = (self.size.text or "").strip()
    if size and size not in self.size_list:
      self.size_list.append(size)
      self.repeating_panel_sizes.items = self.size_list[:]
    self.size.text = ""

  def remove_size(self, value, **event_args):
    if value in self.size_list:
      self.size_list.remove(value)
      self.repeating_panel_sizes.items = self.size_list[:]