from ._anvil_designer import documents_itemtemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class documents_itemtemplate(documents_itemtemplateTemplate):
  def __init__(self, item=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item = item

    # Default icon URLs
    doc_icon = "https://cdn-icons-png.flaticon.com/512/124/124837.png"
    img_video_icon = "https://cdn-icons-png.flaticon.com/128/1850/1850108.png"
    excel_icon = "https://cdn-icons-png.flaticon.com/128/17667/17667149.png"

    file_media = self.item['doc_name']

    # Convert to lowercase string
    filename = str(file_media).lower() if file_media else ""

    if filename.endswith((".png", ".jpg", ".jpeg", ".gif")):
      self.img_preview.source = img_video_icon
    elif filename.endswith((".mp4", ".mov", ".avi")):
      self.img_preview.source = img_video_icon
    elif filename.endswith((".xls", ".xlsx")):
      self.img_preview.source = excel_icon
    elif filename.endswith(".pdf"):
      self.img_preview.source = doc_icon
    else:
      # fallback
      self.img_preview.source = doc_icon