"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.dataclass.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'simple_all_optional.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_schema_input.py'}


def test_uses_dataclass_decorator(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert '@dataclass(kw_only=True)' in content
    assert '@validataclass' not in content


def test_class_without_mixin(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'class SimpleSchemaInput:' in content
    assert 'ValidataclassMixin' not in content


def test_optional_fields_use_none(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'test_string: str | None = None' in content
    assert 'test_integer: int | None = None' in content
    assert 'test_number: int | None = None' in content
    assert 'test_boolean: bool | None = None' in content


def test_no_validators(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'Validator' not in content
    assert 'UnsetValue' not in content
    assert 'Default(' not in content


def test_imports_dataclass(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'from dataclasses import dataclass' in content
    assert 'validataclass' not in content.split('from dataclasses')[0]
