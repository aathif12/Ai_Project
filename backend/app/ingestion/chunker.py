"""
Text chunking for RAG retrieval.
Implements smart chunking with overlap for better context preservation.
"""

import tiktoken
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class TextChunk:
    """Represents a chunk of text for embedding."""
    
    def __init__(
        self, 
        text: str, 
        chunk_index: int,
        page_number: int,
        metadata: Dict[str, Any] = None
    ):
        self.text = text
        self.chunk_index = chunk_index
        self.page_number = page_number
        self.metadata = metadata or {}
        self.token_count = 0  # Set by chunker


class TextChunker:
    """
    Split text into overlapping chunks for RAG retrieval.
    
    Uses tiktoken for accurate token counting with OpenAI models.
    Implements sentence-aware chunking to avoid cutting mid-sentence.
    """
    
    def __init__(
        self, 
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        encoding_name: str = "cl100k_base"  # For GPT-4 and embeddings
    ):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Number of overlapping tokens between chunks
            encoding_name: Tiktoken encoding to use
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def chunk_text(
        self, 
        text: str, 
        page_number: int = 1,
        base_metadata: Dict[str, Any] = None
    ) -> List[TextChunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            page_number: Source page number for citations
            base_metadata: Metadata to include with each chunk
            
        Returns:
            List of TextChunk objects
        """
        if not text.strip():
            return []
        
        base_metadata = base_metadata or {}
        chunks = []
        
        # Split into sentences first for smarter chunking
        sentences = self._split_into_sentences(text)
        
        current_chunk = []
        current_tokens = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # If single sentence is bigger than chunk_size, split it
            if sentence_tokens > self.chunk_size:
                # First, save current chunk if any
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, chunk_index, page_number, base_metadata
                    ))
                    chunk_index += 1
                    current_chunk = []
                    current_tokens = 0
                
                # Split the long sentence
                sub_chunks = self._split_long_text(sentence)
                for sub_chunk in sub_chunks:
                    chunks.append(self._create_chunk(
                        sub_chunk, chunk_index, page_number, base_metadata
                    ))
                    chunk_index += 1
                continue
            
            # Check if adding this sentence exceeds chunk_size
            if current_tokens + sentence_tokens > self.chunk_size:
                # Save current chunk
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, chunk_index, page_number, base_metadata
                    ))
                    chunk_index += 1
                    
                    # Keep overlap sentences
                    overlap_chunk, overlap_tokens = self._get_overlap(
                        current_chunk, current_tokens
                    )
                    current_chunk = overlap_chunk
                    current_tokens = overlap_tokens
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(self._create_chunk(
                chunk_text, chunk_index, page_number, base_metadata
            ))
        
        logger.info(f"Created {len(chunks)} chunks from page {page_number}")
        return chunks
    
    def _create_chunk(
        self, 
        text: str, 
        chunk_index: int, 
        page_number: int,
        base_metadata: Dict[str, Any]
    ) -> TextChunk:
        """Create a TextChunk with token count."""
        chunk = TextChunk(
            text=text.strip(),
            chunk_index=chunk_index,
            page_number=page_number,
            metadata=base_metadata.copy()
        )
        chunk.token_count = self.count_tokens(text)
        return chunk
    
    def _get_overlap(
        self, 
        sentences: List[str], 
        total_tokens: int
    ) -> tuple:
        """
        Get sentences to keep for overlap.
        
        Returns:
            Tuple of (overlap_sentences, overlap_tokens)
        """
        if not sentences:
            return [], 0
        
        overlap_sentences = []
        overlap_tokens = 0
        
        # Work backwards from the end
        for sentence in reversed(sentences):
            sentence_tokens = self.count_tokens(sentence)
            if overlap_tokens + sentence_tokens <= self.chunk_overlap:
                overlap_sentences.insert(0, sentence)
                overlap_tokens += sentence_tokens
            else:
                break
        
        return overlap_sentences, overlap_tokens
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        Uses regex for robust sentence detection.
        """
        # Pattern for sentence endings
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        
        # Split but keep the delimiters
        raw_sentences = re.split(sentence_pattern, text)
        
        # Clean and filter
        sentences = []
        for s in raw_sentences:
            s = s.strip()
            if s:
                sentences.append(s)
        
        return sentences
    
    def _split_long_text(self, text: str) -> List[str]:
        """Split text that's longer than chunk_size into smaller pieces."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for word in words:
            word_tokens = self.count_tokens(word + " ")
            
            if current_tokens + word_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_tokens = word_tokens
            else:
                current_chunk.append(word)
                current_tokens += word_tokens
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def chunk_pages(
        self, 
        pages: List[Any],  # List of ExtractedPage
        document_name: str,
        category: str
    ) -> List[TextChunk]:
        """
        Chunk multiple pages with proper metadata.
        
        Args:
            pages: List of ExtractedPage objects
            document_name: Name of the source document
            category: Document category
            
        Returns:
            List of all chunks from all pages
        """
        all_chunks = []
        
        for page in pages:
            base_metadata = {
                "document_name": document_name,
                "category": category,
                "source": page.metadata.get("source", ""),
            }
            
            page_chunks = self.chunk_text(
                page.text,
                page_number=page.page_number,
                base_metadata=base_metadata
            )
            
            all_chunks.extend(page_chunks)
        
        logger.info(
            f"Created {len(all_chunks)} total chunks from "
            f"{len(pages)} pages of '{document_name}'"
        )
        
        return all_chunks
