"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import Uri, parse_schema
from tests.unit.helpers import make_uri


def test_returns_uri():
    result = parse_schema({'type': 'string', 'format': 'uri'}, uri=make_uri())
    assert isinstance(result, Uri)


def test_uri_with_title():
    result = parse_schema({'type': 'string', 'format': 'uri', 'title': 'Homepage'}, uri=make_uri())
    assert isinstance(result, Uri)
    assert result.title == 'Homepage'


def test_uri_with_default():
    result = parse_schema({'type': 'string', 'format': 'uri', 'default': 'https://example.com'}, uri=make_uri())
    assert isinstance(result, Uri)
    assert result.default == 'https://example.com'
