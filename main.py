#!/usr/bin/env python3
"""
CA' FOSCARI ULTIMATE STUDY SYSTEM
Ana orchestrator sistemi - Tüm modülleri yönetir ve otomatik çalışma sağlar

Emre Aras (907842) - Computer Architecture
Ca' Foscari Üniversitesi
"""

import os
import sys
import json
import time
import schedule
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Kendi modüllerimizi import et
try:
    from moodle_api import MoodleAPI, setup_moodle_connection
    from gmail_analyzer import GmailAnalyzer, setup_gmail_api
    from content_analyzer import ContentAnalyzer
    from study_planner import StudyPlanner, interactive_setup as study_setup
    from mock_exam_generator import MockExamGenerator, interactive_mock_exam_generator
    from notification_system import NotificationSystem, interactive_notification_system
except ImportError as e:
    print(f"❌ Modül import hatası: {e}")
    print("Lütfen tüm Python dosyalarının aynı klasörde olduğundan emin olun.")
    sys.exit(1)

class CaFoscariUltimateSystem:
    def __init__(self):
        """Ana sistem başlatıcısı"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🎓 CA' FOSCARI ULTIMATE STUDY SYSTEM 🎓                   ║
║                                                                  ║
║                    Emre Aras (907842)                            ║
║               Computer Architecture Bölümü                       ║
║                  Ca' Foscari Üniversitesi                        ║
║                                                                  ║
║  📚 Moodle Entegrasyonu    🔔 Akıllı Bildirimler                ║
║  📧 Gmail Analizi          📝 Mock Sınavlar                      ║
║  📄 İçerik Analizi         📊 Performans Takibi                 ║
║  🤖 AI Çalışma Planı       ⚡ Otomatik İşlemler                 ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """)
        
        self.config = self._load_system_config()
        self.running = False
        
        # Sistem bileşenleri
        self.moodle_api = None
        self.gmail_analyzer = None
        self.content_analyzer = ContentAnalyzer()
        self.study_planner = None
        self.mock_generator = None
        self.notification_system = NotificationSystem()
        
        # İstatistikler
        self.stats = {
            'system_start_time': datetime.now(),
            'total_data_syncs': 0,
            'total_notifications': 0,
            'last_full_sync': None,
            'errors': []
        }
    
    def _load_system_config(self) -> Dict:
        """Sistem yapılandırmasını yükle"""
        config_file = "system_config.json"
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Varsayılan yapılandırma
        default_config = {
            'student_info': {
                'name': 'Emre Aras',
                'student_id': '907842',
                'university': 'Ca\' Foscari',
                'program': 'Computer Architecture'
            },
            'auto_sync': {
                'enabled': True,
                'interval_hours': 2,
                'quiet_hours': {
                    'start': '23:00',
                    'end': '07:00'
                }
            },
            'data_sources': {
                'moodle': {'enabled': False, 'last_sync': None},
                'gmail': {'enabled': False, 'last_sync': None},
                'content': {'enabled': True, 'last_sync': None}
            },
            'ai_features': {
                'claude_api_key': '',
                'auto_study_plans': True,
                'auto_mock_exams': True,
                'smart_notifications': True
            },
            'backup': {
                'enabled': True,
                'keep_days': 30
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        return default_config
    
    def save_system_config(self):
        """Sistem yapılandırmasını kaydet"""
        with open("system_config.json", 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def setup_system_components(self):
        """Sistem bileşenlerini kur"""
        print("\n🔧 SİSTEM BİLEŞENLERİ KURULUYOR...")
        print("-" * 50)
        
        # Claude API Key
        if not self.config['ai_features']['claude_api_key']:
            claude_key = input("Claude API Key (isteğe bağlı): ").strip()
            if claude_key:
                self.config['ai_features']['claude_api_key'] = claude_key
        
        # Moodle kurulumu
        moodle_setup = input("Moodle entegrasyonu kurmak istiyor musunuz? (y/n): ").lower() == 'y'
        if moodle_setup:
            self.moodle_api = setup_moodle_connection()
            if self.moodle_api:
                self.config['data_sources']['moodle']['enabled'] = True
                print("✅ Moodle entegrasyonu kuruldu")
            else:
                print("❌ Moodle entegrasyonu kurulamadı")
        
        # Gmail kurulumu
        gmail_setup = input("Gmail entegrasyonu kurmak istiyor musunuz? (y/n): ").lower() == 'y'
        if gmail_setup:
            self.gmail_analyzer = setup_gmail_api()
            if self.gmail_analyzer:
                self.config['data_sources']['gmail']['enabled'] = True
                print("✅ Gmail entegrasyonu kuruldu")
            else:
                print("❌ Gmail entegrasyonu kurulamadı")
        
        # Diğer bileşenleri başlat
        claude_key = self.config['ai_features']['claude_api_key']
        self.study_planner = StudyPlanner(claude_key if claude_key else None)
        self.mock_generator = MockExamGenerator(claude_key if claude_key else None)
        
        # Yapılandırmayı kaydet
        self.save_system_config()
        print("\n✅ Sistem bileşenleri hazır!")
    
    def run_full_data_sync(self) -> Dict:
        """Tam veri senkronizasyonu"""
        print("\n🔄 TAM VERİ SENKRONİZASYONU BAŞLATIYOR...")
        
        sync_results = {
            'start_time': datetime.now(),
            'moodle': {'status': 'disabled', 'data_count': 0},
            'gmail': {'status': 'disabled', 'data_count': 0},
            'content': {'status': 'disabled', 'data_count': 0},
            'errors': []
        }
        
        try:
            # Moodle verilerini çek
            if self.config['data_sources']['moodle']['enabled'] and self.moodle_api:
                print("📚 Moodle verileri çekiliyor...")
                try:
                    moodle_data = self.moodle_api.get_full_course_data()
                    
                    with open('moodle_data.json', 'w', encoding='utf-8') as f:
                        json.dump(moodle_data, f, indent=2, ensure_ascii=False, default=str)
                    
                    sync_results['moodle']['status'] = 'success'
                    sync_results['moodle']['data_count'] = (
                        len(moodle_data.get('courses', [])) + 
                        len(moodle_data.get('assignments', [])) + 
                        len(moodle_data.get('events', []))
                    )
                    self.config['data_sources']['moodle']['last_sync'] = datetime.now().isoformat()
                    
                except Exception as e:
                    sync_results['moodle']['status'] = 'error'
                    sync_results['errors'].append(f"Moodle: {str(e)}")
            
            # Gmail verilerini çek
            if self.config['data_sources']['gmail']['enabled'] and self.gmail_analyzer:
                print("📧 Gmail verileri çekiliyor...")
                try:
                    emails = self.gmail_analyzer.get_university_emails(days_back=7)
                    
                    with open('gmail_analysis.json', 'w', encoding='utf-8') as f:
                        json.dump(emails, f, indent=2, ensure_ascii=False)
                    
                    sync_results['gmail']['status'] = 'success'
                    sync_results['gmail']['data_count'] = len(emails)
                    self.config['data_sources']['gmail']['last_sync'] = datetime.now().isoformat()
                    
                except Exception as e:
                    sync_results['gmail']['status'] = 'error'
                    sync_results['errors'].append(f"Gmail: {str(e)}")
            
            # İçerik analizini çalıştır
            if self.config['data_sources']['content']['enabled']:
                print("📄 İçerik analizi yapılıyor...")
                try:
                    content_results = self.content_analyzer.analyze_folder()
                    
                    with open('content_analysis.json', 'w', encoding='utf-8') as f:
                        json.dump(content_results, f, indent=2, ensure_ascii=False, default=str)
                    
                    sync_results['content']['status'] = 'success'
                    sync_results['content']['data_count'] = content_results['summary']['total_pdfs'] + content_results['summary']['total_videos']
                    self.config['data_sources']['content']['last_sync'] = datetime.now().isoformat()
                    
                except Exception as e:
                    sync_results['content']['status'] = 'error'
                    sync_results['errors'].append(f"Content: {str(e)}")
            
            # İstatistikleri güncelle
            self.stats['total_data_syncs'] += 1
            self.stats['last_full_sync'] = datetime.now().isoformat()
            
            # Bildirim kontrolü yap
            notification_results = self.notification_system.run_notification_check()
            self.stats['total_notifications'] += notification_results['sent_notifications']
            
            sync_results['end_time'] = datetime.now()
            sync_results['duration'] = (sync_results['end_time'] - sync_results['start_time']).total_seconds()
            
            print(f"✅ Veri senkronizasyonu tamamlandı ({sync_results['duration']:.1f}s)")
            
        except Exception as e:
            sync_results['errors'].append(f"System: {str(e)}")
            self.stats['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })
        
        # Yapılandırmayı kaydet
        self.save_system_config()
        
        return sync_results
    
    def run_ai_analysis(self) -> Dict:
        """AI analizi ve çalışma planı güncellemesi"""
        if not self.config['ai_features']['claude_api_key']:
            return {'status': 'disabled', 'message': 'Claude API key yok'}
        
        print("\n🤖 AI ANALİZİ ÇALIŞIYOR...")
        
        results = {'study_plan': None, 'mock_exams': None}
        
        try:
            # Çalışma planı oluştur/güncelle
            if self.config['ai_features']['auto_study_plans']:
                print("📊 Çalışma planı güncelleniyor...")
                study_plan = self.study_planner.generate_comprehensive_study_plan(days_ahead=14)
                results['study_plan'] = {
                    'status': 'success',
                    'total_days': len(study_plan['daily_schedules']),
                    'file': 'comprehensive_study_plan.json'
                }
            
            # Mock sınavlar oluştur
            if self.config['ai_features']['auto_mock_exams']:
                print("📝 Mock sınavlar kontrol ediliyor...")
                # Eğer son 5 günde mock sınav oluşturulmamışsa yeni bir tane oluştur
                mock_files = [f for f in os.listdir('.') if f.startswith('mock_exam_') and f.endswith('.json')]
                
                needs_new_mock = True
                if mock_files:
                    # En son oluşturulan mock sınavın tarihini kontrol et
                    latest_file = max(mock_files, key=lambda f: os.path.getctime(f))
                    file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(latest_file))
                    if file_age.days < 5:
                        needs_new_mock = False
                
                if needs_new_mock:
                    print("📝 Yeni mock sınav oluşturuluyor...")
                    mock_exam = self.mock_generator.create_mock_exam()
                    mock_file = self.mock_generator.create_single_exam_file(mock_exam)
                    self.mock_generator.generate_answer_key(mock_exam)
                    
                    results['mock_exams'] = {
                        'status': 'created',
                        'file': mock_file,
                        'questions': mock_exam['total_questions']
                    }
                else:
                    results['mock_exams'] = {'status': 'up_to_date'}
            
        except Exception as e:
            results['error'] = str(e)
            self.stats['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': f"AI Analysis: {str(e)}"
            })
        
        return results
    
    def run_scheduled_tasks(self):
        """Zamanlanmış görevleri çalıştır"""
        print(f"\n⏰ Zamanlanmış görevler çalışıyor: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Sessiz saatlerde mi?
        if self._is_quiet_hours():
            print("🔇 Sessiz saatlerde - sadece kritik işlemler")
            # Sadece bildirim kontrolü yap
            self.notification_system.run_notification_check()
            return
        
        # Tam veri senkronizasyonu
        sync_results = self.run_full_data_sync()
        
        # AI analizi (günde 1-2 kez)
        current_hour = datetime.now().hour
        if current_hour in [9, 18]:  # Sabah 9 ve akşam 6
            ai_results = self.run_ai_analysis()
            print(f"🤖 AI analizi tamamlandı: {ai_results}")
        
        # Backup oluştur (gece yarısı)
        if current_hour == 0 and self.config['backup']['enabled']:
            self.create_backup()
    
    def _is_quiet_hours(self) -> bool:
        """Sessiz saatlerde miyiz?"""
        quiet_hours = self.config['auto_sync']['quiet_hours']
        current_time = datetime.now().time()
        
        start_time = datetime.strptime(quiet_hours['start'], '%H:%M').time()
        end_time = datetime.strptime(quiet_hours['end'], '%H:%M').time()
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # Gece geçişi
            return current_time >= start_time or current_time <= end_time
    
    def create_backup(self):
        """Sistem verilerini yedekle"""
        print("💾 Backup oluşturuluyor...")
        
        backup_dir = f"backup_{datetime.now().strftime('%Y%m%d')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Yedeklenecek dosyalar
        backup_files = [
            'system_config.json',
            'moodle_data.json',
            'gmail_analysis.json',
            'content_analysis.json',
            'manual_exams.json',
            'comprehensive_study_plan.json',
            'notification_history.json'
        ]
        
        import shutil
        
        backed_up = 0
        for filename in backup_files:
            if os.path.exists(filename):
                try:
                    shutil.copy2(filename, os.path.join(backup_dir, filename))
                    backed_up += 1
                except Exception as e:
                    print(f"⚠️  {filename} backup hatası: {e}")
        
        print(f"✅ Backup tamamlandı: {backed_up} dosya - {backup_dir}/")
        
        # Eski backupları temizle
        self.cleanup_old_backups()
    
    def cleanup_old_backups(self):
        """Eski backupları temizle"""
        keep_days = self.config['backup']['keep_days']
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        backup_dirs = [d for d in os.listdir('.') if d.startswith('backup_') and os.path.isdir(d)]
        
        for backup_dir in backup_dirs:
            try:
                dir_date = datetime.strptime(backup_dir.split('_')[1], '%Y%m%d')
                if dir_date < cutoff_date:
                    import shutil
                    shutil.rmtree(backup_dir)
                    print(f"🗑️  Eski backup silindi: {backup_dir}")
            except:
                pass
    
    def start_auto_sync(self):
        """Otomatik senkronizasyonu başlat"""
        if not self.config['auto_sync']['enabled']:
            print("⚠️  Otomatik senkronizasyon devre dışı")
            return
        
        print(f"⏰ Otomatik senkronizasyon başlatılıyor (her {self.config['auto_sync']['interval_hours']} saatte)")
        
        # Zamanlanmış görevleri ayarla
        schedule.every(self.config['auto_sync']['interval_hours']).hours.do(self.run_scheduled_tasks)
        
        # İlk çalıştırma
        self.run_scheduled_tasks()
        
        # Scheduler loop
        self.running = True
        
        def scheduler_thread():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Her dakika kontrol et
        
        scheduler = threading.Thread(target=scheduler_thread, daemon=True)
        scheduler.start()
        
        print("✅ Otomatik senkronizasyon başlatıldı!")
        return scheduler
    
    def stop_auto_sync(self):
        """Otomatik senkronizasyonu durdur"""
        self.running = False
        schedule.clear()
        print("🛑 Otomatik senkronizasyon durduruldu")
    
    def get_system_status(self) -> Dict:
        """Sistem durumunu getir"""
        status = {
            'uptime': str(datetime.now() - self.stats['system_start_time']),
            'running': self.running,
            'data_sources': {
                'moodle': 'connected' if self.moodle_api else 'disabled',
                'gmail': 'connected' if self.gmail_analyzer else 'disabled',
                'content': 'enabled' if self.config['data_sources']['content']['enabled'] else 'disabled'
            },
            'last_sync': self.stats['last_full_sync'],
            'total_syncs': self.stats['total_data_syncs'],
            'total_notifications': self.stats['total_notifications'],
            'errors': len(self.stats['errors'])
        }
        
        # Dosya durumları
        data_files = {
            'moodle_data.json': os.path.exists('moodle_data.json'),
            'gmail_analysis.json': os.path.exists('gmail_analysis.json'),
            'content_analysis.json': os.path.exists('content_analysis.json'),
            'comprehensive_study_plan.json': os.path.exists('comprehensive_study_plan.json')
        }
        
        status['data_files'] = data_files
        
        return status
    
    def interactive_menu(self):
        """Ana etkileşimli menü"""
        while True:
            status = self.get_system_status()
            
            print(f"\n" + "="*60)
            print(f"🎓 CA' FOSCARI ULTIMATE SYSTEM - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            print(f"📊 Durum: {'🟢 Çalışıyor' if status['running'] else '🔴 Durduruldu'} | Uptime: {status['uptime']}")
            print(f"📈 Sync: {status['total_syncs']} | 🔔 Bildirim: {status['total_notifications']} | ❌ Hata: {status['errors']}")
            print("="*60)
            
            print("\n🎯 ANA MENÜ:")
            print("1. 🔄 Şimdi tam senkronizasyon yap")
            print("2. 🤖 AI analizi ve plan güncellemesi")
            print("3. ⚙️  Sistem bileşenlerini yapılandır")
            print("4. 🔔 Bildirim sistemi")
            print("5. 📝 Mock sınav oluşturucu")
            print("6. 📚 Çalışma planı sistemi")
            print("7. ⏰ Otomatik senkronizasyon başlat/durdur")
            print("8. 📊 Sistem durumu ve istatistikler")
            print("9. 💾 Manuel backup oluştur")
            print("10. ❌ Çıkış")
            
            choice = input(f"\nSeçiminiz (1-10): ").strip()
            
            if choice == "1":
                sync_results = self.run_full_data_sync()
                self._print_sync_results(sync_results)
            
            elif choice == "2":
                ai_results = self.run_ai_analysis()
                print(f"\n🤖 AI Analiz Sonuçları:")
                if 'study_plan' in ai_results:
                    print(f"   📊 Çalışma Planı: {ai_results['study_plan']}")
                if 'mock_exams' in ai_results:
                    print(f"   📝 Mock Sınavlar: {ai_results['mock_exams']}")
            
            elif choice == "3":
                self.setup_system_components()
            
            elif choice == "4":
                interactive_notification_system()
            
            elif choice == "5":
                interactive_mock_exam_generator()
            
            elif choice == "6":
                study_setup()
            
            elif choice == "7":
                if status['running']:
                    self.stop_auto_sync()
                else:
                    scheduler = self.start_auto_sync()
                    print("Otomatik senkronizasyon çalışıyor. Durdurmak için tekrar seçin.")
            
            elif choice == "8":
                self._print_system_status(status)
            
            elif choice == "9":
                self.create_backup()
            
            elif choice == "10":
                if status['running']:
                    self.stop_auto_sync()
                print("\n👋 CA' FOSCARI ULTIMATE SYSTEM KAPATILIYOR...")
                print("📚 Çalışmalarınızda başarılar!")
                print("🎓 Ca' Foscari - Computer Architecture")
                print("👨‍🎓 Emre Aras (907842)")
                break
            
            else:
                print("❌ Geçersiz seçim!")
    
    def _print_sync_results(self, results: Dict):
        """Senkronizasyon sonuçlarını yazdır"""
        print(f"\n📊 SENKRONİZASYON SONUÇLARI ({results['duration']:.1f}s)")
        print("-" * 40)
        
        for source, data in results.items():
            if source in ['moodle', 'gmail', 'content']:
                status_icon = "✅" if data['status'] == 'success' else "❌" if data['status'] == 'error' else "⚪"
                print(f"{status_icon} {source.title()}: {data['status']} ({data['data_count']} öğe)")
        
        if results['errors']:
            print("\n❌ HATALAR:")
            for error in results['errors']:
                print(f"   • {error}")
    
    def _print_system_status(self, status: Dict):
        """Sistem durumunu yazdır"""
        print(f"\n📊 SİSTEM DURUMU")
        print("-" * 30)
        print(f"🔄 Çalışma süresi: {status['uptime']}")
        print(f"🔄 Durum: {'Aktif' if status['running'] else 'Durduruldu'}")
        print(f"📈 Toplam senkronizasyon: {status['total_syncs']}")
        print(f"🔔 Toplam bildirim: {status['total_notifications']}")
        print(f"❌ Hata sayısı: {status['errors']}")
        
        print(f"\n📡 VERİ KAYNAKLARI:")
        for source, state in status['data_sources'].items():
            icon = "✅" if state == 'connected' or state == 'enabled' else "❌"
            print(f"   {icon} {source.title()}: {state}")
        
        print(f"\n📁 VERİ DOSYALARI:")
        for filename, exists in status['data_files'].items():
            icon = "✅" if exists else "❌"
            print(f"   {icon} {filename}")
        
        if status['last_sync']:
            last_sync = datetime.fromisoformat(status['last_sync'])
            print(f"\n🕒 Son senkronizasyon: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Ana program"""
    try:
        system = CaFoscariUltimateSystem()
        
        # İlk kurulum kontrolü
        if not any([
            system.config['data_sources']['moodle']['enabled'],
            system.config['data_sources']['gmail']['enabled']
        ]):
            print("\n🔧 İLK KURULUM GEREKLİ")
            print("Sistem bileşenlerini yapılandırın...")
            system.setup_system_components()
        
        # Ana menüyü başlat
        system.interactive_menu()
        
    except KeyboardInterrupt:
        print("\n\n👋 Sistem kapatılıyor... (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ SISTEM HATASI: {e}")
        print("Lütfen tekrar deneyin veya hata kayıtlarını kontrol edin.")

if __name__ == "__main__":
    main()