from __future__ import annotations

import ast
import os
from collections import defaultdict
from pathlib import Path

from importsorcery.utils import format_absolute_import
from importsorcery.utils import format_relative_import

class MyVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self._symbols: list[str] = []

    @property
    def symbols(self) -> list[str]:
        return self._symbols

    def visit_def(self, node: ast.FunctionDef | ast.ClassDef | ast.AsyncFunctionDef) -> None:
        if not node.name.startswith('_'):
            self._symbols.append(node.name)

    visit_ClassDef = visit_FunctionDef = visit_AsyncFunctionDef = visit_def


class Index:
    def __init__(self) -> None:
        self._cache: dict[str, list[str]] = defaultdict(list)
        self._ignored_dirs = [  # TODO
            '.mypy_cache',
            '__pycache__',
            '.venv',
            '.git',
        ]

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
                        self._cache[symbol].append(abs_file_path)

    def get_candidates(self, project_root: Path, symbol: str, current_file_path: Path | None = None) -> list[str]:
        ret = []
        candidates_paths = self._cache.get(symbol, [])

        for candidate_path in candidates_paths:
            print(candidate_path, current_file_path)
            if not current_file_path.samefile(candidate_path):
                absolute_import = format_absolute_import(project_root, Path(candidate_path), symbol)
                ret.append(absolute_import)
            if current_file_path is not None:
                relative_import = format_relative_import(project_root, current_file_path, Path(candidate_path), symbol)
                ret.append(relative_import)

        return ret
