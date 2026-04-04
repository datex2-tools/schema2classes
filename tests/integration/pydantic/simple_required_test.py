"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.pydantic.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'simple_required.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_schema_input.py', 'test_enum.py'}


def test_required_field_is_plain_type(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'test_required_string: str' in content
    assert 'test_required_string: str |' not in content


def test_optional_fields_use_none(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'test_string: str | None = None' in content
    assert 'test_integer: int | None = None' in content


def test_enum_field_optional(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'test_enum: TestEnum | None = None' in content


def test_enum_file_generated(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'test_enum.py').read_text()

    assert 'class TestEnum(Enum):' in content
    assert 'FOO = "foo"' in content
    assert 'BAR = "bar"' in content
