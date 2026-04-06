"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import String
from tests.unit.helpers import make_uri


def test_basic():
    result = String({'type': 'string'}, uri=make_uri())
    assert result.pattern is None
    assert result.default is None


def test_with_pattern():
    result = String({'type': 'string', 'pattern': r'^[a-z]+$'}, uri=make_uri())
    assert result.pattern == r'^[a-z]+$'


def test_with_default():
    result = String({'type': 'string', 'default': 'hello'}, uri=make_uri())
    assert result.default == 'hello'


def test_with_title_and_description():
    result = String({'type': 'string', 'title': 'Name', 'description': 'The name'}, uri=make_uri())
    assert result.title == 'Name'
    assert result.description == 'The name'
