"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(Path(__file__).parent.parent, 'src')))  # noqa: E402

import argparse

from schema2validataclass import App
from schema2validataclass.common.uri import URI


def main():
    parser = argparse.ArgumentParser(
        prog='schema to validataclass',
        description='Transforms schema to validataclasses and Enums',
    )

    parser.add_argument(
        'schema_path',
        type=Path,
        help='Path to schema file',
    )

    parser.add_argument(
        'output_path',
        type=Path,
        help='Path to output directory',
    )

    args = parser.parse_args()
    schema_path: Path = args.schema_path
    output_path: Path = args.output_path

    app = App()
    schema_uri = URI(file_path=schema_path)
    app.generate(schema_uri, output_path)


if __name__ == '__main__':
    main()
