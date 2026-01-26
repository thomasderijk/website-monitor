# Website Monitor - Troubleshooting Guide

## Issues Found & Solutions

### 1. "undefined" Display Issue ✓ FIXED

**Problem:** The HTML template had character encoding issues with emoji characters (📊, 🔥, etc.), causing "undefined" to appear in the "Last check" field.

**Solution:** Replace your current `templates/index.html` with the fixed version provided (`index_fixed.html`).

**How to Fix:**
1. Stop your Flask app (Ctrl+C in terminal)
2. Replace `D:\Dropbox\02_Areas\webmonitor\simple-monitor\templates\index.html` with the new `index_fixed.html`
3. Restart the app

---

### 2. Email Notifications Not Arriving

**Problem:** Changes ARE being detected (nos.nl shows "changed" status), but you're not receiving email notifications.

**Possible Causes & Solutions:**

#### A. Email Configuration Issue
Your notifier.py has these settings:
- SMTP Server: smtp.mail.me.com
- Username: thomasderijk@me.com
- Password: svgs-pbgk-ckyc-sady

**To Test Email:**
1. Run the diagnostic tool: `python email_diagnostic.py`
2. This will check your configuration and offer to send a test email
3. If the test fails, you may need to regenerate your app-specific password at appleid.apple.com

#### B. Scheduled Job Runs But Doesn't Send
Looking at your terminal output, the scheduled job IS running (you see the "missed by" messages), which means it's executing at 9:00 AM.

**Check if emails are being sent:**
1. Look for "Email sent successfully" messages in your terminal output
2. Check your spam/junk folder for emails from thomasderijk@me.com
3. Look for error messages about SMTP failures

#### C. Changes Detected But Status Already Updated
Once a change is detected and the email is sent, the status changes from "changed" to "unchanged" on the next check. This is normal behavior.

---

## Current Status Analysis

Based on your snapshots.json file:

**Sites with recent changes detected (Jan 24, 22:05):**
- ✓ nos.nl - Changed (this is working!)
- ✓ vacaturesuvahva.nl/HvA/search/ - Changed
- ✓ www.conservatoriumvanamsterdam.nl/vacatures/ - Changed
- ✓ www.stimuleringsfonds.nl/vacatures - Changed
- ✓ submarine.nl/careers/ - Changed

**This proves the change detection IS working!**

---

## Quick Fixes

### Fix 1: Update HTML Template
```
# Navigate to your project
cd D:\Dropbox\02_Areas\webmonitor\simple-monitor

# Backup current template
copy templates\index.html templates\index.html.backup

# Replace with fixed version
copy <path-to-new-index.html> templates\index.html

# Restart the app
```

### Fix 2: Test Email Notifications
```
# Run the diagnostic tool
python email_diagnostic.py

# Or manually test
python notifier.py
```

### Fix 3: Force a Fresh Check
1. Go to http://localhost:5000
2. Click "Check Now" button
3. Watch the terminal for email sending messages
4. Check your email inbox

---

## Expected Behavior

### When Changes Are Detected:
1. The fetcher detects content hash has changed
2. Status updates to "changed" in snapshots.json
3. Email notification is sent via send_digest_email()
4. You receive email with list of changed sites
5. On next check, status updates to "unchanged" (assuming no new changes)

### Daily Schedule:
- Checks run automatically at 9:00 AM
- Manual checks can be triggered via "Check Now" button
- Each check compares current content hash with stored hash

---

## Debugging Steps

1. **Check terminal output when clicking "Check Now":**
   - Should see "Checking: <url>" for each site
   - Should see "CHANGE DETECTED!" for changed sites
   - Should see "Connecting to smtp.mail.me.com..." when sending email
   - Should see "Email sent successfully" on success

2. **Verify email credentials:**
   - App-specific password (not regular password)
   - Username matches email address
   - SMTP server is correct for iCloud Mail

3. **Check spam folder:**
   - Emails might be going to spam
   - Add thomasderijk@me.com to contacts

4. **Test with a known-changing site:**
   - nos.nl updates frequently (good choice!)
   - Check multiple times per day to catch changes

---

## Files Provided

1. **index_fixed.html** - Fixed HTML template without encoding issues
2. **email_diagnostic.py** - Tool to test email configuration

## Need More Help?

If notifications still don't work after these fixes:
1. Run `email_diagnostic.py` and share the output
2. Share the terminal output when clicking "Check Now"
3. Check if there are any Python error messages in the terminal
4. Verify your iCloud Mail settings allow app-specific passwords
