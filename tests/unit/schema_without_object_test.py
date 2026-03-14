"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Schema
from tests.unit.helpers import make_uri


def test_no_contained_object():
    schema = Schema(
        {
            'definitions': {'Foo': {'type': 'string'}},
        },
        uri=make_uri(),
    )
    assert schema.contained_object is None


def test_properties_empty():
    schema = Schema(
        {
            'definitions': {'Foo': {'type': 'string'}},
        },
        uri=make_uri(),
    )
    assert schema.properties == []
