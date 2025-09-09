#!/usr/bin/env python3
"""
Quick Email Sender - Send email to sonerozen2004@gmail.com
"""
from main import CaFoscariUltimate

def send_quick_email():
    print("🚀 Quick Email Sender - Ca' Foscari Ultimate")
    print("=" * 50)
    
    # Initialize system
    system = CaFoscariUltimate()
    
    # Send the requested email
    to_email = "sonerozen2004@gmail.com"
    subject = "merhaba sonnnner"
    message = "Merhaba sonnnner! Ca' Foscari Ultimate sistemi üzerinden gönderildi."
    
    print(f"📧 Sending email to: {to_email}")
    print(f"📋 Subject: {subject}")
    print(f"💬 Message: {message}")
    print()
    
    success = system.send_email(to_email, subject, message)
    
    if success:
        print("\n✅ Email sent successfully!")
    else:
        print("\n❌ Failed to send email. Please check Gmail integration.")

if __name__ == "__main__":
    send_quick_email()