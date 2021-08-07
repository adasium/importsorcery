from pathlib import Path

import pytest

from importsorcery.index import Import


@pytest.mark.parametrize(
    "project_root, target_file_path, symbol, expected_import", [
        (Path('/project/'), Path('/project/package/module_b.py'), 'Stuff', 'from package.module_b import Stuff'),
        (Path('/project/'), Path('/project/utils.py'), 'Stuff', 'from utils import Stuff'),
    ],
)
def test_format_absolute_import(project_root, target_file_path, symbol, expected_import):
    absolute_import = Import(target_file_path).get_absolute_import(symbol=symbol, root=project_root)

    assert absolute_import == expected_import


@pytest.mark.parametrize(
    "project_root, current_file_path, target_file_path, symbol, expected_import", [
        ('/project', Path('/project/package/module_a.py'), Path('/project/package/module_b.py'), 'Stuff', 'from .module_b import Stuff'),
    ],
)

def test_format_relative_import(project_root, current_file_path, target_file_path, symbol, expected_import):
    relative_import = Import(target_file_path).get_relative_import(symbol=symbol, current_file_path=current_file_path, root=project_root)

    assert relative_import == expected_import
