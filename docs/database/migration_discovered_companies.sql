-- Migration: Add discovered_companies table for tracking companies found during search
-- Run this in Supabase SQL Editor
--
-- This table stores each unique company+role a user has discovered via search,
-- deduplicating by (user_id, domain, role_title) when domain is available,
-- or by (user_id, company_name, role_title) as fallback.

CREATE TABLE IF NOT EXISTS discovered_companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    domain TEXT,                                   -- company domain e.g. "google.com" (nullable for serp results)
    role_title TEXT NOT NULL,                      -- e.g. "Software Engineer Intern"
    location TEXT,
    job_description_snippet TEXT,
    source_url TEXT,                               -- link to the original job posting
    source_query TEXT,                             -- the search query that surfaced this company
    email_status TEXT NOT NULL DEFAULT 'not_found' CHECK (email_status IN ('not_found', 'found', 'verified')),
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partial unique index: when domain IS known, use it for dedup
CREATE UNIQUE INDEX IF NOT EXISTS idx_dc_unique_domain
    ON discovered_companies(user_id, domain, role_title)
    WHERE domain IS NOT NULL;

-- Partial unique index: when domain IS NOT known, fall back to company_name
CREATE UNIQUE INDEX IF NOT EXISTS idx_dc_unique_name
    ON discovered_companies(user_id, company_name, role_title)
    WHERE domain IS NULL;

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_dc_user_id ON discovered_companies(user_id);
CREATE INDEX IF NOT EXISTS idx_dc_user_email_status ON discovered_companies(user_id, email_status);
CREATE INDEX IF NOT EXISTS idx_dc_last_seen ON discovered_companies(last_seen_at DESC);

-- Enable Row Level Security
ALTER TABLE discovered_companies ENABLE ROW LEVEL SECURITY;

-- RLS: Users can read their own discovered companies
CREATE POLICY "Users can read own discovered companies" ON discovered_companies
    FOR SELECT
    USING (auth.uid()::text = user_id::text);

-- RLS: Service role can insert/update discovered companies (used by backend service key)
CREATE POLICY "Service role can insert discovered companies" ON discovered_companies
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Service role can update discovered companies" ON discovered_companies
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- Comments
COMMENT ON TABLE discovered_companies IS 'Companies discovered during internship searches, deduplicated per user';
COMMENT ON COLUMN discovered_companies.domain IS 'Company domain used for deduplication when available';
COMMENT ON COLUMN discovered_companies.email_status IS 'Email discovery status: not_found, found, or verified';
COMMENT ON COLUMN discovered_companies.source_query IS 'The search keyword combination that surfaced this company';
COMMENT ON COLUMN discovered_companies.last_seen_at IS 'Updated every time the company reappears in a search result';
