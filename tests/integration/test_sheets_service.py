# Azeroth Bound Discord Bot
# Copyright (C) 2025 [Paweł Kochanowicz - <github.com/pkochanowicz> ]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pytest
from unittest.mock import MagicMock, ANY
from services.sheets_service import CharacterRegistryService

class TestSheetsService:
    """
    Integration tests for CharacterRegistryService with mocked Google Sheets API.
    """

    @pytest.fixture
    def registry(self, mock_sheets_client):
        """Initialize service with mocked client."""
        # We need to patch the internal client creation
        with pytest.MonkeyPatch.context() as m:
            # Mock _connect_to_sheet to set self.sheet
            def mock_connect(service_self):
                # Simulate the behavior of _connect_to_sheet using the mock client
                service_self.client = mock_sheets_client
                # In conftest, mock_sheets_client.open_by_key("key").sheet1 is the mock sheet
                # We can just access it directly or via the chain
                service_self.sheet = mock_sheets_client.open_by_key("key").sheet1
            
            m.setattr("services.sheets_service.CharacterRegistryService._connect_to_sheet", mock_connect)
            
            # Also need to mock _validate_schema to avoid error during init if we don't mock the sheet content
            mock_sheets_client.open_by_key("key").sheet1.row_values.return_value = [
                "timestamp", "discord_id", "discord_name", "char_name", "race", "class", 
                "roles", "professions", "backstory", "personality", "quotes", "portrait_url", 
                "trait_1", "trait_2", "trait_3", "status", "confirmation", "request_sdxl", 
                "recruitment_msg_id", "forum_post_url", "reviewed_by", "embed_json", 
                "death_cause", "death_story", "created_at", "updated_at", "notes"
            ]
            
            return CharacterRegistryService()

    def test_initialization_validates_schema(self, registry):
        """Test that initialization checks for all 27 columns."""
        # The fixture already mocks valid schema, so init should succeed.
        assert registry.sheet is not None

    def test_log_character_27_columns(self, registry, sample_character_data):
        """Test logging a character writes all 27 columns correctly."""
        
        # Act
        registry.log_character(sample_character_data)
        
        # Assert
        registry.sheet.append_row.assert_called_once()
        args, _ = registry.sheet.append_row.call_args
        row_data = args[0]
        
        assert len(row_data) == 27
        assert row_data[3] == "Thorgar"  # char_name
        assert row_data[15] == "PENDING" # status

    def test_update_character_status(self, registry):
        """Test updating character status."""
        # Mock finding the cell
        mock_cell = MagicMock()
        mock_cell.row = 5
        registry.sheet.find.return_value = mock_cell
        
        # Act
        registry.update_character_status("Thorgar", "REGISTERED", forum_post_url="http://url")
        
        # Assert
        registry.sheet.find.assert_called_with("Thorgar", in_column=ANY) # Assuming name search
        # Should update status (col 16) and forum_url (col 20)
        # Note: update_cell(row, col, value)
        registry.sheet.update_cell.assert_any_call(5, 16, "REGISTERED")
        registry.sheet.update_cell.assert_any_call(5, 20, "http://url")

    def test_get_character_by_name(self, registry):
        """Test retrieving character data."""
        registry.sheet.get_all_records.return_value = [
            {"char_name": "Thorgar", "race": "Dwarf", "status": "PENDING"}
        ]
        
        char_data = registry.get_character_by_name("Thorgar")
        
        assert char_data is not None
        assert char_data["char_name"] == "Thorgar"
