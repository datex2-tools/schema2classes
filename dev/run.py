"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(Path(__file__).parent.parent, 'src')))  # noqa: E402

from schema2classes.scripts.schema2classes import main

if __name__ == '__main__':
    main()
