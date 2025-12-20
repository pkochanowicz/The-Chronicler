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
from domain.talent_data import TALENT_DATA # Import the mutable TALENT_DATA dict


logger = logging.getLogger(__name__)

# Scopes required for Google Sheets API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Character Sheet specific constants
CHARACTER_SHEET_NAME = "Character_Submissions"
CHARACTER_SCHEMA_COLUMNS = [
    "timestamp", "discord_id", "discord_name", "char_name", "race", "class", 
    "roles", "professions", "backstory", "personality", "quotes", "portrait_url", 
    "trait_1", "trait_2", "trait_3", "status", "confirmation", "request_sdxl", 
    "recruitment_msg_id", "forum_post_url", "reviewed_by", "embed_json", 
    "death_cause", "death_story", "created_at", "updated_at", "notes",
    "talents"
]
CHARACTER_FIELD_MAPPING = {
    "timestamp": "timestamp", "discord_id": "discord_id", "discord_name": "discord_name",
    "char_name": "char_name", "name": "char_name", "race": "race", "class": "class",
    "char_class": "class", "roles": "roles", "professions": "professions",
    "backstory": "backstory", "personality": "personality", "quotes": "quotes",
    "portrait_url": "portrait_url", "trait_1": "trait_1", "trait_2": "trait_2",
    "trait_3": "trait_3", "status": "status", "confirmation": "confirmation",
    "request_sdxl": "request_sdxl", "recruitment_msg_id": "recruitment_msg_id",
    "forum_post_url": "forum_post_url", "reviewed_by": "reviewed_by",
    "embed_json": "embed_json", "death_cause": "death_cause", "death_story": "death_story",
    "created_at": "created_at", "updated_at": "updated_at", "notes": "notes",
    "talents": "talents"
}

# Talent Library Sheet specific constants
TALENT_LIBRARY_SHEET_NAME = "Talent_Library"
TALENT_LIBRARY_SCHEMA_COLUMNS = [
    "Class", "Tree", "TalentName", "MaxRank", "Level", "Tier",
    "Requires", "RequiredBy" # Requires and RequiredBy will be JSON strings
]


