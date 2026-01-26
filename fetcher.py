import requests
import hashlib
import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

SNAPSHOTS_FILE = 'data/snapshots.json'
CONFIG_FILE = 'data/config.json'

def clean_html_content(html):
    """Clean HTML content to reduce false positives"""
    soup = BeautifulSoup(html, 'html.parser')

    # Remove dynamic elements that change frequently
    for tag in soup(['script', 'style', 'noscript', 'iframe']):
        tag.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, type(soup))):
        comment.extract()

    # Get text content
    text = soup.get_text()

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text

def extract_content_by_selector(html, selector):
    """Extract specific content using CSS selector"""
    soup = BeautifulSoup(html, 'html.parser')

    # Find elements matching the selector
    elements = soup.select(selector)

    if not elements:
        # Fallback to full content if selector doesn't match
        return clean_html_content(html)

    # Combine all matching elements
    combined_html = ''.join(str(elem) for elem in elements)
    return clean_html_content(combined_html)

def get_page_title(html):
    """Extract page title from HTML"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        return None
    except:
        return None

def get_page_hash(url, selector=None):
    """Fetch a URL and return its content hash"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Extract page title
        page_title = get_page_title(response.text)

        # Process content based on selector
        if selector:
            content = extract_content_by_selector(response.text, selector)
        else:
            content = clean_html_content(response.text)

        # Hash the cleaned content
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        return {
            'hash': content_hash,
            'title': page_title,
            'status': 'success',
            'status_code': response.status_code
        }
    except requests.exceptions.RequestException as e:
        return {
            'hash': None,
            'title': None,
            'status': 'error',
            'error': str(e)
        }

def load_snapshots():
    """Load existing snapshots from JSON"""
    if os.path.exists(SNAPSHOTS_FILE):
        with open(SNAPSHOTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_snapshots(snapshots):
    """Save snapshots to JSON"""
    with open(SNAPSHOTS_FILE, 'w') as f:
        json.dump(snapshots, f, indent=2)

def load_config():
    """Load site configuration"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    """Save site configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def check_all_sites():
    """Check all monitored sites for changes"""
    config = load_config()
    snapshots = load_snapshots()
    changes = []
    config_changed = False

    for site in config['sites']:
        url = site['url']
        category = site.get('category', 'Uncategorized')
        selector = site.get('selector', None)

        print(f"Checking: {url}")
        if selector:
            print(f"  Using selector: {selector}")

        result = get_page_hash(url, selector)
        current_time = datetime.now().isoformat()

        # Update title if we got one
        if result.get('title') and result['title'] != site.get('title'):
            site['title'] = result['title']
            config_changed = True
            print(f"  Updated title: {result['title']}")

        if result['status'] == 'error':
            # Update snapshot with error status
            snapshots[url] = {
                'last_check': current_time,
                'status': 'error',
                'error': result['error']
            }
            print(f"  ✗ Error: {result['error']}")
            continue
        
        current_hash = result['hash']
        
        # Check if this is a new site or if content changed
        if url not in snapshots:
            # First time checking this site
            snapshots[url] = {
                'hash': current_hash,
                'last_check': current_time,
                'status': 'baseline'
            }
            print(f"  → Baseline recorded")
        else:
            previous_hash = snapshots[url].get('hash')
            
            if previous_hash != current_hash:
                # Content changed!
                changes.append({
                    'url': url,
                    'category': category,
                    'previous_hash': previous_hash,
                    'new_hash': current_hash,
                    'detected_at': current_time
                })
                
                snapshots[url] = {
                    'hash': current_hash,
                    'last_check': current_time,
                    'status': 'changed',
                    'previous_hash': previous_hash
                }
                print(f"  ✓ CHANGE DETECTED!")
            else:
                # No change
                snapshots[url]['last_check'] = current_time
                snapshots[url]['status'] = 'unchanged'
                print(f"  - No change")

    save_snapshots(snapshots)

    # Save config if titles were updated
    if config_changed:
        save_config(config)

    return changes

if __name__ == '__main__':
    # For testing
    print("Running manual check...")
    changes = check_all_sites()
    if changes:
        print(f"\n{len(changes)} change(s) detected:")
        for change in changes:
            print(f"  - {change['url']} ({change['category']})")
    else:
        print("\nNo changes detected.")
