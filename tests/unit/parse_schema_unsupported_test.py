"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from schema2classes.schema.models import parse_schema
from tests.unit.helpers import make_uri


def test_raises_on_unsupported_type():
    with pytest.raises(ValueError, match='Unsupported type'):
        parse_schema({'type': 'null'}, uri=make_uri())


def test_raises_on_missing_type():
    with pytest.raises(ValueError, match='Unsupported type'):
        parse_schema({}, uri=make_uri())
