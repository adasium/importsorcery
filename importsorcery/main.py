#!/usr/bin/env python3.8
from __future__ import annotations

import ast
import datetime
import inspect
import os
import sys
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from types import ModuleType
from typing import Sequence

from .index import Index


def main(args: Sequence[str] | None = None) -> int:
    parser = ArgumentParser()
    parser.add_argument('--symbol', '--import-symbol')
    parser.add_argument('--index', metavar='DIRECTORY', required=True)
    parser.add_argument('--exclude', '-e', metavar='DIRECTORIES', nargs='+')
    parser.add_argument('--python-path', '-p', metavar='PATH', required=True)
    parser.add_argument('--current-file', metavar='PATH', required=False)
    args_ = parser.parse_args()

    index = Index()
    index.index_system_modules()

    if args_.index:
        # index_directory(args_.index, ignored_dirs=args_.exclude)
        index.index_project(args_.index)

    if args_.symbol:
        symbol = args_.symbol
        if args_.current_file is not None:
            current_file_path: Path | None = Path(args_.current_file)
        else:
            current_file_path = None
        candidates = index.get_candidates(project_root=args_.index, symbol=symbol, current_file_path=current_file_path)
        candidates.sort()
        for candidate in candidates:
            print(candidate)
    return 0


if __name__ == '__main__':
    sys.exit(main())
