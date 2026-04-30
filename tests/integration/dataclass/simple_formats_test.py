"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, time
from pathlib import Path

from tests.integration.dataclass.helpers import INPUT_DIR, generated_files, import_module, run_generate

SCHEMA_PATH = INPUT_DIR / 'simple_formats.json'


def test_generates_expected_files(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    assert generated_files(tmp_path) == {'__init__.py', 'simple_formats_input.py'}


def test_required_datetime_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_required_datetime: datetime\n' in content or 'test_required_datetime: datetime' in content
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

    assert 'test_email: str | None = None' in content


def test_optional_uri_field(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'test_uri: str | None = None' in content


def test_datetime_imports(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    content = (tmp_path / 'simple_formats_input.py').read_text()

    assert 'from datetime import' in content


def test_import_and_instantiate_all_fields(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    mod = import_module(tmp_path, 'simple_formats_input')

    obj = mod.SimpleFormatsInput(
        test_required_datetime=datetime(2025, 1, 1),
        test_datetime=datetime(2025, 6, 15, 12, 30),
        test_time=time(14, 30),
        test_email='user@example.com',
        test_uri='https://example.com',
    )

    assert obj.test_required_datetime == datetime(2025, 1, 1)
    assert obj.test_datetime == datetime(2025, 6, 15, 12, 30)
    assert obj.test_time == time(14, 30)
    assert obj.test_email == 'user@example.com'
    assert obj.test_uri == 'https://example.com'


def test_import_and_instantiate_required_only(tmp_path: Path):
    run_generate(SCHEMA_PATH, tmp_path)
    mod = import_module(tmp_path, 'simple_formats_input')

    obj = mod.SimpleFormatsInput(test_required_datetime=datetime(2025, 1, 1))

    assert obj.test_required_datetime == datetime(2025, 1, 1)
    assert obj.test_datetime is None
    assert obj.test_time is None
    assert obj.test_email is None
    assert obj.test_uri is None
