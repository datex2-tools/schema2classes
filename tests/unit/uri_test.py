"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import Uri
from tests.unit.helpers import make_uri


def test_basic():
    result = Uri({'type': 'string', 'format': 'uri'}, uri=make_uri())
    assert result.default is None


def test_with_default():
    result = Uri({'type': 'string', 'format': 'uri', 'default': 'https://example.com'}, uri=make_uri())
    assert result.default == 'https://example.com'


def test_with_title_and_description():
    result = Uri(
        {'type': 'string', 'format': 'uri', 'title': 'Homepage', 'description': 'Website URL'},
        uri=make_uri(),
    )
    assert result.title == 'Homepage'
    assert result.description == 'Website URL'
