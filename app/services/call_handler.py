"""
Call Handler
Orchestrates all services for phone call processing
"""
import logging
from typing import Optional
from datetime import datetime
from app.models import CallData, CallStatus, ConversationMessage
from app.services.elevenlabs_service import ElevenLabsService
from app.services.openai_service import OpenAIService
from app.services.qdrant_service import QdrantService
from app.services.redis_service import RedisService
from app.services.hubspot_service import HubSpotService
from app.services.sheets_service import GoogleSheetsService

logger = logging.getLogger(__name__)


class CallHandler:
    """Orchestrates phone call processing"""
    
    def __init__(
        self,
        elevenlabs_service: ElevenLabsService,
        openai_service: OpenAIService,
        qdrant_service: QdrantService,
        redis_service: RedisService,
        hubspot_service: Optional[HubSpotService] = None,
        sheets_service: Optional[GoogleSheetsService] = None
    ):
        self.elevenlabs = elevenlabs_service
        self.openai = openai_service
        self.qdrant = qdrant_service
        self.redis = redis_service
        self.hubspot = hubspot_service
        self.sheets = sheets_service
    
    async def start_call(self, caller_phone: str) -> CallData:
        """
        Start new phone call
        
        Args:
            caller_phone: Caller phone number
        
        Returns:
            CallData object
        """
        try:
            # Create ElevenLabs conversation
            session_id = await self.elevenlabs.create_conversation(caller_phone)
            
            # Create call data
            call_data = CallData(
                call_id=f"call_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                session_id=session_id,
                caller_phone=caller_phone,
                status=CallStatus.INITIATED
            )
            
            # Store in Redis
            await self.redis.set_call_context(
                call_data.call_id,
                call_data.model_dump()
            )
            
            logger.info(f"Started call: {call_data.call_id}")
            return call_data
        
        except Exception as e:
            logger.error(f"Error starting call: {str(e)}")
            raise
    
    async def process_user_message(
        self,
        call_id: str,
        user_message: str
    ) -> str:
        """
        Process user message and generate AI response
        
        Args:
            call_id: Call identifier
            user_message: User's spoken message
        
        Returns:
            AI response
        """
        try:
            # Get call context
            context = await self.redis.get_call_context(call_id)
            
            if not context:
                return "Entschuldigung, ich konnte Ihren Anruf nicht finden."
            
            # Add user message to conversation
            await self.redis.append_to_conversation(
                call_id,
                "user",
                user_message
            )
            
            # Search knowledge base
            knowledge_results = await self.qdrant.search_knowledge(
                query=user_message,
                limit=3
            )
            
            # Build knowledge context
            knowledge_context = "\n\n".join([
                f"- {result.content}"
                for result in knowledge_results
            ])
            
            # Get conversation history
            updated_context = await self.redis.get_call_context(call_id)
            conversation = [
                ConversationMessage(**msg)
                for msg in updated_context.get("conversation", [])
            ]
            
            # Generate AI response
            ai_response = await self.openai.generate_response(
                conversation_history=conversation,
                knowledge_context=knowledge_context if knowledge_context else None
            )
            
            # Add AI response to conversation
            await self.redis.append_to_conversation(
                call_id,
                "assistant",
                ai_response
            )
            
            logger.info(f"Processed message for call: {call_id}")
            return ai_response
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "Entschuldigung, ich hatte ein technisches Problem. Können Sie das bitte wiederholen?"
    
    async def end_call(self, call_id: str) -> CallData:
        """
        End call and process final data
        
        Args:
            call_id: Call identifier
        
        Returns:
            Final CallData
        """
        try:
            # Get call context
            context = await self.redis.get_call_context(call_id)
            
            if not context:
                raise ValueError(f"Call not found: {call_id}")
            
            # Build conversation history
            conversation = [
                ConversationMessage(**msg)
                for msg in context.get("conversation", [])
            ]
            
            # Extract call information
            call_info = await self.openai.extract_call_info(conversation)
            
            # Generate summary
            summary = await self.openai.generate_call_summary(conversation)
            
            # Build transcript
            transcript = "\n\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in context.get("conversation", [])
            ])
            
            # Update call data
            call_data = CallData(**context)
            call_data.status = CallStatus.COMPLETED
            call_data.ended_at = datetime.utcnow()
            call_data.duration_seconds = int(
                (call_data.ended_at - call_data.started_at).total_seconds()
            )
            call_data.conversation = conversation
            call_data.transcript = transcript
            call_data.summary = summary
            
            # Update with extracted info
            call_data.caller_name = call_info.get("caller_name")
            call_data.company_name = call_info.get("company_name")
            call_data.call_purpose = call_info.get("call_purpose")
            call_data.should_book_meeting = call_info.get("should_book_meeting", False)
            call_data.call_sentiment = call_info.get("call_sentiment", "neutral")
            call_data.call_urgency = call_info.get("call_urgency", "medium")
            call_data.preferred_time = call_info.get("preferred_time")
            
            # Save to HubSpot
            if self.hubspot:
                contact_id = await self.hubspot.create_or_update_contact(call_data)
                if contact_id:
                    call_data.hubspot_contact_id = contact_id
                    await self.hubspot.create_note(contact_id, call_data)
                    
                    # Create task if meeting requested
                    if call_data.should_book_meeting:
                        await self.hubspot.create_task(
                            contact_id,
                            "Follow-up: Meeting buchen",
                            f"Kunde möchte Meeting buchen.\nBevorzugte Zeit: {call_data.preferred_time or 'Nicht angegeben'}"
                        )
            
            # Save to Google Sheets
            if self.sheets:
                row_number = await self.sheets.append_call(call_data)
                if row_number:
                    call_data.sheet_row = row_number
            
            # Update Redis
            await self.redis.set_call_context(
                call_id,
                call_data.model_dump()
            )
            
            logger.info(f"Ended call: {call_id}")
            return call_data
        
        except Exception as e:
            logger.error(f"Error ending call: {str(e)}")
            raise
