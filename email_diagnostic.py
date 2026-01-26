"""
Email Notification Diagnostic Tool
Tests the email configuration and shows what's happening with notifications
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from notifier import send_digest_email, SMTP_SERVER, SMTP_USERNAME, TO_EMAIL
from datetime import datetime
import json

def check_email_config():
    """Check if email configuration looks valid"""
    print("=== EMAIL CONFIGURATION CHECK ===\n")
    
    print(f"SMTP Server: {SMTP_SERVER}")
    print(f"SMTP Username: {SMTP_USERNAME}")
    print(f"To Email: {TO_EMAIL}")
    
    if not SMTP_USERNAME or not TO_EMAIL:
        print("\n[ERROR] Email configuration is incomplete!")
        return False
    
    print("\n[OK] Email configuration appears complete")
    return True

def send_test_email():
    """Send a test email"""
    print("\n=== SENDING TEST EMAIL ===\n")
    
    test_changes = [{
        'url': 'https://example.com/test-page',
        'category': 'Test Category',
        'detected_at': datetime.now().isoformat(),
        'previous_hash': 'abc123',
        'new_hash': 'def456'
    }]
    
    print("Attempting to send test email...")
    result = send_digest_email(test_changes)
    
    if result:
        print("\n[SUCCESS] Test email sent successfully!")
        print(f"Check your inbox at {TO_EMAIL}")
        return True
    else:
        print("\n[FAILED] Could not send test email")
        print("\nTroubleshooting:")
        print("1. Check if you're using an app-specific password (not your regular password)")
        print("2. For Apple Mail: Go to appleid.apple.com > Security > App-Specific Passwords")
        print("3. Check if your email credentials in notifier.py are correct")
        return False

def check_recent_changes():
    """Check if there are any recent changes in snapshots"""
    print("\n=== CHECKING RECENT CHANGES ===\n")
    
    snapshots_file = os.path.join('data', 'snapshots.json')
    
    if not os.path.exists(snapshots_file):
        print("[INFO] No snapshots file found")
        return
    
    with open(snapshots_file, 'r') as f:
        snapshots = json.load(f)
    
    changed_sites = []
    for url, data in snapshots.items():
        if data.get('status') == 'changed':
            changed_sites.append({
                'url': url,
                'last_check': data.get('last_check', 'Unknown'),
                'status': data.get('status')
            })
    
    if changed_sites:
        print(f"Found {len(changed_sites)} sites with changes detected:\n")
        for site in changed_sites:
            print(f"  URL: {site['url']}")
            print(f"  Last Check: {site['last_check']}")
            print(f"  Status: {site['status']}\n")
    else:
        print("[INFO] No sites showing 'changed' status")
        print("This could mean:")
        print("1. No changes have been detected yet")
        print("2. Changes were detected but status was updated after email was sent")

def main():
    print("\n" + "="*60)
    print(" WEBSITE MONITOR - EMAIL DIAGNOSTIC TOOL")
    print("="*60 + "\n")
    
    # Step 1: Check configuration
    if not check_email_config():
        return
    
    # Step 2: Check recent changes
    check_recent_changes()
    
    # Step 3: Offer to send test email
    print("\n" + "="*60)
    response = input("\nDo you want to send a test email? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        send_test_email()
    else:
        print("\nTest email skipped")
    
    print("\n" + "="*60)
    print("Diagnostic complete")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
