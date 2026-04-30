"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import importlib
import sys
from pathlib import Path
from types import ModuleType

from schema2classes import App
from schema2classes.common.uri import URI
from schema2classes.config import Config, OutputFormat

INPUT_DIR = Path(__file__).resolve().parent.parent.parent / 'test_schema' / 'input'


def generated_files(output_path: Path) -> set[str]:
    return {f.name for f in output_path.iterdir() if f.is_file()}


def run_generate(schema_path: Path, output_path: Path):
    config = Config(output_format=OutputFormat.PYDANTIC, post_processing=[])
    app = App(config=config)
    app.generate(URI(file_path=schema_path), output_path)


def import_module(output_path: Path, module_name: str) -> ModuleType:
    pkg_name = output_path.name
    parent = str(output_path.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    for key in [k for k in sys.modules if k == pkg_name or k.startswith(f'{pkg_name}.')]:
        del sys.modules[key]
    importlib.import_module(pkg_name)
    return importlib.import_module(f'{pkg_name}.{module_name}')
