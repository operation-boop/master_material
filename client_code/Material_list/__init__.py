from ._anvil_designer import Material_listTemplate
from anvil import *
import anvil.server
from ..Material_input_form import Material_input_form


class Material_list(Material_listTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.load_material_cards()
  

  def form_show(self, **event_args):
    self.load_material_cards()

  def add_btn_click(self, **event_args):
    """Reserve a preview document_id (no DB write) and open Material_input_form in an alert."""
    try:
      # 1) Get a preview id (read-only; does not create DB rows)
      doc_id = anvil.server.call("preview_next_document_id")
      Notification(f"Preparing new material: {doc_id}", style="info", timeout=1500).show()
  
      # 2) Build the popup form and wire events
      from ..Material_input_form import Material_input_form
      popup = Material_input_form(current_document_id=doc_id)
  
      # When the form saves/submits it will raise x-refresh-list with document_id
      popup.set_event_handler("x-refresh-list", lambda **e: self.load_material_cards())
  
      # When the form wants the alert closed it raises x-close-alert.
      # We keep a reference to the alert dialog (dlg) so we can dismiss it cleanly.
      def _on_child_close(**event_data):
        # event_data may contain keys: closed_by ('close'|'cancel'|'save'|'submit'), document_id
        try:
          # refresh to make sure latest data is shown (harmless if no changes)
          self.load_material_cards()
        except Exception:
          pass
          # dismiss the alert if the dialog object still exists
        try:
          dlg.dismiss()
        except Exception:
          # fallback: nothing — UI should still be fine
          pass
  
      popup.set_event_handler("x-close-alert", _on_child_close)
  
      # 3) Open the popup and keep the returned dialog object
      dlg = alert(content=popup, title=None, large=True, buttons=None)
  
    except Exception as e:
      alert(f"Could not open material editor: {e}")

  def load_material_cards(self, **event_args):
    try:
      self.repeating_panel_materials.items = anvil.server.call('list_material_cards')
    except Exception as e:
      alert(f"Could not load material cards: {e}", title="Load error")





  