class GoogleSheetsService: # Renamed class
    """
    Service for interacting with various Google Sheets within the workbook.
    Manages connections and provides methods for sheet-specific operations.
    """
    
    def __init__(self):
        self.client = None
        self.workbook = None
        self.character_sheet_instance = None # Renamed for clarity
        self.talent_library_sheet_instance = None
        self.character_column_mapping = {}
        self.talent_library_column_mapping = {}
        
        self._connect_to_workbook()
        self._initialize_sheets()
        self.load_talent_data() # Load talent data into domain/talent_data.py

    def _connect_to_workbook(self):
        """Establish connection to Google Sheets workbook."""
        try:
            creds = Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
            )
            self.client = gspread.authorize(creds)
            self.workbook = self.client.open_by_key(settings.GOOGLE_SHEET_ID)
            logger.info("Successfully connected to Google Sheets workbook.")
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets workbook: {e}")
            raise

    def _initialize_sheets(self):
        """Initialize and validate schemas for all managed sheets."""
        # Initialize Character_Submissions sheet
        self.character_sheet_instance = self._get_or_create_sheet(
            CHARACTER_SHEET_NAME, CHARACTER_SCHEMA_COLUMNS
        )
        self.character_column_mapping = self._build_column_mapping(self.character_sheet_instance)
        self._validate_schema(self.character_sheet_instance, CHARACTER_SCHEMA_COLUMNS)

        # Initialize Talent_Library sheet
        self.talent_library_sheet_instance = self._get_or_create_sheet(
            TALENT_LIBRARY_SHEET_NAME, TALENT_LIBRARY_SCHEMA_COLUMNS
        )
        self.talent_library_column_mapping = self._build_column_mapping(self.talent_library_sheet_instance)
        self._validate_schema(self.talent_library_sheet_instance, TALENT_LIBRARY_SCHEMA_COLUMNS)


    def _get_or_create_sheet(self, sheet_name: str, schema_columns: List[str]):
        """
        Retrieves a worksheet by name, creating it if it doesn't exist.
        Ensures the header row matches the schema_columns.
        """
        try:
            worksheet = self.workbook.worksheet(sheet_name)
            logger.info(f"Worksheet '{sheet_name}' found.")
        except gspread.exceptions.WorksheetNotFound:
            logger.warning(f"Worksheet '{sheet_name}' not found. Creating it with schema.")
            worksheet = self.workbook.add_worksheet(title=sheet_name, rows="100", cols=str(len(schema_columns)))
            worksheet.append_row(schema_columns)
            logger.info(f"Worksheet '{sheet_name}' created and headers set.")
        return worksheet

    def _build_column_mapping(self, worksheet) -> Dict[str, int]:
        """Builds a column name to index mapping for a given worksheet."""
        headers = worksheet.row_values(1)
        if not headers:
            raise ValueError(f"Worksheet '{worksheet.title}' has no header row.")
        return {name.strip(): i for i, name in enumerate(headers)}

    def _validate_schema(self, worksheet, expected_schema_columns: List[str]):
        """Validates that a worksheet's header matches the expected schema."""
        current_headers = [h.strip() for h in worksheet.row_values(1)]
        if current_headers != expected_schema_columns:
            raise ValueError(
                f"Schema mismatch for worksheet '{worksheet.title}'. "
                f"Expected: {expected_schema_columns}, Got: {current_headers}"
            )
        logger.info(f"Schema validation successful for worksheet '{worksheet.title}'.")


    def load_talent_data(self):
        """
        Loads talent data from the Talent_Library sheet into domain/talent_data.py's TALENT_DATA.
        """
        logger.info("Loading talent data from Talent_Library sheet...")
        try:
            records = self.talent_library_sheet_instance.get_all_records()
            TALENT_DATA.clear() # Clear existing static data
            
            for record in records:
                char_class = record.get("Class")
                tree = record.get("Tree")
                talent_name = record.get("TalentName")

                if not all([char_class, tree, talent_name]):
                    logger.warning(f"Skipping malformed talent record: {record}")
                    continue

                if char_class not in TALENT_DATA:
                    TALENT_DATA[char_class] = {}
                if tree not in TALENT_DATA[char_class]:
                    TALENT_DATA[char_class][tree] = {}
                
                # Deserialize JSON fields
                requires_json = record.get("Requires", "[]")
                required_by_json = record.get("RequiredBy", "[]")
                
                try:
                    requires = json.loads(requires_json)
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode 'Requires' for {talent_name}: {requires_json}. Defaulting to empty list.")
                    requires = []
                
                try:
                    required_by = json.loads(required_by_json)
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode 'RequiredBy' for {talent_name}: {required_by_json}. Defaulting to empty list.")
                    required_by = []

                TALENT_DATA[char_class][tree][talent_name] = {
                    "level": int(record.get("Level", 10)),
                    "max_rank": int(record.get("MaxRank", 1)),
                    "tier": int(record.get("Tier", 1)),
                    "requires": requires,
                    "required_by": required_by,
                }
            logger.info(f"Successfully loaded {len(records)} talents from Talent_Library.")
        except Exception as e:
            logger.error(f"Failed to load talent data from Talent_Library sheet: {e}")
            raise

    def _get_timestamp(self) -> str:
        """Generate consistent ISO 8601 timestamp (UTC, no microseconds)."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def log_character(self, character_data: Dict[str, Any]) -> bool:
        """
        Log a new character to the sheet (Character_Submissions).
        Expects a dictionary with keys matching the columns (or aliases).
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
            # Prepare row for Character_Submissions
            row = [""] * len(CHARACTER_SCHEMA_COLUMNS) 
            
            # Use max index from mapping to determine row size (should be len(SCHEMA_COLUMNS))
            max_idx = max(self.character_column_mapping.values())
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
                col_name = CHARACTER_FIELD_MAPPING.get(key)
                if col_name and col_name in self.character_column_mapping:
                    idx = self.character_column_mapping[col_name]
                    # Handle boolean conversion
                    if isinstance(value, bool):
                        value = "TRUE" if value else "FALSE"
                    # Handle talents conversion to JSON string
                    if key == "talents" and value is not None:
                        value = json.dumps(value) # Convert dict to JSON string
                    row[idx] = str(value) if value is not None else ""
            
            self.character_sheet_instance.append_row(row)
            logger.info(f"Logged character: {character_data.get('char_name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging character: {e}")
            return False

    def update_character_status(self, char_name: str, new_status: str, **kwargs) -> bool:
        """
        Update status and optional fields for a character (Character_Submissions).
        """
        try:
            # Find the row (search in char_name column)
            name_col_idx = self.character_column_mapping.get("char_name")
            if name_col_idx is None:
                raise ValueError("Column 'char_name' not found in Character_Submissions")
                
            cell = self.character_sheet_instance.find(char_name, in_column=name_col_idx + 1) # gspread is 1-based
            
            if not cell:
                logger.warning(f"Character '{char_name}' not found in Character_Submissions.")
                return False
                
            row_num = cell.row
            
            # Update status
            status_col_idx = self.character_column_mapping.get("status")
            if status_col_idx is not None:
                self.character_sheet_instance.update_cell(row_num, status_col_idx + 1, new_status)

            # Update additional fields
            kwargs["updated_at"] = self._get_timestamp()
            
            for key, value in kwargs.items():
                col_name = CHARACTER_FIELD_MAPPING.get(key, key) # Fallback to key itself
                if col_name in self.character_column_mapping:
                    col_idx = self.character_column_mapping[col_name]
                    if isinstance(value, bool):
                        value = "TRUE" if value else "FALSE"
                    self.character_sheet_instance.update_cell(row_num, col_idx + 1, str(value))
            
            logger.info(f"Updated status for {char_name} to {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating character {char_name}: {e}")
            return False

    def _process_character_record(self, record: Dict[str, str]) -> Dict[str, Any]: # Renamed helper
        """Processes a single character record from the sheet, deserializing JSON fields."""
        if "talents" in record and record["talents"]:
            try:
                record["talents"] = json.loads(record["talents"])
            except json.JSONDecodeError:
                logger.warning(f"Failed to decode talents for character {record.get('char_name')}. Defaulting to empty dict.")
                record["talents"] = {} 
        else:
            record["talents"] = {} 
        return record

    def get_character_by_name(self, char_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve character data by name (Character_Submissions)."""
        try:
            records = self.character_sheet_instance.get_all_records()
            for record in records:
                if record.get("char_name") == char_name:
                    return self._process_character_record(record) 
            return None
        except Exception as e:
            logger.error(f"Error getting character {char_name}: {e}")
            return None

    def get_characters_by_user(self, discord_id: str) -> List[Dict[str, Any]]:
        """Retrieve all characters for a Discord user (Character_Submissions)."""
        try:
            records = self.character_sheet_instance.get_all_records()
            processed_records = [self._process_character_record(r) for r in records if str(r.get("discord_id")) == str(discord_id)]
            return processed_records
        except Exception as e:
            logger.error(f"Error getting characters for user {discord_id}: {e}")
            return []

    def get_all_characters(self) -> List[Dict[str, Any]]:
        """Retrieve all characters from the sheet (Character_Submissions)."""
        try:
            records = self.character_sheet_instance.get_all_records()
            processed_records = [self._process_character_record(r) for r in records]
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
        Update a single field for a specific character (Character_Submissions).
        """
        try:
            # Find the character's row
            all_records = self.character_sheet_instance.get_all_records()

            for idx, record in enumerate(all_records):
                if (record.get('char_name') == char_name and
                    str(record.get('discord_id')) == str(discord_id)):

                    # Row number (idx + 2 because: 1=header, idx is 0-based)
                    row_number = idx + 2

                    # Get column index for the field
                    col_name = CHARACTER_FIELD_MAPPING.get(field_name, field_name)
                    if col_name not in self.character_column_mapping:
                        logger.error(f"Field '{field_name}' not in schema")
                        return False

                    col_index = self.character_column_mapping[col_name] + 1  # +1 for 1-based

                    # Convert boolean values
                    if isinstance(value, bool):
                        value = "TRUE" if value else "FALSE"
                    # Convert talents to JSON string
                    if field_name == "talents" and value is not None:
                        value = json.dumps(value)

                    # Update the cell
                    self.character_sheet_instance.update_cell(row_num, col_index, str(value))

                    # Update updated_at timestamp
                    updated_at_col = self.character_column_mapping.get("updated_at")
                    if updated_at_col is not None:
                        self.character_sheet_instance.update_cell(
                            row_num,
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

    def log_talent(self, talent_data: Dict[str, Any]) -> bool:
        """Logs a new talent to the Talent_Library sheet."""
        try:
            # Prepare row for Talent_Library
            row = [""] * len(TALENT_LIBRARY_SCHEMA_COLUMNS)
            
            talent_column_mapping = self._build_column_mapping(self.talent_library_sheet_instance)

            # Populate row using talent_column_mapping
            for key, value in talent_data.items():
                col_name = key # Keys in talent_data should match schema
                if col_name in talent_column_mapping:
                    idx = talent_column_mapping[col_name]
                    # Handle JSON serialization for 'Requires' and 'RequiredBy'
                    if key in ["Requires", "RequiredBy"] and value is not None:
                        value = json.dumps(value)
                    row[idx] = str(value) if value is not None else ""
            
            self.talent_library_sheet_instance.append_row(row)
            logger.info(f"Logged talent: {talent_data.get('TalentName', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Error logging talent: {e}")
            return False

# Initialize the service globally
google_sheets_service = GoogleSheetsService()