-- =====================================================
-- COPY AND PASTE THIS ENTIRE FILE INTO SUPABASE SQL EDITOR
-- =====================================================

-- Step 1: Check if internships table exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'internships'
    ) THEN
        -- Table doesn't exist, create it with all columns
        CREATE TABLE internships (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            link TEXT,
            description TEXT,
            location TEXT,
            posted_at TIMESTAMP,
            contact_email TEXT,
            contact_phone TEXT,
            contact_website TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        RAISE NOTICE 'Created internships table';
    ELSE
        -- Table exists, add missing columns
        ALTER TABLE internships 
        ADD COLUMN IF NOT EXISTS contact_email TEXT,
        ADD COLUMN IF NOT EXISTS contact_phone TEXT,
        ADD COLUMN IF NOT EXISTS contact_website TEXT;
        
        RAISE NOTICE 'Added contact columns to existing internships table';
    END IF;
END $$;

-- Step 2: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_internships_company ON internships(company);
CREATE INDEX IF NOT EXISTS idx_internships_location ON internships(location);
CREATE INDEX IF NOT EXISTS idx_internships_contact_email ON internships(contact_email) WHERE contact_email IS NOT NULL;

-- Step 3: Enable Row Level Security
ALTER TABLE internships ENABLE ROW LEVEL SECURITY;

-- Step 4: Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Authenticated users can read internships" ON internships;
DROP POLICY IF EXISTS "Service role can insert internships" ON internships;

-- Step 5: Create RLS policies
CREATE POLICY "Authenticated users can read internships" 
ON internships
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Service role can insert internships" 
ON internships
FOR INSERT
WITH CHECK (true);

-- Step 6: Verify the table structure
SELECT 
    column_name, 
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'internships' 
ORDER BY ordinal_position;

-- Success message will be displayed above
-- You should see all columns including contact_email, contact_phone, contact_website
