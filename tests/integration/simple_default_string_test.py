"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'simple_default_string.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_schema_input.py', 'test_enum.py'}


def test_all_fields_optional_without_required_array(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'test_required_string: str | UnsetValueType = StringValidator(), Default(UnsetValue)' in content
    assert 'test_enum: TestEnum | UnsetValueType = EnumValidator(TestEnum), Default(UnsetValue)' in content
