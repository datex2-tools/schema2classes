"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(Path(__file__).parent.parent, 'src')))  # noqa: E402

import argparse

from schema2classes import App
from schema2classes.common.uri import URI
from schema2classes.config import Config


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

    parser.add_argument(
        '-c',
        '--config',
        type=Path,
        help='Path to YAML configuration file',
    )

    args = parser.parse_args()

    config = Config.from_yaml(args.config) if args.config else Config()

    app = App(config=config)
    schema_uri = URI(file_path=args.schema_path)
    app.generate(schema_uri, args.output_path)


if __name__ == '__main__':
    main()
