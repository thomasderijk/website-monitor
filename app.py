from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date
import json
import os
from fetcher import check_all_sites
from notifier import send_digest_email

app = Flask(__name__)

DATA_DIR = 'data'
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
SNAPSHOTS_FILE = os.path.join(DATA_DIR, 'snapshots.json')
METADATA_FILE = os.path.join(DATA_DIR, 'metadata.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize files if they don't exist
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'sites': []}, f, indent=2)

if not os.path.exists(SNAPSHOTS_FILE):
    with open(SNAPSHOTS_FILE, 'w') as f:
        json.dump({}, f, indent=2)

if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, 'w') as f:
        json.dump({'last_check_date': None}, f, indent=2)

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.start()

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_metadata():
    with open(METADATA_FILE, 'r') as f:
        return json.load(f)

def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def has_checked_today():
    """Check if we've already run the daily check today"""
    metadata = load_metadata()
    last_check = metadata.get('last_check_date')

    if not last_check:
        return False

    today = date.today().isoformat()
    return last_check == today

def daily_check_job():
    """Run daily check and send digest email if changes detected"""
    print(f"[{datetime.now()}] Running scheduled check...")
    changes = check_all_sites()

    # Update last check date
    metadata = load_metadata()
    metadata['last_check_date'] = date.today().isoformat()
    save_metadata(metadata)

    if changes:
        send_digest_email(changes)
        print(f"Changes detected! Email sent with {len(changes)} updates.")
    else:
        print("No changes detected.")

# Schedule daily check at 9 AM
scheduler.add_job(daily_check_job, 'cron', hour=9, minute=0, id='daily_check')

def startup_check():
    """Run check on startup if we haven't checked today"""
    if not has_checked_today():
        print(f"[{datetime.now()}] No check performed today - running startup check...")
        daily_check_job()
    else:
        print(f"[{datetime.now()}] Already checked today - skipping startup check")

@app.route('/')
def index():
    config = load_config()
    
    # Load snapshots for status display
    with open(SNAPSHOTS_FILE, 'r') as f:
        snapshots = json.load(f)
    
    # Enrich sites with status info
    for site in config['sites']:
        url = site['url']
        if url in snapshots:
            site['last_check'] = snapshots[url].get('last_check', 'Never')
            site['status'] = snapshots[url].get('status', 'unknown')
        else:
            site['last_check'] = 'Never'
            site['status'] = 'new'
    
    return render_template('index.html', sites=config['sites'])

@app.route('/api/sites', methods=['GET'])
def get_sites():
    config = load_config()

    # Load snapshots to enrich with status
    with open(SNAPSHOTS_FILE, 'r') as f:
        snapshots = json.load(f)

    # Enrich sites with status info
    for site in config['sites']:
        url = site['url']
        if url in snapshots:
            site['last_check'] = snapshots[url].get('last_check', 'Never')
            site['status'] = snapshots[url].get('status', 'unknown')
        else:
            site['last_check'] = 'Never'
            site['status'] = 'new'

    response = jsonify(config['sites'])
    # Prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/sites', methods=['POST'])
def add_site():
    data = request.json
    url = data.get('url', '').strip()
    category = data.get('category', '').strip()
    selector = data.get('selector', '').strip()

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    config = load_config()

    # Check if URL already exists
    if any(site['url'] == url for site in config['sites']):
        return jsonify({'error': 'URL already monitored'}), 400

    site_config = {
        'url': url,
        'category': category or 'Uncategorized',
        'added': datetime.now().isoformat()
    }

    # Only add selector if provided
    if selector:
        site_config['selector'] = selector

    config['sites'].append(site_config)

    save_config(config)
    return jsonify({'success': True})

@app.route('/api/sites/<int:index>', methods=['DELETE'])
def delete_site(index):
    config = load_config()

    if index < 0 or index >= len(config['sites']):
        return jsonify({'error': 'Invalid index'}), 400

    removed = config['sites'].pop(index)
    save_config(config)

    # Also remove from snapshots
    with open(SNAPSHOTS_FILE, 'r') as f:
        snapshots = json.load(f)

    if removed['url'] in snapshots:
        del snapshots[removed['url']]
        with open(SNAPSHOTS_FILE, 'w') as f:
            json.dump(snapshots, f, indent=2)

    return jsonify({'success': True})

@app.route('/api/sites/<int:index>/category', methods=['PATCH'])
def update_category(index):
    config = load_config()

    if index < 0 or index >= len(config['sites']):
        return jsonify({'error': 'Invalid index'}), 400

    data = request.json
    new_category = data.get('category', '').strip()

    if not new_category:
        new_category = 'Uncategorized'

    config['sites'][index]['category'] = new_category
    save_config(config)

    return jsonify({'success': True, 'category': new_category})

@app.route('/api/check-now', methods=['POST'])
def check_now():
    """Manually trigger a check of all sites"""
    changes = check_all_sites()
    
    if changes:
        send_digest_email(changes)
        return jsonify({
            'success': True,
            'changes': len(changes),
            'message': f'Found {len(changes)} change(s). Email sent!'
        })
    else:
        return jsonify({
            'success': True,
            'changes': 0,
            'message': 'No changes detected.'
        })

if __name__ == '__main__':
    print("=" * 50)
    print("Website Monitor Started")
    print("=" * 50)
    print(f"Web GUI: http://localhost:5000")
    print(f"Daily check scheduled: 9:00 AM")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    # Run startup check if needed
    startup_check()

    app.run(debug=True, use_reloader=False)
