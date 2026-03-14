"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from tests.integration.validataclass.helpers import INPUT_DIR, generated_files, run_generate

SCHEMA_PATH = INPUT_DIR / 'main_without_title.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'main_without_title_input.py'}


def test_class_name_derived_from_filename(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'main_without_title_input.py').read_text()

    assert 'class MainWithoutTitleInput(ValidataclassMixin):' in content


def test_fields_present(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'main_without_title_input.py').read_text()

    assert 'test_string: str | UnsetValueType = StringValidator(), Default(UnsetValue)' in content
    assert 'test_integer: int | UnsetValueType = IntegerValidator(), Default(UnsetValue)' in content
    assert 'test_number: int | UnsetValueType = FloatValidator(), Default(UnsetValue)' in content
    assert 'test_boolean: bool | UnsetValueType = BooleanValidator(), Default(UnsetValue)' in content
