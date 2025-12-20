"""
Tests for the Google Sheets auto-formatting feature.
"""
import pytest
from unittest.mock import MagicMock, patch
import os

# This fixture runs automatically for all tests in this module.
# It sets the required environment variables before any other code runs.
@pytest.fixture(scope='module', autouse=True)
def setup_environment():
    """Sets dummy env vars required by the settings module."""
    os.environ['MCP_API_KEY'] = 'test-key'
    os.environ['GRAPHICS_STORAGE_CHANNEL_ID'] = '12345'

    # To reliably reload, we must get the module object from sys.modules
    import sys
    import importlib
    
    # Ensure the module is loaded before trying to reload it
    import config.settings
    
    if 'config.settings' in sys.modules:
        importlib.reload(sys.modules['config.settings'])

    yield

    # Clean up the environment variables after tests are done
    del os.environ['MCP_API_KEY']
    del os.environ['GRAPHICS_STORAGE_CHANNEL_ID']


@patch('services.sheets_service.Credentials.from_service_account_file')
@patch('gspread.authorize')
def test_schema_valid_no_formatting_triggered(mock_gspread_authorize, mock_creds, monkeypatch):
    """
    Tests that if the sheet schema is valid, no formatting action is taken.
    """
    # Import the service here to ensure env vars are set
    from services.sheets_service import GoogleSheetsService, CHARACTER_SCHEMA_COLUMNS
    
    # Setup mock worksheet
    mock_worksheet = MagicMock()
    mock_worksheet.row_values.return_value = CHARACTER_SCHEMA_COLUMNS
    mock_worksheet.title = "Character_Submissions"

    # Setup mock gspread client
    mock_workbook = MagicMock()
    mock_talent_sheet = MagicMock() # Mock the second sheet as well
    mock_talent_sheet.row_values.return_value = ['Class', 'Tree', 'TalentName', 'MaxRank', 'Level', 'Tier', 'Requires', 'RequiredBy']
    mock_workbook.worksheet.side_effect = [mock_worksheet, mock_talent_sheet]
    mock_gspread_authorize.return_value.open_by_key.return_value = mock_workbook

    # Ensure auto-formatting is disabled
    monkeypatch.setattr('config.settings.settings.AUTOFORMAT_SHEETS_ON_STARTUP', False)

    # Instantiate the service
    service = GoogleSheetsService()

    # Assertions
    mock_worksheet.clear.assert_not_called()
    assert service.character_sheet_instance is not None


@patch('services.sheets_service.Credentials.from_service_account_file')
@patch('gspread.authorize')
def test_schema_invalid_and_formatting_disabled_raises_error(mock_gspread_authorize, mock_creds, monkeypatch):
    """
    Tests that if the schema is invalid and auto-formatting is disabled,
    a ValueError is raised, and the application halts.
    """
    from services.sheets_service import GoogleSheetsService, CHARACTER_SCHEMA_COLUMNS

    # Setup mock worksheet with a bad schema
    bad_schema = list(CHARACTER_SCHEMA_COLUMNS)
    bad_schema[-1] = "a_very_wrong_column" # Mismatch last column
    mock_worksheet = MagicMock()
    mock_worksheet.row_values.return_value = bad_schema
    mock_worksheet.title = "Character_Submissions"

    # Setup mock gspread client
    mock_workbook = MagicMock()
    mock_talent_sheet = MagicMock()
    mock_talent_sheet.row_values.return_value = ['Class', 'Tree', 'TalentName', 'MaxRank', 'Level', 'Tier', 'Requires', 'RequiredBy']
    mock_workbook.worksheet.side_effect = [mock_worksheet, mock_talent_sheet]
    mock_gspread_authorize.return_value.open_by_key.return_value = mock_workbook

    # Ensure auto-formatting is disabled
    monkeypatch.setattr('config.settings.settings.AUTOFORMAT_SHEETS_ON_STARTUP', False)

    # Assert that instantiating the service raises a ValueError
    with pytest.raises(ValueError, match="Invalid schema for worksheet 'Character_Submissions'. Halting startup."):
        GoogleSheetsService()

    # Verify no destructive actions were taken
    mock_worksheet.clear.assert_not_called()


@patch('services.sheets_service.Credentials.from_service_account_file')
@patch('gspread.authorize')
def test_schema_invalid_and_formatting_enabled_formats_sheet(mock_gspread_authorize, mock_creds, monkeypatch):
    """
    Tests that if the schema is invalid but auto-formatting is enabled,
    the service formats the sheet correctly.
    """
    from services.sheets_service import GoogleSheetsService, CHARACTER_SCHEMA_COLUMNS
    
    # Setup mock worksheet with a bad schema
    bad_schema = list(CHARACTER_SCHEMA_COLUMNS)
    bad_schema[0] = "wrong_timestamp_column"
    mock_worksheet = MagicMock()
    mock_worksheet.row_values.return_value = bad_schema
    mock_worksheet.title = "Character_Submissions"

    # Setup mock gspread client
    mock_workbook = MagicMock()
    mock_talent_sheet = MagicMock()
    mock_talent_sheet.row_values.return_value = ['Class', 'Tree', 'TalentName', 'MaxRank', 'Level', 'Tier', 'Requires', 'RequiredBy']
    mock_workbook.worksheet.side_effect = [mock_worksheet, mock_talent_sheet]
    mock_gspread_authorize.return_value.open_by_key.return_value = mock_workbook

    # Enable auto-formatting
    monkeypatch.setattr('config.settings.settings.AUTOFORMAT_SHEETS_ON_STARTUP', True)
    
    # Reload settings to ensure the monkeypatch is applied before service instantiation
    from config import settings
    import importlib
    importlib.reload(settings)

    # Instantiate the service (should not raise an error)
    service = GoogleSheetsService()

    # Assertions
    mock_worksheet.clear.assert_called_once()
    mock_worksheet.append_row.assert_called_once_with(CHARACTER_SCHEMA_COLUMNS)
    assert service.character_sheet_instance is not None

