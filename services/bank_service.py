# services/bank_service.py
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import uuid
from services.sheets_service import google_sheets_service

logger = logging.getLogger(__name__)

class GuildBankService:
    """
    Service for managing the Guild Bank using a one-member-to-many-items relationship.
    Schema: item_id, item_name, item_category, quantity, deposited_by, deposited_by_name,
            deposited_at, withdrawn_by, withdrawn_by_name, withdrawn_at, notes, status
    """
    SHEET_NAME = "Guild_Bank"
    SCHEMA_COLUMNS = [
        "item_id", "item_name", "item_category", "quantity",
        "deposited_by", "deposited_by_name", "deposited_at",
        "withdrawn_by", "withdrawn_by_name", "withdrawn_at",
        "notes", "status"
    ]
    
    # Column mapping for easier access
    COL_MAPPING = {col: i for i, col in enumerate(SCHEMA_COLUMNS)}

    def __init__(self):
        self.sheet = None
        # Lazy initialization: Do not initialize sheet here.

    def _initialize_sheet(self):
        """Initializes the bank sheet using GoogleSheetsService."""
        if self.sheet:
            return

        google_sheets_service._ensure_connected()
        self.sheet = google_sheets_service._get_or_create_sheet(
            self.SHEET_NAME, self.SCHEMA_COLUMNS
        )
        # Re-validate schema to be safe
        google_sheets_service._validate_schema(self.sheet, self.SCHEMA_COLUMNS)

    def _get_timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def deposit_item(self, item_name: str, quantity: int, depositor_id: str, depositor_name: str, category: str = "Other", notes: str = "") -> bool:
        """
        Deposits an item into the guild bank.
        Generates a unique item_id.
        """
        self._initialize_sheet()
        try:
            item_id = str(uuid.uuid4())
            timestamp = self._get_timestamp()
            
            row_data = {
                "item_id": item_id,
                "item_name": item_name,
                "item_category": category,
                "quantity": quantity,
                "deposited_by": str(depositor_id),
                "deposited_by_name": depositor_name,
                "deposited_at": timestamp,
                "withdrawn_by": "",
                "withdrawn_by_name": "",
                "withdrawn_at": "",
                "notes": notes,
                "status": "AVAILABLE"
            }
            
            # Convert dict to row list based on schema order
            row = [str(row_data.get(col, "")) for col in self.SCHEMA_COLUMNS]
            
            self.sheet.append_row(row)
            logger.info(f"Deposited: {quantity}x {item_name} by {depositor_name} (ID: {item_id})")
            return True
        except Exception as e:
            logger.error(f"Error depositing item: {e}")
            return False

    def withdraw_item(self, item_id: str, withdrawer_id: str, withdrawer_name: str) -> bool:
        """
        Withdraws an item (marks it as WITHDRAWN).
        """
        self._initialize_sheet()
        try:
            # Find the row with the item_id
            # Fetch all records is expensive but robust for finding by ID without knowing row num
            # Optimization: Use search? gspread find function.
            cell = self.sheet.find(item_id, in_column=self.COL_MAPPING["item_id"] + 1)
            
            if not cell:
                logger.warning(f"Item ID {item_id} not found for withdrawal.")
                return False
            
            row_num = cell.row
            
            # Update withdrawn fields
            timestamp = self._get_timestamp()
            
            updates = [
                (self.COL_MAPPING["withdrawn_by"], str(withdrawer_id)),
                (self.COL_MAPPING["withdrawn_by_name"], withdrawer_name),
                (self.COL_MAPPING["withdrawn_at"], timestamp),
                (self.COL_MAPPING["status"], "WITHDRAWN")
            ]
            
            # Batch update or individual cell updates? Individual is easier logic.
            for col_idx, val in updates:
                self.sheet.update_cell(row_num, col_idx + 1, val)
                
            logger.info(f"Withdrawn item {item_id} by {withdrawer_name}")
            return True

        except Exception as e:
            logger.error(f"Error withdrawing item {item_id}: {e}")
            return False

    def get_available_items(self) -> List[Dict[str, Any]]:
        """Returns all items with status 'AVAILABLE'."""
        self._initialize_sheet()
        try:
            all_records = self.sheet.get_all_records()
            return [item for item in all_records if item.get("status") == "AVAILABLE"]
        except Exception as e:
            logger.error(f"Error fetching available items: {e}")
            return []

    def get_member_deposits(self, discord_id: str) -> List[Dict[str, Any]]:
        """Returns items deposited by a specific member."""
        self._initialize_sheet()
        try:
            all_records = self.sheet.get_all_records()
            return [item for item in all_records if str(item.get("deposited_by")) == str(discord_id)]
        except Exception as e:
            logger.error(f"Error fetching deposits for {discord_id}: {e}")
            return []

    def get_member_withdrawals(self, discord_id: str) -> List[Dict[str, Any]]:
        """Returns items withdrawn by a specific member."""
        self._initialize_sheet()
        try:
            all_records = self.sheet.get_all_records()
            return [item for item in all_records if str(item.get("withdrawn_by")) == str(discord_id)]
        except Exception as e:
            logger.error(f"Error fetching withdrawals for {discord_id}: {e}")
            return []

# Global instance
guild_bank_service = GuildBankService()
