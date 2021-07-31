from __future__ import annotations

import ast
import os
import sys
from argparse import ArgumentParser
from collections import defaultdict
from typing import List
from typing import Optional
from typing import Sequence

IMPORTS = []
DEFS = defaultdict(list)



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
        DEFS[node.name].append((self.import_path, node))

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
                module = ast.parse(f.read())
                visitor = MyVisitor(
                    root_path=directory,
                    module_path=os.path.join(root, file),
                )
                visitor.visit(module)
                visitor.import_path


def main(args: Optional[Sequence[str]] = None) -> int:
    parser = ArgumentParser()
    parser.add_argument('--symbol', '--import-symbol')
    parser.add_argument('--index', metavar='DIRECTORY')
    parser.add_argument('--exclude', '-e', metavar='PATHS', nargs='+')
    args_ = parser.parse_args()

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
