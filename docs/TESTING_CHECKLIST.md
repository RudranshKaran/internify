# 🧪 Testing Checklist - Authentication Fixes

## Before Testing

1. **Hard Refresh Browser**: Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. **Clear Browser Storage**: Open DevTools (F12) → Console → Run:
   ```javascript
   localStorage.clear()
   sessionStorage.clear()
   location.reload()
   ```
3. **Verify Server Running**: http://localhost:3000 should be accessible

---

## Test Case 1: Direct Login from Login Page ✅

**Steps**:
1. Navigate to http://localhost:3000/login
2. Enter your email and password
3. Click "Sign In"

**Expected Result**:
- ✅ See "Logged in successfully!" toast message
- ✅ Redirect to /dashboard after ~1 second
- ✅ Dashboard loads with your data
- ✅ NO page flickering or jumping
- ✅ NO redirect back to login

**If Failed**: Check browser console for errors, note the exact behavior

---

## Test Case 2: Resume Upload ✅

**Steps**:
1. Login and go to dashboard
2. Click on the resume upload area
3. Select a PDF file from your computer
4. Wait for upload to complete

**Expected Result**:
- ✅ See "Resume uploaded successfully!" toast
- ✅ Stay on /dashboard page
- ✅ Resume appears in the resume section
- ✅ NO redirect to login
- ✅ NO 401 errors in console

**If Failed**: Check Network tab in DevTools for the resume upload request

---

## Test Case 3: Direct URL Navigation to Login (While Logged In) ✅

**Steps**:
1. Login first (you should be on /dashboard)
2. Manually type http://localhost:3000/login in the address bar
3. Press Enter

**Expected Result**:
- ✅ Immediately redirect to /dashboard
- ✅ NO flash of login page
- ✅ NO loading spinner
- ✅ Stay on dashboard

**If Failed**: Note if you see login page briefly before redirect

---

## Test Case 4: Direct URL Navigation to Dashboard (While Logged Out) ✅

**Steps**:
1. Logout first (or open in incognito mode)
2. Navigate to http://localhost:3000/dashboard
3. Observe what happens

**Expected Result**:
- ✅ Redirect to /login once
- ✅ See login form
- ✅ NO continuous redirects
- ✅ NO page flickering

**If Failed**: Open Network tab to see if requests are looping

---

## Test Case 5: Page Refresh on Dashboard ✅

**Steps**:
1. Login and go to /dashboard
2. Press F5 or Ctrl+R to refresh the page

**Expected Result**:
- ✅ Stay on /dashboard
- ✅ Page reloads with your data
- ✅ Resume loads if you uploaded one
- ✅ NO redirect to login

**If Failed**: Check if session is being cleared

---

## Test Case 6: Navigation Between Protected Pages ✅

**Steps**:
1. Login
2. Go to /dashboard
3. Click "History" in navbar
4. Go to /history
5. Click "Dashboard" in navbar
6. Go back to /dashboard

**Expected Result**:
- ✅ All navigation works smoothly
- ✅ NO redirects to login
- ✅ NO auth checks causing delays
- ✅ Data loads on each page

**If Failed**: Note which page causes issues

---

## Test Case 7: Browser Back Button ✅

**Steps**:
1. Login
2. Navigate: /dashboard → /history → /email-preview (select a job first)
3. Click browser back button twice
4. Should go: /email-preview → /history → /dashboard

**Expected Result**:
- ✅ Navigation works as expected
- ✅ NO unexpected redirects
- ✅ NO auth re-checks on back navigation

**If Failed**: Note if redirects happen during back navigation

---

## Test Case 8: Logout and Login Again ✅

**Steps**:
1. Login
2. Go to dashboard
3. Click "Sign Out" button
4. Should redirect to /login
5. Login again

**Expected Result**:
- ✅ Logout clears session
- ✅ Redirect to /login
- ✅ Can login again successfully
- ✅ NO redirect loops

**If Failed**: Check if session is properly cleared

---

## Test Case 9: Open Multiple Tabs ✅

**Steps**:
1. Login in Tab 1
2. Open http://localhost:3000/dashboard in Tab 2
3. Both tabs should work
4. Logout in Tab 1
5. Refresh Tab 2

**Expected Result**:
- ✅ Tab 2 works when logged in
- ✅ Tab 2 redirects to login after logout + refresh
- ✅ NO conflicts between tabs

**If Failed**: SessionStorage should be per-tab, so no conflicts should occur

---

## Test Case 10: Network Issues Simulation ✅

**Steps**:
1. Login
2. Open DevTools → Network tab
3. Set network to "Slow 3G"
4. Try to upload resume
5. Observe behavior

**Expected Result**:
- ✅ Upload takes longer but succeeds
- ✅ NO premature timeout redirects
- ✅ Loading indicator shows
- ✅ Success message when done

**If Failed**: Check if timeout is causing issues

---

## Debugging Commands

If you encounter issues, run these in browser console (F12):

### Check Current Session
```javascript
const { data: { session } } = await supabase.auth.getSession()
console.log('Session:', session)
console.log('User:', session?.user)
console.log('Token:', session?.access_token)
```

### Check Storage
```javascript
console.log('LocalStorage:', {...localStorage})
console.log('SessionStorage:', {...sessionStorage})
```

### Clear Everything
```javascript
localStorage.clear()
sessionStorage.clear()
await supabase.auth.signOut()
location.reload()
```

### Watch for Redirects
```javascript
// Run this before testing
const originalPush = window.history.pushState
window.history.pushState = function(...args) {
  console.log('Navigation:', args[2])
  return originalPush.apply(this, args)
}
```

---

## What to Report

If any test fails, please provide:

1. **Test Case Number**: e.g., "Test Case 2 failed"
2. **Actual Behavior**: What actually happened
3. **Browser Console Errors**: Any red errors in console
4. **Network Tab**: Screenshot of Network tab during the issue
5. **Steps to Reproduce**: Exact steps to make it happen again

---

## Success Criteria

All 10 test cases should pass ✅

If all pass:
- 🎉 Authentication is working correctly!
- 🎉 Resume upload is working!
- 🎉 Navigation is smooth!
- 🎉 No redirect loops!

---

**Ready to Test?** Start with Test Case 1 and work through them in order!
