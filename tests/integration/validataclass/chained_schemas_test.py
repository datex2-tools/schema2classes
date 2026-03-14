"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.validataclass.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'chained_schemas' / 'main_schema.json'


def test_generates_expected_files(tmp_path: Path):
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

    assert 'class SimpleSchemaInput(ValidataclassMixin):' in content
    assert (
        'SecondObject: SecondObjectInput | UnsetValueType = DataclassValidator(SecondObjectInput), Default(UnsetValue)'
        in content
    )


def test_second_class_references_third(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'second_object_input.py').read_text()

    assert 'class SecondObjectInput(ValidataclassMixin):' in content
    assert (
        'ThirdObject: ThirdObjectInput | UnsetValueType = DataclassValidator(ThirdObjectInput), Default(UnsetValue)'
        in content
    )
    assert 'second_string: str | UnsetValueType = StringValidator(), Default(UnsetValue)' in content


def test_third_class(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'third_object_input.py').read_text()

    assert 'class ThirdObjectInput(ValidataclassMixin):' in content
    assert 'third_string: str | UnsetValueType = StringValidator(), Default(UnsetValue)' in content
