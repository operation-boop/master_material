import anvil.server
from api_framework import APIRegistry
from pydantic import TypeAdapter
import json
import material_api
import materialcard_api
import admin_api

@anvil.server.callable
def get_api_documentation():
  """
    Returns API documentation in a format suitable for the front-end viewer
    """
  docs = APIRegistry.get_all_endpoints()

  # This helper function resolves properties whether they are defined at the root 
  # or inside the $defs section (which Pydantic V2 uses heavily).
  def get_properties_from_schema(schema_root):
    if not schema_root:
      return {}

      # 1. Check for Reference Pointer ($ref)
    if '$ref' in schema_root:
      # Get the definition name (e.g., 'MaterialDetailResponse')
      ref_name = schema_root['$ref'].split('/')[-1]

      # Look inside the $defs section for the actual properties
      # Note: We must assume the definitions are also available in the schema output
      if '$defs' in schema_root and ref_name in schema_root['$defs']:
        return schema_root['$defs'][ref_name].get('properties', {})
      return {}

      # 2. Check for Array (List)
    if schema_root.get('type') == 'array':
      items = schema_root.get('items', {})
      # If the items are also a ref, try to resolve them recursively
      if '$ref' in items and '$defs' in schema_root:
        ref_name = items['$ref'].split('/')[-1]
        return schema_root['$defs'][ref_name].get('properties', {})
      return items.get('properties', {})

      # 3. Standard Object (Properties defined directly)
    return schema_root.get('properties', {})

  result = {}
  for name, endpoint in docs.items():

    # --- 1. BUILD REQUEST SCHEMA ---
    request_schema = {}
    if endpoint.request_model:
      schema = TypeAdapter(endpoint.request_model).json_schema()
      properties = get_properties_from_schema(schema) 
      required = schema.get('required', [])

      for field_name, field_info in properties.items():
        request_schema[field_name] = {
          'type': field_info.get('type', 'any'),
          'required': field_name in required,
          'description': field_info.get('description', ''),
          'example': field_info.get('example')
        }

        # --- 2. BUILD RESPONSE SCHEMA ---
    response_schema = {}
    if endpoint.response_model:
      schema = TypeAdapter(endpoint.response_model).json_schema()
      properties = get_properties_from_schema(schema) # Use helper here too
      required = schema.get('required', [])

      for field_name, field_info in properties.items():
        response_schema[field_name] = {
          'type': field_info.get('type', 'any'),
          'required': field_name in required,
          'description': field_info.get('description', ''),
          'example': field_info.get('example')
        }

    result[name] = {
      'name': endpoint.name,
      'summary': endpoint.summary,
      'description': endpoint.description,
      'tags': endpoint.tags,
      'request': request_schema,
      'response': response_schema,
      'exampleRequest': endpoint.example_request or {},
      'exampleResponse': endpoint.example_response or {}
    }

  return result


@anvil.server.callable
def get_api_documentation_markdown():
  """
    Returns API documentation in markdown format
    """
  from api_framework import export_api_docs
  return export_api_docs(format='markdown')


@anvil.server.callable
def get_api_documentation_openapi():
  """
    Returns API documentation in OpenAPI 3.0 format
    """
  return APIRegistry.generate_documentation()