#!/usr/bin/env python3
"""
PDF ve Video İçerik Analiz Modülü
Ders materyallerini analiz eder ve önemli bilgileri çıkarır
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

# PDF okuma için
try:
    import PyPDF2
    import pdfplumber
except ImportError:
    print("⚠️  PyPDF2 ve pdfplumber kurun: pip install PyPDF2 pdfplumber")

# OCR için
try:
    import pytesseract
    from PIL import Image
except ImportError:
    print("⚠️  OCR için kurun: pip install pytesseract pillow")

# Video metadata için
try:
    import cv2
    import moviepy.editor as mp
except ImportError:
    print("⚠️  Video analiz için kurun: pip install opencv-python moviepy")

class ContentAnalyzer:
    def __init__(self, download_folder: str = "downloads"):
        """
        İçerik analiz sistemi başlatıcısı
        Args:
            download_folder: İndirilen dosyaların bulunduğu klasör
        """
        self.download_folder = download_folder
        self.analysis_cache = {}
        self.cache_file = "content_analysis_cache.json"
        self._load_cache()
        
        # Önemli anahtar kelimeler (Computer Architecture için)
        self.important_keywords = [
            # İşlemci mimarisi
            'cpu', 'processor', 'architecture', 'instruction', 'pipeline',
            'cache', 'memory', 'register', 'alu', 'control unit',
            'datapath', 'hazard', 'branch prediction', 'superscalar',
            
            # Bellek sistemi
            'memory hierarchy', 'cache miss', 'cache hit', 'tlb',
            'virtual memory', 'paging', 'segmentation', 'dram', 'sram',
            
            # Performans
            'performance', 'throughput', 'latency', 'cpi', 'clock cycle',
            'benchmark', 'speedup', 'efficiency', 'bottleneck',
            
            # Türkçe terimler
            'işlemci', 'bellek', 'mimari', 'komut', 'döngü', 'performans',
            'cache', 'kayıt', 'veri yolu', 'kontrol birimi'
        ]
    
    def _load_cache(self):
        """Analiz cache'ini yükle"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.analysis_cache = json.load(f)
            except:
                self.analysis_cache = {}
    
    def _save_cache(self):
        """Analiz cache'ini kaydet"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_cache, f, indent=2, ensure_ascii=False)
    
    def _get_file_hash(self, file_path: str) -> str:
        """Dosya hash'ini hesapla"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except:
            return ""
    
    def analyze_pdf(self, pdf_path: str) -> Dict:
        """PDF dosyasını analiz et"""
        if not os.path.exists(pdf_path):
            return {"error": "Dosya bulunamadı"}
        
        # Cache kontrolü
        file_hash = self._get_file_hash(pdf_path)
        if file_hash in self.analysis_cache:
            return self.analysis_cache[file_hash]
        
        print(f"📄 PDF analizi: {os.path.basename(pdf_path)}")
        
        analysis = {
            'file_path': pdf_path,
            'file_name': os.path.basename(pdf_path),
            'file_size': os.path.getsize(pdf_path),
            'analysis_date': datetime.now().isoformat(),
            'content': {}
        }
        
        try:
            # PyPDF2 ile temel analiz
            analysis['content'].update(self._analyze_pdf_pypdf2(pdf_path))
            
            # pdfplumber ile gelişmiş analiz
            analysis['content'].update(self._analyze_pdf_plumber(pdf_path))
            
            # Önemli bilgileri çıkar
            analysis['summary'] = self._generate_pdf_summary(analysis['content'])
            
            # Cache'e kaydet
            self.analysis_cache[file_hash] = analysis
            self._save_cache()
            
            return analysis
            
        except Exception as e:
            return {"error": f"PDF analiz hatası: {e}"}
    
    def _analyze_pdf_pypdf2(self, pdf_path: str) -> Dict:
        """PyPDF2 ile PDF analizi"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                content = {
                    'page_count': len(reader.pages),
                    'text_content': "",
                    'metadata': {}
                }
                
                # Metadata
                if reader.metadata:
                    content['metadata'] = {
                        'title': reader.metadata.get('/Title', ''),
                        'author': reader.metadata.get('/Author', ''),
                        'subject': reader.metadata.get('/Subject', ''),
                        'creator': reader.metadata.get('/Creator', ''),
                        'creation_date': str(reader.metadata.get('/CreationDate', ''))
                    }
                
                # Her sayfadan metin çıkar
                full_text = ""
                for page_num, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text()
                        full_text += f"\n--- Sayfa {page_num + 1} ---\n{text}\n"
                    except:
                        continue
                
                content['text_content'] = full_text
                content['character_count'] = len(full_text)
                content['word_count'] = len(full_text.split())
                
                return content
                
        except Exception as e:
            return {"pypdf2_error": str(e)}
    
    def _analyze_pdf_plumber(self, pdf_path: str) -> Dict:
        """pdfplumber ile gelişmiş PDF analizi"""
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                content = {
                    'tables': [],
                    'images': [],
                    'page_details': []
                }
                
                for page_num, page in enumerate(pdf.pages):
                    page_info = {
                        'page_number': page_num + 1,
                        'width': page.width,
                        'height': page.height,
                        'tables_count': 0,
                        'images_count': 0
                    }
                    
                    # Tabloları bul
                    tables = page.find_tables()
                    if tables:
                        page_info['tables_count'] = len(tables)
                        for table in tables:
                            try:
                                table_data = table.extract()
                                content['tables'].append({
                                    'page': page_num + 1,
                                    'data': table_data[:5],  # İlk 5 satır
                                    'row_count': len(table_data),
                                    'col_count': len(table_data[0]) if table_data else 0
                                })
                            except:
                                continue
                    
                    # Görsel sayısını tahmin et
                    images = page.images
                    if images:
                        page_info['images_count'] = len(images)
                        content['images'].extend([{
                            'page': page_num + 1,
                            'x0': img['x0'],
                            'y0': img['y0'],
                            'x1': img['x1'],
                            'y1': img['y1']
                        } for img in images])
                    
                    content['page_details'].append(page_info)
                
                return content
                
        except Exception as e:
            return {"pdfplumber_error": str(e)}
    
    def _generate_pdf_summary(self, content: Dict) -> Dict:
        """PDF için özet oluştur"""
        summary = {
            'page_count': content.get('page_count', 0),
            'word_count': content.get('word_count', 0),
            'has_tables': len(content.get('tables', [])) > 0,
            'has_images': len(content.get('images', [])) > 0,
            'estimated_reading_time': max(1, content.get('word_count', 0) // 200),  # dakika
            'important_topics': [],
            'key_concepts': [],
            'difficulty_level': 'MEDIUM'
        }
        
        text = content.get('text_content', '').lower()
        
        # Önemli konuları bul
        topic_keywords = {
            'processor_architecture': ['cpu', 'processor', 'architecture', 'datapath'],
            'memory_system': ['memory', 'cache', 'dram', 'sram', 'virtual'],
            'instruction_set': ['instruction', 'opcode', 'addressing', 'risc', 'cisc'],
            'performance': ['performance', 'benchmark', 'speedup', 'throughput'],
            'pipelining': ['pipeline', 'hazard', 'forwarding', 'stall']
        }
        
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score >= 2:
                summary['important_topics'].append({
                    'topic': topic,
                    'relevance': score
                })
        
        # Anahtar kavramları çıkar
        found_keywords = []
        for keyword in self.important_keywords:
            if keyword in text:
                # Kelimeyi içeren cümleyi bul
                sentences = re.split(r'[.!?]+', text)
                for sentence in sentences:
                    if keyword in sentence and len(sentence.strip()) > 10:
                        found_keywords.append({
                            'keyword': keyword,
                            'context': sentence.strip()[:200] + "..."
                        })
                        break
        
        summary['key_concepts'] = found_keywords[:10]  # İlk 10 kavram
        
        # Zorluk seviyesi tahmini
        technical_terms = len([k for k in self.important_keywords if k in text])
        if technical_terms > 15:
            summary['difficulty_level'] = 'ADVANCED'
        elif technical_terms > 8:
            summary['difficulty_level'] = 'MEDIUM'
        else:
            summary['difficulty_level'] = 'BASIC'
        
        return summary
    
    def analyze_video(self, video_path: str) -> Dict:
        """Video dosyasını analiz et"""
        if not os.path.exists(video_path):
            return {"error": "Video dosyası bulunamadı"}
        
        # Cache kontrolü
        file_hash = self._get_file_hash(video_path)
        if file_hash in self.analysis_cache:
            return self.analysis_cache[file_hash]
        
        print(f"🎥 Video analizi: {os.path.basename(video_path)}")
        
        analysis = {
            'file_path': video_path,
            'file_name': os.path.basename(video_path),
            'file_size': os.path.getsize(video_path),
            'analysis_date': datetime.now().isoformat(),
            'content': {}
        }
        
        try:
            # Video metadata'sını al
            analysis['content'].update(self._get_video_metadata(video_path))
            
            # Frame'lerden text çıkar (OCR)
            analysis['content'].update(self._extract_text_from_video(video_path))
            
            # Özet oluştur
            analysis['summary'] = self._generate_video_summary(analysis['content'])
            
            # Cache'e kaydet
            self.analysis_cache[file_hash] = analysis
            self._save_cache()
            
            return analysis
            
        except Exception as e:
            return {"error": f"Video analiz hatası: {e}"}
    
    def _get_video_metadata(self, video_path: str) -> Dict:
        """Video metadata'sını al"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {"error": "Video açılamadı"}
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            cap.release()
            
            return {
                'duration_seconds': duration,
                'duration_minutes': duration / 60,
                'fps': fps,
                'frame_count': frame_count,
                'resolution': f"{width}x{height}",
                'width': width,
                'height': height
            }
            
        except Exception as e:
            return {"metadata_error": str(e)}
    
    def _extract_text_from_video(self, video_path: str, sample_frames: int = 10) -> Dict:
        """Video'dan OCR ile metin çıkar"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {"error": "Video açılamadı"}
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            extracted_texts = []
            
            # Belirli aralıklarla frame'leri örnekle
            for i in range(sample_frames):
                frame_pos = int(i * frame_count / sample_frames)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                
                ret, frame = cap.read()
                if not ret:
                    continue
                
                try:
                    # OCR uygula
                    text = pytesseract.image_to_string(frame, lang='eng+tur')
                    if len(text.strip()) > 10:
                        extracted_texts.append({
                            'frame_number': frame_pos,
                            'timestamp': frame_pos / cap.get(cv2.CAP_PROP_FPS),
                            'text': text.strip()
                        })
                except:
                    continue
            
            cap.release()
            
            # Tüm metinleri birleştir
            all_text = " ".join([item['text'] for item in extracted_texts])
            
            return {
                'ocr_results': extracted_texts,
                'combined_text': all_text,
                'text_segments': len(extracted_texts),
                'total_characters': len(all_text)
            }
            
        except Exception as e:
            return {"ocr_error": str(e)}
    
    def _generate_video_summary(self, content: Dict) -> Dict:
        """Video için özet oluştur"""
        summary = {
            'duration_minutes': content.get('duration_minutes', 0),
            'estimated_watch_time': content.get('duration_minutes', 0),
            'has_text_content': len(content.get('combined_text', '')) > 50,
            'key_topics': [],
            'recommended_speed': '1x',
            'difficulty_level': 'MEDIUM'
        }
        
        duration = content.get('duration_minutes', 0)
        
        # İzleme hızı önerisi
        if duration > 60:  # 1 saat+
            summary['recommended_speed'] = '1.25x'
        elif duration > 30:  # 30 dk+
            summary['recommended_speed'] = '1x'
        else:
            summary['recommended_speed'] = '1x'
        
        # Metin içeriği varsa analiz et
        text = content.get('combined_text', '').lower()
        if text:
            # Önemli kelimeleri bul
            found_topics = []
            for keyword in self.important_keywords:
                if keyword in text:
                    found_topics.append(keyword)
            
            summary['key_topics'] = found_topics[:10]
            
            # Zorluk seviyesi
            technical_count = len(found_topics)
            if technical_count > 10:
                summary['difficulty_level'] = 'ADVANCED'
            elif technical_count > 5:
                summary['difficulty_level'] = 'MEDIUM'
            else:
                summary['difficulty_level'] = 'BASIC'
        
        return summary
    
    def analyze_folder(self, folder_path: str = None) -> Dict:
        """Klasördeki tüm dosyaları analiz et"""
        if folder_path is None:
            folder_path = self.download_folder
        
        if not os.path.exists(folder_path):
            print(f"❌ Klasör bulunamadı: {folder_path}")
            return {}
        
        print(f"📁 Klasör analizi: {folder_path}")
        
        results = {
            'folder_path': folder_path,
            'analysis_date': datetime.now().isoformat(),
            'files': {
                'pdfs': [],
                'videos': [],
                'others': []
            },
            'summary': {}
        }
        
        # Tüm dosyaları tara
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext == '.pdf':
                    analysis = self.analyze_pdf(file_path)
                    results['files']['pdfs'].append(analysis)
                
                elif file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv']:
                    analysis = self.analyze_video(file_path)
                    results['files']['videos'].append(analysis)
                
                else:
                    results['files']['others'].append({
                        'file_path': file_path,
                        'file_name': file,
                        'file_size': os.path.getsize(file_path),
                        'extension': file_ext
                    })
        
        # Genel özet
        results['summary'] = {
            'total_pdfs': len(results['files']['pdfs']),
            'total_videos': len(results['files']['videos']),
            'total_other_files': len(results['files']['others']),
            'total_study_time_estimate': self._calculate_total_study_time(results['files']),
            'priority_files': self._get_priority_files(results['files']),
            'common_topics': self._get_common_topics(results['files'])
        }
        
        return results
    
    def _calculate_total_study_time(self, files: Dict) -> int:
        """Toplam çalışma süresi tahmini (dakika)"""
        total_minutes = 0
        
        # PDF'ler için okuma süresi
        for pdf in files['pdfs']:
            if 'summary' in pdf and 'estimated_reading_time' in pdf['summary']:
                total_minutes += pdf['summary']['estimated_reading_time']
        
        # Video'lar için izleme süresi
        for video in files['videos']:
            if 'summary' in video and 'estimated_watch_time' in video['summary']:
                total_minutes += video['summary']['estimated_watch_time']
        
        return total_minutes
    
    def _get_priority_files(self, files: Dict) -> List[Dict]:
        """Öncelikli dosyaları belirle"""
        priority_files = []
        
        # PDF'leri öncelik sırasına koy
        for pdf in files['pdfs']:
            if 'summary' in pdf:
                summary = pdf['summary']
                score = 0
                
                # Zorlu içerik yüksek öncelik
                if summary.get('difficulty_level') == 'ADVANCED':
                    score += 3
                elif summary.get('difficulty_level') == 'MEDIUM':
                    score += 2
                
                # Çok konu içeren dosyalar öncelikli
                score += len(summary.get('important_topics', []))
                
                if score > 3:
                    priority_files.append({
                        'file': pdf['file_name'],
                        'type': 'PDF',
                        'priority_score': score,
                        'reason': f"Zorluk: {summary.get('difficulty_level', 'UNKNOWN')}, Konu sayısı: {len(summary.get('important_topics', []))}"
                    })
        
        return sorted(priority_files, key=lambda x: x['priority_score'], reverse=True)[:5]
    
    def _get_common_topics(self, files: Dict) -> List[str]:
        """Ortak konuları bul"""
        all_topics = []
        
        for pdf in files['pdfs']:
            if 'summary' in pdf and 'important_topics' in pdf['summary']:
                for topic in pdf['summary']['important_topics']:
                    all_topics.append(topic['topic'])
        
        # Sıklık hesapla
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # En sık geçenleri döndür
        return [topic for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)][:10]

if __name__ == "__main__":
    # Test
    analyzer = ContentAnalyzer()
    
    # Downloads klasörünü oluştur
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
        print("📁 'downloads' klasörü oluşturuldu")
        print("PDF ve video dosyalarınızı bu klasöre koyun")
    
    # Mevcut dosyaları analiz et
    results = analyzer.analyze_folder()
    
    # Sonuçları kaydet
    with open('content_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📊 ANALİZ ÖZETİ")
    print("=" * 30)
    print(f"PDF dosyaları: {results['summary']['total_pdfs']}")
    print(f"Video dosyaları: {results['summary']['total_videos']}")
    print(f"Toplam çalışma süresi: {results['summary']['total_study_time_estimate']} dakika")
    
    if results['summary']['priority_files']:
        print("\n🎯 ÖNCELİKLİ DOSYALAR:")
        for file in results['summary']['priority_files']:
            print(f"   • {file['file']} - {file['reason']}")
    
    if results['summary']['common_topics']:
        print("\n📚 ANA KONULAR:")
        for topic in results['summary']['common_topics']:
            print(f"   • {topic}")
    
    print("\n📁 Detaylar 'content_analysis.json' dosyasında")