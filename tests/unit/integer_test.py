"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2classes.schema.models import Integer
from tests.unit.helpers import make_uri


def test_basic():
    result = Integer({'type': 'integer'}, uri=make_uri())
    assert result.minimum is None
    assert result.maximum is None
    assert result.exclusiveMinimum is None
    assert result.exclusiveMaximum is None
    assert result.default is None


def test_with_minimum():
    result = Integer({'type': 'integer', 'minimum': 0}, uri=make_uri())
    assert result.minimum == 0


def test_with_maximum():
    result = Integer({'type': 'integer', 'maximum': 100}, uri=make_uri())
    assert result.maximum == 100


def test_with_exclusive_minimum():
    result = Integer({'type': 'integer', 'exclusiveMinimum': 5}, uri=make_uri())
    assert result.exclusiveMinimum == 5


def test_with_exclusive_maximum():
    result = Integer({'type': 'integer', 'exclusiveMaximum': 50}, uri=make_uri())
    assert result.exclusiveMaximum == 50


def test_with_all_bounds():
    result = Integer(
        {
            'type': 'integer',
            'minimum': 1,
            'maximum': 99,
            'exclusiveMinimum': 0,
            'exclusiveMaximum': 100,
        },
        uri=make_uri(),
    )
    assert result.minimum == 1
    assert result.maximum == 99
    assert result.exclusiveMinimum == 0
    assert result.exclusiveMaximum == 100


def test_float_minimum_converted_to_int():
    result = Integer({'type': 'integer', 'minimum': 0.0}, uri=make_uri())
    assert result.minimum == 0
    assert isinstance(result.minimum, int)


def test_float_maximum_converted_to_int():
    result = Integer({'type': 'integer', 'maximum': 100.0}, uri=make_uri())
    assert result.maximum == 100
    assert isinstance(result.maximum, int)


def test_float_exclusive_minimum_converted_to_int():
    result = Integer({'type': 'integer', 'exclusiveMinimum': 5.0}, uri=make_uri())
    assert result.exclusiveMinimum == 5
    assert isinstance(result.exclusiveMinimum, int)


def test_float_exclusive_maximum_converted_to_int():
    result = Integer({'type': 'integer', 'exclusiveMaximum': 50.0}, uri=make_uri())
    assert result.exclusiveMaximum == 50
    assert isinstance(result.exclusiveMaximum, int)


def test_float_default_converted_to_int():
    result = Integer({'type': 'integer', 'default': 0.0}, uri=make_uri())
    assert result.default == 0
    assert isinstance(result.default, int)


def test_int_default_stays_int():
    result = Integer({'type': 'integer', 'default': 42}, uri=make_uri())
    assert result.default == 42
    assert isinstance(result.default, int)
