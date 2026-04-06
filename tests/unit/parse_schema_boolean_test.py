"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import Boolean, parse_schema
from tests.unit.helpers import make_uri


def test_returns_boolean():
    result = parse_schema({'type': 'boolean'}, uri=make_uri())
    assert isinstance(result, Boolean)


def test_boolean_default_false():
    result = parse_schema({'type': 'boolean'}, uri=make_uri())
    assert result.required is False
