-- Supabase Database Setup for UniRAG
-- Run this SQL in your Supabase SQL Editor (Dashboard > SQL Editor)

-- Enable the pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- The vecs library will automatically create the necessary tables
-- when you first run the application. However, if you want to
-- manually set up the documents metadata table for direct queries,
-- you can use this:

-- Create a table for storing document metadata (optional, for admin purposes)
CREATE TABLE IF NOT EXISTS documents_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    category TEXT DEFAULT 'other',
    page_count INTEGER DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,
    file_size BIGINT DEFAULT 0,
    uploaded_by TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents_metadata(category);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at ON documents_metadata(uploaded_at);

-- Create a table for chat history (optional)
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    citations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for conversation lookups
CREATE INDEX IF NOT EXISTS idx_chat_conversation_id ON chat_history(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_created_at ON chat_history(created_at);

-- Create a table for feedback
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id TEXT NOT NULL,
    message_index INTEGER NOT NULL,
    is_helpful BOOLEAN NOT NULL,
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security (RLS) policies
-- Enable RLS on tables
ALTER TABLE documents_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated access
-- For development, allow all operations. In production, customize these.

-- Documents: Allow all operations for authenticated users
CREATE POLICY "Allow all for documents" ON documents_metadata
    FOR ALL USING (true);

-- Chat history: Allow all operations
CREATE POLICY "Allow all for chat" ON chat_history
    FOR ALL USING (true);

-- Feedback: Allow all operations
CREATE POLICY "Allow all for feedback" ON feedback
    FOR ALL USING (true);

-- Grant permissions (for service role)
GRANT ALL ON documents_metadata TO service_role;
GRANT ALL ON chat_history TO service_role;
GRANT ALL ON feedback TO service_role;

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_documents_metadata_updated_at
    BEFORE UPDATE ON documents_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Helpful queries for monitoring:

-- Count documents by category
-- SELECT category, COUNT(*) FROM documents_metadata GROUP BY category;

-- Get recent uploads
-- SELECT * FROM documents_metadata ORDER BY uploaded_at DESC LIMIT 10;

-- Get chat statistics
-- SELECT conversation_id, COUNT(*) as messages FROM chat_history GROUP BY conversation_id;

-- Feedback summary
-- SELECT 
--     COUNT(*) as total_feedback,
--     SUM(CASE WHEN is_helpful THEN 1 ELSE 0 END) as positive,
--     SUM(CASE WHEN NOT is_helpful THEN 1 ELSE 0 END) as negative
-- FROM feedback;
