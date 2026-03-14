"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.validataclass.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'list_reference' / 'main_schema.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_schema_input.py', 'second_object_input.py'}


def test_list_field_with_reference(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'class SimpleSchemaInput(ValidataclassMixin):' in content
    assert (
        'second_objects: list[SecondObjectInput] | UnsetValueType = ListValidator(DataclassValidator(SecondObjectInput)), Default(UnsetValue)'
        in content
    )


def test_referenced_object(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'second_object_input.py').read_text()

    assert 'class SecondObjectInput(ValidataclassMixin):' in content
    assert 'second_string: str | UnsetValueType = StringValidator(), Default(UnsetValue)' in content


def test_list_validator_import(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_schema_input.py').read_text()

    assert 'ListValidator' in content
