"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.pydantic.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'simple_all_optional.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_schema_input.py'}


def test_inherits_base_model(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'class SimpleSchemaInput(BaseModel):' in content
    assert 'from pydantic import BaseModel' in content


def test_optional_fields_use_none(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'test_string: str | None = None' in content
    assert 'test_integer: int | None = None' in content
    assert 'test_number: float | None = None' in content
    assert 'test_boolean: bool | None = None' in content


def test_no_validataclass_artifacts(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'Validator' not in content
    assert 'UnsetValue' not in content
    assert 'validataclass' not in content
    assert '@dataclass' not in content
