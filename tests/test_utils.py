import pytest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils import get_duckdb_path, get_ducklake_catalog_path, get_ducklake_data_path


def test_get_duckdb_path_returns_string():
    result = get_duckdb_path()
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_ducklake_catalog_path_returns_string():
    result = get_ducklake_catalog_path()
    assert isinstance(result, str)
    assert result.endswith(".ducklake")


def test_get_ducklake_data_path_returns_string():
    result = get_ducklake_data_path()
    assert isinstance(result, str)
    assert len(result) > 0