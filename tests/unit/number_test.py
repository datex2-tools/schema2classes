"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Number
from tests.unit.helpers import make_uri


def test_basic():
    result = Number({'type': 'number'}, uri=make_uri())
    assert result.minimum is None
    assert result.maximum is None
    assert result.exclusiveMinimum is None
    assert result.exclusiveMaximum is None
    assert result.default is None


def test_with_minimum():
    result = Number({'type': 'number', 'minimum': 0.5}, uri=make_uri())
    assert result.minimum == 0.5


def test_with_maximum():
    result = Number({'type': 'number', 'maximum': 99.9}, uri=make_uri())
    assert result.maximum == 99.9


def test_with_exclusive_minimum():
    result = Number({'type': 'number', 'exclusiveMinimum': 1.1}, uri=make_uri())
    assert result.exclusiveMinimum == 1.1


def test_with_exclusive_maximum():
    result = Number({'type': 'number', 'exclusiveMaximum': 50.5}, uri=make_uri())
    assert result.exclusiveMaximum == 50.5


def test_with_int_values():
    result = Number({'type': 'number', 'minimum': 0, 'maximum': 100}, uri=make_uri())
    assert result.minimum == 0
    assert result.maximum == 100


def test_with_default():
    result = Number({'type': 'number', 'default': 3.14}, uri=make_uri())
    assert result.default == 3.14
