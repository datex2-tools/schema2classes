"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Schema

from tests.unit.helpers import make_uri


def test_from_object_properties():
    schema = Schema(
        {
            'type': 'object',
            'properties': {
                'ref_field': {'$ref': 'other.json#/definitions/Foo'},
            },
        },
        uri=make_uri(),
    )
    uris = schema.get_reference_base_uris()
    assert len(uris) == 1


def test_from_definitions():
    schema = Schema(
        {
            'definitions': {
                'Ref': {'$ref': 'other.json#/definitions/Foo'},
            },
        },
        uri=make_uri(),
    )
    uris = schema.get_reference_base_uris()
    assert len(uris) == 1


def test_from_both():
    schema = Schema(
        {
            'type': 'object',
            'properties': {
                'ref_a': {'$ref': 'a.json#/definitions/A'},
            },
            'definitions': {
                'Ref': {'$ref': 'b.json#/definitions/B'},
            },
        },
        uri=make_uri(),
    )
    uris = schema.get_reference_base_uris()
    assert len(uris) == 2


def test_no_references():
    schema = Schema(
        {
            'type': 'object',
            'properties': {'name': {'type': 'string'}},
        },
        uri=make_uri(),
    )
    assert schema.get_reference_base_uris() == []


def test_definitions_only_no_object():
    schema = Schema(
        {
            'definitions': {
                'Ref': {'$ref': 'other.json#/definitions/Foo'},
            },
        },
        uri=make_uri(),
    )
    uris = schema.get_reference_base_uris()
    assert len(uris) == 1
