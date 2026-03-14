"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
import sys
from pathlib import Path

sys.path.append(str(Path(Path(__file__).parent.parent, 'src')))  # noqa: E402

import argparse

from schema2validataclass import App
from schema2validataclass.common.uri import URI
from schema2validataclass.config import Config


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

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    app = App(config=config)
    schema_uri = URI(file_path=args.schema_path)
    app.generate(schema_uri, args.output_path)


if __name__ == '__main__':
    main()
