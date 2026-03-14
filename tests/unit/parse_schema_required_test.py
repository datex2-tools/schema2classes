"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import parse_schema

from tests.unit.helpers import make_uri


def test_required_passed_through():
    result = parse_schema({'type': 'string'}, uri=make_uri(), required=True)
    assert result.required is True


def test_default_not_required():
    result = parse_schema({'type': 'string'}, uri=make_uri())
    assert result.required is False
