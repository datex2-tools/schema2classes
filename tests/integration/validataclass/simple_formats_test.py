"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, time
from pathlib import Path

from validataclass.helpers import UnsetValue
from validataclass.validators import DataclassValidator

from tests.integration.validataclass.helpers import INPUT_DIR, generated_files, import_module, run_generate

SCHEMA_PATH = INPUT_DIR / 'simple_formats.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_formats_input.py'}


def test_required_datetime_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_required_datetime: datetime = DateTimeValidator()' in content


def test_optional_datetime_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_datetime: datetime | UnsetValueType = DateTimeValidator(), Default(UnsetValue)' in content


def test_optional_time_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_time: time | UnsetValueType = TimeValidator(), Default(UnsetValue)' in content


def test_optional_email_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_email: str | UnsetValueType = EmailValidator(), Default(UnsetValue)' in content


def test_optional_uri_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_uri: str | UnsetValueType = UrlValidator(), Default(UnsetValue)' in content


def test_imports(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'DateTimeValidator' in content
    assert 'TimeValidator' in content
    assert 'EmailValidator' in content
    assert 'UrlValidator' in content
    assert 'from datetime import' in content


def test_validate_all_fields(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    mod = import_module(tmp_path, 'simple_formats_input')

    validator = DataclassValidator(mod.SimpleFormatsInput)
    result = validator.validate({
        'test_required_datetime': '2025-01-01T00:00:00',
        'test_datetime': '2025-06-15T12:30:00',
        'test_time': '14:30:00',
        'test_email': 'user@example.com',
        'test_uri': 'https://example.com',
    })

    assert result.test_required_datetime == datetime(2025, 1, 1)
    assert result.test_datetime == datetime(2025, 6, 15, 12, 30)
    assert result.test_time == time(14, 30)
    assert result.test_email == 'user@example.com'
    assert result.test_uri == 'https://example.com'


def test_validate_required_only(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    mod = import_module(tmp_path, 'simple_formats_input')

    validator = DataclassValidator(mod.SimpleFormatsInput)
    result = validator.validate({
        'test_required_datetime': '2025-01-01T00:00:00',
    })

    assert result.test_required_datetime == datetime(2025, 1, 1)
    assert result.test_datetime is UnsetValue
    assert result.test_time is UnsetValue
    assert result.test_email is UnsetValue
    assert result.test_uri is UnsetValue
