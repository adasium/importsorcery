from pathlib import Path

import pytest

from importsorcery.utils import format_absolute_import
from importsorcery.utils import format_relative_import


@pytest.mark.parametrize(
    "project_root, target_file_path, symbol, expected_import", [
        (Path('/project/'), Path('/project/package/module_b.py'), 'Stuff', 'from package.module_b import Stuff'),
    ],
)
def test_format_absolute_import(project_root, target_file_path, symbol, expected_import):
    absolute_import = format_absolute_import(project_root, target_file_path, symbol)

    assert absolute_import == expected_import


@pytest.mark.parametrize(
    "project_root, current_file_path, target_file_path, symbol, expected_import", [
        ('/project', Path('/project/package/module_a.py'), Path('/project/package/module_b.py'), 'Stuff', 'from .module_b import Stuff'),
    ],
)

def test_format_relative_import(project_root, current_file_path, target_file_path, symbol, expected_import):
    relative_import = format_relative_import(project_root, current_file_path, target_file_path, symbol)

    assert relative_import == expected_import
