-- Migration: Add contact information fields to internships table
-- Run this in Supabase SQL Editor to add contact information columns

-- Add contact information columns to internships table
ALTER TABLE internships 
ADD COLUMN IF NOT EXISTS contact_email TEXT,
ADD COLUMN IF NOT EXISTS contact_phone TEXT,
ADD COLUMN IF NOT EXISTS contact_website TEXT;

-- Create indexes for contact information searches
CREATE INDEX IF NOT EXISTS idx_internships_contact_email ON internships(contact_email) WHERE contact_email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_internships_location ON internships(location);

-- Add comment to document the purpose of new columns
COMMENT ON COLUMN internships.contact_email IS 'Email address for internship applications or inquiries';
COMMENT ON COLUMN internships.contact_phone IS 'Phone number for internship applications or inquiries';
COMMENT ON COLUMN internships.contact_website IS 'Company website or career page URL';
