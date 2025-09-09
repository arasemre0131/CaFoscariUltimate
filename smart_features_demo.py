#!/usr/bin/env python3
"""
Smart Features Demo - Show new contact system and unique mock exams
"""
from main import CaFoscariUltimate

def demo_smart_features():
    print("🚀 SMART FEATURES DEMO")
    print("="*50)
    
    # Initialize system
    system = CaFoscariUltimate()
    
    print("\n🧠 NEW SMART EMAIL FEATURES:")
    print("✅ Contact recognition by name")
    print("✅ Smart message extraction")
    print("✅ Auto subject generation")
    print("✅ Natural Turkish language support")
    
    print("\n📧 SMART EMAIL EXAMPLES:")
    print("--" * 30)
    
    # Test smart email commands
    test_commands = [
        "erdeme anneni yırtayım diye mail gönder",
        "sonere merhaba nasılsın yolla",
        "emreye önemli bir konu hakkında email at"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}. User says: '{command}'")
        print("   → Claude will:")
        
        # Simulate contact recognition
        user_input_lower = command.lower()
        found_contact = None
        
        for contact_name, email in system.contacts.items():
            if contact_name in user_input_lower:
                found_contact = contact_name
                found_email = email
                break
        
        if found_contact:
            print(f"     ✅ Find contact: {found_contact}")
            print(f"     ✅ Get email: {found_email}")
            print(f"     ✅ Extract clean message")
            print(f"     ✅ Send email automatically")
        
    print("\n📚 UNIQUE MOCK EXAM SYSTEM:")
    print("--" * 30)
    print("✅ Each exam is completely different")
    print("✅ Random exam styles: theoretical, practical, mixed, etc.")
    print("✅ Tracks previous exams to ensure uniqueness")
    print("✅ Varies difficulty and question types")
    
    print(f"\n📋 CURRENT CONTACTS:")
    for name, email in system.contacts.items():
        print(f"  {name}: {email}")
    
    print("\n" + "="*50)
    print("🎯 SMART FEATURES READY!")
    print("Try: python3 main.py → Chat Mode")
    print("Say: 'erdeme anneni yırtayım diye mail gönder'")
    print("="*50)

if __name__ == "__main__":
    demo_smart_features()