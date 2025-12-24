-- BidDeed.AI Conversational Agent - Vector Search Setup
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Property embeddings table for semantic search
CREATE TABLE IF NOT EXISTS property_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_number TEXT NOT NULL UNIQUE,
  property_address TEXT,
  embedding vector(1536),  -- OpenAI text-embedding-3-small dimension
  content TEXT,            -- Combined text for search
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversation history for context
CREATE TABLE IF NOT EXISTS agent_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  intent JSONB DEFAULT '{}',
  properties_referenced TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for session lookup
CREATE INDEX IF NOT EXISTS idx_conversations_session ON agent_conversations(session_id, created_at DESC);

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_properties(
  query_embedding vector(1536),
  match_count INT DEFAULT 5,
  match_threshold FLOAT DEFAULT 0.7
)
RETURNS TABLE (
  case_number TEXT,
  property_address TEXT,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    pe.case_number,
    pe.property_address,
    pe.content,
    pe.metadata,
    1 - (pe.embedding <=> query_embedding) as similarity
  FROM property_embeddings pe
  WHERE 1 - (pe.embedding <=> query_embedding) > match_threshold
  ORDER BY pe.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- RLS policies
ALTER TABLE property_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_conversations ENABLE ROW LEVEL SECURITY;

-- Public read access for embeddings
CREATE POLICY "Public read embeddings" ON property_embeddings
  FOR SELECT USING (true);

-- Service role full access
CREATE POLICY "Service role full access embeddings" ON property_embeddings
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access conversations" ON agent_conversations
  FOR ALL USING (auth.role() = 'service_role');

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_property_embeddings_updated_at
  BEFORE UPDATE ON property_embeddings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
