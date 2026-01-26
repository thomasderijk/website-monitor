# Website Monitor

Simple cross-platform website change detection with email alerts.

## Features

- ✅ Monitor dozens of websites with hash-based change detection
- ✅ Daily automated checks (9 AM scheduled)
- ✅ Email digest notifications (one email per day with all changes)
- ✅ Web dashboard to manage URLs
- ✅ Optional categories for organization
- ✅ Manual "Check Now" button
- ✅ Works on Windows & Mac

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Email (Apple Mail)

Edit `notifier.py` and update these lines with your Apple Mail credentials:

```python
SMTP_USERNAME = 'your-email@icloud.com'
SMTP_PASSWORD = 'your-app-specific-password'
FROM_EMAIL = 'your-email@icloud.com'
TO_EMAIL = 'your-email@icloud.com'
```

**Important:** You need an app-specific password, not your regular iCloud password:
1. Go to https://appleid.apple.com
2. Sign in → Security section
3. Click "Generate Password" under App-Specific Passwords
4. Use this password in `notifier.py`

### 3. Test Email Configuration

```bash
python notifier.py
```

This sends a test email. If successful, you're ready!

## Usage

### Start the Monitor

```bash
python app.py
```

This will:
- Start the web dashboard at http://localhost:5000
- Schedule daily checks at 9:00 AM
- Keep running until you press Ctrl+C

### Add Websites

1. Open http://localhost:5000 in your browser
2. Enter a URL (e.g., `https://example.com`)
3. Optionally add a category (e.g., `News`, `Shopping`, `Work`)
4. Click "Add Site"

### Check Manually

Click the green "Check Now" button in the dashboard to run an immediate check.

### Remove Sites

Click the red "Remove" button next to any site.

## How It Works

1. **Hash Comparison:** Fetches each page's HTML content and creates a SHA-256 hash
2. **Change Detection:** Compares current hash with previous snapshot
3. **Notifications:** Sends one digest email with all detected changes
4. **Storage:** Uses JSON files in `data/` directory
   - `config.json` - Your monitored URLs and categories
   - `snapshots.json` - Last known hashes and timestamps

## File Structure

```
simple-monitor/
├── app.py              # Flask app + APScheduler
├── fetcher.py          # Hash-based change detection
├── notifier.py         # Email sender (configure this!)
├── requirements.txt    # Python dependencies
├── data/
│   ├── config.json     # Your sites
│   └── snapshots.json  # Hashes
└── templates/
    └── index.html      # Dashboard UI
```

## Customization

### Change Check Schedule

Edit `app.py`, line with `scheduler.add_job`:

```python
# Current: Daily at 9:00 AM
scheduler.add_job(daily_check_job, 'cron', hour=9, minute=0)

# Every 6 hours:
scheduler.add_job(daily_check_job, 'interval', hours=6)

# Every Monday at 10:30 AM:
scheduler.add_job(daily_check_job, 'cron', day_of_week='mon', hour=10, minute=30)
```

### Change Port

Edit `app.py`, last line:

```python
app.run(debug=True, use_reloader=False, port=8080)  # Use port 8080 instead
```

## Troubleshooting

**Email not sending?**
- Verify your app-specific password (not regular iCloud password)
- Check SMTP settings in `notifier.py`
- Run `python notifier.py` to test

**Site not being checked?**
- Some sites block automated requests
- Check the dashboard status column for errors

**Changes not detected?**
- Some sites update timestamps/ads constantly (hash changes on every load)
- Consider using a more selective approach if needed

## Platform Notes

- **Mac:** Works out of the box
- **Windows:** Same setup, just use Command Prompt or PowerShell

## Safety

- Starts manually (not as background service by default)
- Press Ctrl+C to stop at any time
- Data stored locally in JSON files
- No external dependencies except SMTP for email

---

Built with Flask, APScheduler, and requests. Inspired by changedetection.io.
