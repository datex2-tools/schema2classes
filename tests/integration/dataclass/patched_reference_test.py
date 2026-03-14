"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.dataclass.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'patched_reference' / 'main_schema.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_schema_input.py'}


def test_patched_integer_as_plain_type(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'class SimpleSchemaInput:' in content
    assert 'energy: int | None = None' in content
    assert 'IntegerValidator' not in content


def test_no_extra_object_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    py_files = {f.name for f in tmp_path.glob('*.py')} - {'__init__.py'}
    assert py_files == {'simple_schema_input.py'}
