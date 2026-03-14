"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Object, parse_schema
from tests.unit.helpers import make_uri


def test_returns_object():
    result = parse_schema({'type': 'object', 'properties': {}}, uri=make_uri())
    assert isinstance(result, Object)
