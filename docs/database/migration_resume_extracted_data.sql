-- Migration: Add extracted_data JSONB column to resumes table
--
-- Stores structured resume data extracted by Gemini (skills, projects,
-- experience, achievements) so it only needs to be generated once per
-- upload and can be reused across all future email generations.
--
-- Run this in Supabase SQL Editor.

ALTER TABLE resumes
ADD COLUMN IF NOT EXISTS extracted_data JSONB;

COMMENT ON COLUMN resumes.extracted_data IS 'Structured resume data extracted by Gemini: {skills, projects, experience, achievements}';
