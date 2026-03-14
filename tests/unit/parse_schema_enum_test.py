"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Enum, parse_schema

from tests.unit.helpers import make_uri


def test_returns_enum():
    result = parse_schema({'enum': ['a', 'b']}, uri=make_uri())
    assert isinstance(result, Enum)


def test_enum_takes_priority_over_type():
    result = parse_schema({'type': 'string', 'enum': ['a', 'b']}, uri=make_uri())
    assert isinstance(result, Enum)
