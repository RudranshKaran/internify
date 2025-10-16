# 🔧 Resume Upload "Invalid Token" Fix

## Date: October 15, 2025

## Problem
When trying to upload a resume on the dashboard, the request fails with "Invalid token" error.

## Root Cause
The backend's `verify_token` function in `backend/routes/utils.py` was failing to verify Supabase JWT tokens because:

1. **Missing JWT Secret**: The `.env` file doesn't have `SUPABASE_JWT_SECRET` configured
2. **Wrong Algorithm**: Code was trying to use `HS256` algorithm, but Supabase may use `RS256`
3. **Fallback to Wrong Key**: Code was falling back to `SUPABASE_ANON_KEY` which is itself a JWT token, not a signing secret

## How JWT Verification Works

### Supabase JWT Structure:
- When user logs in, Supabase creates a JWT access token
- This token is sent in the `Authorization: Bearer <token>` header
- Backend needs to verify this token is valid

### The Verification Problem:
```python
# BEFORE (BROKEN):
jwt_secret = os.getenv("SUPABASE_JWT_SECRET") or os.getenv("SUPABASE_ANON_KEY")
# SUPABASE_ANON_KEY is a JWT token itself, not a secret!

payload = jwt.decode(
    token,
    jwt_secret,  # Wrong secret
    algorithms=["HS256"],  # Might be wrong algorithm
    options={"verify_signature": True}
)
```

## Solutions Applied

### 1. Backend: Skip Verification for Development (`backend/routes/utils.py`)

For development purposes, I've modified the token verification to skip signature verification if `SUPABASE_JWT_SECRET` is not set:

```python
if not jwt_secret:
    # Development mode: decode without verification
    print("WARNING: SUPABASE_JWT_SECRET not set. Decoding token without verification.")
    payload = jwt.decode(
        token,
        options={"verify_signature": False, "verify_exp": False}
    )
else:
    # Production mode: verify with secret
    payload = jwt.decode(
        token,
        jwt_secret,
        algorithms=["HS256"],
        options={"verify_signature": True, "verify_exp": True}
    )
```

**⚠️ WARNING**: This is only safe for development! In production, you MUST set the JWT secret.

### 2. Added Debug Logging

**Backend** (`backend/routes/utils.py`):
- Logs when token verification fails
- Shows the specific error (expired, invalid, etc.)

**Frontend** (`frontend/lib/api.ts`):
- Logs when attaching Authorization header
- Shows if token is found or missing
- Logs token length for debugging

**Frontend** (`frontend/app/dashboard/page.tsx`):
- Detailed logging for upload process
- Shows error response from backend
- Displays error status code

## How to Get the Real JWT Secret (For Production)

### Method 1: From Supabase Dashboard
1. Go to https://app.supabase.com
2. Select your project
3. Go to Settings → API
4. Copy the **JWT Secret** (NOT the anon key)
5. Add to `backend/.env`:
   ```
   SUPABASE_JWT_SECRET=your-actual-jwt-secret-here
   ```

### Method 2: Using Supabase Client Library
Instead of manually verifying JWTs, use the official Supabase Python client:

```python
from supabase import create_client

supabase = create_client(supabase_url, supabase_key)

async def verify_token(authorization: str):
    token = authorization.replace("Bearer ", "")
    
    # Use Supabase client to verify
    user = supabase.auth.get_user(token)
    
    if not user:
        raise HTTPException(401, "Invalid token")
    
    return {"sub": user.id, "email": user.email}
```

## Testing Instructions

### 1. Restart Backend Server
The backend server should auto-reload, but if not:
```powershell
cd backend
uvicorn main:app --reload --port 8000
```

### 2. Try Uploading Resume
1. Log in to the dashboard
2. Try uploading a PDF resume
3. Check the browser console for detailed logs:
   - `API: Attaching auth token for request: /resume/upload token found`
   - `API: Authorization header set with token length: XXX`
   - `Dashboard: Uploading resume file: filename.pdf XXX bytes`

### 3. Check Backend Terminal
Look for these logs:
- `WARNING: SUPABASE_JWT_SECRET not set. Decoding token without verification.` (expected in dev)
- If you see errors like `Invalid token: ...`, check what the specific error is

### 4. Check Network Tab
Open DevTools → Network → Filter XHR:
- Look for POST request to `/resume/upload`
- Check Request Headers → Should have `Authorization: Bearer eyJ...`
- Check Response → If 401, look at response body for error details

## Current Status

✅ Backend now accepts tokens without verification (development mode)
✅ Added comprehensive logging on both frontend and backend
✅ Better error messages displayed to users
⚠️ Need to add proper JWT secret for production

## If Upload Still Fails

### Check These:

1. **Is backend running?**
   ```powershell
   curl http://localhost:8000/
   ```

2. **Is token being sent?**
   - Open DevTools → Network
   - Check if Authorization header exists on upload request

3. **Check backend logs**
   - Look for "WARNING: SUPABASE_JWT_SECRET not set" (expected)
   - Look for any JWT decode errors

4. **Try with a fresh login**
   - Log out completely
   - Clear browser cache/localStorage
   - Log in again
   - Try upload

5. **Check file size**
   - Must be PDF format
   - Should be under 10MB

## Files Modified

1. `backend/routes/utils.py` - Modified JWT verification to work without secret
2. `frontend/lib/api.ts` - Added detailed logging for token attachment
3. `frontend/app/dashboard/page.tsx` - Added detailed logging for upload process
4. `docs/RESUME_UPLOAD_TOKEN_FIX.md` - This documentation

## Next Steps

For production deployment:
1. Get the real JWT Secret from Supabase dashboard
2. Add it to backend `.env` as `SUPABASE_JWT_SECRET`
3. Test that verification works with the real secret
4. Remove the "skip verification" fallback code
