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

"""
Google Sheets Service (27-Column Schema)
Handles all interactions with the Character_Submissions Google Sheet.
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import gspread
from google.oauth2.service_account import Credentials
import json
from config.settings import settings


logger = logging.getLogger(__name__)

# Scopes required for Google Sheets API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

class CharacterRegistryService:
    """
    Service for logging registered characters to Google Sheets.
    Enforces the 27-column schema defined in TECHNICAL.md.
    """
    SHEET_NAME = "Character_Submissions"

    # Schema definition (ordered 27 columns)
    SCHEMA_COLUMNS = [
        "timestamp", "discord_id", "discord_name", "char_name", "race", "class", 
        "roles", "professions", "backstory", "personality", "quotes", "portrait_url", 
        "trait_1", "trait_2", "trait_3", "status", "confirmation", "request_sdxl", 
        "recruitment_msg_id", "forum_post_url", "reviewed_by", "embed_json", 
        "death_cause", "death_story", "created_at", "updated_at", "notes",
        "talents_json"
    ]

    # Field mapping: domain_model_field -> sheet_column
    # Note: Some fields map 1:1, others might need transformation
    FIELD_MAPPING = {
        "timestamp": "timestamp",
        "discord_id": "discord_id",
        "discord_name": "discord_name",
        "char_name": "char_name",
        "name": "char_name", # Alias
        "race": "race",
        "class": "class",
        "char_class": "class", # Alias
        "roles": "roles",
        "professions": "professions",
        "backstory": "backstory",
        "personality": "personality",
        "quotes": "quotes",
        "portrait_url": "portrait_url",
        "trait_1": "trait_1",
        "trait_2": "trait_2",
        "trait_3": "trait_3",
        "status": "status",
        "confirmation": "confirmation",
        "request_sdxl": "request_sdxl",
        "recruitment_msg_id": "recruitment_msg_id",
        "forum_post_url": "forum_post_url",
        "reviewed_by": "reviewed_by",
        "embed_json": "embed_json",
        "death_cause": "death_cause",
        "death_story": "death_story",
        "created_at": "created_at",
        "updated_at": "updated_at",
        "notes": "notes",
        "talents": "talents_json"
    }

    def __init__(self):
        """Initialize the character registry sheet connection."""
        self.client = None
        self.sheet = None
        self.column_mapping = {}  # column_name -> column_index (0-based)
        self._connect_to_sheet()
        self._validate_schema()

    def _connect_to_sheet(self):
        """Establish connection to Google Sheets."""
        try:
            creds = Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
            )
            self.client = gspread.authorize(creds)
            workbook = self.client.open_by_key(settings.GOOGLE_SHEET_ID)

            # Try to get the specified worksheet
            self.sheet = workbook.worksheet(self.SHEET_NAME)
            logger.info(f"Successfully connected to Google Sheets (worksheet: {self.SHEET_NAME})")
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"Worksheet '{self.SHEET_NAME}' not found. Please create it with 27 columns.")
            raise ValueError(f"Worksheet '{self.SHEET_NAME}' not found")
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise

    def _validate_schema(self):
        """
        Validate that the sheet has the correct 27-column schema.
        """
        try:
            headers = self.sheet.row_values(1)
            
            if not headers:
                raise ValueError("Sheet has no header row.")

            # Build mapping
            self.column_mapping = {name.strip(): i for i, name in enumerate(headers)}
            
            # Check for missing columns
            missing = [col for col in self.SCHEMA_COLUMNS if col not in self.column_mapping]
            if missing:
                raise ValueError(f"Required columns missing from sheet: {', '.join(missing)}")
                
            logger.info("Schema validation successful (27 columns confirmed)")
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            raise

    def _get_timestamp(self) -> str:
        """Generate consistent ISO 8601 timestamp (UTC, no microseconds)."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def log_character(self, character_data: Dict[str, Any]) -> bool:
        """
        Log a new character to the sheet.
        Expects a dictionary with keys matching the 27 columns (or aliases).
        Returns False if character name already exists (duplicate prevention).
        """
        # Check for duplicate character name
        char_name = character_data.get("char_name", "")
        if char_name:
            existing = self.get_character_by_name(char_name)
            if existing:
                logger.warning(f"Character '{char_name}' already exists, rejecting duplicate registration")
                return False

        try:
            # Prepare row
            row = [""] * len(self.SCHEMA_COLUMNS) # Initialize with empty strings, assuming schema columns match headers order
            # Actually, headers might be in different order than SCHEMA_COLUMNS list if user reordered them,
            # but we assume the user follows the schema. 
            # Safer: Use self.column_mapping to find index.
            
            # Use max index from mapping to determine row size
            max_idx = max(self.column_mapping.values())
            row = [""] * (max_idx + 1)

            # Populate auto-fields if missing
            now = self._get_timestamp()
            if "timestamp" not in character_data:
                character_data["timestamp"] = now
            if "created_at" not in character_data:
                character_data["created_at"] = now
            if "updated_at" not in character_data:
                character_data["updated_at"] = now
                
            for key, value in character_data.items():
                col_name = self.FIELD_MAPPING.get(key)
                if col_name and col_name in self.column_mapping:
                    idx = self.column_mapping[col_name]
                    # Handle boolean conversion
                    if isinstance(value, bool):
                        value = "TRUE" if value else "FALSE"
                    # Handle talents conversion to JSON string
                    if key == "talents" and value is not None:
                        value = json.dumps(value) # Convert dict to JSON string
                    row[idx] = str(value) if value is not None else ""
            
            self.sheet.append_row(row)
            logger.info(f"Logged character: {character_data.get('char_name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging character: {e}")
            return False

    def update_character_status(self, char_name: str, new_status: str, **kwargs) -> bool:
        """
        Update status and optional fields for a character.
        """
        try:
            # Find the row (search in char_name column)
            name_col_idx = self.column_mapping.get("char_name")
            if name_col_idx is None:
                raise ValueError("Column 'char_name' not found")
                
            # Use find function for exact match? 
            # gspread find searches whole sheet.
            # Ideally we search specifically in the column.
            # cells = self.sheet.findall(char_name)
            # But simpler: use find() and check column?
            
            cell = self.sheet.find(char_name, in_column=name_col_idx + 1) # gspread is 1-based
            
            if not cell:
                logger.warning(f"Character '{char_name}' not found.")
                return False
                
            row_num = cell.row
            
            # Update status
            status_col_idx = self.column_mapping.get("status")
            if status_col_idx is not None:
                self.sheet.update_cell(row_num, status_col_idx + 1, new_status)

            # Update additional fields
            # Always update updated_at
            kwargs["updated_at"] = self._get_timestamp()
            
            for key, value in kwargs.items():
                col_name = self.FIELD_MAPPING.get(key, key) # Fallback to key itself
                if col_name in self.column_mapping:
                    col_idx = self.column_mapping[col_name]
                    if isinstance(value, bool):
                        value = "TRUE" if value else "FALSE"
                    self.sheet.update_cell(row_num, col_idx + 1, str(value))
            
            logger.info(f"Updated status for {char_name} to {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating character {char_name}: {e}")
            return False

    def _process_record(self, record: Dict[str, str]) -> Dict[str, Any]:
        """Processes a single record from the sheet, deserializing JSON fields."""
        if "talents_json" in record and record["talents_json"]:
            try:
                record["talents"] = json.loads(record["talents_json"])
            except json.JSONDecodeError:
                logger.warning(f"Failed to decode talents_json for character {record.get('char_name')}")
                record["talents"] = {} # Default to empty dict on error
        else:
            record["talents"] = {} # Ensure talents key exists, even if empty
        return record

    def get_character_by_name(self, char_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve character data by name."""
        try:
            records = self.sheet.get_all_records()
            for record in records:
                if record.get("char_name") == char_name:
                    return self._process_record(record) # Use helper here
            return None
        except Exception as e:
            logger.error(f"Error getting character {char_name}: {e}")
            return None

    def get_characters_by_user(self, discord_id: str) -> List[Dict[str, Any]]:
        """Retrieve all characters for a Discord user."""
        try:
            records = self.sheet.get_all_records()
            processed_records = [self._process_record(r) for r in records if str(r.get("discord_id")) == str(discord_id)]
            return processed_records
        except Exception as e:
            logger.error(f"Error getting characters for user {discord_id}: {e}")
            return []

    def get_all_characters(self) -> List[Dict[str, Any]]:
        """Retrieve all characters from the sheet."""
        try:
            records = self.sheet.get_all_records()
            processed_records = [self._process_record(r) for r in records]
            return processed_records
        except Exception as e:
            logger.error(f"Error getting all characters: {e}")
            return []

    def update_character_field(
        self,
        char_name: str,
        discord_id: str,
        field_name: str,
        value: Any
    ) -> bool:
        """
        Update a single field for a specific character.

        Args:
            char_name: Character name
            discord_id: Discord user ID
            field_name: Name of field to update (must be in schema)
            value: New value for the field

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the character's row
            all_records = self.sheet.get_all_records()

            for idx, record in enumerate(all_records):
                if (record.get('char_name') == char_name and
                    str(record.get('discord_id')) == str(discord_id)):

                    # Row number (idx + 2 because: 1=header, idx is 0-based)
                    row_number = idx + 2

                    # Get column index for the field
                    col_name = self.FIELD_MAPPING.get(field_name, field_name)
                    if col_name not in self.column_mapping:
                        logger.error(f"Field '{field_name}' not in schema")
                        return False

                    col_index = self.column_mapping[col_name] + 1  # +1 for 1-based

                    # Convert boolean values
                    if isinstance(value, bool):
                        value = "TRUE" if value else "FALSE"
                    # Convert talents to JSON string
                    if field_name == "talents" and value is not None:
                        value = json.dumps(value)

                    # Update the cell
                    self.sheet.update_cell(row_number, col_index, str(value))

                    # Update updated_at timestamp
                    updated_at_col = self.column_mapping.get("updated_at")
                    if updated_at_col is not None:
                        self.sheet.update_cell(
                            row_number,
                            updated_at_col + 1,
                            self._get_timestamp()
                        )

                    logger.info(f"Updated {field_name}={value} for {char_name}")
                    return True

            logger.warning(f"Character not found: {char_name} ({discord_id})")
            return False

        except Exception as e:
            logger.error(f"Error updating field: {e}")
            return False
