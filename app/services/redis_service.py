"""
Redis Service
Session and context management for phone calls
"""
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime
import redis.asyncio as redis
from app.config import get_settings

logger = logging.getLogger(__name__)


class RedisService:
    """Redis service for session management"""
    
    def __init__(self):
        settings = get_settings()
        self.redis_client = redis.from_url(
            settings.redis_url,
            password=settings.redis_password,
            decode_responses=True
        )
        self.default_ttl = 3600  # 1 hour
    
    async def set_session(
        self,
        session_id: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store session data
        
        Args:
            session_id: Session identifier
            data: Session data dictionary
            ttl: Time to live in seconds
        
        Returns:
            Success status
        """
        try:
            key = f"session:{session_id}"
            value = json.dumps(data)
            
            await self.redis_client.set(
                key,
                value,
                ex=ttl or self.default_ttl
            )
            
            logger.info(f"Stored session: {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error storing session: {str(e)}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session data or None
        """
        try:
            key = f"session:{session_id}"
            value = await self.redis_client.get(key)
            
            if value:
                return json.loads(value)
            return None
        
        except Exception as e:
            logger.error(f"Error getting session: {str(e)}")
            return None
    
    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update session data
        
        Args:
            session_id: Session identifier
            updates: Data to update
        
        Returns:
            Success status
        """
        try:
            # Get existing session
            session = await self.get_session(session_id)
            
            if session:
                # Merge updates
                session.update(updates)
                
                # Store back
                return await self.set_session(session_id, session)
            
            return False
        
        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            key = f"session:{session_id}"
            await self.redis_client.delete(key)
            logger.info(f"Deleted session: {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            return False
    
    async def set_call_context(
        self,
        call_id: str,
        context: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Store call context"""
        try:
            key = f"call:{call_id}"
            value = json.dumps(context)
            
            await self.redis_client.set(
                key,
                value,
                ex=ttl or self.default_ttl
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Error storing call context: {str(e)}")
            return False
    
    async def get_call_context(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get call context"""
        try:
            key = f"call:{call_id}"
            value = await self.redis_client.get(key)
            
            if value:
                return json.loads(value)
            return None
        
        except Exception as e:
            logger.error(f"Error getting call context: {str(e)}")
            return None
    
    async def append_to_conversation(
        self,
        call_id: str,
        role: str,
        content: str
    ) -> bool:
        """Append message to conversation history"""
        try:
            context = await self.get_call_context(call_id) or {"conversation": []}
            
            context["conversation"].append({
                "role": role,
                "content": content,
                "timestamp": str(datetime.utcnow())
            })
            
            return await self.set_call_context(call_id, context)
        
        except Exception as e:
            logger.error(f"Error appending to conversation: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check Redis connection"""
        try:
            await self.redis_client.ping()
            return True
        except:
            return False
