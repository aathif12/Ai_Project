"""
RAG (Retrieval-Augmented Generation) Chain.
Handles the retrieval and generation pipeline for answering questions.
"""

from openai import OpenAI
from typing import List, Dict, Any, Optional, Tuple
import logging
import time

from app.config import get_settings
from app.models import Citation, DocumentCategory
from app.ingestion.embedder import EmbeddingService
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class RAGChain:
    """
    RAG Chain for answering questions based on retrieved documents.
    
    Pipeline:
    1. Embed the user's question
    2. Retrieve relevant document chunks
    3. Build context from retrieved chunks
    4. Generate answer using LLM with context
    5. Return answer with citations
    """
    
    # System prompt that enforces grounded responses
    SYSTEM_PROMPT = """You are a helpful university assistant that answers questions based ONLY on the provided document context.

IMPORTANT RULES:
1. ONLY use information from the provided context to answer questions
2. If the answer is not in the context, say "I don't have information about this in the uploaded documents."
3. Be concise but complete in your answers
4. When referencing information, mention which document it comes from
5. If asked about something outside the context, politely redirect to document-related questions
6. Format your answers clearly with bullet points or numbered lists when appropriate

Remember: You can ONLY answer based on the uploaded university documents. Do not make up information."""

    CONTEXT_TEMPLATE = """Here is the relevant context from university documents:

{context}

---

Based ONLY on the above context, please answer the following question. If the information is not in the context, say so clearly.

Question: {question}"""

    def __init__(self):
        """Initialize the RAG chain with required services."""
        self.settings = get_settings()
        self.embedder = EmbeddingService()
        self.vector_store = VectorStoreService()
        
        self.client = OpenAI(api_key=self.settings.openai_api_key)
    
    def answer(
        self,
        question: str,
        category_filter: Optional[List[DocumentCategory]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, List[Citation], float]:
        """
        Answer a question using RAG.
        
        Args:
            question: The user's question
            category_filter: Optional categories to filter documents
            conversation_history: Optional previous messages for context
            
        Returns:
            Tuple of (answer, citations, confidence_score)
        """
        start_time = time.time()
        
        try:
            # Step 1: Embed the question
            logger.info(f"RAG: Processing question: {question[:50]}...")
            question_embedding = self.embedder.get_embedding(question)
            
            # Step 2: Retrieve relevant chunks
            category_values = None
            if category_filter:
                category_values = [c.value for c in category_filter]
            
            results = self.vector_store.search(
                query_embedding=question_embedding,
                n_results=self.settings.top_k_results,
                category_filter=category_values
            )
            
            # Check if we found relevant documents
            if not results["documents"]:
                return (
                    "I don't have any documents to search through. Please upload some university documents first.",
                    [],
                    0.0
                )
            
            # Step 3: Build context and citations
            context, citations = self._build_context(results)
            
            # Check relevance (using distance threshold)
            avg_distance = sum(results["distances"]) / len(results["distances"])
            confidence = max(0, 1 - avg_distance)  # Convert distance to confidence
            
            # If results are too far (low relevance), warn about it
            if avg_distance > 1.5:  # Threshold for low relevance
                logger.warning(f"Low relevance results (avg distance: {avg_distance})")
            
            # Step 4: Generate answer
            answer = self._generate_answer(
                question=question,
                context=context,
                conversation_history=conversation_history
            )
            
            elapsed = time.time() - start_time
            logger.info(f"RAG: Generated answer in {elapsed:.2f}s (confidence: {confidence:.2f})")
            
            return answer, citations, confidence
            
        except Exception as e:
            logger.error(f"Error in RAG chain: {e}")
            raise
    
    def _build_context(
        self, 
        results: Dict[str, Any]
    ) -> Tuple[str, List[Citation]]:
        """
        Build context string and citations from search results.
        
        Returns:
            Tuple of (context_string, list_of_citations)
        """
        context_parts = []
        citations = []
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"],
            results["metadatas"],
            results["distances"]
        )):
            doc_name = metadata.get("document_name", "Unknown")
            page_num = metadata.get("page_number", None)
            
            # Build context part with source info
            source_info = f"[Source: {doc_name}"
            if page_num:
                source_info += f", Page {page_num}"
            source_info += "]"
            
            context_parts.append(f"{source_info}\n{doc}\n")
            
            # Build citation
            relevance_score = max(0, 1 - distance)
            citations.append(Citation(
                document_name=doc_name,
                page_number=page_num,
                chunk_text=doc[:200] + "..." if len(doc) > 200 else doc,
                relevance_score=round(relevance_score, 3)
            ))
        
        context = "\n---\n".join(context_parts)
        return context, citations
    
    def _generate_answer(
        self,
        question: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate answer using OpenAI with the retrieved context.
        """
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                messages.append(msg)
        
        # Add the current question with context
        user_message = self.CONTEXT_TEMPLATE.format(
            context=context,
            question=question
        )
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.settings.llm_model,
                messages=messages,
                temperature=0.3,  # Lower for more factual responses
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def get_suggested_questions(self) -> List[str]:
        """
        Get suggested questions based on available documents.
        Useful for empty chat state.
        """
        documents = self.vector_store.get_unique_documents()
        
        if not documents:
            return [
                "Upload a document to get started!",
                "I can answer questions about university rules, courses, exams, and more."
            ]
        
        # Generate suggestions based on categories
        categories = set(d.get("category", "") for d in documents)
        suggestions = []
        
        category_questions = {
            "rules": "What are the main campus rules I should know?",
            "exams": "What are the exam policies and requirements?",
            "courses": "How do I register for courses?",
            "hostel": "What are the hostel accommodation rules?",
            "timetable": "What is the class schedule?",
            "notices": "Are there any important announcements?",
            "handbook": "What should I know as a new student?",
        }
        
        for cat in categories:
            if cat in category_questions:
                suggestions.append(category_questions[cat])
        
        # Add general suggestion
        suggestions.append("What documents are available?")
        
        return suggestions[:5]  # Max 5 suggestions
