"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from schema2validataclass import App
from schema2validataclass.common.uri import URI
from schema2validataclass.config import Config, OutputFormat
from tests.integration.pydantic.helpers import INPUT_DIR, generated_files

SCHEMA_PATH = INPUT_DIR / 'chained_schemas_list_ignore' / 'main_schema.json'


def run_generate(schema_path: Path, output_path: Path, **config_kwargs):
    config = Config(output_format=OutputFormat.PYDANTIC, **config_kwargs)
    app = App(config=config)
    app.generate(URI(file_path=schema_path), output_path)


def test_without_ignoring_generates_all_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {
        '__init__.py',
        'simple_schema_input.py',
        'second_object_input.py',
        'third_object_input.py',
        'ignored_object_input.py',
    }


def test_ignored_reference_not_loaded(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path, ignore_references=['third_schema.json#/definitions/IgnoredObject'])
    assert generated_files(tmp_path) == {
        '__init__.py',
        'simple_schema_input.py',
        'second_object_input.py',
        'third_object_input.py',
    }


def test_ignored_reference_property_removed_from_parent(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path, ignore_references=['third_schema.json#/definitions/IgnoredObject'])
    content = (tmp_path / 'second_object_input.py').read_text()

    assert 'IgnoredObject' not in content
    assert 'ThirdObject' in content


def test_third_object_still_works(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path, ignore_references=['third_schema.json#/definitions/IgnoredObject'])
    content = (tmp_path / 'third_object_input.py').read_text()

    assert 'class ThirdObjectInput(BaseModel):' in content
    assert 'third_string' in content
