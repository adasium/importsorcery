from pathlib import Path

import pytest
from importsorcery.index import Index
from testing.fixtures import FakeProject


@pytest.mark.parametrize(
    "currently_edited_file, symbol,  expected_import", [
        ('package_a/module_a.py', 'AnotherStuff', 'from package_a.module_b import AnotherStuff'),
    ],
)
def test_index_absolute_import(currently_edited_file, symbol, expected_import):
    with FakeProject() as fp:
        index = Index()
        index.index_project(root=fp.project_root)
        candidates = index.get_candidates(fp.project_root, symbol, fp.project_root / currently_edited_file)
        assert expected_import in candidates


@pytest.mark.parametrize(
    "currently_edited_file, target_import_path, symbol,  unexpected_import", [
        ('package_a/module_a.py', 'package_a/module_a.py', 'Stuff', 'from package_a.module_a import Stuff'),
    ],
)
def test_index_absolute_import_skip_importing_from_currently_edited_file(currently_edited_file, target_import_path, symbol, unexpected_import):
    with FakeProject() as fp:
        index = Index()
        index.index_project(root=fp.project_root)
        candidates = index.get_candidates(fp.project_root, symbol, fp.project_root / currently_edited_file)
        assert unexpected_import not in candidates


@pytest.mark.parametrize(
    "currently_edited_file, target_import_path, symbol,  expected_import", [
        (Path('package_a/module_a.py'), 'package_a/module_b.py', 'AnotherStuff', 'from .module_b import AnotherStuff'),
    ],
)
def test_index_relative_import(currently_edited_file, target_import_path, symbol, expected_import):

    with FakeProject() as fp:
        index = Index()
        index.index_project(root=fp.project_root)
        candidates = index.get_candidates(fp.project_root, symbol, current_file_path=fp.project_root / currently_edited_file)
        assert expected_import in candidates


@pytest.mark.parametrize(
    "currently_edited_file, target_import_path, symbol,  unexpected_import", [
        (Path('package_a/module_b.py'), 'package_a/module_b.py', 'AnotherStuff', 'from .module_b import AnotherStuff'),
    ],
)
def test_index_relative_import_skip_importing_from_currently_edited_file(currently_edited_file, target_import_path, symbol, unexpected_import):

    with FakeProject() as fp:
        index = Index()
        index.index_project(root=fp.project_root)
        candidates = index.get_candidates(fp.project_root, symbol, current_file_path=fp.project_root / currently_edited_file)
        assert unexpected_import not in candidates
