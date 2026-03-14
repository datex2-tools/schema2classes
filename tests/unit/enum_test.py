"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Enum

from tests.unit.helpers import make_uri


def test_basic():
    result = Enum({'enum': ['a', 'b', 'c']}, uri=make_uri())
    assert result.enum == ['a', 'b', 'c']


def test_with_default():
    result = Enum({'enum': ['x', 'y'], 'default': 'x'}, uri=make_uri())
    assert result.default == 'x'


def test_preserves_order():
    result = Enum({'enum': ['z', 'a', 'm']}, uri=make_uri())
    assert result.enum == ['z', 'a', 'm']


def test_single_value():
    result = Enum({'enum': ['only']}, uri=make_uri())
    assert result.enum == ['only']
