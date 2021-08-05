#!/usr/bin/env python3.8
from __future__ import annotations

import ast
import datetime
import inspect
import os
import sys
from argparse import ArgumentParser
from collections import defaultdict
from types import ModuleType
from typing import Sequence

from .index import Index

DEFS: dict[str, set] = defaultdict(set)
INDEXED_MODULES: set[ModuleType] = set()


class Import:
    SCORE = 1.0

    def __init__(self, import_str: str, score: float | None = None) -> None:
        self.import_str = import_str
        self.parts = import_str.split('.')
        self._score = score or self.SCORE

    @property
    def score(self) -> float:
        if len(self.parts) > 1:
            return self._score
        else:
            return self._score + 0.2


    def __str__(self) -> str:
        *head, tail = self.parts
        if len(self.parts) > 1:
            return 'from {head} import {tail}'.format(
                head='.'.join(head),
                tail=tail,
            )
        else:
            return f'import {tail}'

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Import):
            return NotImplemented
        else:
            return other.score < self.score


class LocalImport(Import):
    SCORE = 2


class SystemImport(Import):
    SCORE = 1


def _index_system_module(module_name: str, module: ModuleType, prefix: str = '') -> None:
    """module_name is to workaround os.path being os.posixpath on Linux."""
    if module in INDEXED_MODULES:
        return
    INDEXED_MODULES.add(module)
    for attr in dir(module):
        if attr.startswith('_'):
            continue
        value = getattr(module, attr)
        DEFS[attr].add(SystemImport('.'.join((prefix, module_name, attr)).lstrip('.')))
        if inspect.ismodule(value):
            _index_system_module(attr, value, prefix='.'.join((prefix, attr)).lstrip('.'))


def index_system_modules() -> None:
    for name, module in sys.modules.items():
        if not name.startswith('_'):
            DEFS[name].add(SystemImport(name))
            _index_system_module(name, module)


def main(args: Sequence[str] | None = None) -> int:
    parser = ArgumentParser()
    parser.add_argument('--symbol', '--import-symbol')
    parser.add_argument('--index', metavar='DIRECTORY', required=True)
    parser.add_argument('--exclude', '-e', metavar='DIRECTORIES', nargs='+')
    parser.add_argument('--python-path', '-p', metavar='PATH', required=True)
    args_ = parser.parse_args()

    index_system_modules()

    index = Index()

    if args_.index:
        # index_directory(args_.index, ignored_dirs=args_.exclude)
        index.index_project(args_.index)

    if args_.symbol:
        symbol = args_.symbol
        candidates = index.get_candidates(project_root=args_.index, symbol=symbol)
        candidates.sort()
        for candidate in candidates:
            print(candidate)
    return 0


if __name__ == '__main__':
    sys.exit(main())
