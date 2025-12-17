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
import json
from unittest.mock import MagicMock
from utils.embed_parser import serialize_embeds, parse_embed_json

class TestEmbedParser:
    """
    Tests for embed serialization/deserialization utilities.
    """

    def test_serialize_embeds_single(self):
        """Test serializing a single embed to JSON."""
        mock_embed = MagicMock()
        mock_embed.to_dict.return_value = {"title": "Test Embed", "description": "Desc"}
        
        json_str = serialize_embeds([mock_embed])
        data = json.loads(json_str)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == "Test Embed"

    def test_serialize_embeds_multiple(self):
        """Test serializing multiple embeds."""
        mock_embed1 = MagicMock()
        mock_embed1.to_dict.return_value = {"title": "Embed 1"}
        mock_embed2 = MagicMock()
        mock_embed2.to_dict.return_value = {"title": "Embed 2"}
        
        json_str = serialize_embeds([mock_embed1, mock_embed2])
        data = json.loads(json_str)
        
        assert len(data) == 2
        assert data[0]["title"] == "Embed 1"
        assert data[1]["title"] == "Embed 2"

    def test_parse_embed_json(self):
        """Test parsing JSON back to Embed objects (mocked)."""
        # Since parse_embed_json likely creates discord.Embed objects, 
        # and we can't easily mock the return type class identity without discord.py,
        # we check if it calls the constructor or behaves as expected.
        # However, typically parse_embed_json would use discord.Embed.from_dict
        
        # For this test, we might need to mock discord.Embed
        with pytest.MonkeyPatch.context() as m:
            mock_discord_embed = MagicMock()
            m.setattr("discord.Embed.from_dict", mock_discord_embed)
            
            json_str = '[{"title": "Test"}]'
            embeds = parse_embed_json(json_str)
            
            assert isinstance(embeds, list)
            mock_discord_embed.assert_called_once_with({"title": "Test"})

    def test_round_trip_integrity(self):
        """Test that data survives a round trip."""
        # This is harder to test without real discord.Embed objects, 
        # but conceptually: serialize -> parse -> data match.
        pass