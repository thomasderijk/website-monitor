import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Email configuration - set these in your .env file (see .env.example)
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.mail.me.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', '')
TO_EMAIL = os.getenv('TO_EMAIL', '')

def send_digest_email(changes):
    """Send a single digest email with all detected changes"""
    
    if not changes:
        return
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Website Monitor: {len(changes)} Change(s) Detected'
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    
    # Build email body
    text_parts = [
        f"Website Change Detection Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\n{len(changes)} website(s) changed:\n",
        "=" * 60
    ]
    
    html_parts = [
        "<html><body style='font-family: Arial, sans-serif;'>",
        f"<h2>Website Change Detection Report</h2>",
        f"<p><small>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>",
        f"<p><strong>{len(changes)} website(s) changed:</strong></p>",
        "<hr>"
    ]
    
    # Group by category
    by_category = {}
    for change in changes:
        category = change.get('category', 'Uncategorized')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(change)
    
    # Add each change
    for category, category_changes in sorted(by_category.items()):
        text_parts.append(f"\n📁 {category}")
        html_parts.append(f"<h3>📁 {category}</h3><ul>")
        
        for change in category_changes:
            url = change['url']
            detected_at = change['detected_at']
            
            text_parts.append(f"  • {url}")
            text_parts.append(f"    Detected: {detected_at}")
            
            html_parts.append(f"<li>")
            html_parts.append(f"<a href='{url}'>{url}</a>")
            html_parts.append(f"<br><small>Detected: {detected_at}</small>")
            html_parts.append(f"</li>")
        
        text_parts.append("")
        html_parts.append("</ul>")
    
    text_parts.append("=" * 60)
    text_parts.append("\nThis is an automated message from Website Monitor.")
    
    html_parts.append("<hr>")
    html_parts.append("<p><small>This is an automated message from Website Monitor.</small></p>")
    html_parts.append("</body></html>")
    
    # Attach both plain text and HTML versions
    text_body = '\n'.join(text_parts)
    html_body = '\n'.join(html_parts)
    
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    # Send email
    try:
        print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        
        print("Logging in...")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        print("Sending email...")
        server.send_message(msg)
        server.quit()
        
        print(f"✓ Digest email sent successfully to {TO_EMAIL}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to send email: {e}")
        return False

def test_email_config():
    """Test email configuration with a simple test message"""
    test_change = [{
        'url': 'https://example.com',
        'category': 'Test',
        'detected_at': datetime.now().isoformat()
    }]
    
    print("Testing email configuration...")
    success = send_digest_email(test_change)
    
    if success:
        print("\n✓ Email test successful! Check your inbox.")
    else:
        print("\n✗ Email test failed. Please check your credentials.")
        print("\nFor Apple Mail, you need an app-specific password:")
        print("1. Go to appleid.apple.com")
        print("2. Sign in and go to Security section")
        print("3. Generate an app-specific password")
        print("4. Use that password in notifier.py (not your regular password)")

if __name__ == '__main__':
    # Run email test
    test_email_config()
