"""
ElevenLabs Conversational AI Service
WebSocket-based real-time voice conversation
"""
import logging
import asyncio
import json
from typing import Optional, Callable
import websockets
from elevenlabs import ElevenLabs
from app.config import get_settings

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """ElevenLabs Conversational AI service"""
    
    def __init__(self):
        settings = get_settings()
        self.client = ElevenLabs(api_key=settings.elevenlabs_api_key)
        self.agent_id = settings.elevenlabs_agent_id
        self.api_key = settings.elevenlabs_api_key
    
    async def create_conversation(
        self,
        phone_number: str,
        on_message: Optional[Callable] = None,
        on_end: Optional[Callable] = None
    ) -> str:
        """
        Create new conversation session
        
        Args:
            phone_number: Caller phone number
            on_message: Callback for incoming messages
            on_end: Callback when conversation ends
        
        Returns:
            Session ID
        """
        try:
            # Create conversation via API
            response = self.client.conversational_ai.create_conversation(
                agent_id=self.agent_id,
                metadata={
                    "phone_number": phone_number
                }
            )
            
            session_id = response.conversation_id
            logger.info(f"Created ElevenLabs conversation: {session_id}")
            
            return session_id
        
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise
    
    async def connect_websocket(
        self,
        session_id: str,
        on_message: Callable,
        on_transcript: Callable,
        on_end: Callable
    ):
        """
        Connect to ElevenLabs WebSocket for real-time conversation
        
        Args:
            session_id: Conversation session ID
            on_message: Callback for AI messages
            on_transcript: Callback for user transcripts
            on_end: Callback when conversation ends
        """
        try:
            # WebSocket URL
            ws_url = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={self.agent_id}"
            
            async with websockets.connect(
                ws_url,
                extra_headers={
                    "xi-api-key": self.api_key
                }
            ) as websocket:
                logger.info(f"Connected to ElevenLabs WebSocket: {session_id}")
                
                # Listen for messages
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        event_type = data.get("type")
                        
                        if event_type == "agent_response":
                            # AI response
                            text = data.get("text", "")
                            await on_message(text)
                        
                        elif event_type == "user_transcript":
                            # User speech transcript
                            text = data.get("text", "")
                            await on_transcript(text)
                        
                        elif event_type == "conversation_end":
                            # Conversation ended
                            await on_end(data)
                            break
                    
                    except json.JSONDecodeError:
                        logger.error("Invalid JSON from WebSocket")
                        continue
        
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            raise
    
    async def send_message(
        self,
        session_id: str,
        message: str
    ) -> bool:
        """
        Send message to conversation (for function calls, etc.)
        
        Args:
            session_id: Conversation session ID
            message: Message to send
        
        Returns:
            Success status
        """
        try:
            # Send via API
            self.client.conversational_ai.send_message(
                conversation_id=session_id,
                message=message
            )
            
            logger.info(f"Sent message to conversation: {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    async def end_conversation(self, session_id: str) -> bool:
        """End conversation"""
        try:
            self.client.conversational_ai.end_conversation(
                conversation_id=session_id
            )
            
            logger.info(f"Ended conversation: {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
            return False
    
    async def get_conversation_history(self, session_id: str) -> dict:
        """Get conversation history"""
        try:
            response = self.client.conversational_ai.get_conversation(
                conversation_id=session_id
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return {}
