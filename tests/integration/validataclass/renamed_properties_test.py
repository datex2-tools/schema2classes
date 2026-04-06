"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from schema2classes import App
from schema2classes.common.uri import URI
from schema2classes.config import Config
from tests.integration.validataclass.helpers import INPUT_DIR, generated_files

SCHEMA_PATH = INPUT_DIR / 'renamed_properties.json'


def run_generate(schema_path: Path, output_path: Path, **config_kwargs):
    config = Config(**config_kwargs)
    app = App(config=config)
    app.generate(URI(file_path=schema_path), output_path)


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'renamed_properties_schema_input.py'}


def test_from_field_renamed_to_from_(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert 'from_: str = StringValidator()' in content
    assert 'from: str' not in content


def test_normal_fields_unchanged(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert 'to: str = StringValidator()' in content
    assert 'normal_field: int' in content


def test_pre_validate_generated(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert '@staticmethod' in content
    assert 'def __pre_validate__(input_data: dict) -> dict:' in content
    assert "'from': 'from_'" in content


def test_pre_validate_mapping_logic(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert 'for from_key, to_key in field_mapping.items():' in content
    assert 'if from_key in input_data:' in content
    assert 'input_data[to_key] = input_data.pop(from_key)' in content
    assert 'return input_data' in content


def test_no_pre_validate_without_renamed_properties(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path, renamed_properties=[])
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert '__pre_validate__' not in content
    assert 'from: str = StringValidator()' in content


def test_custom_renamed_properties(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path, renamed_properties=['to'])
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert 'to_: str = StringValidator()' in content
    assert 'from: str = StringValidator()' in content
    assert "'to': 'to_'" in content
