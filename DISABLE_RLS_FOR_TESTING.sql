-- EMERGENCY FIX: Disable RLS completely for testing
-- Run this in Supabase SQL Editor if all else fails

-- Disable RLS on users table
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Disable RLS on resumes table  
ALTER TABLE resumes DISABLE ROW LEVEL SECURITY;

-- Verify RLS is disabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'resumes');

-- This should show rowsecurity = false for both tables
