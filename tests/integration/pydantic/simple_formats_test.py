"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, time
from pathlib import Path

from pydantic import AnyUrl

from tests.integration.pydantic.helpers import INPUT_DIR, generated_files, import_module, run_generate

SCHEMA_PATH = INPUT_DIR / 'simple_formats.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_formats_input.py'}


def test_required_datetime_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_required_datetime: datetime' in content
    assert 'test_required_datetime: datetime |' not in content


def test_optional_datetime_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_datetime: datetime | None = None' in content


def test_optional_time_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_time: time | None = None' in content


def test_optional_email_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_email: EmailStr | None = None' in content


def test_optional_uri_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_uri: AnyUrl | None = None' in content


def test_imports(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'from datetime import' in content
    assert 'EmailStr' in content
    assert 'AnyUrl' in content


def test_validate_all_fields(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    mod = import_module(tmp_path, 'simple_formats_input')

    result = mod.SimpleFormatsInput.model_validate({
        'test_required_datetime': '2025-01-01T00:00:00Z',
        'test_datetime': '2025-06-15T12:30:00Z',
        'test_time': '14:30:00',
        'test_email': 'user@example.com',
        'test_uri': 'https://example.com',
    })

    assert result.test_required_datetime == datetime(2025, 1, 1, tzinfo=result.test_required_datetime.tzinfo)
    assert result.test_datetime == datetime(2025, 6, 15, 12, 30, tzinfo=result.test_datetime.tzinfo)
    assert result.test_time == time(14, 30)
    assert result.test_email == 'user@example.com'
    assert isinstance(result.test_uri, AnyUrl)


def test_validate_required_only(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    mod = import_module(tmp_path, 'simple_formats_input')

    result = mod.SimpleFormatsInput.model_validate({
        'test_required_datetime': '2025-01-01T00:00:00Z',
    })

    assert isinstance(result.test_required_datetime, datetime)
    assert result.test_datetime is None
    assert result.test_time is None
    assert result.test_email is None
    assert result.test_uri is None
