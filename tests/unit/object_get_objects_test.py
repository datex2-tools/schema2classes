"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import Object
from tests.unit.helpers import make_uri


def test_returns_self():
    obj = Object({'type': 'object', 'properties': {}}, uri=make_uri())
    assert obj.get_objects() == [obj]


def test_includes_nested_object():
    obj = Object(
        {
            'type': 'object',
            'properties': {
                'inner': {'type': 'object', 'properties': {'x': {'type': 'string'}}},
            },
        },
        uri=make_uri(),
    )
    objects = obj.get_objects()
    assert len(objects) == 2
    assert objects[0] is obj
    assert isinstance(objects[1], Object)


def test_includes_deeply_nested_objects():
    obj = Object(
        {
            'type': 'object',
            'properties': {
                'level1': {
                    'type': 'object',
                    'properties': {
                        'level2': {
                            'type': 'object',
                            'properties': {'val': {'type': 'string'}},
                        },
                    },
                },
            },
        },
        uri=make_uri(),
    )
    objects = obj.get_objects()
    assert len(objects) == 3


def test_includes_object_in_array():
    obj = Object(
        {
            'type': 'object',
            'properties': {
                'items': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {'name': {'type': 'string'}},
                    },
                },
            },
        },
        uri=make_uri(),
    )
    objects = obj.get_objects()
    assert len(objects) == 2


def test_skips_non_object_properties():
    obj = Object(
        {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'count': {'type': 'integer'},
            },
        },
        uri=make_uri(),
    )
    objects = obj.get_objects()
    assert len(objects) == 1
