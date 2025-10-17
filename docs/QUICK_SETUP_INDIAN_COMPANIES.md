# Quick Setup for Indian Companies & Contact Info Feature

## Step 1: Apply Database Migration

### Option A: Using Supabase Dashboard (Recommended)
1. Go to your Supabase project dashboard
2. Click on "SQL Editor" in the left sidebar
3. Click "New Query"
4. Copy and paste the following SQL:

```sql
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
```

5. Click "Run" button
6. You should see "Success. No rows returned"

### Option B: Using Supabase CLI
```bash
# If you have Supabase CLI installed
supabase db push docs/database/migration_add_contact_info.sql
```

## Step 2: Restart Backend (If Running)

If your backend is currently running, restart it to load the changes:

### Windows PowerShell:
```powershell
# Press Ctrl+C in the uvicorn terminal to stop
cd backend
uvicorn main:app --reload
```

## Step 3: Test the Changes

### Test 1: Search Without Location (Defaults to India)
```
Search Query: "AI Engineer"
Expected: Should show Indian companies
```

### Test 2: Search With Specific Indian City
```
Search Query: "Software Developer"
Location: "Bangalore"
Expected: Should show "Bangalore, India" companies
```

### Test 3: Verify Contact Information
```
After search, check internship cards for:
- Email icon with email address
- Phone icon with phone number
- Globe icon for website
```

## Step 4: Verify Database Changes

Run this query in Supabase SQL Editor to verify columns were added:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'internships' 
AND column_name IN ('contact_email', 'contact_phone', 'contact_website');
```

Expected result: Should show 3 rows with the new columns

## What Changed

### Backend (`backend/services/scraper_service.py`)
✅ Now targets India by default
✅ Uses Google India domain (google.co.in)
✅ Extracts contact information (email, phone, website)
✅ Supports Indian phone number formats (+91, etc.)
✅ Supports INR currency (₹)

### Frontend (`frontend/components/InternshipCard.tsx`)
✅ Displays contact email with mailto: link
✅ Displays phone number with tel: link
✅ Displays company website link
✅ Icons for each contact method (Mail, Phone, Globe)

### Database
✅ Added contact_email column
✅ Added contact_phone column
✅ Added contact_website column
✅ Added indexes for better search performance

## Troubleshooting

### Issue: "Column already exists" error
**Solution**: This is fine! It means the columns were already added. Skip to Step 2.

### Issue: No contact information showing
**Reason**: Not all job postings include contact details in their descriptions.
**Solution**: This is normal. Try different search queries or companies that typically include contact info.

### Issue: Still seeing US companies
**Reason**: Some global companies may appear in Indian search results.
**Solution**: Add specific Indian cities like "Bangalore", "Mumbai", "Hyderabad" to filter better.

### Issue: Backend errors after changes
**Solution**: 
1. Check if Python packages are up to date: `pip install -r requirements.txt`
2. Verify .env file has SERPAPI_KEY
3. Check backend logs for specific error messages

## Next Steps

Once setup is complete:

1. **Test thoroughly** with various search queries
2. **Check different Indian cities**: Bangalore, Mumbai, Delhi, Hyderabad, Pune
3. **Try different roles**: Software Engineer, Data Scientist, AI Engineer, etc.
4. **Verify contact information** appears when available
5. **Report any issues** you encounter

## Expected Search Results

After setup, you should see:

### Companies:
- Indian startups (Swiggy, Zomato, Ola, etc.)
- Indian offices of global companies
- Local tech companies

### Locations:
- Bangalore, Karnataka
- Mumbai, Maharashtra
- Hyderabad, Telangana
- Pune, Maharashtra
- Delhi NCR

### Contact Information:
- HR emails (@company.com)
- Indian phone numbers (+91-XXX-XXX-XXXX)
- Career page URLs

## Success Criteria

✅ Search without location shows Indian companies
✅ Location field auto-appends "India"
✅ Contact information visible when available
✅ Email/phone/website links work correctly
✅ Salaries show in INR (₹) when available

---

**Need Help?** Check the full documentation in `docs/INDIAN_COMPANIES_UPDATE.md`
