"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import Email
from tests.unit.helpers import make_uri


def test_basic():
    result = Email({'type': 'string', 'format': 'email'}, uri=make_uri())
    assert result.default is None


def test_with_default():
    result = Email({'type': 'string', 'format': 'email', 'default': 'test@example.com'}, uri=make_uri())
    assert result.default == 'test@example.com'


def test_with_title_and_description():
    result = Email(
        {'type': 'string', 'format': 'email', 'title': 'Contact', 'description': 'Email address'},
        uri=make_uri(),
    )
    assert result.title == 'Contact'
    assert result.description == 'Email address'
