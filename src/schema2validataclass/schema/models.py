"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import dataclass
from typing import Any

from schema2validataclass.common.uri import URI


@dataclass(kw_only=True, init=False)
class BaseField:
    uri: URI
    title: str | None = None
    description: str | None = None
    default: Any | None = None
    required: bool = False

    def __init__(self, schema: dict, uri: URI, required: bool = False):
        self.uri = uri
        self.required = required
        self.title = schema.get('title')
        self.description = schema.get('description')
        self.default = schema.get('default')


@dataclass(kw_only=True, init=False)
class Boolean(BaseField):
    default: bool | None = None


@dataclass(kw_only=True, init=False)
class String(BaseField):
    default: str | None = None
    minLength: int | None = None
    maxLength: int | None = None

    pattern: str | None = None

    def __init__(self, schema: dict, **kwargs):
        super().__init__(schema, **kwargs)
        self.pattern = schema.get('pattern')


@dataclass(kw_only=True, init=False)
class Integer(BaseField):
    default: int | None = None

    minimum: int | None = None
    exclusiveMinimum: int | None = None
    maximum: int | None = None
    exclusiveMaximum: int | None = None

    def __init__(self, schema: dict, **kwargs):
        super().__init__(schema, **kwargs)

        # 0.0 is a valid integer in JSON
        if isinstance(self.default, float):
            self.default = int(self.default)
        self.minimum = schema.get('minimum')
        if isinstance(self.minimum, float):
            self.minimum = int(self.minimum)
        self.exclusiveMinimum = schema.get('exclusiveMinimum')
        if isinstance(self.exclusiveMinimum, float):
            self.exclusiveMinimum = int(self.exclusiveMinimum)
        self.maximum = schema.get('maximum')
        if isinstance(self.maximum, float):
            self.maximum = int(self.maximum)
        self.exclusiveMaximum = schema.get('exclusiveMaximum')
        if isinstance(self.exclusiveMaximum, float):
            self.exclusiveMaximum = int(self.exclusiveMaximum)


@dataclass(kw_only=True, init=False)
class Number(BaseField):
    default: float | int | None = None

    minimum: float | int | None = None
    exclusiveMinimum: float | int | None = None
    maximum: float | int | None = None
    exclusiveMaximum: float | int | None = None

    def __init__(self, schema: dict, **kwargs):
        super().__init__(schema, **kwargs)
        self.minimum = schema.get('minimum')
        self.exclusiveMinimum = schema.get('exclusiveMinimum')
        self.maximum = schema.get('maximum')
        self.exclusiveMaximum = schema.get('exclusiveMaximum')


@dataclass(kw_only=True, init=False)
class Enum(BaseField):
    default: str | None = None

    enum: list[str]

    def __init__(self, schema: dict, **kwargs):
        super().__init__(schema, **kwargs)
        self.enum = schema.get('enum')


@dataclass(kw_only=True, init=False)
class Array(BaseField):
    default: list[Any] | None = None

    minItems: int | None = None
    maxItems: int | None = None

    items: BaseField

    def __init__(self, schema: dict, uri: URI, **kwargs):
        super().__init__(schema, uri=uri, **kwargs)
        self.items = parse_schema(schema.get('items'), uri=uri)


@dataclass(kw_only=True, init=False)
class Reference(BaseField):
    uri: URI
    to: URI

    # References can have all possible values, which should be patched on the referenced object
    # TODO: for proper null support, we will need a special UnsetValue

    # Array
    minItems: int | None = None
    maxItems: int | None = None

    # Integer and Number
    minimum: float | int | None = None
    exclusiveMinimum: float | int | None = None
    maximum: float | int | None = None
    exclusiveMaximum: float | int | None = None

    # String
    minLength: int | None = None
    maxLength: int | None = None

    # Regex
    pattern: str | None = None

    # Enum
    enum: list[str] | None = None

    def __init__(self, schema: dict, uri: URI, **kwargs):
        super().__init__(schema, uri=uri, **kwargs)
        self.to = URI.from_reference(uri=uri, reference=schema.get('$ref'))

        keys: list[str] = [
            'minItems',
            'maxItems',
            'minimum',
            'exclusiveMinimum',
            'maximum',
            'exclusiveMaximum',
            'minLength',
            'maxLength',
            'pattern',
            'enum',
        ]
        for key in keys:
            setattr(self, key, schema.get(key))


@dataclass(kw_only=True, init=False)
class Object(BaseField):
    properties: list[BaseField]
    required: list[str]

    def __init__(self, schema: dict, uri: URI, **kwargs):
        super().__init__(schema, uri=uri, **kwargs)
        self.required = schema.get('required', [])

        self.properties = []
        for key, child_schema in schema.get('properties', {}).items():
            child_uri = URI.from_uri(uri, f'/properties/{key}')
            self.properties.append(parse_schema(child_schema, uri=child_uri, required=key in self.required))

    def get_objects(self) -> list['Object']:
        result = [self]
        for field in self.properties:
            if isinstance(field, Object):
                result.extend(field.get_objects())
            if isinstance(field, Array) and isinstance(field.items, Object):
                result.extend(field.items.get_objects())
        return result

    def get_reference_base_uris(self) -> list[URI]:
        return get_reference_base_uris(self.properties)


@dataclass(kw_only=True, init=False)
class Schema:
    definitions: list[BaseField]
    contained_object: Object | None = None

    def __init__(self, schema: dict, uri: URI):
        # TODO: does it make sense to have something else then objects here?
        if schema.get('type') == 'object':
            self.contained_object = Object(schema, uri=uri)

        self.definitions = []
        raw_definitions: dict[str, Any] = schema.get('$defs', {}) or schema.get('definitions', {})
        for key, child_schema in raw_definitions.items():
            self.definitions.append(parse_schema(child_schema, uri=URI.from_uri(uri, f'/definitions/{key}')))

    @property
    def properties(self) -> list[BaseField]:
        return self.contained_object.properties if self.contained_object else []

    def get_reference_base_uris(self) -> list[URI]:
        reference_uris = get_reference_base_uris(self.definitions)
        if self.contained_object:
            reference_uris.extend(self.contained_object.get_reference_base_uris())
        return reference_uris


def parse_schema(schema: dict, **kwargs) -> BaseField:
    # Special cases without type
    if schema.get('enum') is not None:
        return Enum(schema, **kwargs)
    if schema.get('$ref') is not None:
        return Reference(schema, **kwargs)

    # Type cases
    if schema.get('type') == 'boolean':
        return Boolean(schema, **kwargs)
    if schema.get('type') == 'integer':
        return Integer(schema, **kwargs)
    if schema.get('type') == 'number':
        return Number(schema, **kwargs)
    if schema.get('type') == 'string':
        return String(schema, **kwargs)
    if schema.get('type') == 'array':
        return Array(schema, **kwargs)
    if schema.get('type') == 'object':
        return Object(schema, **kwargs)

    raise ValueError(f'Unsupported type: {schema.get("type")}')


def get_reference_base_uris(fields: list[BaseField]) -> list[URI]:
    result: list[URI] = []
    for field in fields:
        # Incrementally look in children
        if isinstance(field, Object):
            result.extend(field.get_reference_base_uris())

        # Get References
        if isinstance(field, Reference) and field.uri is not None:
            result.append(URI.from_uri_without_json_path(field.to))
        if isinstance(field, Array) and isinstance(field.items, Reference) and field.items.uri is not None:
            result.append(URI.from_uri_without_json_path(field.items.to))

    return list(set(result))
