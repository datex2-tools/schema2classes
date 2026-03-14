"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Reference, parse_schema
from tests.unit.helpers import make_uri


def test_returns_reference():
    result = parse_schema({'$ref': 'other.json#/definitions/Foo'}, uri=make_uri())
    assert isinstance(result, Reference)


def test_ref_takes_priority_over_type():
    result = parse_schema({'type': 'string', '$ref': 'other.json#/definitions/Foo'}, uri=make_uri())
    assert isinstance(result, Reference)
