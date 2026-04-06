"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Array, Integer, Object, Reference, String, get_reference_uris
from tests.unit.helpers import make_uri


def test_empty_list():
    assert get_reference_uris([]) == []


def test_non_reference_fields_ignored():
    fields = [
        String({'type': 'string'}, uri=make_uri()),
        Integer({'type': 'integer'}, uri=make_uri()),
    ]
    assert get_reference_uris(fields) == []


def test_reference_field():
    ref = Reference({'$ref': 'other.json#/definitions/Foo'}, uri=make_uri())
    result = get_reference_uris([ref])
    assert len(result) == 1
    assert result[0].json_path == '/definitions/Foo'


def test_array_with_reference_items():
    arr = Array(
        {
            'type': 'array',
            'items': {'$ref': 'other.json#/definitions/Bar'},
        },
        uri=make_uri(),
    )
    result = get_reference_uris([arr])
    assert len(result) == 1


def test_array_with_non_reference_items():
    arr = Array(
        {
            'type': 'array',
            'items': {'type': 'string'},
        },
        uri=make_uri(),
    )
    assert get_reference_uris([arr]) == []


def test_object_with_reference_property():
    obj = Object(
        {
            'type': 'object',
            'properties': {
                'ref_field': {'$ref': 'other.json#/definitions/Foo'},
            },
        },
        uri=make_uri(),
    )
    result = get_reference_uris([obj])
    assert len(result) == 1


def test_duplicate_references_deduplicated():
    ref1 = Reference({'$ref': 'other.json#/definitions/Foo'}, uri=make_uri())
    ref2 = Reference({'$ref': 'other.json#/definitions/Foo'}, uri=make_uri())
    result = get_reference_uris([ref1, ref2])
    assert len(result) == 1


def test_same_file_different_definitions_not_deduplicated():
    ref1 = Reference({'$ref': 'other.json#/definitions/Foo'}, uri=make_uri())
    ref2 = Reference({'$ref': 'other.json#/definitions/Bar'}, uri=make_uri())
    result = get_reference_uris([ref1, ref2])
    assert len(result) == 2


def test_different_file_references_not_deduplicated():
    ref1 = Reference({'$ref': 'one.json#/definitions/A'}, uri=make_uri())
    ref2 = Reference({'$ref': 'two.json#/definitions/B'}, uri=make_uri())
    result = get_reference_uris([ref1, ref2])
    assert len(result) == 2


def test_mixed_field_types():
    fields = [
        String({'type': 'string'}, uri=make_uri()),
        Reference({'$ref': 'other.json#/definitions/Foo'}, uri=make_uri()),
        Integer({'type': 'integer'}, uri=make_uri()),
    ]
    result = get_reference_uris(fields)
    assert len(result) == 1
