#!/usr/bin/env python3
"""
Storage Manager - Tüm dosya ve veri organizasyonu
Klasör yapısını organize eder ve veri kayıtlarını yönetir
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class StorageManager:
    def __init__(self, base_path: str = None):
        """Storage Manager başlatıcısı"""
        self.base_path = base_path or os.getcwd()
        self.setup_directory_structure()
        
    def setup_directory_structure(self):
        """Klasör yapısını oluştur"""
        self.directories = {
            # Ana veri klasörleri
            'data': os.path.join(self.base_path, 'data'),
            'moodle_data': os.path.join(self.base_path, 'data', 'moodle'),
            'gmail_data': os.path.join(self.base_path, 'data', 'gmail'),
            'content_data': os.path.join(self.base_path, 'data', 'content'),
            
            # Ders bazlı klasörler
            'courses': os.path.join(self.base_path, 'data', 'courses'),
            'pdfs': os.path.join(self.base_path, 'data', 'courses', 'pdfs'),
            'videos': os.path.join(self.base_path, 'data', 'courses', 'videos'),
            'documents': os.path.join(self.base_path, 'data', 'courses', 'documents'),
            
            # Mock exam klasörleri  
            'mock_exams': os.path.join(self.base_path, 'mock_exams'),
            'mock_exams_created': os.path.join(self.base_path, 'mock_exams', 'created'),
            'mock_exams_completed': os.path.join(self.base_path, 'mock_exams', 'completed'),
            'exam_analyses': os.path.join(self.base_path, 'mock_exams', 'analyses'),
            
            # Sistem klasörleri
            'backups': os.path.join(self.base_path, 'backups'),
            'logs': os.path.join(self.base_path, 'logs'),
            'temp': os.path.join(self.base_path, 'temp'),
            'reports': os.path.join(self.base_path, 'reports'),
            
            # AI ve analiz
            'ai_analyses': os.path.join(self.base_path, 'ai_analyses'),
            'study_plans': os.path.join(self.base_path, 'study_plans')
        }
        
        # Tüm klasörleri oluştur
        for dir_name, dir_path in self.directories.items():
            os.makedirs(dir_path, exist_ok=True)
            
        print(f"📁 Klasör yapısı oluşturuldu: {len(self.directories)} klasör")
        
    def get_path(self, directory: str) -> str:
        """Belirli bir klasörün yolunu al"""
        return self.directories.get(directory, self.base_path)
    
    def create_course_folder(self, course_name: str) -> Dict[str, str]:
        """Ders için özel klasör oluştur"""
        # Dosya sistemi için güvenli isim
        safe_name = self.sanitize_filename(course_name)
        
        course_paths = {
            'main': os.path.join(self.directories['courses'], safe_name),
            'pdfs': os.path.join(self.directories['courses'], safe_name, 'pdfs'),
            'videos': os.path.join(self.directories['courses'], safe_name, 'videos'),
            'documents': os.path.join(self.directories['courses'], safe_name, 'documents'),
            'analysis': os.path.join(self.directories['courses'], safe_name, 'analysis'),
            'mock_exams': os.path.join(self.directories['courses'], safe_name, 'mock_exams')
        }
        
        # Klasörleri oluştur
        for folder_type, folder_path in course_paths.items():
            os.makedirs(folder_path, exist_ok=True)
            
        return course_paths
    
    def sanitize_filename(self, filename: str) -> str:
        """Dosya isimlerini güvenli hale getir"""
        # Türkçe karakterleri değiştir
        replacements = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U',
            ' ': '_', '/': '_', '\\': '_', ':': '_', '*': '_', 
            '?': '_', '"': '_', '<': '_', '>': '_', '|': '_'
        }
        
        safe_name = filename
        for old, new in replacements.items():
            safe_name = safe_name.replace(old, new)
            
        # Birden fazla alt çizgiyi tek yapmak
        while '__' in safe_name:
            safe_name = safe_name.replace('__', '_')
            
        return safe_name.strip('_')
    
    def save_moodle_data(self, data: Dict) -> str:
        """Moodle verilerini kaydet"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"moodle_data_{timestamp}.json"
        filepath = os.path.join(self.directories['moodle_data'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
        # En son veriyi de kaydet (latest)
        latest_path = os.path.join(self.directories['moodle_data'], 'latest.json')
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
        return filepath
    
    def save_gmail_data(self, data: List[Dict]) -> str:
        """Gmail verilerini kaydet"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"gmail_data_{timestamp}.json"
        filepath = os.path.join(self.directories['gmail_data'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
        # En son veriyi de kaydet
        latest_path = os.path.join(self.directories['gmail_data'], 'latest.json')
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
        return filepath
    
    def organize_course_files(self, moodle_data: Dict):
        """Ders dosyalarını düzenle"""
        print("\n📁 Ders dosyaları organize ediliyor...")
        
        courses_organized = 0
        files_organized = 0
        
        for course in moodle_data.get('courses', []):
            course_name = course['name']
            course_paths = self.create_course_folder(course_name)
            
            # Kurs bilgilerini kaydet
            course_info = {
                'course_id': course['id'],
                'name': course_name,
                'shortname': course.get('shortname', ''),
                'summary': course.get('summary', ''),
                'organized_at': datetime.now().isoformat(),
                'file_paths': {
                    'pdfs': [],
                    'videos': [],
                    'documents': []
                }
            }
            
            courses_organized += 1
            
        # PDF'leri organize et
        for pdf in moodle_data.get('pdfs', []):
            course_id = str(pdf['course_id'])
            course_name = self.get_course_name_by_id(course_id, moodle_data)
            
            if course_name:
                course_paths = self.create_course_folder(course_name)
                
                # PDF bilgilerini kaydet
                pdf_info = {
                    'name': pdf['name'],
                    'url': pdf['url'],
                    'size': pdf.get('size', 0),
                    'section': pdf.get('section', ''),
                    'module': pdf.get('module', ''),
                    'download_date': datetime.now().isoformat(),
                    'local_path': None  # İleride PDF'ler indirileceği zaman kullanılır
                }
                
                # PDF listesine ekle
                pdf_list_file = os.path.join(course_paths['main'], 'pdf_list.json')
                self.append_to_file_list(pdf_list_file, pdf_info)
                files_organized += 1
        
        # Videoları organize et
        for video in moodle_data.get('videos', []):
            course_id = str(video['course_id'])
            course_name = self.get_course_name_by_id(course_id, moodle_data)
            
            if course_name:
                course_paths = self.create_course_folder(course_name)
                
                video_info = {
                    'name': video['name'],
                    'url': video['url'],
                    'type': video.get('type', ''),
                    'section': video.get('section', ''),
                    'module': video.get('module', ''),
                    'indexed_date': datetime.now().isoformat()
                }
                
                video_list_file = os.path.join(course_paths['main'], 'video_list.json')
                self.append_to_file_list(video_list_file, video_info)
                files_organized += 1
        
        # Dökümanları organize et
        for doc in moodle_data.get('documents', []):
            course_id = str(doc['course_id'])
            course_name = self.get_course_name_by_id(course_id, moodle_data)
            
            if course_name:
                course_paths = self.create_course_folder(course_name)
                
                doc_info = {
                    'name': doc['name'],
                    'url': doc['url'],
                    'type': doc.get('type', ''),
                    'section': doc.get('section', ''),
                    'module': doc.get('module', ''),
                    'indexed_date': datetime.now().isoformat()
                }
                
                doc_list_file = os.path.join(course_paths['main'], 'document_list.json')
                self.append_to_file_list(doc_list_file, doc_info)
                files_organized += 1
        
        print(f"✅ {courses_organized} ders, {files_organized} dosya organize edildi")
        
    def get_course_name_by_id(self, course_id: str, moodle_data: Dict) -> str:
        """Ders ID'den ders ismini bul"""
        for course in moodle_data.get('courses', []):
            if str(course['id']) == course_id:
                return course['name']
        return None
    
    def append_to_file_list(self, file_path: str, new_item: Dict):
        """Dosya listesine yeni öğe ekle"""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                file_list = json.load(f)
        else:
            file_list = []
        
        # Aynı öğenin tekrar eklenmesini engelle
        existing = False
        for item in file_list:
            if item.get('url') == new_item.get('url'):
                existing = True
                break
        
        if not existing:
            file_list.append(new_item)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(file_list, f, indent=2, ensure_ascii=False, default=str)
    
    def save_mock_exam(self, exam_content: Dict, exam_file_path: str) -> str:
        """Mock sınavı kaydet"""
        course_name = exam_content.get('course_name', 'Unknown')
        safe_course_name = self.sanitize_filename(course_name)
        
        # Ders için mock exam klasörü oluştur
        course_exam_folder = os.path.join(self.directories['mock_exams_created'], safe_course_name)
        os.makedirs(course_exam_folder, exist_ok=True)
        
        # Sınav dosyasını kopyala
        exam_filename = os.path.basename(exam_file_path)
        new_exam_path = os.path.join(course_exam_folder, exam_filename)
        
        # Eğer dosya mevcutsa, kopyala
        if os.path.exists(exam_file_path):
            import shutil
            shutil.copy2(exam_file_path, new_exam_path)
        
        # Sınav meta verilerini kaydet
        meta_filename = exam_filename.replace('.txt', '_meta.json').replace('.pdf', '_meta.json')
        meta_path = os.path.join(course_exam_folder, meta_filename)
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(exam_content, f, indent=2, ensure_ascii=False, default=str)
        
        return new_exam_path
    
    def save_exam_analysis(self, analysis: Dict, exam_id: str) -> str:
        """Sınav analizini kaydet"""
        course_name = analysis.get('course_name', 'Unknown')
        safe_course_name = self.sanitize_filename(course_name)
        
        # Analiz klasörü oluştur
        analysis_folder = os.path.join(self.directories['exam_analyses'], safe_course_name)
        os.makedirs(analysis_folder, exist_ok=True)
        
        # Analiz dosyasını kaydet
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        analysis_filename = f"analysis_{exam_id}_{timestamp}.json"
        analysis_path = os.path.join(analysis_folder, analysis_filename)
        
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        
        return analysis_path
    
    def get_directory_summary(self) -> Dict:
        """Klasör özeti"""
        summary = {
            'base_path': self.base_path,
            'total_directories': len(self.directories),
            'directories': {},
            'total_files': 0,
            'total_size_mb': 0
        }
        
        for dir_name, dir_path in self.directories.items():
            if os.path.exists(dir_path):
                files = []
                total_size = 0
                
                for root, dirs, filenames in os.walk(dir_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        try:
                            size = os.path.getsize(file_path)
                            files.append({
                                'name': filename,
                                'path': file_path,
                                'size': size
                            })
                            total_size += size
                        except:
                            pass
                
                summary['directories'][dir_name] = {
                    'path': dir_path,
                    'file_count': len(files),
                    'size_mb': total_size / (1024 * 1024),
                    'files': files[:10]  # İlk 10 dosyayı göster
                }
                
                summary['total_files'] += len(files)
                summary['total_size_mb'] += total_size / (1024 * 1024)
        
        return summary
    
    def cleanup_old_files(self, days_to_keep: int = 30):
        """Eski dosyaları temizle"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cleaned_files = 0
        
        # Temp dosyaları temizle
        temp_path = self.directories['temp']
        if os.path.exists(temp_path):
            for filename in os.listdir(temp_path):
                file_path = os.path.join(temp_path, filename)
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        cleaned_files += 1
                except:
                    pass
        
        # Eski backup'ları temizle
        backup_path = self.directories['backups']
        if os.path.exists(backup_path):
            for filename in os.listdir(backup_path):
                if filename.endswith('.zip'):
                    file_path = os.path.join(backup_path, filename)
                    try:
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_date:
                            os.remove(file_path)
                            cleaned_files += 1
                    except:
                        pass
        
        print(f"🧹 {cleaned_files} eski dosya temizlendi")
        
    def show_directory_structure(self):
        """Klasör yapısını göster"""
        print("\n📁 KLASÖR YAPISI:")
        print("=" * 50)
        
        summary = self.get_directory_summary()
        
        for dir_name, info in summary['directories'].items():
            files_count = info['file_count']
            size_mb = info['size_mb']
            
            print(f"📂 {dir_name}")
            print(f"   📍 {info['path']}")
            print(f"   📊 {files_count} dosya, {size_mb:.1f} MB")
            
            if files_count > 0 and info['files']:
                print("   📄 İçerik:")
                for file_info in info['files'][:3]:  # İlk 3 dosyayı göster
                    print(f"      • {file_info['name']}")
                if files_count > 3:
                    print(f"      ... ve {files_count - 3} dosya daha")
            print()
        
        print(f"📊 TOPLAM: {summary['total_files']} dosya, {summary['total_size_mb']:.1f} MB")

# Global storage manager instance
storage_manager = StorageManager()

if __name__ == "__main__":
    # Test
    sm = StorageManager()
    sm.show_directory_structure()