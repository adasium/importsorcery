import os
from pathlib import Path


def _format_import_path(path: Path) -> str:
    if path.parent == Path('.'):
        return path.stem
    else:
        return str(path.parent).replace(os.sep, '.') + '.' + path.stem


def format_absolute_import(root_path: Path, file_path: Path, symbol: str) -> str:
    relative = Path(os.path.relpath(file_path, start=root_path))
    import_path = _format_import_path(relative)
    return f'from {import_path} import {symbol}'


def format_relative_import(root_path: Path, current_file_path: Path, target_file_path: Path, symbol: str) -> str:
    relative = Path(os.path.relpath(target_file_path, start=current_file_path.parent))
    stem = '.' + str(relative.stem)
    return f'from {stem} import {symbol}'
