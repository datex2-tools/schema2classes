"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'simple_all_optional.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_schema_input.py'}


def test_main_class_has_all_optional_fields(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'class SimpleSchemaInput(ValidataclassMixin):' in content
    assert 'test_string: str | UnsetValueType = StringValidator(), Default(UnsetValue)' in content
    assert 'test_integer: int | UnsetValueType = IntegerValidator(), Default(UnsetValue)' in content
    assert 'test_number: int | UnsetValueType = FloatValidator(), Default(UnsetValue)' in content
    assert 'test_boolean: bool | UnsetValueType = BooleanValidator(), Default(UnsetValue)' in content


def test_init_file_contains_header(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / '__init__.py').read_text()

    assert 'Copyright 2026 binary butterfly GmbH' in content


def test_init_file_is_minimal(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / '__init__.py').read_text().strip()
    lines = [line for line in content.splitlines() if line.strip()]

    # Init file should only contain the copyright header
    assert all('Copyright' in line or 'LICENSE' in line or line.startswith('"""') for line in lines)


def test_optional_fields_import_unset_value(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'from validataclass.helpers import' in content
    assert 'UnsetValue' in content
    assert 'UnsetValueType' in content
    assert 'from validataclass.dataclasses import' in content
    assert 'Default' in content


def test_validataclass_mixin_import(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'from validataclass.dataclasses import ValidataclassMixin' in content


def test_validataclass_decorator_import(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert '@validataclass' in content
