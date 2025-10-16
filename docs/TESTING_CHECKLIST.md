# Internify - Quick Testing Checklist

Use this checklist to verify all features are working correctly after the improvements.

---

## 🔐 Authentication Tests

- [ ] **Sign Up**
  - Visit `/login`
  - Click "Sign up instead"
  - Enter email and password
  - Verify email confirmation works
  - Login with new account

- [ ] **Sign In**
  - Visit `/login`
  - Enter credentials
  - Successfully redirects to `/dashboard`
  - No redirect loop occurs

- [ ] **Session Persistence**
  - Login successfully
  - Refresh page
  - Should stay logged in
  - Should not redirect to login

- [ ] **Sign Out**
  - Click "Sign Out" in navbar
  - Redirects to `/login`
  - Session cleared
  - Cannot access `/dashboard` without login

---

## 📄 Resume Management Tests

- [ ] **Upload Resume**
  - Click or drag PDF file to upload area
  - Shows "Uploading..." state
  - Success toast appears
  - File name displays
  - "Replace" and "Delete" buttons appear

- [ ] **Replace Resume**
  - Click "Replace" button
  - File picker opens
  - Select new PDF
  - New resume uploads successfully
  - New filename displays

- [ ] **Delete Resume**
  - Click "Delete" button
  - Confirmation modal appears
  - Click "Cancel" → modal closes, resume stays
  - Click "Delete" button again
  - Click "Delete" in modal → resume deleted
  - Success toast appears
  - Job results clear (if any)
  - Upload area reappears

- [ ] **Invalid File Upload**
  - Try uploading .docx or .txt file
  - Error message appears
  - Resume not uploaded

---

## 🔍 Job Search Tests

- [ ] **Search Jobs**
  - Upload resume first
  - Enter search query (e.g., "Software Engineer Intern")
  - Click "Search Jobs"
  - Shows "Searching..." state
  - Job cards appear
  - Success toast shows job count

- [ ] **Empty Search**
  - Clear search field
  - Try to search
  - Should prevent search or show error

- [ ] **No Results**
  - Search for nonsense term (e.g., "xyzabc123")
  - Shows "No jobs found" message
  - No error occurs

---

## ✅ Job Selection Tests

- [ ] **Select Job Card**
  - Search and display jobs
  - Job cards show "Click to select" badge
  - Click any job card
  - Card border turns blue/primary
  - Checkmark appears in top-right
  - "Generate Email" button appears in header
  - Green confirmation banner appears at bottom
  - Selected job details show in banner

- [ ] **Change Selection**
  - Click different job card
  - Previous card deselects
  - New card selects
  - Confirmation banner updates

- [ ] **Hover Effects**
  - Hover over unselected card
  - Card scales slightly
  - Border color changes
  - Smooth animation

---

## ✉️ Email Generation Tests

- [ ] **Generate Email - Top Button**
  - Select a job
  - Click "Generate Email" button in header
  - Navigates to `/email-preview`
  - Shows "Generating personalized email..." loading
  - Email preview loads with AI-generated content
  - Subject field populated
  - Body field populated
  - Recipient email extracted or placeholder shown

- [ ] **Generate Email - Bottom Button**
  - Select a job
  - Scroll to green confirmation banner
  - Click "Continue →" button
  - Same flow as above

- [ ] **Edit Email**
  - On email preview page
  - Edit subject field → changes save
  - Edit body field → changes save
  - Edit recipient email → changes save

- [ ] **Regenerate Email**
  - Click "Regenerate" button with refresh icon
  - Shows generating state
  - New email content appears
  - Subject and body update

- [ ] **Send Email**
  - Review/edit email
  - Click "Send Email" button
  - Shows "Sending..." state
  - Success toast appears
  - Redirects to `/history`
  - Sent email appears in history

- [ ] **Back Navigation**
  - Click "Back to Dashboard" link
  - Returns to dashboard
  - Job selection persists (or clears, depending on implementation)

---

## 📜 History Tests

- [ ] **View History - Empty**
  - Fresh account with no sent emails
  - Visit `/history` via navbar
  - Shows empty state message
  - "Go to Dashboard" button works

- [ ] **View History - With Emails**
  - After sending at least one email
  - Visit `/history`
  - Email card appears
  - Shows: subject, company, date
  - Click to expand → shows full body (if implemented)

- [ ] **History Details**
  - Verify correct company name
  - Verify correct date/time
  - Verify emails sorted by date (newest first)
  - All sent emails appear

---

## 📋 Legal Pages Tests

- [ ] **Privacy Policy**
  - Scroll to footer
  - Click "Privacy Policy" link
  - Page loads at `/privacy`
  - Content displays correctly
  - "Back to Home" link works
  - Footer shows on page

- [ ] **Terms of Service**
  - Scroll to footer
  - Click "Terms of Service" link
  - Page loads at `/terms`
  - Content displays correctly
  - "Back to Home" link works
  - Footer shows on page

