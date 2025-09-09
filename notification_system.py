#!/usr/bin/env python3
"""
Akıllı Bildirim Sistemi
Moodle, Gmail ve çalışma planı verilerini analiz ederek önemli bildiriler gönderir
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationSystem:
    def __init__(self, config_file: str = "notification_config.json"):
        """
        Bildirim sistemi başlatıcısı
        Args:
            config_file: Bildirim yapılandırma dosyası
        """
        self.config_file = config_file
        self.config = self._load_or_create_config()
        self.notification_history = self._load_notification_history()
        
    def _load_or_create_config(self) -> Dict:
        """Bildirim yapılandırmasını yükle veya oluştur"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Varsayılan yapılandırma
        config = {
            'notification_methods': {
                'desktop': True,
                'email': False,
                'sound': True,
                'file_log': True
            },
            'email_settings': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': '',
                'sender_password': '',
                'recipient_email': ''
            },
            'notification_rules': {
                'critical_assignments': {
                    'enabled': True,
                    'days_before': 3,
                    'repeat_hours': 6
                },
                'exam_reminders': {
                    'enabled': True,
                    'days_before': [7, 3, 1],
                    'times': ['09:00', '18:00']
                },
                'high_priority_emails': {
                    'enabled': True,
                    'immediate': True
                },
                'study_plan_reminders': {
                    'enabled': True,
                    'daily_time': '20:00'
                },
                'mock_exam_schedule': {
                    'enabled': True,
                    'hours_before': 2
                }
            },
            'quiet_hours': {
                'enabled': True,
                'start_time': '22:00',
                'end_time': '08:00'
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return config
    
    def _load_notification_history(self) -> Dict:
        """Bildirim geçmişini yükle"""
        history_file = "notification_history.json"
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'notifications': [], 'last_check': None}
    
    def _save_notification_history(self):
        """Bildirim geçmişini kaydet"""
        with open("notification_history.json", 'w', encoding='utf-8') as f:
            json.dump(self.notification_history, f, indent=2, ensure_ascii=False, default=str)
    
    def _is_quiet_hours(self) -> bool:
        """Sessiz saatlerde miyiz?"""
        if not self.config['quiet_hours']['enabled']:
            return False
        
        now = datetime.now().time()
        start_time = datetime.strptime(self.config['quiet_hours']['start_time'], '%H:%M').time()
        end_time = datetime.strptime(self.config['quiet_hours']['end_time'], '%H:%M').time()
        
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:  # Gece geçişi
            return now >= start_time or now <= end_time
    
    def send_desktop_notification(self, title: str, message: str, urgency: str = "normal"):
        """macOS desktop bildirimi gönder"""
        if not self.config['notification_methods']['desktop']:
            return
        
        if self._is_quiet_hours() and urgency != "critical":
            return
        
        try:
            # macOS için osascript kullan
            script = f'''
            display notification "{message}" with title "{title}" sound name "default"
            '''
            subprocess.run(['osascript', '-e', script], check=True, capture_output=True)
            
        except Exception as e:
            print(f"❌ Desktop bildirim hatası: {e}")
    
    def send_email_notification(self, subject: str, body: str):
        """Email bildirimi gönder"""
        if not self.config['notification_methods']['email']:
            return
        
        email_settings = self.config['email_settings']
        if not email_settings['sender_email'] or not email_settings['recipient_email']:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_settings['sender_email']
            msg['To'] = email_settings['recipient_email']
            msg['Subject'] = f"[Ca' Foscari System] {subject}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_settings['smtp_server'], email_settings['smtp_port'])
            server.starttls()
            server.login(email_settings['sender_email'], email_settings['sender_password'])
            
            text = msg.as_string()
            server.sendmail(email_settings['sender_email'], email_settings['recipient_email'], text)
            server.quit()
            
            print("✅ Email bildirimi gönderildi")
            
        except Exception as e:
            print(f"❌ Email bildirim hatası: {e}")
    
    def log_notification(self, notification_type: str, title: str, message: str, urgency: str = "normal"):
        """Bildirimi kaydet"""
        if self.config['notification_methods']['file_log']:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': notification_type,
                'title': title,
                'message': message,
                'urgency': urgency
            }
            
            self.notification_history['notifications'].append(log_entry)
            self._save_notification_history()
    
    def send_notification(self, notification_type: str, title: str, message: str, urgency: str = "normal"):
        """Bildirim gönder (tüm aktif yöntemlerle)"""
        # Desktop bildirimi
        self.send_desktop_notification(title, message, urgency)
        
        # Email bildirimi (kritik durumlar için)
        if urgency == "critical":
            self.send_email_notification(title, message)
        
        # Ses bildirimi
        if self.config['notification_methods']['sound'] and urgency == "critical":
            self.play_notification_sound()
        
        # Loga kaydet
        self.log_notification(notification_type, title, message, urgency)
        
        print(f"🔔 [{urgency.upper()}] {title}: {message}")
    
    def play_notification_sound(self):
        """Bildirim sesi çal"""
        try:
            # macOS için ses çal
            subprocess.run(['afplay', '/System/Library/Sounds/Sosumi.aiff'], check=True)
        except:
            pass
    
    def load_all_data(self) -> Dict:
        """Tüm sistem verilerini yükle"""
        data = {}
        
        files_to_load = [
            'moodle_data.json',
            'gmail_analysis.json', 
            'content_analysis.json',
            'manual_exams.json',
            'comprehensive_study_plan.json'
        ]
        
        for filename in files_to_load:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        key = filename.replace('.json', '')
                        data[key] = json.load(f)
                except Exception as e:
                    print(f"⚠️  {filename} yükleme hatası: {e}")
        
        return data
    
    def check_critical_assignments(self, data: Dict) -> List[Dict]:
        """Kritik ödevleri kontrol et"""
        notifications = []
        
        if 'moodle_data' not in data:
            return notifications
        
        assignments = data['moodle_data'].get('assignments', [])
        critical_days = self.config['notification_rules']['critical_assignments']['days_before']
        
        for assignment in assignments:
            if assignment.get('priority') in ['CRITICAL', 'HIGH']:
                try:
                    if assignment.get('due_date'):
                        # Tarih parsing
                        if isinstance(assignment['due_date'], str):
                            if 'T' in assignment['due_date']:
                                due_date = datetime.fromisoformat(assignment['due_date'].replace('Z', '+00:00'))
                            else:
                                due_date = datetime.strptime(assignment['due_date'], '%Y-%m-%d')
                        else:
                            due_date = assignment['due_date']
                        
                        days_until = (due_date.replace(tzinfo=None) - datetime.now()).days
                        
                        if 0 <= days_until <= critical_days:
                            urgency = "critical" if days_until <= 1 else "high"
                            
                            notifications.append({
                                'type': 'critical_assignment',
                                'title': '⚠️ KRİTİK ÖDEV',
                                'message': f"{assignment['name']} - {days_until} gün kaldı!",
                                'urgency': urgency,
                                'data': assignment
                            })
                except Exception as e:
                    print(f"⚠️  Ödev tarih parsing hatası: {e}")
        
        return notifications
    
    def check_exam_reminders(self, data: Dict) -> List[Dict]:
        """Sınav hatırlatmalarını kontrol et"""
        notifications = []
        
        if 'manual_exams' not in data:
            return notifications
        
        exams = data['manual_exams']
        reminder_days = self.config['notification_rules']['exam_reminders']['days_before']
        
        for exam in exams:
            try:
                exam_date = datetime.strptime(exam['exam_date'], '%Y-%m-%d')
                days_until = (exam_date - datetime.now()).days
                
                if days_until in reminder_days:
                    if days_until <= 1:
                        urgency = "critical"
                        icon = "🚨"
                    elif days_until <= 3:
                        urgency = "high"
                        icon = "⚠️"
                    else:
                        urgency = "normal"
                        icon = "📅"
                    
                    notifications.append({
                        'type': 'exam_reminder',
                        'title': f'{icon} SINAV HATIRLATMASI',
                        'message': f"{exam['course']} - {exam['exam_name']} ({days_until} gün)",
                        'urgency': urgency,
                        'data': exam
                    })
            except Exception as e:
                print(f"⚠️  Sınav tarih parsing hatası: {e}")
        
        return notifications
    
    def check_high_priority_emails(self, data: Dict) -> List[Dict]:
        """Yüksek öncelikli emailleri kontrol et"""
        notifications = []
        
        if 'gmail_analysis' not in data:
            return notifications
        
        emails = data['gmail_analysis']
        if not isinstance(emails, list):
            return notifications
        
        # Son kontrol zamanını al
        last_check = self.notification_history.get('last_check')
        if last_check:
            last_check_dt = datetime.fromisoformat(last_check)
        else:
            last_check_dt = datetime.now() - timedelta(hours=1)
        
        for email in emails:
            if email.get('priority_level') in ['CRITICAL', 'HIGH']:
                try:
                    email_date = datetime.fromisoformat(email['date'])
                    
                    # Yeni email mi?
                    if email_date > last_check_dt:
                        notifications.append({
                            'type': 'high_priority_email',
                            'title': '📧 ÖNEMLİ MAİL',
                            'message': f"{email['from']}: {email['subject'][:50]}...",
                            'urgency': 'high' if email['priority_level'] == 'CRITICAL' else 'normal',
                            'data': email
                        })
                except Exception as e:
                    print(f"⚠️  Email tarih parsing hatası: {e}")
        
        return notifications
    
    def check_study_plan_reminders(self, data: Dict) -> List[Dict]:
        """Çalışma planı hatırlatmalarını kontrol et"""
        notifications = []
        
        if 'comprehensive_study_plan' not in data:
            return notifications
        
        study_plan = data['comprehensive_study_plan']
        daily_schedules = study_plan.get('daily_schedules', [])
        
        # Bugünün planını bul
        today = datetime.now().strftime('%Y-%m-%d')
        today_schedule = None
        
        for schedule in daily_schedules:
            if schedule['date'] == today:
                today_schedule = schedule
                break
        
        if today_schedule:
            # Yüksek öncelikli görevler var mı?
            high_priority_blocks = [
                block for block in today_schedule.get('study_blocks', [])
                if block.get('priority') == 'HIGH'
            ]
            
            if high_priority_blocks:
                notifications.append({
                    'type': 'study_plan_reminder',
                    'title': '📚 ÇALIŞMA PLANI',
                    'message': f"Bugün {len(high_priority_blocks)} yüksek öncelikli görev var!",
                    'urgency': 'normal',
                    'data': today_schedule
                })
        
        return notifications
    
    def check_mock_exam_schedule(self, data: Dict) -> List[Dict]:
        """Mock sınav programını kontrol et"""
        notifications = []
        
        # Mock sınav dosyalarını tara
        mock_exam_files = [f for f in os.listdir('.') if f.startswith('mock_exam_series_') and f.endswith('.json')]
        
        hours_before = self.config['notification_rules']['mock_exam_schedule']['hours_before']
        
        for filename in mock_exam_files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    series_data = json.load(f)
                
                for exam in series_data.get('exam_schedule', []):
                    exam_datetime_str = f"{exam['scheduled_date']} {exam['scheduled_time']}"
                    exam_datetime = datetime.strptime(exam_datetime_str, '%Y-%m-%d %H:%M')
                    
                    time_until = (exam_datetime - datetime.now()).total_seconds() / 3600  # saat cinsinden
                    
                    if 0 <= time_until <= hours_before:
                        notifications.append({
                            'type': 'mock_exam_reminder',
                            'title': '📝 MOCK SINAV',
                            'message': f"{exam['title']} - {int(time_until)} saat kaldı!",
                            'urgency': 'normal',
                            'data': exam
                        })
            except Exception as e:
                print(f"⚠️  Mock sınav dosyası okuma hatası: {e}")
        
        return notifications
    
    def run_notification_check(self) -> Dict:
        """Tüm bildirimleri kontrol et ve gönder"""
        print("\n🔔 Bildirim kontrolü yapılıyor...")
        
        # Tüm verileri yükle
        data = self.load_all_data()
        
        all_notifications = []
        
        # Farklı bildirim türlerini kontrol et
        check_functions = [
            self.check_critical_assignments,
            self.check_exam_reminders,
            self.check_high_priority_emails,
            self.check_study_plan_reminders,
            self.check_mock_exam_schedule
        ]
        
        for check_func in check_functions:
            try:
                notifications = check_func(data)
                all_notifications.extend(notifications)
            except Exception as e:
                print(f"⚠️  Bildirim kontrol hatası ({check_func.__name__}): {e}")
        
        # Bildirimleri gönder
        sent_notifications = []
        for notification in all_notifications:
            # Duplicate kontrolü (son 1 saat içinde aynı bildirim gönderilmiş mi?)
            if not self._is_duplicate_notification(notification):
                self.send_notification(
                    notification['type'],
                    notification['title'],
                    notification['message'],
                    notification['urgency']
                )
                sent_notifications.append(notification)
        
        # Son kontrol zamanını güncelle
        self.notification_history['last_check'] = datetime.now().isoformat()
        self._save_notification_history()
        
        result = {
            'check_time': datetime.now().isoformat(),
            'total_checks': len(all_notifications),
            'sent_notifications': len(sent_notifications),
            'notifications': sent_notifications
        }
        
        print(f"✅ Bildirim kontrolü tamamlandı: {len(sent_notifications)} bildirim gönderildi")
        
        return result
    
    def _is_duplicate_notification(self, notification: Dict) -> bool:
        """Duplicate bildirim kontrolü"""
        recent_notifications = [
            n for n in self.notification_history['notifications']
            if datetime.now() - datetime.fromisoformat(n['timestamp']) < timedelta(hours=1)
        ]
        
        for recent in recent_notifications:
            if (recent['type'] == notification['type'] and 
                recent['title'] == notification['title']):
                return True
        
        return False
    
    def get_notification_stats(self) -> Dict:
        """Bildirim istatistiklerini getir"""
        history = self.notification_history['notifications']
        
        # Son 7 gün
        week_ago = datetime.now() - timedelta(days=7)
        recent_notifications = [
            n for n in history
            if datetime.fromisoformat(n['timestamp']) > week_ago
        ]
        
        stats = {
            'total_notifications': len(history),
            'last_7_days': len(recent_notifications),
            'by_type': {},
            'by_urgency': {},
            'last_notification': history[-1] if history else None
        }
        
        for notification in recent_notifications:
            # Tür bazında
            n_type = notification['type']
            stats['by_type'][n_type] = stats['by_type'].get(n_type, 0) + 1
            
            # Aciliyet bazında  
            urgency = notification['urgency']
            stats['by_urgency'][urgency] = stats['by_urgency'].get(urgency, 0) + 1
        
        return stats
    
    def setup_notification_config(self):
        """Bildirim yapılandırmasını ayarla"""
        print("\n⚙️  BİLDİRİM YAPILARI")
        print("-" * 30)
        
        # Bildirim yöntemleri
        print("📱 Bildirim yöntemleri:")
        self.config['notification_methods']['desktop'] = input("Desktop bildirimi? (y/n, varsayılan y): ").lower() != 'n'
        
        email_choice = input("Email bildirimi kurmak istiyor musunuz? (y/n): ").lower() == 'y'
        if email_choice:
            self.config['notification_methods']['email'] = True
            print("\n📧 Email ayarları:")
            self.config['email_settings']['sender_email'] = input("Gmail adresiniz: ")
            self.config['email_settings']['sender_password'] = input("Gmail uygulama şifresi: ")
            self.config['email_settings']['recipient_email'] = input("Bildirim alacak email (varsayılan: aynı): ") or self.config['email_settings']['sender_email']
        
        # Sessiz saatler
        print("\n🔕 Sessiz saatler:")
        quiet_enabled = input("Sessiz saatler aktif? (y/n, varsayılan y): ").lower() != 'n'
        if quiet_enabled:
            self.config['quiet_hours']['enabled'] = True
            self.config['quiet_hours']['start_time'] = input("Başlangıç saati (varsayılan 22:00): ") or "22:00"
            self.config['quiet_hours']['end_time'] = input("Bitiş saati (varsayılan 08:00): ") or "08:00"
        
        # Yapılandırmayı kaydet
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        print("✅ Bildirim yapılandırması kaydedildi!")

