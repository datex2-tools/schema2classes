"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from schema2validataclass.schema.models import Reference
from tests.unit.helpers import make_uri


def test_local_file_reference():
    uri = make_uri()
    result = Reference({'$ref': 'other.json#/definitions/Foo'}, uri=uri)
    assert result.to.json_path == '/definitions/Foo'
    assert result.to.file_path == uri.file_path.parent / 'other.json'


def test_http_reference():
    uri = make_uri()
    result = Reference({'$ref': 'https://example.com/schema.json#/definitions/Bar'}, uri=uri)
    assert result.to.json_path == '/definitions/Bar'
    assert result.to.url == 'https://example.com/schema.json'


def test_reference_without_fragment():
    uri = make_uri()
    result = Reference({'$ref': 'other.json'}, uri=uri)
    assert result.to.json_path == '/'


def test_sibling_min_items():
    result = Reference({'$ref': 'o.json', 'minItems': 1}, uri=make_uri())
    assert result.minItems == 1


def test_sibling_max_items():
    result = Reference({'$ref': 'o.json', 'maxItems': 10}, uri=make_uri())
    assert result.maxItems == 10


def test_sibling_minimum():
    result = Reference({'$ref': 'o.json', 'minimum': 0}, uri=make_uri())
    assert result.minimum == 0


def test_sibling_maximum():
    result = Reference({'$ref': 'o.json', 'maximum': 100}, uri=make_uri())
    assert result.maximum == 100


def test_sibling_exclusive_minimum():
    result = Reference({'$ref': 'o.json', 'exclusiveMinimum': 5}, uri=make_uri())
    assert result.exclusiveMinimum == 5


def test_sibling_exclusive_maximum():
    result = Reference({'$ref': 'o.json', 'exclusiveMaximum': 50}, uri=make_uri())
    assert result.exclusiveMaximum == 50


def test_sibling_min_length():
    result = Reference({'$ref': 'o.json', 'minLength': 1}, uri=make_uri())
    assert result.minLength == 1


def test_sibling_max_length():
    result = Reference({'$ref': 'o.json', 'maxLength': 255}, uri=make_uri())
    assert result.maxLength == 255


def test_sibling_pattern():
    result = Reference({'$ref': 'o.json', 'pattern': r'^\d+$'}, uri=make_uri())
    assert result.pattern == r'^\d+$'


def test_sibling_enum():
    result = Reference({'$ref': 'o.json', 'enum': ['a', 'b']}, uri=make_uri())
    assert result.enum == ['a', 'b']


def test_no_sibling_properties():
    result = Reference({'$ref': 'o.json'}, uri=make_uri())
    assert result.minItems is None
    assert result.maxItems is None
    assert result.minimum is None
    assert result.maximum is None
    assert result.exclusiveMinimum is None
    assert result.exclusiveMaximum is None
    assert result.minLength is None
    assert result.maxLength is None
    assert result.pattern is None
    assert result.enum is None


def test_title_from_reference():
    result = Reference({'$ref': 'o.json', 'title': 'Overridden Title'}, uri=make_uri())
    assert result.title == 'Overridden Title'


def test_description_from_reference():
    result = Reference({'$ref': 'o.json', 'description': 'Overridden desc'}, uri=make_uri())
    assert result.description == 'Overridden desc'


def test_required_from_reference():
    result = Reference({'$ref': 'o.json'}, uri=make_uri(), required=True)
    assert result.required is True
