"""
Google Sheets Service
Store call data in Google Sheets
"""
import logging
from typing import Optional, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.config import get_settings
from app.models import CallData

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Google Sheets integration"""
    
    def __init__(self):
        settings = get_settings()
        self.sheet_id = settings.google_sheet_id
        self.service = None
        
        if settings.google_service_account_file:
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    settings.google_service_account_file,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                
                self.service = build('sheets', 'v4', credentials=credentials)
                logger.info("Google Sheets service initialized")
            
            except Exception as e:
                logger.error(f"Error initializing Google Sheets: {str(e)}")
    
    async def append_call(self, call_data: CallData) -> Optional[int]:
        """
        Append call to Google Sheets
        
        Args:
            call_data: Call data to append
        
        Returns:
            Row number or None
        """
        if not self.service or not self.sheet_id:
            logger.warning("Google Sheets not configured")
            return None
        
        try:
            # Build row data
            row = [
                call_data.call_id,
                call_data.started_at.isoformat(),
                call_data.ended_at.isoformat() if call_data.ended_at else "",
                str(call_data.duration_seconds or 0),
                call_data.caller_phone,
                call_data.caller_name or "",
                call_data.caller_email or "",
                call_data.company_name or "",
                call_data.call_purpose or "",
                call_data.call_sentiment.value,
                call_data.call_urgency.value,
                call_data.status.value,
                "Ja" if call_data.should_book_meeting else "Nein",
                "Ja" if call_data.meeting_booked else "Nein",
                call_data.meeting_url or "",
                call_data.summary or "",
                call_data.transcript or ""
            ]
            
            # Append to sheet
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range='Calls!A:Q',
                valueInputOption='RAW',
                body={'values': [row]}
            ).execute()
            
            # Get row number
            updates = result.get('updates', {})
            updated_range = updates.get('updatedRange', '')
            
            if updated_range:
                row_number = int(updated_range.split('!')[1].split(':')[0][1:])
                logger.info(f"Appended call to Google Sheets row: {row_number}")
                return row_number
            
            return None
        
        except Exception as e:
            logger.error(f"Error appending to Google Sheets: {str(e)}")
            return None
    
    async def create_sheet_if_not_exists(self):
        """Create Calls sheet with headers if it doesn't exist"""
        if not self.service or not self.sheet_id:
            return
        
        try:
            # Check if Calls sheet exists
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            sheets = spreadsheet.get('sheets', [])
            calls_sheet_exists = any(
                sheet['properties']['title'] == 'Calls' 
                for sheet in sheets
            )
            
            if not calls_sheet_exists:
                # Create Calls sheet
                requests = [{
                    'addSheet': {
                        'properties': {
                            'title': 'Calls'
                        }
                    }
                }]
                
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.sheet_id,
                    body={'requests': requests}
                ).execute()
                
                # Add headers
                headers = [[
                    'call_id', 'started_at', 'ended_at', 'duration_seconds',
                    'caller_phone', 'caller_name', 'caller_email', 'company_name',
                    'call_purpose', 'sentiment', 'urgency', 'status',
                    'should_book_meeting', 'meeting_booked', 'meeting_url',
                    'summary', 'transcript'
                ]]
                
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.sheet_id,
                    range='Calls!A1:Q1',
                    valueInputOption='RAW',
                    body={'values': headers}
                ).execute()
                
                logger.info("Created Calls sheet with headers")
        
        except Exception as e:
            logger.error(f"Error creating sheet: {str(e)}")
