"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from schema2classes.common.uri import URI


def make_uri(**kwargs) -> URI:
    if not kwargs:
        return URI(file_path=Path('/test/schema.json'))
    return URI(**kwargs)
