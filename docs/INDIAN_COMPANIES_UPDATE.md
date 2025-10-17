# Indian Companies & Contact Information Update

## Overview
Updated Internify to target Indian companies and include contact information in internship listings.

## Changes Made

### 1. Backend Changes

#### `backend/services/scraper_service.py`
- **Modified search parameters** to target Indian companies:
  - Defaults to "India" location if none specified
  - Uses Google India domain (`google.co.in`)
  - Sets country code to India (`gl=in`)
  - Automatically appends "India" to location searches

- **Enhanced salary extraction** to support Indian Rupee (₹):
  - Added support for ₹ symbol
  - Added INR keyword detection

- **Added contact information extraction**:
  - New `_extract_contact_info()` method
  - Extracts email addresses using regex
  - Extracts Indian phone numbers (various formats):
    - +91-XXXXXXXXXX
    - 91XXXXXXXXXX
    - 0XXXXXXXXXX
    - XXXXXXXXXX
  - Extracts company websites from related links

#### `backend/models/internship.py`
- Added three new optional fields to `InternshipBase`:
  - `contact_email: Optional[str]`
  - `contact_phone: Optional[str]`
  - `contact_website: Optional[str]`

### 2. Database Changes

#### New Migration: `docs/database/migration_add_contact_info.sql`
Created migration file to add contact information columns:
```sql
ALTER TABLE internships 
ADD COLUMN IF NOT EXISTS contact_email TEXT,
ADD COLUMN IF NOT EXISTS contact_phone TEXT,
ADD COLUMN IF NOT EXISTS contact_website TEXT;
```

**To apply this migration:**
1. Open Supabase Dashboard
2. Go to SQL Editor
3. Run the migration file content

### 3. Frontend Changes

#### `frontend/components/InternshipCard.tsx`
- Added contact information icons from lucide-react: `Mail`, `Phone`, `Globe`
- Updated interface to include contact fields
- Added contact information display section:
  - Email with mailto: link
  - Phone with tel: link
  - Website with external link
  - Styled with gray background badges
  - Truncated email display for space efficiency

## Features

### Automatic India Targeting
- All searches now default to India if no location specified
- Uses Google India domain for better local results
- Geographic targeting ensures Indian companies appear first

### Contact Information Display
- **Email**: Click to open email client
- **Phone**: Click to initiate call (mobile)
- **Website**: Opens company career page in new tab
- Compact badge design fits well in card layout

### Phone Number Format Support
Supports various Indian phone number formats:
- With country code: +91-9876543210
- Without spaces: 919876543210
- With dashes: 987-654-3210
- Standard 10-digit: 9876543210

## Testing

### Test the Changes

1. **Apply Database Migration**:
   ```bash
   # In Supabase SQL Editor, run:
   # docs/database/migration_add_contact_info.sql
   ```

2. **Restart Backend** (if running):
   ```bash
   cd backend
   # Stop current process (Ctrl+C)
   uvicorn main:app --reload
   ```

3. **Test Search**:
   - Search for "AI Engineer" (without location)
   - Should show Indian companies
   - Check if contact information appears

4. **Test with Specific Location**:
   - Search "Software Engineer" in "Bangalore"
   - Should show: "Bangalore, India" results

### Expected Behavior

#### Search Results:
- Companies located in India (Bangalore, Mumbai, Delhi, Hyderabad, etc.)
- Indian startups and tech companies
- Salaries in INR (₹)
- Indian phone numbers (+91)

#### Contact Information:
- May not appear for all listings (depends on job posting)
- Email addresses extracted from description
- Phone numbers in various Indian formats
- Website links to company career pages

## Sample Search Queries

Try these to find Indian internships:
- "AI Engineer"
- "Software Developer"
- "Data Science Intern"
- "Full Stack Developer"
- "Machine Learning" in "Bangalore"
- "Python Developer" in "Mumbai"

## Known Limitations

1. **Contact Information Availability**:
   - Not all job postings include contact details
   - Some companies only provide application links
   - Email/phone extraction depends on structured data

2. **Search Results**:
   - Google Jobs API may still show some non-Indian companies
   - Results depend on available listings
   - Quality varies by search query

3. **Phone Number Extraction**:
   - May occasionally pick up non-phone numbers
   - Regex pattern is comprehensive but not perfect

## Future Improvements

1. **Enhanced Contact Extraction**:
   - LinkedIn scraping for company contact pages
   - Company website crawling for HR emails
   - Integration with company databases

2. **Indian Job Boards**:
   - Add Naukri.com integration
   - Add Internshala.com scraping
   - Add AngelList India

3. **Better Filtering**:
   - Filter by Indian cities
   - Indian startup filter
   - Remote-friendly filter

4. **Salary Normalization**:
   - Convert all to INR
   - Show monthly/annual options
   - Stipend range filters

## Troubleshooting

### No Indian Companies Appearing
- Check SERPAPI_KEY is valid
- Verify internet connection
- Try more specific location (e.g., "Bangalore, India")

### Contact Information Not Showing
- This is normal - not all listings have contact info
- Try different search queries
- Contact info depends on job posting structure

### Database Errors
- Ensure migration was applied successfully
- Check Supabase connection
- Verify internships table has new columns

## Support

If you encounter issues:
1. Check backend logs for errors
2. Verify .env has correct SERPAPI_KEY
3. Test API endpoint directly: `/internships/search?role=AI%20Engineer`
4. Check Supabase table structure includes new columns
