"""
OpenAPI YAML Export for Redoc
Add this to your Anvil server modules
"""
import anvil.server

import yaml
import json
from datetime import datetime


@anvil.server.callable
def download_openapi_yaml():
  """
    Generate and return OpenAPI specification in YAML format for Redoc.
    
    Returns:
        anvil.BlobMedia: YAML file ready for download
    """
  # Generate OpenAPI documentation
  openapi_dict = APIRegistry.generate_documentation()

  # Convert to YAML
  yaml_content = yaml.dump(
    openapi_dict,
    default_flow_style=False,
    sort_keys=False,
    allow_unicode=True
  )

  # Create a downloadable file
  from anvil import BlobMedia

  # Generate filename with timestamp
  filename = f"openapi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"

  return BlobMedia(
    content_type="application/x-yaml",
    content=yaml_content.encode('utf-8'),
    name=filename
  )


@anvil.server.callable
def get_openapi_yaml_string():
  """
    Get OpenAPI specification as a YAML string.
    Useful for displaying in the UI or copying to clipboard.
    
    Returns:
        str: YAML formatted OpenAPI specification
    """
  openapi_dict = APIRegistry.generate_documentation()

  yaml_content = yaml.dump(
    openapi_dict,
    default_flow_style=False,
    sort_keys=False,
    allow_unicode=True
  )

  return yaml_content


@anvil.server.callable
def get_redoc_html():
  """
    Generate a complete HTML page with embedded Redoc viewer.
    This can be displayed directly in Anvil or saved as standalone HTML.
    
    Returns:
        str: Complete HTML with Redoc and your API spec embedded
    """
  # Get the OpenAPI spec as JSON (Redoc accepts both YAML and JSON)
  openapi_dict = APIRegistry.generate_documentation()
  openapi_json = json.dumps(openapi_dict, indent=2)

  html = f"""<!DOCTYPE html>
<html>
<head>
    <title>API Documentation - Redoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <redoc spec-url='#'></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
    <script>
        // Embed the spec directly in the page
        const spec = {openapi_json};
        Redoc.init(spec, {{}}, document.querySelector('redoc'));
    </script>
</body>
</html>"""

  return html


@anvil.server.callable
def download_redoc_html():
  """
    Generate and return a complete standalone Redoc HTML file for download.
    
    Returns:
        anvil.BlobMedia: Self-contained HTML file with Redoc
    """
  html_content = get_redoc_html()

  from anvil import BlobMedia

  filename = f"api_docs_redoc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

  return BlobMedia(
    content_type="text/html",
    content=html_content.encode('utf-8'),
    name=filename
  )


# Optional: Function to get spec URL for external Redoc
@anvil.server.callable
def get_openapi_spec_url():
  """
    If you host the YAML file somewhere, return its URL.
    This is useful for pointing Redoc to an external spec file.
    
    Returns:
        str: URL where the OpenAPI spec is hosted
    """
  # You would implement this if you host the YAML file on a CDN or server
  # For now, return a placeholder
  return "https://your-domain.com/openapi.yaml"