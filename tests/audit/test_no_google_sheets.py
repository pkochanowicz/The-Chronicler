# tests/audit/test_no_google_sheets.py
import pytest
from config.settings import Settings

def test_google_sheet_id_removed():
    """
    Verify that GOOGLE_SHEET_ID is no longer a field in the Settings class.
    This ensures adherence to the architectural decision to ban Google Sheets.
    """
    settings_instance = Settings() # This should be mocked later, but for now we expect it to exist
    with pytest.raises(AttributeError, match="object has no attribute 'GOOGLE_SHEET_ID'"):
        # Accessing the attribute should raise an AttributeError if it's truly removed
        _ = settings_instance.GOOGLE_SHEET_ID
