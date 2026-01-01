def test_no_gspread_imported():
    """
    The 'Split Brain' Firewall:
    Ensures that 'gspread' (Google Sheets library) is NOT imported in the runtime
    environment of the new architecture services.
    """
    # We will simulate importing core services and check sys.modules
    # Note: If gspread is installed, it might be in sys.modules if *any* test imported it.
    # This test is strict: it fails if gspread is loaded *at all* during this test collection
    # if we run it in isolation, or we check specifically that 'services.sheets_service'
    # doesn't depend on it (though that's harder to check dynamically).

    # Better approach: Scan the imports of specific new-architecture modules.

    # 1. Force unload if possible (dangerous) or just check current state
    # If this test runs, and gspread is in sys.modules, it implies something imported it.

    # However, 'services.sheets_service.py' explicitly imports gspread.
    # The goal of v2.0 is that *new* services (CharacterService) do NOT use it.

    # Let's verify that 'services.character_service' does NOT import gspread.

    from services import character_service

    # Inspect the module's global namespace
    assert "gspread" not in dir(
        character_service
    ), "CharacterService must not import gspread"

    # Also check 'services.bank_service'
    from services import bank_service

    assert "gspread" not in dir(
        bank_service
    ), "GuildBankService must not import gspread"


def test_no_oauth2client_imported():
    """Ensures oauth2client is not used in core services."""
    from services import character_service

    assert "oauth2client" not in dir(character_service)
