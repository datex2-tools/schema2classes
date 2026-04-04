"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from schema2validataclass import App
from schema2validataclass.common.uri import URI
from schema2validataclass.config import Config, OutputFormat
from tests.integration.dataclass.helpers import INPUT_DIR, generated_files

SCHEMA_PATH = INPUT_DIR / 'renamed_properties.json'


def run_generate(schema_path: Path, output_path: Path, **config_kwargs):
    config = Config(output_format=OutputFormat.DATACLASS, **config_kwargs)
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


def test_no_pre_validate_in_dataclass(tmp_path: Path):
    """Dataclass output has no validation mechanism, so no __pre_validate__ is generated."""
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert '__pre_validate__' not in content


def test_no_rename_with_empty_renamed_properties(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path, renamed_properties=[])
    content = (tmp_path / 'renamed_properties_schema_input.py').read_text()

    assert 'from: str' in content
