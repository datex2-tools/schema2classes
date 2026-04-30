"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import DateTime
from tests.unit.helpers import make_uri


def test_basic():
    result = DateTime({'type': 'string', 'format': 'date-time'}, uri=make_uri())
    assert result.default is None


def test_with_default():
    result = DateTime({'type': 'string', 'format': 'date-time', 'default': '2025-01-01T00:00:00Z'}, uri=make_uri())
    assert result.default == '2025-01-01T00:00:00Z'


def test_with_title_and_description():
    result = DateTime(
        {'type': 'string', 'format': 'date-time', 'title': 'Created At', 'description': 'Creation timestamp'},
        uri=make_uri(),
    )
    assert result.title == 'Created At'
    assert result.description == 'Creation timestamp'
