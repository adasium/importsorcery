#!/usr/bin/env python3.8
from __future__ import annotations

import sys
from pathlib import Path
from typing import List
from typing import Optional
from typing import Sequence

from tap import Tap

from importsorcery.index import Index


class ImportSorceryArgs(Tap):
    symbol: str
    index: Path
    exclude: List[Path]
    python_path: Path
    current_file: Optional[Path]

    def configure(self) -> None:
        self.add_argument('--python-path', '-p', type=Path)
        self.add_argument('--current-file', type=Path)
        self.add_argument('--exclude', '-e')


def main(argv: Sequence[str] | None = None) -> int:
    args = ImportSorceryArgs().parse_args()

    index = Index()
    index.index_system_modules()

    if args.index:
        index.index_project(args.index)

    if args.symbol:
        candidates = index.get_candidates(
            project_root=args.index,
            symbol=args.symbol,
            current_file_path=args.current_file,
        )
        for candidate in sorted(candidates):
            print(candidate)
    return 0


if __name__ == '__main__':
    sys.exit(main())
