from __future__ import annotations

import ast
import inspect
import os
import sys
from collections import defaultdict
from pathlib import Path
from types import ModuleType

from importsorcery.imports import Import
from importsorcery.imports import ImportSource

SYSTEM_MODULES = (
    'argparse',
    'ast',
    'collections',
    'csv',
    'datetime',
    'enum',
    'inspect',
    'inspect',
    'itertools',
    'json',
    'logging',
    'os',
    'pathlib',
    'random',
    're',
    'sys',
    'time',
    'types',
    'typing',
    'urllib',
)


class MyVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self._symbols: list[str] = []

    @property
    def symbols(self) -> list[str]:
        return self._symbols

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name) and not target.id.startswith('_'):
                self._symbols.append(target.id)

    def visit_def(self, node: ast.FunctionDef | ast.ClassDef | ast.AsyncFunctionDef) -> None:
        if not node.name.startswith('_'):
            self._symbols.append(node.name)

    visit_ClassDef = visit_FunctionDef = visit_AsyncFunctionDef = visit_def


class Index:
    def __init__(self) -> None:
        self._cache: dict[str, set[Import]] = defaultdict(set)
        self._ignored_dirs = [  # TODO
            '.mypy_cache',
            '__pycache__',
            '.venv',
            '.git',
        ]
        self._indexed_modules: set[ModuleType] = set()

    def index_project(self, root: Path) -> None:
        for root_, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in self._ignored_dirs]

            for file in files:
                if not file.endswith('.py') or file.startswith('.'):
                    continue
                abs_file_path = os.path.join(root_, file)
                with open(abs_file_path) as f:
                    module = ast.parse(f.read())
                    visitor = MyVisitor()
                    visitor.visit(module)
                    for symbol in visitor.symbols:
                        self._cache[symbol].add(Import(abs_file_path, source=ImportSource.PROJECT))

    def get_candidates(self, project_root: Path, symbol: str, current_file_path: Path | None = None) -> list[str]:
        ret = []
        candidates = self._cache.get(symbol, set())

        for candidate in candidates:
            if candidate.source == ImportSource.SYSTEM:
                ret.append(candidate.get_absolute_import(symbol))
            else:
                if current_file_path is None or not current_file_path.samefile(candidate.path):
                    absolute_import = candidate.get_absolute_import(symbol=symbol, root=project_root)
                    ret.append(absolute_import)
                if current_file_path is not None and not current_file_path.samefile(candidate.path):
                    relative_import = candidate.get_relative_import(symbol=symbol, current_file_path=current_file_path, root=project_root)
                    ret.append(relative_import)

        return ret

    def _index_system_module(self, name: str, module: ModuleType, _parts: list[str]) -> None:
        _parts = _parts or []
        if module in self._indexed_modules:
            return
        self._indexed_modules.add(module)

        for attr in dir(module):
            if not attr.startswith('_'):
                value = getattr(module, attr)
                self._cache[attr].add(Import(parts=_parts + [attr], source=ImportSource.SYSTEM))

                if inspect.ismodule(value):
                    self._index_system_module(name=attr, module=value, _parts=_parts + [attr])

    def index_system_modules(self) -> None:
        system_modules = {k: v for k, v in sys.modules.items() if k in SYSTEM_MODULES}
        for name, module in system_modules.items():
            if not name.startswith('_'):
                self._cache[name].add(Import(parts=[name], source=ImportSource.SYSTEM))
                self._index_system_module(name=name, module=module, _parts=[name])
