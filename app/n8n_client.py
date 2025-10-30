import httpx
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class N8NClient:
    """Client for n8n webhook communication"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.timeout = 30.0
    
    async def send_call_data(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send call data to n8n webhook
        
        Args:
            call_data: Call data dictionary
            
        Returns:
            n8n response dictionary
            
        Raises:
            httpx.HTTPError: If request fails
        """
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Sending call data to n8n: {call_data.get('call_id')}")
                
                response = await client.post(
                    self.webhook_url,
                    json=call_data,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                
                logger.info(f"n8n response: {response.status_code}")
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"n8n webhook error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending to n8n: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if n8n webhook is reachable
        
        Returns:
            True if n8n is reachable, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                # Try to reach n8n (without sending data)
                response = await client.get(
                    self.webhook_url.replace('/webhook/', '/healthz'),
                    timeout=5.0
                )
                return response.status_code == 200
        except:
            return False
