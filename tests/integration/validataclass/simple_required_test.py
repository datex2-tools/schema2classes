"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.validataclass.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'simple_required.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_schema_input.py', 'test_enum.py'}


def test_required_field_has_no_default(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'test_required_string: str = StringValidator()' in content


def test_optional_fields_have_defaults(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'test_string: str | UnsetValueType = StringValidator(), Default(UnsetValue)' in content
    assert 'test_integer: int | UnsetValueType = IntegerValidator(), Default(UnsetValue)' in content


def test_enum_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'test_enum: TestEnum | UnsetValueType = EnumValidator(TestEnum), Default(UnsetValue)' in content


def test_enum_file_generated(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'test_enum.py').read_text()

    assert 'class TestEnum(Enum):' in content
    assert "FOO = 'foo'" in content
    assert "BAR = 'bar'" in content


def test_required_field_imports(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'from validataclass.dataclasses import' in content
    assert 'validataclass' in content
