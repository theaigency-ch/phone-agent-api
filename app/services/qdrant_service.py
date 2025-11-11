"""
Qdrant Vector Database Service
Company Knowledge Base for Phone Agent
"""
import logging
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from openai import OpenAI
from app.models import CompanyKnowledge, KnowledgeSearchResult
from app.config import get_settings

logger = logging.getLogger(__name__)


class QdrantService:
    """Qdrant vector database service for company knowledge"""
    
    def __init__(self):
        settings = get_settings()
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        self.collection_name = settings.qdrant_collection
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        
        # Initialize collection
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection exists: {self.collection_name}")
        
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {str(e)}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            raise
    
    async def add_knowledge(self, knowledge: CompanyKnowledge) -> str:
        """
        Add knowledge entry to vector database
        
        Args:
            knowledge: CompanyKnowledge entry
        
        Returns:
            Entry ID
        """
        try:
            # Create searchable text
            searchable_text = f"{knowledge.title}\n\n{knowledge.content}"
            
            # Get embedding
            embedding = self._get_embedding(searchable_text)
            
            # Generate ID
            import uuid
            entry_id = knowledge.id or str(uuid.uuid4())
            
            # Create point
            point = PointStruct(
                id=entry_id,
                vector=embedding,
                payload={
                    "title": knowledge.title,
                    "content": knowledge.content,
                    "category": knowledge.category,
                    "tags": knowledge.tags,
                    "metadata": knowledge.metadata,
                    "created_at": knowledge.created_at.isoformat()
                }
            )
            
            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Added knowledge entry: {entry_id}")
            return entry_id
        
        except Exception as e:
            logger.error(f"Error adding knowledge: {str(e)}")
            raise
    
    async def search_knowledge(
        self,
        query: str,
        limit: int = 5,
        category: Optional[str] = None,
        score_threshold: float = 0.7
    ) -> List[KnowledgeSearchResult]:
        """
        Search knowledge base
        
        Args:
            query: Search query
            limit: Max results
            category: Filter by category
            score_threshold: Minimum similarity score
        
        Returns:
            List of search results
        """
        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            
            # Build filter
            query_filter = None
            if category:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="category",
                            match=MatchValue(value=category)
                        )
                    ]
                )
            
            # Search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=query_filter,
                score_threshold=score_threshold
            )
            
            # Convert to KnowledgeSearchResult
            results = []
            for hit in search_results:
                results.append(KnowledgeSearchResult(
                    content=hit.payload.get("content", ""),
                    score=hit.score,
                    metadata={
                        "title": hit.payload.get("title", ""),
                        "category": hit.payload.get("category", ""),
                        "tags": hit.payload.get("tags", [])
                    }
                ))
            
            logger.info(f"Found {len(results)} knowledge entries for query: {query}")
            return results
        
        except Exception as e:
            logger.error(f"Error searching knowledge: {str(e)}")
            return []
    
    async def get_all_knowledge(self, category: Optional[str] = None) -> List[CompanyKnowledge]:
        """Get all knowledge entries"""
        try:
            # Build filter
            query_filter = None
            if category:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="category",
                            match=MatchValue(value=category)
                        )
                    ]
                )
            
            # Scroll through all points
            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=100
            )
            
            # Convert to CompanyKnowledge
            results = []
            for point in points:
                results.append(CompanyKnowledge(
                    id=str(point.id),
                    title=point.payload.get("title", ""),
                    content=point.payload.get("content", ""),
                    category=point.payload.get("category", "general"),
                    tags=point.payload.get("tags", []),
                    metadata=point.payload.get("metadata", {})
                ))
            
            return results
        
        except Exception as e:
            logger.error(f"Error getting all knowledge: {str(e)}")
            return []
    
    async def delete_knowledge(self, entry_id: str) -> bool:
        """Delete knowledge entry"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[entry_id]
            )
            logger.info(f"Deleted knowledge entry: {entry_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting knowledge: {str(e)}")
            return False
