"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import String, parse_schema
from tests.unit.helpers import make_uri


def test_returns_string():
    result = parse_schema({'type': 'string'}, uri=make_uri())
    assert isinstance(result, String)


def test_string_with_pattern():
    result = parse_schema({'type': 'string', 'pattern': r'^\d+$'}, uri=make_uri())
    assert isinstance(result, String)
    assert result.pattern == r'^\d+$'
