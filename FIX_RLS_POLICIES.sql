-- Fix RLS Policies for Internify
-- Run this in your Supabase SQL Editor to allow user creation and resume uploads

-- First, let's check and fix the users table policies
DROP POLICY IF EXISTS "Users can view own data" ON users;
DROP POLICY IF EXISTS "Users can view their own data" ON users;
DROP POLICY IF EXISTS "Users can update own data" ON users;
DROP POLICY IF EXISTS "Users can update their own data" ON users;
DROP POLICY IF EXISTS "Allow user creation" ON users;
DROP POLICY IF EXISTS "Users can create own record" ON users;
DROP POLICY IF EXISTS "Users can create their own record" ON users;
DROP POLICY IF EXISTS "Service role can manage users" ON users;

-- Allow authenticated users to insert their own user record
CREATE POLICY "Users can create own record"
ON users FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = id);

-- Allow users to read their own data
CREATE POLICY "Users can view own data"
ON users FOR SELECT
TO authenticated
USING (auth.uid() = id);

-- Allow users to update their own data
CREATE POLICY "Users can update own data"
ON users FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- Now fix resumes table policies
-- Drop all possible variations of policy names
DROP POLICY IF EXISTS "Users can insert their own resumes" ON resumes;
DROP POLICY IF EXISTS "Users can insert own resumes" ON resumes;
DROP POLICY IF EXISTS "Users can view their own resumes" ON resumes;
DROP POLICY IF EXISTS "Users can view own resumes" ON resumes;
DROP POLICY IF EXISTS "Users can update their own resumes" ON resumes;
DROP POLICY IF EXISTS "Users can update own resumes" ON resumes;
DROP POLICY IF EXISTS "Users can delete their own resumes" ON resumes;
DROP POLICY IF EXISTS "Users can delete own resumes" ON resumes;

-- Allow authenticated users to insert their own resumes
CREATE POLICY "Users can insert own resumes"
ON resumes FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Allow users to view their own resumes
CREATE POLICY "Users can view own resumes"
ON resumes FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- Allow users to update their own resumes
CREATE POLICY "Users can update own resumes"
ON resumes FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Allow users to delete their own resumes
CREATE POLICY "Users can delete own resumes"
ON resumes FOR DELETE
TO authenticated
USING (auth.uid() = user_id);

-- Fix emails table policies (if needed)
DROP POLICY IF EXISTS "Users can insert their own emails" ON emails;
DROP POLICY IF EXISTS "Users can insert own emails" ON emails;
DROP POLICY IF EXISTS "Users can view their own emails" ON emails;
DROP POLICY IF EXISTS "Users can view own emails" ON emails;

CREATE POLICY "Users can insert own emails"
ON emails FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own emails"
ON emails FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- Fix internships table policies (if needed)
DROP POLICY IF EXISTS "Anyone can view internships" ON internships;
DROP POLICY IF EXISTS "Service can insert internships" ON internships;

CREATE POLICY "Anyone can view internships"
ON internships FOR SELECT
TO authenticated
USING (true);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON users TO authenticated;
GRANT ALL ON resumes TO authenticated;
GRANT ALL ON emails TO authenticated;
GRANT SELECT ON internships TO authenticated;

-- Verify RLS is enabled
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE internships ENABLE ROW LEVEL SECURITY;