def interactive_notification_system():
    """Etkileşimli bildirim sistemi"""
    print("""
╔══════════════════════════════════════════════════╗
║              BİLDİRİM SİSTEMİ                    ║
║        Ca' Foscari Otomatik Takip                ║
╚══════════════════════════════════════════════════╝
    """)
    
    notification_system = NotificationSystem()
    
    while True:
        print("\n🔔 BİLDİRİM MENÜSÜ:")
        print("1. 🔍 Şimdi bildirim kontrolü yap")
        print("2. ⚙️  Bildirim ayarlarını yapılandır")
        print("3. 📊 Bildirim istatistikleri")
        print("4. 📝 Bildirim geçmişi")
        print("5. 🧪 Test bildirimi gönder")
        print("6. ❌ Çıkış")
        
        choice = input("\nSeçiminiz (1-6): ").strip()
        
        if choice == "1":
            result = notification_system.run_notification_check()
            print(f"\n📈 Sonuç: {result['sent_notifications']} bildirim gönderildi")
            
            for notification in result['notifications']:
                print(f"   • {notification['title']}: {notification['message']}")
        
        elif choice == "2":
            notification_system.setup_notification_config()
        
        elif choice == "3":
            stats = notification_system.get_notification_stats()
            print(f"\n📊 BİLDİRİM İSTATİSTİKLERİ")
            print(f"Toplam bildirim: {stats['total_notifications']}")
            print(f"Son 7 gün: {stats['last_7_days']}")
            
            if stats['by_type']:
                print("\n📋 Tür bazında:")
                for n_type, count in stats['by_type'].items():
                    print(f"   {n_type}: {count}")
            
            if stats['by_urgency']:
                print("\n⚡ Aciliyet bazında:")
                for urgency, count in stats['by_urgency'].items():
                    print(f"   {urgency}: {count}")
        
        elif choice == "4":
            history = notification_system.notification_history['notifications'][-10:]  # Son 10
            
            print(f"\n📝 BİLDİRİM GEÇMİŞİ (Son 10)")
            for notification in reversed(history):
                timestamp = datetime.fromisoformat(notification['timestamp'])
                print(f"   📅 {timestamp.strftime('%Y-%m-%d %H:%M')} - {notification['title']}")
                print(f"      {notification['message']}")
        
        elif choice == "5":
            notification_system.send_notification(
                'test',
                '🧪 TEST BİLDİRİMİ',
                'Bu bir test bildirimidir. Sistem düzgün çalışıyor!',
                'normal'
            )
            print("✅ Test bildirimi gönderildi!")
        
        elif choice == "6":
            print("👋 Bildirimlerde görüşmek üzere! 🔔")
            break
        
        else:
            print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    interactive_notification_system()