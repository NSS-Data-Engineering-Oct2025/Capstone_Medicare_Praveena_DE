import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
import pandas as pd
import requests
from src.upload_to_rustfs.api1_inpatient_data import fetch_inpatient_data
from src.upload_to_rustfs.api2_physician_data import fetch_physician_data


def test_fetch_inpatient_returns_dataframe_on_success():
    """Should return a DataFrame when API responds successfully."""
    mock_batch = [{"provider_ccn": "123", "drg_code": "001", "total_discharges": "10"}]

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.side_effect = [mock_batch, []]  # first call returns data, second empty = stop
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_inpatient_data()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1

def test_fetch_inpatient_returns_empty_df_on_failure():
    """Should return empty DataFrame when all retries fail."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = fetch_inpatient_data(max_retries=2, base_delay=0)

    assert isinstance(result, pd.DataFrame)
    assert result.empty

def test_fetch_inpatient_returns_empty_df_on_empty_response():
    """Should return empty DataFrame when API returns no data."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = []  # API returns empty list
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_inpatient_data()

    assert isinstance(result, pd.DataFrame)
    assert result.empty

def test_fetch_inpatient_handles_timeout():
    """Should retry and eventually return empty DataFrame on timeout."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Timed out")

        result = fetch_inpatient_data(max_retries=2, base_delay=0)

    assert result.empty

def test_fetch_physician_returns_dataframe_on_success():
    """Should return a DataFrame when API responds successfully."""
    mock_batch = [{"npi": "1234567890", "hcpcs_code": "99213", "total_services": "5"}]

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.side_effect = [mock_batch, []]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_physician_data()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1


def test_fetch_physician_returns_empty_df_on_failure():
    """Should return empty DataFrame when all retries fail."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = fetch_physician_data(max_retries=2, base_delay=0)

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_fetch_physician_respects_max_rows():
    """Should stop fetching once max_rows limit is reached."""
    # each batch has 3 rows, max_rows set to 5 → should stop after 2 batches
    mock_batch = [
        {"npi": "111", "hcpcs_code": "A", "total_services": "1"},
        {"npi": "222", "hcpcs_code": "B", "total_services": "2"},
        {"npi": "333", "hcpcs_code": "C", "total_services": "3"},
    ]

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_batch
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with patch("src.upload_to_rustfs.api2_physician_data.settings") as mock_settings:
            mock_settings.cms_api_base_url = "http://fake-api.com"
            mock_settings.cms_physician_dataset_id = "fake-id"
            mock_settings.physician_max_rows = 5  # limit to 5 rows

            result = fetch_physician_data()

    assert len(result) <= 5


def test_fetch_physician_handles_timeout():
    """Should retry and eventually return empty DataFrame on timeout."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Timed out")

        result = fetch_physician_data(max_retries=2, base_delay=0)

    assert result.empty