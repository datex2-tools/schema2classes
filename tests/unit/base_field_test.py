"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import BaseField
from tests.unit.helpers import make_uri


def test_uri_stored():
    uri = make_uri()
    field = BaseField({'type': 'string'}, uri=uri)
    assert field.uri == uri


def test_title():
    field = BaseField({'title': 'My Title'}, uri=make_uri())
    assert field.title == 'My Title'


def test_description():
    field = BaseField({'description': 'Some description'}, uri=make_uri())
    assert field.description == 'Some description'


def test_default():
    field = BaseField({'default': 'hello'}, uri=make_uri())
    assert field.default == 'hello'


def test_no_optional_fields():
    field = BaseField({}, uri=make_uri())
    assert field.title is None
    assert field.description is None
    assert field.default is None
    assert field.required is False


def test_required_kwarg():
    field = BaseField({}, uri=make_uri(), required=True)
    assert field.required is True
