"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import Email, parse_schema
from tests.unit.helpers import make_uri


def test_returns_email():
    result = parse_schema({'type': 'string', 'format': 'email'}, uri=make_uri())
    assert isinstance(result, Email)


def test_email_with_title():
    result = parse_schema({'type': 'string', 'format': 'email', 'title': 'Contact'}, uri=make_uri())
    assert isinstance(result, Email)
    assert result.title == 'Contact'


def test_email_with_default():
    result = parse_schema({'type': 'string', 'format': 'email', 'default': 'test@example.com'}, uri=make_uri())
    assert isinstance(result, Email)
    assert result.default == 'test@example.com'
