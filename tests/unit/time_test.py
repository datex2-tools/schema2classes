"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import Time
from tests.unit.helpers import make_uri


def test_basic():
    result = Time({'type': 'string', 'format': 'time'}, uri=make_uri())
    assert result.default is None


def test_with_default():
    result = Time({'type': 'string', 'format': 'time', 'default': '12:00:00'}, uri=make_uri())
    assert result.default == '12:00:00'


def test_with_title_and_description():
    result = Time(
        {'type': 'string', 'format': 'time', 'title': 'Start Time', 'description': 'The start time'},
        uri=make_uri(),
    )
    assert result.title == 'Start Time'
    assert result.description == 'The start time'
