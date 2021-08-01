from __future__ import annotations

import ast
import inspect
import os
import sys
from argparse import ArgumentParser
from collections import defaultdict
from types import ModuleType
from typing import List
from typing import Optional
from typing import Sequence

IMPORTS = []
DEFS: dict[str, set] = defaultdict(set)
INDEXED_MODULES: set[ModuleType] = set()



class MyVisitor(ast.NodeVisitor):
    def __init__(self, root_path: str, module_path: str) -> None:
        super().__init__()
        self.root_path = root_path
        self.module_path = module_path

    @property
    def rel_path(self) -> str:
        return os.path.relpath(self.module_path, self.root_path)

    @property
    def import_path(self) -> str:
        dir, filename = os.path.split(self.rel_path)
        if filename == '__init__.py':
            path = dir
        else:
            path = os.path.splitext(self.rel_path)[0]

        return path.replace(os.sep, '.')

    def visit_import(self, node: ast.Import | ast.ImportFrom) -> None:
        IMPORTS.append(node)

    visit_Import = visit_ImportFrom = visit_import

    def visit_def(self, node: ast.FunctionDef | ast.ClassDef | ast.AsyncFunctionDef) -> None:
        if not node.name.startswith('_'):
            DEFS[node.name].add((self.import_path))

    visit_ClassDef = visit_FunctionDef = visit_AsyncFunctionDef = visit_def



def get_import_candidates(symbol: str) -> List[str]:
    if symbol not in DEFS:
        return []

    return [import_path for import_path, ast_obj in DEFS[symbol]]


def index_directory(directory: str, ignored_dirs: List[str] = None) -> None:
    ignored_dirs = ignored_dirs or []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]

        for file in files:
            if not file.endswith('.py'):
                continue
            with open(os.path.join(root, file)) as f:
                try:
                    module = ast.parse(f.read())
                except (SyntaxError, UnicodeDecodeError):
                    continue
                visitor = MyVisitor(
                    root_path=directory,
                    module_path=os.path.join(root, file),
                )
                visitor.visit(module)
                visitor.import_path


def _index_system_module(module_name: str, module: ModuleType, prefix: str = '') -> None:
    """module_name is to workaround os.path being os.posixpath on Linux."""
    DEFS[module.__name__].add(module.__name__)
    if module in INDEXED_MODULES:
        return
    INDEXED_MODULES.add(module)
    for attr in dir(module):
        if attr.startswith('_'):
            continue
        value = getattr(module, attr)
        DEFS[attr].add(module.__name__ + '.' + attr)
        if inspect.ismodule(value):
            _index_system_module(attr, value, prefix='.'.join((prefix, attr)))


def index_system_modules() -> None:
    for name, module in sys.modules.items():
        if not name.startswith('_'):
            _index_system_module(name, module)


def main(args: Optional[Sequence[str]] = None) -> int:
    parser = ArgumentParser()
    parser.add_argument('--symbol', '--import-symbol')
    parser.add_argument('--index', metavar='DIRECTORY', required=True)
    parser.add_argument('--exclude', '-e', metavar='DIRECTORIES', nargs='+')
    parser.add_argument('--python-path', '-p', metavar='PATH', required=True)
    args_ = parser.parse_args()

    index_system_modules()
    __import__('pprint').pprint(DEFS)
    return 0

    print(args_.exclude)
    if args_.index:
        index_directory(args_.index, ignored_dirs=args_.exclude)

        if args_.symbol:
            symbol = args_.symbol
            candidates = get_import_candidates(symbol)
            if len(candidates) > 1:
                print([f'from {candidate} import {symbol}' for candidate in candidates])
            else:
                print(f'No candidates for symbol {symbol}')


    __import__('pprint').pprint(DEFS)
    return 0


if __name__ == '__main__':
    sys.exit(main())
