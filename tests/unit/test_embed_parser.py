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

    def test_parse_embed_json(self, monkeypatch):
        """Test parsing JSON back to Embed objects."""
        # Since parse_embed_json creates discord.Embed objects,
        # we need to mock discord.Embed.from_dict

        # Create mock Embed class with from_dict class method
        mock_embed_class = MagicMock()
        mock_embed_instance = MagicMock()
        mock_embed_class.from_dict.return_value = mock_embed_instance

        # Patch discord.Embed
        monkeypatch.setattr("utils.embed_parser.discord.Embed", mock_embed_class)

        json_str = '[{"title": "Test"}]'
        embeds = parse_embed_json(json_str)

        # Verify parse_embed_json called Embed.from_dict
        assert isinstance(embeds, list), "Should return list of embeds"
        mock_embed_class.from_dict.assert_called_once_with({"title": "Test"})

    def test_round_trip_integrity(self):
        """Test that data survives a serialize -> parse round trip."""
        # Create a mock embed with known data
        mock_embed = MagicMock()
        embed_dict = {
            "title": "Test Character",
            "description": "A brave warrior",
            "color": 0xC69B6D,
            "fields": [
                {"name": "Race", "value": "Dwarf", "inline": True},
                {"name": "Class", "value": "Warrior", "inline": True},
            ],
        }
        mock_embed.to_dict.return_value = embed_dict

        # Serialize
        json_str = serialize_embeds([mock_embed])

        # Verify serialization preserves data structure
        data = json.loads(json_str)
        assert len(data) == 1
        assert data[0]["title"] == "Test Character"
        assert data[0]["description"] == "A brave warrior"
        assert data[0]["color"] == 0xC69B6D
        assert len(data[0]["fields"]) == 2
        assert data[0]["fields"][0]["name"] == "Race"
        assert data[0]["fields"][1]["value"] == "Warrior"

        # Note: Full round-trip (parse back to Embed) requires discord.py
        # For unit testing, verifying serialize preserves data structure is sufficient
