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
    Returns:
        dict: Complete API documentation
    """
  docs = APIRegistry.get_all_endpoints()

  result = {}
  for name, endpoint in docs.items():
    # Build request schema
    request_schema = {}
    if endpoint.request_model:
      schema = TypeAdapter(endpoint.request_model).json_schema()
      properties = schema.get('properties', {})
      required = schema.get('required', [])

      for field_name, field_info in properties.items():
        request_schema[field_name] = {
          'type': field_info.get('type', 'any'),
          'required': field_name in required,
          'description': field_info.get('description', ''),
          'example': field_info.get('example')
        }

        # Build response schema
    response_schema = {}
    if endpoint.response_model:
      schema = TypeAdapter(endpoint.response_model).json_schema()
      properties = schema.get('properties', {})
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
    
    Returns:
        str: Markdown documentation
    """
  from api_framework import export_api_docs
  return export_api_docs(format='markdown')


@anvil.server.callable
def get_api_documentation_openapi():
  """
    Returns API documentation in OpenAPI 3.0 format
    """
  return APIRegistry.generate_documentation()

