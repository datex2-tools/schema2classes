"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import Array, Boolean, Enum, Integer, Object, Reference, String
from tests.unit.helpers import make_uri


def test_empty_properties():
    result = Object({'type': 'object', 'properties': {}}, uri=make_uri())
    assert result.properties == []


def test_no_properties_key():
    result = Object({'type': 'object'}, uri=make_uri())
    assert result.properties == []


def test_single_string_property():
    result = Object(
        {
            'type': 'object',
            'properties': {'name': {'type': 'string'}},
        },
        uri=make_uri(),
    )
    assert len(result.properties) == 1
    assert isinstance(result.properties[0], String)


def test_multiple_properties():
    result = Object(
        {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'},
                'active': {'type': 'boolean'},
            },
        },
        uri=make_uri(),
    )
    assert len(result.properties) == 3
    assert isinstance(result.properties[0], String)
    assert isinstance(result.properties[1], Integer)
    assert isinstance(result.properties[2], Boolean)


def test_required_fields():
    result = Object(
        {
            'type': 'object',
            'required': ['name'],
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'},
            },
        },
        uri=make_uri(),
    )
    assert result.properties[0].required is True
    assert result.properties[1].required is False


def test_all_required():
    result = Object(
        {
            'type': 'object',
            'required': ['name', 'age'],
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'},
            },
        },
        uri=make_uri(),
    )
    assert all(prop.required for prop in result.properties)


def test_no_required_array():
    result = Object(
        {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
            },
        },
        uri=make_uri(),
    )
    assert result.required == []
    assert result.properties[0].required is False


def test_child_uris_have_properties_path():
    uri = make_uri()
    result = Object(
        {
            'type': 'object',
            'properties': {'field_a': {'type': 'string'}},
        },
        uri=uri,
    )
    assert result.properties[0].uri.json_path.endswith('/properties/field_a')


def test_nested_object():
    result = Object(
        {
            'type': 'object',
            'properties': {
                'inner': {
                    'type': 'object',
                    'properties': {'value': {'type': 'integer'}},
                },
            },
        },
        uri=make_uri(),
    )
    assert isinstance(result.properties[0], Object)
    inner = result.properties[0]
    assert len(inner.properties) == 1
    assert isinstance(inner.properties[0], Integer)


def test_property_with_reference():
    result = Object(
        {
            'type': 'object',
            'properties': {
                'ref_field': {'$ref': 'other.json#/definitions/Thing'},
            },
        },
        uri=make_uri(),
    )
    assert isinstance(result.properties[0], Reference)


def test_property_with_enum():
    result = Object(
        {
            'type': 'object',
            'properties': {
                'status': {'enum': ['active', 'inactive']},
            },
        },
        uri=make_uri(),
    )
    assert isinstance(result.properties[0], Enum)


def test_property_with_array():
    result = Object(
        {
            'type': 'object',
            'properties': {
                'tags': {'type': 'array', 'items': {'type': 'string'}},
            },
        },
        uri=make_uri(),
    )
    assert isinstance(result.properties[0], Array)


def test_title_and_description():
    result = Object(
        {
            'type': 'object',
            'title': 'My Object',
            'description': 'An object',
            'properties': {},
        },
        uri=make_uri(),
    )
    assert result.title == 'My Object'
    assert result.description == 'An object'
