# in services/bank_service.py
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
import gspread
from google.oauth2.service_account import Credentials
from config.settings import settings

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

class BankService:
    SHEET_NAME = "Bank"
    SCHEMA_COLUMNS = [
        "timestamp", "member", "transaction_type", "item", "quantity", "notes"
    ]

    def __init__(self):
        self.client = None
        self.sheet = None
        self._connect_to_sheet()
        self._validate_schema()

    def _connect_to_sheet(self):
        try:
            creds = Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
            )
            self.client = gspread.authorize(creds)
            workbook = self.client.open_by_key(settings.GOOGLE_SHEET_ID)
            self.sheet = workbook.worksheet(self.SHEET_NAME)
            logger.info(f"Successfully connected to Google Sheets (worksheet: {self.SHEET_NAME})")
        except gspread.exceptions.WorksheetNotFound:
            logger.warning(f"Worksheet '{self.SHEET_NAME}' not found. Creating it now.")
            self._create_sheet(workbook)
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise

    def _create_sheet(self, workbook):
        try:
            self.sheet = workbook.add_worksheet(title=self.SHEET_NAME, rows="100", cols="20")
            self.sheet.append_row(self.SCHEMA_COLUMNS)
            logger.info(f"Worksheet '{self.SHEET_NAME}' created successfully.")
        except Exception as e:
            logger.error(f"Failed to create worksheet '{self.SHEET_NAME}': {e}")
            raise

    def _validate_schema(self):
        try:
            headers = self.sheet.row_values(1)
            if not headers or headers != self.SCHEMA_COLUMNS:
                raise ValueError(f"Sheet '{self.SHEET_NAME}' has incorrect schema. Expected: {self.SCHEMA_COLUMNS}")
            logger.info("Bank schema validation successful")
        except Exception as e:
            logger.error(f"Bank schema validation failed: {e}")
            raise

    def _get_timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def log_transaction(self, member: str, transaction_type: str, item: str, quantity: int, notes: str = "") -> bool:
        try:
            timestamp = self._get_timestamp()
            row = [timestamp, member, transaction_type, item, quantity, notes]
            self.sheet.append_row(row)
            logger.info(f"Logged bank transaction: {member}, {transaction_type}, {quantity}x {item}")
            return True
        except Exception as e:
            logger.error(f"Error logging bank transaction: {e}")
            return False

    def get_all_transactions(self) -> List[Dict[str, Any]]:
        try:
            records = self.sheet.get_all_records()
            return records
        except Exception as e:
            logger.error(f"Error getting all bank transactions: {e}")
            return []
