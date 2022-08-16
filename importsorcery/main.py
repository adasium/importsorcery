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
    project_root: Path
    exclude_dirs: List[Path]
    python_path: Path
    current_file: Optional[Path]
    include_relative_imports: bool = False


def main(argv: Sequence[str] | None = None) -> int:
    args = ImportSorceryArgs(underscores_to_dashes=True).parse_args()

    index = Index()
    index.index_system_modules()

    if args.project_root:
        index.index_project(args.project_root)

    if args.symbol:
        candidates = index.get_candidates(
            project_root=args.project_root,
            symbol=args.symbol,
            current_file_path=args.current_file,
            include_relative_imports=args.include_relative_imports,
        )
        for candidate in sorted(candidates):
            print(candidate)
    return 0


if __name__ == '__main__':
    sys.exit(main())
