# Website Monitor

A lightweight Python web app that monitors websites for changes and sends email notifications when updates are detected. Includes a dark-themed web GUI for managing monitored sites.

## Features

- Daily automated checks at 9:00 AM (+ startup check if missed)
- Email digest notifications when changes are detected
- Content-aware change detection (ignores scripts, styles, ads)
- Optional CSS selectors for targeted monitoring
- Editable site titles and categories
- Sort by last changed or by category
- Error tracking for unreachable sites

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd website-monitor
pip install -r requirements.txt
```

### 2. Configure email

Copy the example environment file and fill in your email credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your details. See the provider-specific instructions below.

#### Apple Mail (iCloud)

```
SMTP_SERVER=smtp.mail.me.com
SMTP_PORT=587
SMTP_USERNAME=your-email@me.com
SMTP_PASSWORD=your-app-specific-password
FROM_EMAIL=your-email@me.com
TO_EMAIL=your-email@me.com
```

You need an **app-specific password** (not your regular iCloud password):
1. Go to https://appleid.apple.com
2. Sign in and navigate to **Sign-In and Security > App-Specific Passwords**
3. Generate a new password and paste it in `.env`

#### Gmail

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
TO_EMAIL=your-email@gmail.com
```

You need an **app password** (not your regular Google password):
1. Enable 2-Factor Authentication on your Google account if you haven't already
2. Go to https://myaccount.google.com/apppasswords
3. Select **Mail** as the app and generate a password
4. Paste the 16-character password in `.env`

#### Other providers

Use the SMTP settings from your email provider. Common ones:

| Provider     | SMTP Server          | Port |
|-------------|----------------------|------|
| Outlook     | smtp.office365.com   | 587  |
| Yahoo       | smtp.mail.yahoo.com  | 587  |
| Fastmail    | smtp.fastmail.com    | 587  |

### 3. Test email (optional)

```bash
python notifier.py
```

This sends a test email to verify your configuration.

### 4. Run the app

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## Usage

### Adding sites
Enter a URL in the input field and click **Add Site**. You can optionally set a category and a CSS selector for targeted monitoring. URLs without `https://` are auto-completed.

### CSS selectors
If a site triggers false positives (e.g. timestamps or ads change the hash), add a CSS selector to only monitor specific parts of the page. For example: `#main-content`, `.article-body`, `div.vacatures`.

### Editing entries
- Click a **category badge** to change the category (select existing or type a new one)
- Click the **pencil icon** to rename a site (manually set titles won't be overwritten by automatic title detection)
- Click the **x icon** to remove a site (with confirmation)

### Sorting
Use the dropdown to sort by:
- **Last Changed** - most recently changed sites appear first
- **Category** - sites grouped under category headers

### Manual check
Click **Check Now** to trigger an immediate check of all sites.

## File structure

```
website-monitor/
├── app.py              # Flask web server + scheduler
├── fetcher.py          # Site fetching, hashing, change detection
├── notifier.py         # Email notifications
├── requirements.txt    # Python dependencies
├── .env                # Your email credentials (not in git)
├── .env.example        # Template for new users
├── .gitignore          # Keeps secrets and user data out of git
├── templates/
│   └── index.html      # Web GUI
└── data/               # Created automatically on first run
    ├── config.json     # Monitored sites list
    ├── snapshots.json  # Content hashes and status
    └── metadata.json   # Scheduler metadata
```

## Customization

### Change check schedule

Edit `app.py`, find the `scheduler.add_job` line:

```python
# Current: Daily at 9:00 AM
scheduler.add_job(daily_check_job, 'cron', hour=9, minute=0, ...)

# Every 6 hours:
scheduler.add_job(daily_check_job, 'interval', hours=6, ...)

# Every Monday at 10:30 AM:
scheduler.add_job(daily_check_job, 'cron', day_of_week='mon', hour=10, minute=30, ...)
```

### Change port

Edit the last line of `app.py`:

```python
app.run(debug=True, use_reloader=False, port=8080)
```

## Running on startup (Windows)

### Option A: Task Scheduler (recommended)
1. Open **Task Scheduler** and create a new basic task
2. Trigger: **When the computer starts** or **When I log on**
3. Action: Start a program
4. Program: path to `pythonw.exe` (e.g. `C:\Python311\pythonw.exe`)
5. Arguments: `app.py`
6. Start in: the full path to this folder

### Option B: Startup folder
1. Create a `.bat` file:
   ```bat
   @echo off
   cd /d "C:\path\to\website-monitor"
   pythonw app.py
   ```
2. Press `Win+R`, type `shell:startup`, press Enter
3. Place the `.bat` file in that folder

Note: Use `pythonw.exe` (not `python.exe`) to run without a visible terminal window.

## Troubleshooting

**Email not sending?**
- Make sure you're using an app-specific password, not your regular password
- Verify SMTP settings in `.env`
- Run `python notifier.py` to test

**Changes detected every check (false positives)?**
- The site likely has dynamic content (timestamps, ads, session IDs)
- Add a CSS selector to monitor only the relevant part of the page

**Site showing as unreachable?**
- Some sites block automated requests
- Check if the URL is correct and includes `https://`

---

Built with Flask, APScheduler, requests, and BeautifulSoup.
