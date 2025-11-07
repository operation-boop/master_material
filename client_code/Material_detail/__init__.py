# material_detail.py
from ._anvil_designer import Material_detailTemplate
from anvil import *
import anvil.server
from datetime import datetime

class Material_detail(Material_detailTemplate):
  def __init__(self, document_id=None, **properties):
    """
    document_id: the document_id string (e.g. 'vin_mmat_0001')
    Expected designer controls (recommended names):
      - label_material_id
      - label_version_number
      - label_name
      - label_supplier
      - label_material_type
      - label_country_of_origin
      - label_created_at
      - label_created_by
      - label_submitted_at
      - label_submitted_by
      - label_original_cost_per_unit
      - label_unit_of_measure
      - label_landed_cost_per_unit
      - label_fabric_composition (or repeating panel)
      - (optional) repeating_panel_composition (for nicer list)
    The form will set whichever of those controls it finds.
    """

    self.init_components(**properties)
    self.document_id = document_id

    # Friendly header if you have one
    if hasattr(self, "title_label") and self.document_id:
      try:
        self.title_label.text = f"Material details — {self.document_id}"
      except Exception:
        pass

    # load data (non-blocking note: this is a server call; fine on init)
    if self.document_id:
      try:
        master = anvil.server.call('get_master_material', self.document_id)
      except Exception as e:
        Notification(f"Error loading material: {e}", style="danger").show()
        master = None

      if master:
        version = master.get('current_version')
        # fallback: if master stores row fields directly
        if not version:
          version = master

        self._populate_from_version(version, master)
      else:
        # nothing found
        if hasattr(self, "label_empty"):
          self.label_empty.text = "No data found for this document."

  # ----------------- helpers -----------------
  def _set_label(self, control_name, text):
    """Safely set label text if control exists."""
    if not text and text != 0:
      text = ""
    if hasattr(self, control_name):
      try:
        getattr(self, control_name).text = str(text)
      except Exception:
        # some controls may be dropdowns in other forms; try selected_value
        try:
          getattr(self, control_name).selected_value = text
        except Exception:
          pass

  def _format_dt(self, dt):
    if not dt:
      return ""
    if isinstance(dt, datetime):
      return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)

  def _parse_composition(self, comp_str):
    """
    Parse "Cotton:60%|Polyester:40%" -> list of dicts
    """
    items = []
    if not comp_str:
      return items
    for part in comp_str.split("|"):
      if ":" in part:
        mat, pct = part.split(":", 1)
        pct = pct.replace("%", "").strip()
        try:
          pct_val = float(pct)
        except Exception:
          pct_val = pct
        items.append({"material": mat.strip(), "percentage": pct_val})
    return items

  def _populate_from_version(self, version, master_row=None):
    """
    Fill UI controls from a version dict/row.
    Use the same keys as collect_form_data in mat_input_form.py
    """
    # Basic / header fields
    self._set_label("label_material_id", version.get("master_material_id") or version.get("document_id") or (master_row.get("document_id") if master_row else None))
    self._set_label("label_version_number", version.get("ver_num") or version.get("current_version_number") or "")
    self._set_label("label_name", version.get("name"))
    self._set_label("label_supplier", version.get("supplier_name"))
    self._set_label("label_material_type", version.get("material_type"))
    self._set_label("label_country_of_origin", version.get("country_of_origin"))

    # timestamps & users
    self._set_label("label_created_at", self._format_dt(version.get("created_at")))
    self._set_label("label_created_by", version.get("created_by"))

    # version-submitted fields
    # sometimes submitted_at/ submitted_by may be on master row (server sets both) - prefer version
    submitted_ts = version.get("submitted_at") or (master_row.get("submitted_at") if master_row else None)
    submitted_by = version.get("submitted_by") or (master_row.get("submitted_by") if master_row else None)
    self._set_label("label_submitted_at", self._format_dt(submitted_ts))
    self._set_label("label_submitted_by", submitted_by)

    # costs & units
    self._set_label("label_original_cost_per_unit", version.get("original_cost_per_unit"))
    self._set_label("label_unit_of_measure", version.get("unit_of_measurement") or version.get("weight_uom") or version.get("native_cost_currency"))
    self._set_label("label_landed_cost_per_unit", version.get("landed_cost_per_unit"))
    self._set_label("label_effective_cost_per_unit", version.get("effective_cost_per_unit"))

    # composition: either show as label string or populate a repeating panel if present
    comp_raw = version.get("fabric_composition") or version.get("generic_material_composition") or ""
    comp_list = self._parse_composition(comp_raw)
    if hasattr(self, "repeating_panel_composition") and comp_list:
      try:
        # convert to a nice list for RP items
        rp_items = []
        for c in comp_list:
          rp_items.append({
            "material": c.get("material"),
            "percentage": c.get("percentage"),
            "display": f"{c.get('percentage')}% {c.get('material')}"
          })
        self.repeating_panel_composition.items = rp_items
      except Exception:
        # fallback to setting a single label if the repeating panel fail
        self._set_label("label_fabric_composition", comp_raw)
    else:
      # show as simple label
      # If comp_raw empty but comp_list set, format nicely:
      if not comp_raw and comp_list:
        comp_raw = " | ".join([f"{c['material']}:{c['percentage']}%" for c in comp_list])
      self._set_label("label_fabric_composition", comp_raw)

    # other fields you might want to show
    self._set_label("label_weight_per_unit", version.get("weight_per_unit"))
    self._set_label("label_weight_uom", version.get("weight_uom"))
    self._set_label("label_ref_id", version.get("ref_id"))
    self._set_label("label_change_description", version.get("change_description"))
