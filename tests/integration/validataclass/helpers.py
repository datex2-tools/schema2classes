"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from schema2validataclass import App
from schema2validataclass.common.uri import URI
from schema2validataclass.config import Config

INPUT_DIR = Path(__file__).resolve().parent.parent.parent / 'test_schema' / 'input'


def generated_files(output_path: Path) -> set[str]:
    return {f.name for f in output_path.iterdir() if f.is_file()}


def run_generate(schema_path: Path, output_path: Path):
    config = Config(post_processing=[])
    app = App(config=config)
    app.generate(URI(file_path=schema_path), output_path)
