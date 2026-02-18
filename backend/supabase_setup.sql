-- Supabase Database Setup for UniRAG
-- Run this SQL in your Supabase SQL Editor (Dashboard > SQL Editor)
-- URL: https://supabase.com/dashboard/project/YOUR_PROJECT_ID/sql

-- =============================================
-- Step 1: Enable pgvector extension
-- =============================================
CREATE EXTENSION IF NOT EXISTS vector;

-- =============================================
-- Step 2: Create the documents table with vector column
-- =============================================
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster vector similarity search
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Create index for metadata queries
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents
    USING gin (metadata);

-- =============================================
-- Step 3: Create the vector search function
-- =============================================
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_count int DEFAULT 5,
    filter_category text DEFAULT NULL
)
RETURNS TABLE (
    id text,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM documents d
    WHERE
        CASE
            WHEN filter_category IS NOT NULL THEN
                d.metadata->>'category' = filter_category
            ELSE true
        END
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- =============================================
-- Step 4: Create chat history table
-- =============================================
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    citations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_conversation_id ON chat_history(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_created_at ON chat_history(created_at);

-- =============================================
-- Step 5: Create feedback table
-- =============================================
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id TEXT NOT NULL,
    message_index INTEGER NOT NULL,
    is_helpful BOOLEAN NOT NULL,
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- Step 6: Row Level Security (allow all for dev)
-- =============================================
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Allow all operations (for development - restrict in production)
CREATE POLICY "Allow all for documents" ON documents FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for chat" ON chat_history FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for feedback" ON feedback FOR ALL USING (true) WITH CHECK (true);

-- =============================================
-- Done! Your database is ready for UniRAG.
-- =============================================
