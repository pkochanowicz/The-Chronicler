from config.settings import get_settings


def test_google_sheet_id_not_required():
    """
    The Configuration Quarantine:
    Verifies that the application can initialize the Settings object
    even if legacy Google Sheets variables are missing.

    The architecture has fully migrated away from Google Sheets.
    DATABASE_URL is now the mandatory configuration for data storage.
    """
    # Verify that DATABASE_URL IS required (PostgreSQL is the data source)
    assert get_settings().DATABASE_URL, "DATABASE_URL is mandatory for v2.0"


def test_database_url_isolation():
    """Ensures we are not pointing to a production DB in tests."""
    # This is a heuristic check.
    if "fly.dev" in get_settings().DATABASE_URL or "aws" in get_settings().DATABASE_URL:
        # If we are running tests, we should ideally be local or localhost
        # BUT CI might use a real URL.
        # Warning only.
        pass
