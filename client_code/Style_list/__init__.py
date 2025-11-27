from ._anvil_designer import Style_listTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Style_input_form import Style_input_form


class Style_list(Style_listTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.form_show()
    # Any code you write here will run before the form opens.

  def form_show(self, **event_args):
    master_style_list = [
      {
        "id": "MS-001",
        "ref_id": "REF-COAT-001",
        "client": "ZARA",
        "picture": "http://2.bp.blogspot.com/-qv-gBR6zXq4/UG8qGKKQuZI/AAAAAAAAUiI/IqmkCL26kvo/s1600/3_4_length_faux_wool_reefer_coat_camel1344009661.jpg",
        "description": "Classic wool coat with tailored fit.",
        "estimated_completion_time": "12/10/2025"
      },
      {
        "id": "MS-002",
        "ref_id": "REF-JKT-014",
        "client": "UNIQLO",
        "picture": "https://i.pinimg.com/originals/d8/ab/eb/d8abebc15fdb527fce240c60c0d08a8b.jpg",
        "description": "Lightweight padded jacket suitable for mild winter.",
        "estimated_completion_time": "03/11/2025"
      },
      {
        "id": "MS-003",
        "ref_id": "REF-DRESS-020",
        "client": "H&M",
        "picture": "https://i.pinimg.com/originals/bb/4a/7f/bb4a7f1187e471b08edad88fe1d0be08.jpg",
        "description": "Knee-length summer dress with printed fabric.",
        "estimated_completion_time": "23/09/2025"
      },
      {
        "id": "MS-004",
        "ref_id": "REF-TOP-009",
        "client": "SHEIN",
        "picture": "https://images-na.ssl-images-amazon.com/images/I/81In11KF7ML._AC_UL1500_.jpg",
        "description": "Casual cotton short-sleeve top.",
        "estimated_completion_time": "1/11/2025"
      },
      {
        "id": "MS-005",
        "ref_id": "REF-PANTS-012",
        "client": "MANGO",
        "picture": "https://oldnavy.gap.com/webcontent/0056/234/314/cn56234314.jpg",
        "description": "High-waisted straight cut trousers.",
        "estimated_completion_time": "5/10/2025"
      }
    ]


    for style in master_style_list:
      style['picture'] = URLMedia(style['picture'])

    self.repeating_panel_master_style.items = master_style_list

  def add_btn_click(self, **event_args):
    popup = Style_input_form()

    alert(
      content=popup,
      title=None,
      large=True,
      buttons=None 
    )

