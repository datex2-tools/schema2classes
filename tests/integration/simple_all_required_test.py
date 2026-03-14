"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'simple_all_required.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_schema_input.py'}


def test_main_class_fields(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'class SimpleSchemaInput(ValidataclassMixin):' in content
    assert 'test_string: str | UnsetValueType = StringValidator(), Default(UnsetValue)' in content
    assert 'test_integer: int | UnsetValueType = IntegerValidator(), Default(UnsetValue)' in content
    assert 'test_number: int | UnsetValueType = FloatValidator(), Default(UnsetValue)' in content
    assert 'test_boolean: bool | UnsetValueType = BooleanValidator(), Default(UnsetValue)' in content
