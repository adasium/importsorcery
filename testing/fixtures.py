import shutil

import pytest

@pytest.fixture(scope="module")
def change_test_dir(tmp_path_factory):
    my_tmpdir = tmp_path_factory.mktemp("data")
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))
