"""
HubSpot CRM Service
Direct CRM integration for phone calls
"""
import logging
from typing import Optional, Dict, Any
import httpx
from app.config import get_settings
from app.models import CallData

logger = logging.getLogger(__name__)


class HubSpotService:
    """HubSpot CRM integration"""
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.hubspot_api_key
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_or_update_contact(
        self,
        call_data: CallData
    ) -> Optional[str]:
        """
        Create or update HubSpot contact
        
        Args:
            call_data: Call data with contact info
        
        Returns:
            Contact ID or None
        """
        if not self.api_key:
            logger.warning("HubSpot not configured")
            return None
        
        try:
            # Build contact properties
            properties = {
                "phone": call_data.caller_phone,
            }
            
            if call_data.caller_name:
                name_parts = call_data.caller_name.split(" ", 1)
                properties["firstname"] = name_parts[0]
                if len(name_parts) > 1:
                    properties["lastname"] = name_parts[1]
            
            if call_data.caller_email:
                properties["email"] = call_data.caller_email
            
            if call_data.company_name:
                properties["company"] = call_data.company_name
            
            # Search for existing contact by phone
            async with httpx.AsyncClient() as client:
                search_response = await client.post(
                    f"{self.base_url}/crm/v3/objects/contacts/search",
                    headers=self.headers,
                    json={
                        "filterGroups": [{
                            "filters": [{
                                "propertyName": "phone",
                                "operator": "EQ",
                                "value": call_data.caller_phone
                            }]
                        }]
                    },
                    timeout=10.0
                )
                
                if search_response.status_code == 200:
                    results = search_response.json().get("results", [])
                    
                    if results:
                        # Update existing contact
                        contact_id = results[0]["id"]
                        
                        update_response = await client.patch(
                            f"{self.base_url}/crm/v3/objects/contacts/{contact_id}",
                            headers=self.headers,
                            json={"properties": properties},
                            timeout=10.0
                        )
                        
                        if update_response.status_code == 200:
                            logger.info(f"Updated HubSpot contact: {contact_id}")
                            return contact_id
                    
                    else:
                        # Create new contact
                        create_response = await client.post(
                            f"{self.base_url}/crm/v3/objects/contacts",
                            headers=self.headers,
                            json={"properties": properties},
                            timeout=10.0
                        )
                        
                        if create_response.status_code == 201:
                            contact_id = create_response.json()["id"]
                            logger.info(f"Created HubSpot contact: {contact_id}")
                            return contact_id
            
            return None
        
        except Exception as e:
            logger.error(f"Error with HubSpot contact: {str(e)}")
            return None
    
    async def create_note(
        self,
        contact_id: str,
        call_data: CallData
    ) -> bool:
        """Create note on contact with call details"""
        if not self.api_key:
            return False
        
        try:
            # Build note content
            note_content = f"""Telefonanruf vom {call_data.started_at.strftime('%d.%m.%Y %H:%M')}

Dauer: {call_data.duration_seconds}s
Status: {call_data.status.value}
Stimmung: {call_data.call_sentiment.value}
Dringlichkeit: {call_data.call_urgency.value}

Zweck: {call_data.call_purpose or 'Nicht angegeben'}

Zusammenfassung:
{call_data.summary or 'Keine Zusammenfassung verfügbar'}

Transkript:
{call_data.transcript or 'Kein Transkript verfügbar'}
"""
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/crm/v3/objects/notes",
                    headers=self.headers,
                    json={
                        "properties": {
                            "hs_note_body": note_content,
                            "hs_timestamp": call_data.started_at.isoformat()
                        },
                        "associations": [{
                            "to": {"id": contact_id},
                            "types": [{
                                "associationCategory": "HUBSPOT_DEFINED",
                                "associationTypeId": 202  # Note to Contact
                            }]
                        }]
                    },
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    logger.info(f"Created HubSpot note for contact: {contact_id}")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error creating HubSpot note: {str(e)}")
            return False
    
    async def create_task(
        self,
        contact_id: str,
        task_title: str,
        task_body: str
    ) -> bool:
        """Create follow-up task"""
        if not self.api_key:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/crm/v3/objects/tasks",
                    headers=self.headers,
                    json={
                        "properties": {
                            "hs_task_subject": task_title,
                            "hs_task_body": task_body,
                            "hs_task_status": "NOT_STARTED",
                            "hs_task_priority": "HIGH"
                        },
                        "associations": [{
                            "to": {"id": contact_id},
                            "types": [{
                                "associationCategory": "HUBSPOT_DEFINED",
                                "associationTypeId": 204  # Task to Contact
                            }]
                        }]
                    },
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    logger.info(f"Created HubSpot task for contact: {contact_id}")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error creating HubSpot task: {str(e)}")
            return False
