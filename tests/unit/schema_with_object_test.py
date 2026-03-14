"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Object, Schema, String
from tests.unit.helpers import make_uri


def test_contained_object():
    schema = Schema(
        {
            'type': 'object',
            'title': 'Root',
            'properties': {'name': {'type': 'string'}},
        },
        uri=make_uri(),
    )
    assert schema.contained_object is not None
    assert isinstance(schema.contained_object, Object)


def test_properties_delegated():
    schema = Schema(
        {
            'type': 'object',
            'properties': {'name': {'type': 'string'}},
        },
        uri=make_uri(),
    )
    assert len(schema.properties) == 1
    assert isinstance(schema.properties[0], String)
