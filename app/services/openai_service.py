"""
OpenAI Service
Conversation logic and AI processing
"""
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.config import get_settings
from app.models import ConversationMessage

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI service for conversation handling"""
    
    def __init__(self):
        settings = get_settings()
        # Don't store OpenAI client - create fresh for each call
        self.model = settings.openai_model
        self.brand_name = settings.brand_name
        self.company_description = settings.company_description
    
    def _build_system_prompt(self, knowledge_context: Optional[str] = None) -> str:
        """Build system prompt with company knowledge"""
        
        base_prompt = f"""Du bist ein professioneller Telefon-Agent für {self.brand_name}.

ÜBER UNS:
{self.company_description}

DEINE ROLLE:
- Freundlich, professionell und hilfsbereit
- Sprichst Schweizerdeutsch (Sie-Form)
- Beantwortest Fragen zu unseren Produkten und Services
- Buchst Termine wenn gewünscht
- Nimmst Kontaktdaten auf

WICHTIGE REGELN:
1. Sei kurz und präzise (max 2-3 Sätze pro Antwort)
2. Stelle gezielte Fragen um zu helfen
3. Wenn du etwas nicht weisst, sage es ehrlich
4. Biete immer einen Termin mit einem Experten an
5. Sei empathisch und geduldig

GESPRÄCHSFÜHRUNG:
- Begrüsse freundlich: "Grüezi, hier ist [Name] von {self.brand_name}"
- Frage nach dem Anliegen
- Höre aktiv zu
- Biete Lösungen an
- Schliesse mit nächsten Schritten ab"""

        if knowledge_context:
            base_prompt += f"\n\nRELEVANTE INFORMATIONEN:\n{knowledge_context}"
        
        return base_prompt
    
    async def generate_response(
        self,
        conversation_history: List[ConversationMessage],
        knowledge_context: Optional[str] = None
    ) -> str:
        """
        Generate AI response based on conversation
        
        Args:
            conversation_history: List of previous messages
            knowledge_context: Relevant knowledge from Qdrant
        
        Returns:
            AI generated response
        """
        try:
            # Build messages
            messages = [
                {"role": "system", "content": self._build_system_prompt(knowledge_context)}
            ]
            
            # Add conversation history
            for msg in conversation_history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Generate response
            settings = get_settings()
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150  # Keep responses short
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "Entschuldigung, ich hatte ein technisches Problem. Können Sie das bitte wiederholen?"
    
    async def extract_call_info(
        self,
        conversation_history: List[ConversationMessage]
    ) -> Dict[str, Any]:
        """
        Extract structured information from conversation
        
        Returns:
            Dict with: caller_name, company_name, call_purpose, 
                      should_book_meeting, call_sentiment, call_urgency
        """
        try:
            # Build conversation text
            conversation_text = "\n".join([
                f"{msg.role}: {msg.content}"
                for msg in conversation_history
            ])
            
            extraction_prompt = f"""Analysiere dieses Telefongespräch und extrahiere folgende Informationen im JSON Format:

Gespräch:
{conversation_text}

Extrahiere:
1. caller_name (Name des Anrufers, falls erwähnt)
2. company_name (Firmenname, falls erwähnt)
3. call_purpose (Zweck des Anrufs in 1-2 Sätzen)
4. should_book_meeting (true/false - will der Kunde einen Termin?)
5. call_sentiment (positive/neutral/negative)
6. call_urgency (low/medium/high/urgent)
7. preferred_time (Wunschtermin, falls erwähnt)

Antworte NUR mit JSON, keine Erklärungen."""

            settings = get_settings()
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Du bist ein Datenextraktions-Assistent. Antworte nur mit JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            logger.error(f"Error extracting call info: {str(e)}")
            return {
                "caller_name": None,
                "company_name": None,
                "call_purpose": "Unbekannt",
                "should_book_meeting": False,
                "call_sentiment": "neutral",
                "call_urgency": "medium",
                "preferred_time": None
            }
    
    async def generate_call_summary(
        self,
        conversation_history: List[ConversationMessage]
    ) -> str:
        """Generate concise call summary"""
        try:
            conversation_text = "\n".join([
                f"{msg.role}: {msg.content}"
                for msg in conversation_history
            ])
            
            settings = get_settings()
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Erstelle eine prägnante Zusammenfassung (max 3 Sätze) des Telefongesprächs."},
                    {"role": "user", "content": conversation_text}
                ],
                temperature=0.5,
                max_tokens=100
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Zusammenfassung konnte nicht erstellt werden."
