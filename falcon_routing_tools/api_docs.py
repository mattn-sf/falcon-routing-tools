import inspect
from apispec.ext.marshmallow.openapi import OpenAPIConverter

OPEN_API_VERSION = '3.0.2'


class Operation():
    def __init__(self, verb, handler):
        self.verb = verb
        self.handler = handler

class APIDocs():
    @staticmethod
    def generate(routes, title='', version=''):
        return dict(
            openapi=OPEN_API_VERSION,
            info=dict(
                title=title,
                version=version
            ),
            paths={
                route.path: APIDocs._get_resource_spec(route.resource)
                for route in routes
            }
        )

    @staticmethod
    def _get_resource_spec(resource):
        return {
            operation.verb: APIDocs._get_operation_spec(operation.handler)
            for operation in APIDocs._get_operations_from_resource(resource)
        }


    @staticmethod
    def _get_operations_from_resource(resource):
        supported_operations = ['get', 'put', 'post', 'delete', 'patch']

        operations = []

        for operation in supported_operations:
            handler = getattr(resource, f'on_{operation}', None)
            if not handler:
                continue

            operations.append(Operation(operation, handler))

        return operations


    @staticmethod
    def _get_operation_spec(handler):
        closure_vars = inspect.getclosurevars(handler)
        description = closure_vars.nonlocals.get('description', '')
        payload_schema = closure_vars.nonlocals.get('payload_schema')
        response_schema = closure_vars.nonlocals.get('response_schema')
        success_response_code = closure_vars.nonlocals.get('success_response_code')

        openApiConverter = OpenAPIConverter(OPEN_API_VERSION, lambda s: None, None)

        request_body = {}
        response = {}

        if payload_schema:
            payload_schema_dict = openApiConverter.schema2jsonschema(payload_schema)

            request_body = dict(
                requestBody=dict(
                    description=payload_schema.__name__,
                    content={
                        'application/json': {
                            'schema': payload_schema_dict
                        }
                    }
                )
            )

        if response_schema:
            response_schema_dict = openApiConverter.schema2jsonschema(response_schema)

            response = {
                f'{success_response_code}': {
                    'description': 'success',
                    'content': {
                        'application/json': {
                            'schema': response_schema_dict
                        }
                    }
                }
            }
        else:
            response = {
                f'{success_response_code}': ''
            }



        return {
            'description': description,
            'responses': {
                **response
            },
            **request_body
        }
