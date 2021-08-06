from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

import pytest


PROJECT_ROOT = Path('/tmp/project')


class FakeProject:

    def __init__(self) -> None:
        self._project_root = TemporaryDirectory()
        self._construct()

    @property
    def project_root(self) -> Path:
        return Path(self._project_root.name)

    def _construct(self) -> None:
        package_a = self._create_package(at=self.project_root, name='package_a')
        self._create_module(
            at=package_a, name='module_a.py', contents=dedent(
                """\
            class Stuff:
                pass
            """,
            ),
        )
        self._create_module(
            at=package_a, name='module_b.py', contents=dedent("""\
            class AnotherStuff:
                pass
        """),
        )

    def _create_package(self, at: Path, name: str) -> Path:
        package = at / name
        Path(package).mkdir(exist_ok=True)
        with open(package / '__init__.py', 'a') as _: pass
        return package

    def _create_module(self, at: Path, name: str, contents: str = '') -> None:
        with open(at / name, 'w') as f:
            f.write(contents)


    def __enter__(self) -> FakeProject:
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self._project_root.cleanup()



@pytest.fixture(scope="module")
def fake_project():
    with FakeProject() as fp:
        yield fp
