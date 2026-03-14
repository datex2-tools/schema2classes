"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Boolean

from tests.unit.helpers import make_uri


def test_basic():
    result = Boolean({}, uri=make_uri())
    assert isinstance(result, Boolean)
    assert result.default is None


def test_with_default_true():
    result = Boolean({'default': True}, uri=make_uri())
    assert result.default is True


def test_with_default_false():
    result = Boolean({'default': False}, uri=make_uri())
    assert result.default is False
