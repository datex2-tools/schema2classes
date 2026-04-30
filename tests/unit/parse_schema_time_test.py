"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import Time, parse_schema
from tests.unit.helpers import make_uri


def test_returns_time():
    result = parse_schema({'type': 'string', 'format': 'time'}, uri=make_uri())
    assert isinstance(result, Time)


def test_time_with_title():
    result = parse_schema({'type': 'string', 'format': 'time', 'title': 'Start Time'}, uri=make_uri())
    assert isinstance(result, Time)
    assert result.title == 'Start Time'


def test_time_with_default():
    result = parse_schema({'type': 'string', 'format': 'time', 'default': '12:00:00'}, uri=make_uri())
    assert isinstance(result, Time)
    assert result.default == '12:00:00'