---

## 🎨 UI/UX Tests

- [ ] **Responsive Design**
  - Test on mobile view (< 768px)
  - Navbar collapses to hamburger menu
  - Job cards stack vertically
  - All buttons remain accessible
  - No horizontal scroll
  - Footer stacks correctly

- [ ] **Loading States**
  - Resume upload shows spinner
  - Job search shows loader
  - Email generation shows loader
  - All async operations have feedback

- [ ] **Toast Notifications**
  - Success toasts appear (green)
  - Error toasts appear (red)
  - Info toasts appear (blue)
  - Toasts auto-dismiss after 3-5 seconds

- [ ] **Modals**
  - Delete confirmation modal centers on screen
  - Background dims (overlay)
  - Click outside modal → doesn't close (safe)
  - Cancel button closes modal
  - Escape key closes modal (optional)

---

## 🔒 Security Tests

- [ ] **Protected Routes**
  - Logout
  - Try to visit `/dashboard` directly
  - Redirects to `/login`
  - Same for `/history` and `/email-preview`

- [ ] **Resume Ownership**
  - User A uploads resume
  - User A can only delete their own resume
  - (Cannot test cross-user deletion without 2 accounts)

- [ ] **Token Expiration**
  - Login successfully
  - Wait for token to expire (or manually clear storage)
  - Try to perform action
  - Should redirect to login with error

---

## 🐛 Error Handling Tests

- [ ] **Network Errors**
  - Disconnect internet
  - Try to upload resume
  - Shows error toast
  - Graceful failure (no crash)

- [ ] **Backend Errors**
  - (Simulate by stopping backend server)
  - Try any API operation
  - Shows error toast
  - User informed of issue

- [ ] **Invalid JWT**
  - Manipulate token in browser storage
  - Try to access protected route
  - Redirects to login
  - Session cleared

- [ ] **Missing Data**
  - Try to visit `/email-preview` without selecting job
  - Redirects to dashboard
  - Shows error toast

---

## 🚀 End-to-End Flow Test

Complete this full workflow without errors:

1. [ ] Open application in incognito window
2. [ ] Sign up with new email
3. [ ] Verify email (if required)
4. [ ] Login successfully
5. [ ] Upload resume PDF
6. [ ] Verify "Replace" and "Delete" buttons appear
7. [ ] Search for "Python Intern"
8. [ ] Verify job cards display
9. [ ] Click to select a job
10. [ ] Verify selection indicators appear
11. [ ] Click "Generate Email" button
12. [ ] Verify AI-generated email loads
13. [ ] Edit subject line
14. [ ] Edit body text
15. [ ] Change recipient email
16. [ ] Click "Send Email"
17. [ ] Verify success toast
18. [ ] Verify redirect to history
19. [ ] Verify sent email appears in history
20. [ ] Click navbar "Dashboard" link
21. [ ] Verify dashboard loads
22. [ ] Click "Delete" resume button
23. [ ] Confirm deletion in modal
24. [ ] Verify resume deleted and upload area returns
25. [ ] Scroll to footer
26. [ ] Click "Privacy Policy"
27. [ ] Verify page loads
28. [ ] Go back, click "Terms of Service"
29. [ ] Verify page loads
30. [ ] Click "Sign Out"
31. [ ] Verify redirected to login
32. [ ] ✅ **ALL TESTS PASSED**

---

## 📊 Test Results

| Test Category | Status | Notes |
|--------------|--------|-------|
| Authentication | ⬜ Not Tested | |
| Resume Management | ⬜ Not Tested | |
| Job Search | ⬜ Not Tested | |
| Job Selection | ⬜ Not Tested | |
| Email Generation | ⬜ Not Tested | |
| History | ⬜ Not Tested | |
| Legal Pages | ⬜ Not Tested | |
| UI/UX | ⬜ Not Tested | |
| Security | ⬜ Not Tested | |
| Error Handling | ⬜ Not Tested | |
| End-to-End | ⬜ Not Tested | |

**Legend:**
- ⬜ Not Tested
- ✅ Passed
- ❌ Failed
- ⚠️ Partial / Needs Work

---

## 🐞 Bug Report Template

If you find bugs during testing, document them here:

### Bug #1
- **Category:** [Auth / Resume / Jobs / Email / History / UI]
- **Severity:** [Critical / High / Medium / Low]
- **Description:** What happened?
- **Steps to Reproduce:**
  1. Step 1
  2. Step 2
  3. Step 3
- **Expected Behavior:** What should happen?
- **Actual Behavior:** What actually happened?
- **Screenshots:** (if applicable)
- **Browser:** [Chrome / Firefox / Safari]
- **Device:** [Desktop / Mobile / Tablet]

---

## ✅ Sign-off

**Tested By:** ___________________
**Date:** ___________________
**Overall Status:** ⬜ Ready for Production | ⬜ Needs Fixes
**Notes:**

---

**Happy Testing! 🎉**
