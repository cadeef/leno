import pytest

import leno.source as source

from . import fixtures


@pytest.mark.parametrize("name", fixtures.SOURCES)
def test_get_source(tmp_path, name):
    """
    Ensure that the proper class is returned for a given name
    """
    data_dir = tmp_path / "data"
    venv = tmp_path / "venv"
    src = source.get_source(name, data_dir, venv)
    assert src.name == name
    assert hasattr(src, "description")
    assert hasattr(src, "packages")


def test_get_source__invalid(tmp_path):
    data_dir = tmp_path / "data"
    venv = tmp_path / "venv"
    with pytest.raises(source.SourceException):
        source.get_source("a-thoroughly-invalid-source", data_dir, venv)


def test_get_sources():
    sources = source.get_sources()
    assert len(sources) == len(fixtures.SOURCES)
