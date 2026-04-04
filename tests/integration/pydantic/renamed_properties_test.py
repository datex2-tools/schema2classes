"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from schema2validataclass import App
from schema2validataclass.common.uri import URI
from schema2validataclass.config import Config, OutputFormat
from tests.integration.pydantic.helpers import INPUT_DIR, generated_files

SCHEMA_PATH = INPUT_DIR / 'renamed_properties.json'


def run_generate(schema_path: Path, output_path: Path, **config_kwargs):
    config = Config(output_format=OutputFormat.PYDANTIC, **config_kwargs)
    app = App(config=config)
    app.generate(URI(file_path=schema_path), output_path)


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'renamed_properties_schema_input.py'}


def test_from_field_renamed_to_from_(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert 'from_: str' in content
    assert 'from: str' not in content


def test_normal_fields_unchanged(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert 'to: str' in content
    assert 'normal_field: int' in content


def test_model_validator_generated(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert "@model_validator(mode='before')" in content
    assert '_rename_properties' in content
    assert "'from': 'from_'" in content


def test_model_validator_imports(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert 'from pydantic import' in content
    assert 'model_validator' in content
    assert 'from typing import Any' in content


def test_no_model_validator_without_renamed_properties(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path, renamed_properties=[])
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert 'model_validator' not in content
    assert '_rename_properties' not in content
    assert 'from: str' in content
