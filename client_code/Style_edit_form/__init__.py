from ._anvil_designer import Style_edit_formTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Style_edit_form(Style_edit_formTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.variation_count.text = "This will create 0 SKUs (0 colors x 0 sizes)"
    # Any code you write here will run before the form opens.

  def add_color_tag(self, color_text):
    # Create a container for the tag (horizontal layout)
    tag_panel = FlowPanel()
    tag_panel.spacing = "3px"
    tag_panel.role = None

    # Tag label (content)
    tag_label = Label(text=color_text, bold=True)
    tag_label.role = "tag-label"  # We style this role below

    # Remove button
    # Remove button
    remove_btn = Button(text="✕", role="tag-remove", width="18px")

    # Store value so you can retrieve later if needed
    tag_panel.tag_value = color_text

    # Define remove action
    def remove_color(sender, **event_args):
      tag_panel.remove_from_parent()
      self.update_variation_sentence()

    remove_btn.set_event_handler("click", remove_color)

    # Add label + remove button into the tag container
    tag_panel.add_component(tag_label)
    tag_panel.add_component(remove_btn)

    # Add the tag container to the horizontal main FlowPanel
    self.flow_panel_colors.add_component(tag_panel)

  def add_color_btn_click(self, **event_args):
    color_value = self.color.text.strip()
    if color_value:
      self.add_color_tag(color_value)
      self.color.text = ""  # clear input
      self.update_variation_sentence()

  def add_size_tag(self, size_text):
    tag_panel = FlowPanel(spacing="3px")

    tag_label = Label(text=size_text, bold=True)
    tag_label.role = "tag-label"

    remove_btn = Button(text="✕", role="tag-remove", width="18px")
    tag_panel.tag_value = size_text

    def remove_size(sender, **event_args):
      tag_panel.remove_from_parent()
      self.update_variation_sentence()

    remove_btn.set_event_handler("click", remove_size)

    tag_panel.add_component(tag_label)
    tag_panel.add_component(remove_btn)

    self.flow_panel_sizes.add_component(tag_panel)

  def add_size_btn_click(self, **event_args):
    size_value = self.size.text.strip()
    if size_value:
      self.add_size_tag(size_value)
      self.size.text = ""
      self.update_variation_sentence()

  def update_variation_sentence(self):
    color_count = len(self.flow_panel_colors.get_components())
    size_count = len(self.flow_panel_sizes.get_components())
    total = color_count * size_count

    self.variation_count.text = (
      f"This will create {total} SKUs ({color_count} colors x {size_count} sizes)"
    )

  def close_btn_click(self, **event_args):
    self.raise_event("x-close-alert")

  def cancel_btn_click(self, **event_args):
    self.raise_event("x-close-alert")

  def file_loader_change(self, file, **event_args):
    """Called when the user selects a file"""
    if file is not None:
      # Only preview if it's an image
      if isinstance(file, anvil.BlobMedia) and file.content_type.startswith("image/"):
        self.img_preview.source = file
      else:
        # Optional: clear preview if not an image
        self.img_preview.source = None
        alert("Please upload an image file (png, jpg, jpeg)")

  def submit_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
