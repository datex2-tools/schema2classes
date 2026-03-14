"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Object
from tests.unit.helpers import make_uri


def test_no_references():
    obj = Object(
        {
            'type': 'object',
            'properties': {'name': {'type': 'string'}},
        },
        uri=make_uri(),
    )
    assert obj.get_reference_base_uris() == []


def test_direct_reference():
    obj = Object(
        {
            'type': 'object',
            'properties': {
                'ref_field': {'$ref': 'other.json#/definitions/Foo'},
            },
        },
        uri=make_uri(),
    )
    uris = obj.get_reference_base_uris()
    assert len(uris) == 1
    assert uris[0].json_path == ''


def test_reference_in_array_items():
    obj = Object(
        {
            'type': 'object',
            'properties': {
                'items': {
                    'type': 'array',
                    'items': {'$ref': 'other.json#/definitions/Bar'},
                },
            },
        },
        uri=make_uri(),
    )
    uris = obj.get_reference_base_uris()
    assert len(uris) == 1


def test_multiple_references_to_same_file_deduplicated():
    obj = Object(
        {
            'type': 'object',
            'properties': {
                'a': {'$ref': 'other.json#/definitions/Foo'},
                'b': {'$ref': 'other.json#/definitions/Bar'},
            },
        },
        uri=make_uri(),
    )
    uris = obj.get_reference_base_uris()
    assert len(uris) == 1


def test_references_to_different_files():
    obj = Object(
        {
            'type': 'object',
            'properties': {
                'a': {'$ref': 'one.json#/definitions/A'},
                'b': {'$ref': 'two.json#/definitions/B'},
            },
        },
        uri=make_uri(),
    )
    uris = obj.get_reference_base_uris()
    assert len(uris) == 2


def test_reference_in_nested_object():
    obj = Object(
        {
            'type': 'object',
            'properties': {
                'inner': {
                    'type': 'object',
                    'properties': {
                        'ref_field': {'$ref': 'nested.json#/definitions/X'},
                    },
                },
            },
        },
        uri=make_uri(),
    )
    uris = obj.get_reference_base_uris()
    assert len(uris) == 1
