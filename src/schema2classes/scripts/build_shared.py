"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import argparse
import filecmp
import re
import shutil
from pathlib import Path


def find_identical_files(dir1: Path, dir2: Path) -> set[str]:
    """Find Python files that exist in both directories with identical content."""
    files1 = {f.name for f in dir1.glob('*.py') if f.name != '__init__.py'}
    files2 = {f.name for f in dir2.glob('*.py') if f.name != '__init__.py'}
    common = files1 & files2

    return {name for name in common if filecmp.cmp(dir1 / name, dir2 / name, shallow=False)}


def get_relative_imports(file_path: Path) -> set[str]:
    """Extract module names from relative imports (e.g. 'from .module import Class')."""
    content = file_path.read_text()
    return {match.group(1) for match in re.finditer(r'^from \.([\w]+) import', content, re.MULTILINE)}


def compute_movable_files(identical_files: set[str], dir1: Path) -> set[str]:
    """
    Iteratively compute which identical files can be moved to shared/.

    A file is movable only if all its relative imports also point to movable files,
    ensuring the shared directory is self-contained.
    """
    movable = set(identical_files)
    changed = True
    while changed:
        changed = False
        for name in list(movable):
            imports = get_relative_imports(dir1 / name)
            required_files = {module + '.py' for module in imports}
            if not required_files.issubset(movable):
                movable.discard(name)
                changed = True
    return movable


def fix_imports_in_file(file_path: Path, shared_modules: set[str]):
    """Rewrite relative imports to point to ..shared where the module was moved."""
    content = file_path.read_text()

    def replace_import(match: re.Match) -> str:
        module = match.group(2)
        if module in shared_modules:
            return f'{match.group(1)}..shared.{module}{match.group(3)}'
        return match.group(0)

    new_content = re.sub(
        r'^(from )\.(\w+)( import)',
        replace_import,
        content,
        flags=re.MULTILINE,
    )

    if new_content != content:
        file_path.write_text(new_content)


def main():
    parser = argparse.ArgumentParser(
        description='Move identical files from two source directories into a shared directory and fix imports.',
    )
    parser.add_argument('dir1', type=Path, help='First source directory')
    parser.add_argument('dir2', type=Path, help='Second source directory')
    parser.add_argument('shared', type=Path, help='Shared output directory')
    args = parser.parse_args()

    dir1 = args.dir1.resolve()
    dir2 = args.dir2.resolve()
    shared_dir = args.shared.resolve()

    for directory in [dir1, dir2]:
        if not directory.is_dir():
            parser.error(f'Directory does not exist: {directory}')

    # Step 1: find identical files
    identical = find_identical_files(dir1, dir2)
    print(f'Found {len(identical)} identical files between the two directories')

    if not identical:
        print('Nothing to do.')
        return

    # Step 2: compute which files can safely be moved (self-contained imports)
    movable = compute_movable_files(identical, dir1)
    print(f'{len(movable)} files can be moved to shared/')

    skipped = identical - movable
    if skipped:
        print(f'Skipping {len(skipped)} identical files (they import non-shared modules):')
        for name in sorted(skipped):
            print(f'  {name}')

    if not movable:
        print('No files to move.')
        return

    # Step 3: move files to shared directory
    shared_dir.mkdir(parents=True, exist_ok=True)
    shared_modules = {name.removesuffix('.py') for name in movable}

    for name in sorted(movable):
        shutil.move(dir1 / name, shared_dir / name)
        (dir2 / name).unlink()

    print(f'Moved {len(movable)} files to {shared_dir}')

    # Step 4: create __init__.py in shared directory
    init_path = shared_dir / '__init__.py'
    if not init_path.exists():
        init_content = ''
        # copy style from source directory if available
        for source_init in [dir1 / '__init__.py', dir2 / '__init__.py']:
            if source_init.exists():
                init_content = source_init.read_text()
                break
        init_path.write_text(init_content)
        print(f'Created {init_path}')

    # Step 5: fix imports in remaining source directory files
    fixed_count = 0
    for source_dir in [dir1, dir2]:
        for py_file in source_dir.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            content_before = py_file.read_text()
            fix_imports_in_file(py_file, shared_modules)
            if py_file.read_text() != content_before:
                fixed_count += 1

    print(f'Fixed imports in {fixed_count} files')
    print('Done.')


if __name__ == '__main__':
    main()
