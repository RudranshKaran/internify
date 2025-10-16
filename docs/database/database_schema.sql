-- Internify Database Schema
-- Run this in Supabase SQL Editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE internships ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Users: Users can only read their own data
CREATE POLICY "Users can read own data" ON users
    FOR SELECT
    USING (auth.uid()::text = id::text);

-- Users: Service role can insert users
CREATE POLICY "Service role can insert users" ON users
    FOR INSERT
    WITH CHECK (true);

-- Emails: Users can read their own emails
CREATE POLICY "Users can read own emails" ON emails
    FOR SELECT
    USING (auth.uid()::text = user_id::text);

-- Emails: Users can insert their own emails
CREATE POLICY "Users can insert own emails" ON emails
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

-- Resumes: Users can read their own resumes
CREATE POLICY "Users can read own resumes" ON resumes
    FOR SELECT
    USING (auth.uid()::text = user_id::text);

-- Resumes: Users can insert their own resumes
CREATE POLICY "Users can insert own resumes" ON resumes
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

-- Internships: All authenticated users can read internships
CREATE POLICY "Authenticated users can read internships" ON internships
    FOR SELECT
    TO authenticated
    USING (true);

-- Internships: Service role can insert internships
CREATE POLICY "Service role can insert internships" ON internships
    FOR INSERT
    WITH CHECK (true);

-- Storage bucket for resumes
-- Note: Create this through Supabase Dashboard > Storage
-- Bucket name: resumes
-- Public: false

-- Storage policies (run after creating bucket)
-- Allow authenticated users to upload their own resumes
CREATE POLICY "Users can upload own resumes"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'resumes' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Allow users to read their own resumes
CREATE POLICY "Users can read own resumes"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'resumes' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Optional: Create a view for email history with internship details
CREATE OR REPLACE VIEW email_history AS
SELECT 
    e.id,
    e.user_id,
    e.subject,
    e.body,
    e.recipient_email,
    e.sent_at,
    e.status,
    i.title as internship_title,
    i.company,
    i.location,
    i.link as internship_link
FROM emails e
LEFT JOIN internships i ON e.internship_id = i.id
ORDER BY e.sent_at DESC;

-- Grant access to the view
GRANT SELECT ON email_history TO authenticated;

-- Comments for documentation
COMMENT ON TABLE users IS 'User accounts from Supabase Auth';
COMMENT ON TABLE internships IS 'Internship postings scraped from LinkedIn/SerpAPI';
COMMENT ON TABLE emails IS 'Sent email applications with tracking';
COMMENT ON TABLE resumes IS 'User uploaded resumes with extracted text';
COMMENT ON COLUMN resumes.extracted_text IS 'Text extracted from PDF for AI processing';
COMMENT ON COLUMN emails.status IS 'Email status: sent, failed, pending';

-- Success message
DO $$ 
BEGIN 
    RAISE NOTICE 'Database schema created successfully!';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Create storage bucket named "resumes" in Supabase Dashboard';
    RAISE NOTICE '2. Configure your backend .env file';
    RAISE NOTICE '3. Test with a sample resume upload';
END $$;
