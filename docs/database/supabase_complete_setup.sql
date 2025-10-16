-- ===================================================================
-- SUPABASE COMPLETE SETUP SCRIPT
-- Run this entire script in Supabase SQL Editor to set everything up
-- ===================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===================================================================
-- 1. CREATE DATABASE TABLES
-- ===================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Internships table
CREATE TABLE IF NOT EXISTS internships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    link TEXT,
    description TEXT,
    location TEXT,
    posted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index on company for faster searches
CREATE INDEX IF NOT EXISTS idx_internships_company ON internships(company);

-- Emails table
CREATE TABLE IF NOT EXISTS emails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    internship_id UUID REFERENCES internships(id) ON DELETE SET NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'sent',
    recipient_email TEXT
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_emails_user_id ON emails(user_id);
CREATE INDEX IF NOT EXISTS idx_emails_sent_at ON emails(sent_at DESC);

-- Resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    extracted_text TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Create index on user_id and uploaded_at for getting latest resume
CREATE INDEX IF NOT EXISTS idx_resumes_user_uploaded ON resumes(user_id, uploaded_at DESC);

-- ===================================================================
-- 2. ENABLE ROW LEVEL SECURITY (RLS)
-- ===================================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE internships ENABLE ROW LEVEL SECURITY;

-- ===================================================================
-- 3. CREATE RLS POLICIES FOR TABLES
-- ===================================================================

-- Users Policies
DROP POLICY IF EXISTS "Users can read own data" ON users;
CREATE POLICY "Users can read own data" ON users
    FOR SELECT
    USING (auth.uid()::text = id::text);

DROP POLICY IF EXISTS "Service role can insert users" ON users;
CREATE POLICY "Service role can insert users" ON users
    FOR INSERT
    WITH CHECK (true);

-- Emails Policies
DROP POLICY IF EXISTS "Users can read own emails" ON emails;
CREATE POLICY "Users can read own emails" ON emails
    FOR SELECT
    USING (auth.uid()::text = user_id::text);

DROP POLICY IF EXISTS "Users can insert own emails" ON emails;
CREATE POLICY "Users can insert own emails" ON emails
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

-- Resumes Policies
DROP POLICY IF EXISTS "Users can read own resumes" ON resumes;
CREATE POLICY "Users can read own resumes" ON resumes
    FOR SELECT
    USING (auth.uid()::text = user_id::text);

DROP POLICY IF EXISTS "Users can insert own resumes" ON resumes;
CREATE POLICY "Users can insert own resumes" ON resumes
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

-- Internships Policies
DROP POLICY IF EXISTS "Authenticated users can read internships" ON internships;
CREATE POLICY "Authenticated users can read internships" ON internships
    FOR SELECT
    TO authenticated
    USING (true);

DROP POLICY IF EXISTS "Service role can insert internships" ON internships;
CREATE POLICY "Service role can insert internships" ON internships
    FOR INSERT
    WITH CHECK (true);

-- ===================================================================
-- 4. CREATE STORAGE BUCKET (if not exists)
-- ===================================================================

-- Insert bucket if it doesn't exist
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
SELECT 'resumes', 'resumes', false, 10485760, ARRAY['application/pdf']
WHERE NOT EXISTS (
    SELECT 1 FROM storage.buckets WHERE id = 'resumes'
);

-- ===================================================================
-- 5. CREATE STORAGE POLICIES
-- ===================================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can upload own resumes" ON storage.objects;
DROP POLICY IF EXISTS "Users can read own resumes" ON storage.objects;
DROP POLICY IF EXISTS "Users can update own resumes" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete own resumes" ON storage.objects;

-- Policy 1: Users can upload their own resumes
CREATE POLICY "Users can upload own resumes"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'resumes' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy 2: Users can read their own resumes
CREATE POLICY "Users can read own resumes"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'resumes' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy 3: Users can update their own resumes
CREATE POLICY "Users can update own resumes"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'resumes' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy 4: Users can delete their own resumes
CREATE POLICY "Users can delete own resumes"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'resumes' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- ===================================================================
-- SETUP COMPLETE!
-- ===================================================================

-- Verify tables were created
SELECT 'Tables created:' as message;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'resumes', 'internships', 'emails');

-- Verify bucket was created
SELECT 'Storage bucket created:' as message;
SELECT id, name, public FROM storage.buckets WHERE id = 'resumes';

SELECT 'Setup complete! You can now upload resumes.' as message;
