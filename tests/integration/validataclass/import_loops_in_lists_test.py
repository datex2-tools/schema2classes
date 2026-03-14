"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.validataclass.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'import_loops_in_lists' / 'main_schema.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {
        '__init__.py',
        'simple_schema_input.py',
        'second_object_input.py',
        'third_object_input.py',
    }


def test_second_class_has_list_of_third(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'second_object_input.py').read_text()

    assert 'class SecondObjectInput' in content
    assert 'ThirdObjectInput' in content
    assert 'ListValidator' in content
    assert 'second_string' in content


def test_looping_list_reference_removed_from_third(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'third_object_input.py').read_text()

    assert 'class ThirdObjectInput' in content
    assert 'third_string' in content
    # The back-reference list to SecondObjectInput should be removed
    assert 'SecondObject' not in content
    assert 'second_object_input' not in content


def test_no_circular_import(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    second_content = (tmp_path / 'second_object_input.py').read_text()
    third_content = (tmp_path / 'third_object_input.py').read_text()

    assert 'third_object_input' in second_content
    assert 'second_object_input' not in third_content
