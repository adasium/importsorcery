from __future__ import annotations

import os
from enum import Enum
from pathlib import Path


class ImportSource(Enum):
    PROJECT = 'project'
    SYSTEM = 'system'


def _format_import_path(path: Path) -> str:
    if path.parent == Path('.'):
        return path.stem
    else:
        return str(path.parent).replace(os.sep, '.') + '.' + path.stem


class Import:
    def __init__(
            self,
            path: str | Path | None = None,
            parts: list[str] = None,
            source: ImportSource = ImportSource.PROJECT,
    ) -> None:
        if path is None and not parts:
            raise ValueError('Either path or parts must be specified')
        self.source = source
        self._path = path and Path(path) or Path()
        self._parts = parts or []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Import):
            return self._path == other._path and self._parts == other._parts
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self._path) + hash('.'.join(self._parts))

    @property
    def path(self) -> Path:
        if self.source == ImportSource.PROJECT:
            return self._path
        else:
            raise ValueError

    def get_absolute_import(self, symbol: str, root: Path | None = None) -> str:
        if self.source == ImportSource.SYSTEM:
            if len(self._parts) == 1:
                return f'import {self._parts[0]}'
            else:
                *import_path_, symbol = self._parts
                return 'from {} import {}'.format('.'.join(import_path_), symbol)
        else:
            relative = Path(os.path.relpath(self._path, start=root))
            import_path = _format_import_path(relative)
            return f'from {import_path} import {symbol}'

    def get_relative_import(self, symbol: str, current_file_path: Path, root: Path | None = None) -> str:
        if self.source == ImportSource.SYSTEM:
            raise ValueError('Relative import for system modules is invalid.')
        relative = Path(os.path.relpath(self._path, start=current_file_path.parent))
        stem = '.' + str(relative.stem)
        return f'from {stem} import {symbol}'
