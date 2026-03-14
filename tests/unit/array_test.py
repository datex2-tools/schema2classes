"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Array, Boolean, Enum, Integer, Number, Object, Reference, String
from tests.unit.helpers import make_uri


def test_basic_string_items():
    result = Array({'type': 'array', 'items': {'type': 'string'}}, uri=make_uri())
    assert isinstance(result.items, String)


def test_integer_items():
    result = Array({'type': 'array', 'items': {'type': 'integer'}}, uri=make_uri())
    assert isinstance(result.items, Integer)


def test_boolean_items():
    result = Array({'type': 'array', 'items': {'type': 'boolean'}}, uri=make_uri())
    assert isinstance(result.items, Boolean)


def test_number_items():
    result = Array({'type': 'array', 'items': {'type': 'number'}}, uri=make_uri())
    assert isinstance(result.items, Number)


def test_enum_items():
    result = Array({'type': 'array', 'items': {'enum': ['a', 'b']}}, uri=make_uri())
    assert isinstance(result.items, Enum)


def test_object_items():
    result = Array(
        {
            'type': 'array',
            'items': {'type': 'object', 'properties': {'name': {'type': 'string'}}},
        },
        uri=make_uri(),
    )
    assert isinstance(result.items, Object)


def test_reference_items():
    result = Array(
        {
            'type': 'array',
            'items': {'$ref': 'other.json#/definitions/Foo'},
        },
        uri=make_uri(),
    )
    assert isinstance(result.items, Reference)


def test_nested_array_items():
    result = Array(
        {
            'type': 'array',
            'items': {'type': 'array', 'items': {'type': 'string'}},
        },
        uri=make_uri(),
    )
    assert isinstance(result.items, Array)
    assert isinstance(result.items.items, String)


def test_default_none():
    result = Array({'type': 'array', 'items': {'type': 'string'}}, uri=make_uri())
    assert result.default is None
