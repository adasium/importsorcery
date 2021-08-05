import os
from pathlib import Path


def format_absolute_import(root_path: Path, file_path: Path, symbol: str) -> str:
    relative = Path(os.path.relpath(file_path, start=root_path))
    stem = str(relative.parent).replace(os.sep, '.') + '.' + relative.stem
    return f'from {stem} import {symbol}'


def format_relative_import(root_path: Path, current_file_path: Path, target_file_path: Path, symbol: str) -> str:
    relative = Path(os.path.relpath(target_file_path, start=current_file_path.parent))
    print(relative)
    stem = '.' + str(relative.stem)
    print(stem)
    return f'from {stem} import {symbol}'
