"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.dataclass.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'chained_schemas_unused' / 'main_schema.json'


def test_unused_object_not_generated(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {
        '__init__.py',
        'simple_schema_input.py',
        'second_object_input.py',
        'third_object_input.py',
    }


def test_main_class_references_second(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'class SimpleSchemaInput:' in content


def test_third_class_has_no_unused_object(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'third_object_input.py').read_text()

    assert 'class ThirdObjectInput:' in content
    assert 'third_string' in content
    assert 'UnusedObject' not in content
