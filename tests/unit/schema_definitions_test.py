"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Enum, Integer, Object, Reference, Schema, String

from tests.unit.helpers import make_uri


def test_definitions_key():
    schema = Schema(
        {
            'definitions': {
                'Foo': {'type': 'string'},
                'Bar': {'type': 'integer'},
            },
        },
        uri=make_uri(),
    )
    assert len(schema.definitions) == 2
    assert isinstance(schema.definitions[0], String)
    assert isinstance(schema.definitions[1], Integer)


def test_defs_key():
    schema = Schema(
        {
            '$defs': {
                'Foo': {'type': 'string'},
            },
        },
        uri=make_uri(),
    )
    assert len(schema.definitions) == 1
    assert isinstance(schema.definitions[0], String)


def test_no_definitions():
    schema = Schema(
        {
            'type': 'object',
            'properties': {},
        },
        uri=make_uri(),
    )
    assert schema.definitions == []


def test_definition_uris_have_definitions_path():
    schema = Schema(
        {
            'definitions': {'MyType': {'type': 'string'}},
        },
        uri=make_uri(),
    )
    assert schema.definitions[0].uri.json_path.endswith('/definitions/MyType')


def test_definitions_with_objects():
    schema = Schema(
        {
            'definitions': {
                'Inner': {
                    'type': 'object',
                    'properties': {'val': {'type': 'string'}},
                },
            },
        },
        uri=make_uri(),
    )
    assert len(schema.definitions) == 1
    assert isinstance(schema.definitions[0], Object)


def test_definitions_with_enums():
    schema = Schema(
        {
            'definitions': {
                'Status': {'enum': ['active', 'inactive']},
            },
        },
        uri=make_uri(),
    )
    assert isinstance(schema.definitions[0], Enum)


def test_definitions_with_references():
    schema = Schema(
        {
            'definitions': {
                'Ref': {'$ref': 'other.json#/definitions/X'},
            },
        },
        uri=make_uri(),
    )
    assert isinstance(schema.definitions[0], Reference)
