"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import DateTime, parse_schema
from tests.unit.helpers import make_uri


def test_returns_datetime():
    result = parse_schema({'type': 'string', 'format': 'date-time'}, uri=make_uri())
    assert isinstance(result, DateTime)


def test_datetime_with_title():
    result = parse_schema({'type': 'string', 'format': 'date-time', 'title': 'Created At'}, uri=make_uri())
    assert isinstance(result, DateTime)
    assert result.title == 'Created At'


def test_datetime_with_default():
    result = parse_schema({'type': 'string', 'format': 'date-time', 'default': '2025-01-01T00:00:00Z'}, uri=make_uri())
    assert isinstance(result, DateTime)
    assert result.default == '2025-01-01T00:00:00Z'
