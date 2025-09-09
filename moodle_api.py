#!/usr/bin/env python3
"""
Ca' Foscari Moodle Web Services API Integration
Resmi Moodle API kullanarak güvenli veri çekme
"""

import requests
import json
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional

class MoodleAPI:
    def __init__(self, moodle_url: str, token: str):
        """
        Moodle API başlatıcısı
        Args:
            moodle_url: Moodle URL (örn: https://moodle.unive.it)
            token: Moodle Web Services token
        """
        self.base_url = moodle_url.rstrip('/')
        self.token = token
        self.api_url = f"{self.base_url}/webservice/rest/server.php"
        
    def _api_call(self, function: str, params: Dict = None) -> Dict:
        """
        Moodle API çağrısı yap
        Args:
            function: API fonksiyon adı
            params: Ek parametreler
        Returns:
            API yanıtı
        """
        data = {
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json'
        }
        
        if params:
            data.update(params)
            
        try:
            response = requests.post(self.api_url, data=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API çağrı hatası: {e}")
            return {}
    
    def get_user_courses(self) -> List[Dict]:
        """Kullanıcının kayıtlı olduğu dersleri getir"""
        courses = self._api_call('core_enrol_get_users_courses', {'userid': 0})  # 0 = current user
        
        processed_courses = []
        for course in courses:
            processed_courses.append({
                'id': course.get('id'),
                'name': course.get('fullname', ''),
                'shortname': course.get('shortname', ''),
                'summary': course.get('summary', ''),
                'startdate': datetime.fromtimestamp(course.get('startdate', 0)),
                'enddate': datetime.fromtimestamp(course.get('enddate', 0)) if course.get('enddate') else None
            })
        
        return processed_courses
    
    def get_course_contents(self, course_id: int) -> List[Dict]:
        """Ders içeriklerini getir"""
        contents = self._api_call('core_course_get_contents', {'courseid': course_id})
        
        processed_contents = []
        for section in contents:
            section_data = {
                'section_name': section.get('name', ''),
                'summary': section.get('summary', ''),
                'modules': []
            }
            
            for module in section.get('modules', []):
                module_data = {
                    'name': module.get('name', ''),
                    'type': module.get('modname', ''),
                    'url': module.get('url', ''),
                    'description': module.get('description', ''),
                    'contents': []
                }
                
                # Dosya içerikleri
                for content in module.get('contents', []):
                    if content.get('type') == 'file':
                        module_data['contents'].append({
                            'filename': content.get('filename', ''),
                            'fileurl': content.get('fileurl', ''),
                            'filesize': content.get('filesize', 0),
                            'mimetype': content.get('mimetype', '')
                        })
                
                section_data['modules'].append(module_data)
            
            processed_contents.append(section_data)
        
        return processed_contents
    
    def get_assignments(self, course_ids: List[int] = None) -> List[Dict]:
        """Ödevleri getir"""
        params = {}
        if course_ids:
            params['courseids'] = course_ids
            
        assignments = self._api_call('mod_assign_get_assignments', params)
        
        processed_assignments = []
        for course in assignments.get('courses', []):
            for assignment in course.get('assignments', []):
                processed_assignments.append({
                    'id': assignment.get('id'),
                    'course_id': course.get('id'),
                    'name': assignment.get('name', ''),
                    'intro': assignment.get('intro', ''),
                    'due_date': datetime.fromtimestamp(assignment.get('duedate', 0)) if assignment.get('duedate') else None,
                    'allow_submissions_from': datetime.fromtimestamp(assignment.get('allowsubmissionsfromdate', 0)) if assignment.get('allowsubmissionsfromdate') else None,
                    'grade': assignment.get('grade', 0),
                    'priority': self._calculate_priority(assignment.get('duedate', 0))
                })
        
        return processed_assignments
    
    def get_calendar_events(self) -> List[Dict]:
        """Takvim etkinliklerini getir (sınavlar, ödevler vb.)"""
        events = self._api_call('core_calendar_get_calendar_events')
        
        processed_events = []
        for event in events.get('events', []):
            event_time = datetime.fromtimestamp(event.get('timestart', 0)) if event.get('timestart') else None
            
            processed_events.append({
                'id': event.get('id'),
                'name': event.get('name', ''),
                'description': event.get('description', ''),
                'course_id': event.get('courseid'),
                'event_type': event.get('eventtype', ''),
                'time_start': event_time,
                'duration': event.get('timeduration', 0),
                'priority': self._calculate_event_priority(event_time, event.get('eventtype', ''))
            })
        
        return processed_events
    
    def search_content(self, query: str) -> List[Dict]:
        """İçeriklerde arama yap"""
        search_results = self._api_call('core_search_get_results', {
            'query': query,
            'filters': {}
        })
        
        results = []
        for result in search_results.get('results', []):
            results.append({
                'title': result.get('title', ''),
                'content': result.get('content', ''),
                'course_id': result.get('courseid'),
                'url': result.get('url', ''),
                'type': result.get('componentname', '')
            })
        
        return results

    def get_forums_by_courses(self, course_ids: List[int] = None) -> List[Dict]:
        """Derslerdeki forumları getir"""
        if not course_ids:
            courses = self.get_user_courses()
            course_ids = [c['id'] for c in courses]
        
        forums = self._api_call('mod_forum_get_forums_by_courses', {'courseids': course_ids})
        
        processed_forums = []
        # API response is direct list of forums
        for forum in forums if isinstance(forums, list) else []:
            # Intro dosyalarından da içerik topla
            intro_files = []
            for intro_file in forum.get('introfiles', []):
                if intro_file.get('mimetype', ''):
                    intro_files.append({
                        'filename': intro_file.get('filename', ''),
                        'fileurl': intro_file.get('fileurl', ''),
                        'filesize': intro_file.get('filesize', 0),
                        'mimetype': intro_file.get('mimetype', '')
                    })
            
            processed_forums.append({
                'id': forum.get('id'),
                'course_id': forum.get('course'),
                'name': forum.get('name', ''),
                'intro': forum.get('intro', ''),
                'type': forum.get('type', ''),
                'discussions_count': forum.get('numdiscussions', 0),
                'intro_files': intro_files,
                'cmid': forum.get('cmid'),
                'timemodified': datetime.fromtimestamp(forum.get('timemodified', 0)) if forum.get('timemodified') else None
            })
        
        return processed_forums

    def get_resources_by_courses(self, course_ids: List[int] = None) -> List[Dict]:
        """Derslerdeki kaynakları (dosyalar) getir"""
        if not course_ids:
            courses = self.get_user_courses()
            course_ids = [c['id'] for c in courses]
        
        response = self._api_call('mod_resource_get_resources_by_courses', {'courseids': course_ids})
        
        processed_resources = []
        # API response has 'resources' key
        for resource in response.get('resources', []):
            # Intro dosyaları
            intro_files = []
            for intro_file in resource.get('introfiles', []):
                if intro_file.get('mimetype', ''):
                    intro_files.append({
                        'filename': intro_file.get('filename', ''),
                        'fileurl': intro_file.get('fileurl', ''),
                        'filesize': intro_file.get('filesize', 0),
                        'mimetype': intro_file.get('mimetype', '')
                    })
            
            # İçerik dosyaları
            content_files = []
            for content_file in resource.get('contentfiles', []):
                if content_file.get('mimetype', ''):
                    content_files.append({
                        'filename': content_file.get('filename', ''),
                        'fileurl': content_file.get('fileurl', ''),
                        'filesize': content_file.get('filesize', 0),
                        'mimetype': content_file.get('mimetype', '')
                    })
            
            processed_resources.append({
                'id': resource.get('id'),
                'course_id': resource.get('course'),
                'coursemodule': resource.get('coursemodule'),
                'name': resource.get('name', ''),
                'intro': resource.get('intro', ''),
                'section': resource.get('section'),
                'visible': resource.get('visible'),
                'intro_files': intro_files,
                'contentfiles': content_files,
                'timemodified': datetime.fromtimestamp(resource.get('timemodified', 0)) if resource.get('timemodified') else None
            })
        
        return processed_resources

    def get_pages_by_courses(self, course_ids: List[int] = None) -> List[Dict]:
        """Derslerdeki sayfaları getir"""
        if not course_ids:
            courses = self.get_user_courses()
            course_ids = [c['id'] for c in courses]
        
        response = self._api_call('mod_page_get_pages_by_courses', {'courseids': course_ids})
        
        processed_pages = []
        # API response has 'pages' key
        for page in response.get('pages', []):
            # Intro dosyaları
            intro_files = []
            for intro_file in page.get('introfiles', []):
                if intro_file.get('mimetype', ''):
                    intro_files.append({
                        'filename': intro_file.get('filename', ''),
                        'fileurl': intro_file.get('fileurl', ''),
                        'filesize': intro_file.get('filesize', 0),
                        'mimetype': intro_file.get('mimetype', '')
                    })
            
            # İçerik dosyaları
            content_files = []
            for content_file in page.get('contentfiles', []):
                if content_file.get('mimetype', ''):
                    content_files.append({
                        'filename': content_file.get('filename', ''),
                        'fileurl': content_file.get('fileurl', ''),
                        'filesize': content_file.get('filesize', 0),
                        'mimetype': content_file.get('mimetype', '')
                    })
            
            processed_pages.append({
                'id': page.get('id'),
                'course_id': page.get('course'),
                'coursemodule': page.get('coursemodule'),
                'name': page.get('name', ''),
                'intro': page.get('intro', ''),
                'content': page.get('content', ''),
                'section': page.get('section'),
                'visible': page.get('visible'),
                'intro_files': intro_files,
                'content_files': content_files,
                'timemodified': datetime.fromtimestamp(page.get('timemodified', 0)) if page.get('timemodified') else None
            })
        
        return processed_pages
    
    def _calculate_priority(self, due_timestamp: int) -> str:
        """Tarihe göre öncelik hesapla"""
        if not due_timestamp:
            return "LOW"
        
        due_date = datetime.fromtimestamp(due_timestamp)
        today = datetime.now()
        days_left = (due_date - today).days
        
        if days_left < 0:
            return "OVERDUE"
        elif days_left <= 2:
            return "CRITICAL"
        elif days_left <= 7:
            return "HIGH"
        elif days_left <= 14:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_event_priority(self, event_time: datetime, event_type: str) -> str:
        """Etkinlik önceliği hesapla"""
        if not event_time:
            return "LOW"
        
        days_left = (event_time - datetime.now()).days
        
        # Sınav türleri yüksek öncelik
        if any(keyword in event_type.lower() for keyword in ['exam', 'test', 'quiz', 'sınav']):
            if days_left <= 3:
                return "CRITICAL"
            elif days_left <= 7:
                return "HIGH"
            else:
                return "MEDIUM"
        
        # Normal etkinlikler
        if days_left <= 1:
            return "HIGH"
        elif days_left <= 7:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_full_course_data(self) -> Dict:
        """Tüm ders verilerini toplu getir - GELİŞTİRİLMİŞ VERSİYON"""
        print("📚 Moodle verileri çekiliyor...")
        
        # Dersleri getir
        courses = self.get_user_courses()
        course_ids = [c['id'] for c in courses]
        
        # Her ders için içerik getir
        for course in courses:
            print(f"   📖 {course['name']} içerikleri getiriliyor...")
            course['contents'] = self.get_course_contents(course['id'])
        
        # Ek veri kaynakları
        print("   📋 Ek kaynaklar getiriliyor...")
        resources = self.get_resources_by_courses(course_ids)
        pages = self.get_pages_by_courses(course_ids)
        forums = self.get_forums_by_courses(course_ids)
        
        # Ödevleri getir
        assignments = self.get_assignments(course_ids)
        
        # Takvim etkinliklerini getir
        events = self.get_calendar_events()
        
        # PDF ve video linklerini topla - GELİŞTİRİLMİŞ
        pdfs = []
        videos = []
        documents = []
        
        # Ders içeriklerinden topla
        for course in courses:
            for section in course.get('contents', []):
                for module in section.get('modules', []):
                    for content in module.get('contents', []):
                        mimetype = content.get('mimetype', '').lower()
                        file_data = {
                            'course': course['name'],
                            'course_id': course['id'],
                            'section': section.get('section_name', ''),
                            'module': module.get('name', ''),
                            'name': content['filename'],
                            'url': content['fileurl'],
                            'size': content['filesize']
                        }
                        
                        if mimetype.startswith('application/pdf'):
                            pdfs.append(file_data)
                        elif any(video_type in mimetype for video_type in ['video/', 'audio/']):
                            videos.append({**file_data, 'type': mimetype})
                        elif any(doc_type in mimetype for doc_type in ['application/msword', 'application/vnd.openxmlformats', 'text/']):
                            documents.append({**file_data, 'type': mimetype})
        
        # Kaynaklardan (resources) ek dosyalar topla
        for resource in resources:
            course_name = next((c['name'] for c in courses if c['id'] == resource['course_id']), 'Unknown Course')
            
            # Intro dosyalarından
            for intro_file in resource.get('intro_files', []):
                mimetype = intro_file.get('mimetype', '').lower()
                file_data = {
                    'course': course_name,
                    'course_id': resource['course_id'],
                    'section': 'Resource Intro',
                    'module': resource['name'],
                    'name': intro_file.get('filename', ''),
                    'url': intro_file.get('fileurl', ''),
                    'size': intro_file.get('filesize', 0)
                }
                
                if mimetype.startswith('application/pdf'):
                    pdfs.append(file_data)
                elif any(video_type in mimetype for video_type in ['video/', 'audio/']):
                    videos.append({**file_data, 'type': mimetype})
                elif any(doc_type in mimetype for doc_type in ['application/msword', 'application/vnd.openxmlformats', 'text/']):
                    documents.append({**file_data, 'type': mimetype})
            
            # İçerik dosyalarından
            for contentfile in resource.get('contentfiles', []):
                mimetype = contentfile.get('mimetype', '').lower()
                file_data = {
                    'course': course_name,
                    'course_id': resource['course_id'],
                    'section': 'Resources',
                    'module': resource['name'],
                    'name': contentfile.get('filename', ''),
                    'url': contentfile.get('fileurl', ''),
                    'size': contentfile.get('filesize', 0)
                }
                
                if mimetype.startswith('application/pdf'):
                    pdfs.append(file_data)
                elif any(video_type in mimetype for video_type in ['video/', 'audio/']):
                    videos.append({**file_data, 'type': mimetype})
                elif any(doc_type in mimetype for doc_type in ['application/msword', 'application/vnd.openxmlformats', 'text/']):
                    documents.append({**file_data, 'type': mimetype})
        
        # Sayfalardan (pages) ek dosyalar topla
        for page in pages:
            course_name = next((c['name'] for c in courses if c['id'] == page['course_id']), 'Unknown Course')
            
            # Intro dosyalarından
            for intro_file in page.get('intro_files', []):
                mimetype = intro_file.get('mimetype', '').lower()
                file_data = {
                    'course': course_name,
                    'course_id': page['course_id'],
                    'section': 'Page Intro',
                    'module': page['name'],
                    'name': intro_file.get('filename', ''),
                    'url': intro_file.get('fileurl', ''),
                    'size': intro_file.get('filesize', 0)
                }
                
                if mimetype.startswith('application/pdf'):
                    pdfs.append(file_data)
                elif any(video_type in mimetype for video_type in ['video/', 'audio/']):
                    videos.append({**file_data, 'type': mimetype})
                elif any(doc_type in mimetype for doc_type in ['application/msword', 'application/vnd.openxmlformats', 'text/']):
                    documents.append({**file_data, 'type': mimetype})
            
            # İçerik dosyalarından
            for content_file in page.get('content_files', []):
                mimetype = content_file.get('mimetype', '').lower()
                file_data = {
                    'course': course_name,
                    'course_id': page['course_id'],
                    'section': 'Page Content',
                    'module': page['name'],
                    'name': content_file.get('filename', ''),
                    'url': content_file.get('fileurl', ''),
                    'size': content_file.get('filesize', 0)
                }
                
                if mimetype.startswith('application/pdf'):
                    pdfs.append(file_data)
                elif any(video_type in mimetype for video_type in ['video/', 'audio/']):
                    videos.append({**file_data, 'type': mimetype})
                elif any(doc_type in mimetype for doc_type in ['application/msword', 'application/vnd.openxmlformats', 'text/']):
                    documents.append({**file_data, 'type': mimetype})
        
        # Forumlardan dosyalar topla
        for forum in forums:
            course_name = next((c['name'] for c in courses if c['id'] == forum['course_id']), 'Unknown Course')
            
            for intro_file in forum.get('intro_files', []):
                mimetype = intro_file.get('mimetype', '').lower()
                file_data = {
                    'course': course_name,
                    'course_id': forum['course_id'],
                    'section': 'Forum',
                    'module': forum['name'],
                    'name': intro_file.get('filename', ''),
                    'url': intro_file.get('fileurl', ''),
                    'size': intro_file.get('filesize', 0)
                }
                
                if mimetype.startswith('application/pdf'):
                    pdfs.append(file_data)
                elif any(video_type in mimetype for video_type in ['video/', 'audio/']):
                    videos.append({**file_data, 'type': mimetype})
                elif any(doc_type in mimetype for doc_type in ['application/msword', 'application/vnd.openxmlformats', 'text/']):
                    documents.append({**file_data, 'type': mimetype})
        
        result = {
            'courses': courses,
            'assignments': assignments,
            'events': events,
            'pdfs': pdfs,
            'videos': videos,
            'documents': documents,
            'pages': pages,
            'forums': forums,
            'resources': resources,
            'last_updated': datetime.now().isoformat()
        }
        
        print(f"✅ Veri çekme tamamlandı:")
        print(f"   🎓 {len(courses)} ders")
        print(f"   📝 {len(assignments)} ödev")
        print(f"   📅 {len(events)} etkinlik")
        print(f"   📄 {len(pdfs)} PDF")
        print(f"   🎥 {len(videos)} video/ses dosyası")
        print(f"   📋 {len(documents)} doküman")
        print(f"   📰 {len(pages)} sayfa")
        print(f"   💬 {len(forums)} forum")
        
        return result

def setup_moodle_connection():
    """Moodle bağlantısını kur - otomatik yapılandırma ile"""
    from api_config import api_config
    
    print("🔧 Moodle API kurulumu")
    print("-" * 30)
    
    # API config'den ayarları al
    moodle_config = api_config.get_moodle_config()
    
    # URL otomatik dolu
    moodle_url = moodle_config.get('url', 'https://moodle.unive.it')
    print(f"Moodle URL: {moodle_url}")
    
    # Token kontrolü
    token = moodle_config.get('token')
    
    if not token:
        print("\n📱 Moodle Web Services Token almak için:")
        print("1. Moodle'a giriş yapın")
        print("2. User menu > Preferences > User account > Security keys")
        print("3. 'Create token for service' seçin")
        print("4. Service: 'Moodle mobile web service'")
        print("5. Token'ı kopyalayın")
        
        token = input("\nMoodle Web Services Token: ").strip()
        
        if not token:
            print("❌ Token gerekli!")
            return None
        
        # Token'ı kaydet
        api_config.set_moodle_token(token)
    else:
        print(f"✅ Token mevcut (api_keys klasöründen yüklendi)")
    
    # Bağlantıyı test et
    api = MoodleAPI(moodle_url, token)
    test_result = api._api_call('core_webservice_get_site_info')
    
    if 'sitename' in test_result:
        print(f"✅ Bağlantı başarılı: {test_result.get('sitename', 'Unknown')}")
        return api
    else:
        print("❌ Bağlantı hatası. Token'ı kontrol edin.")
        return None

if __name__ == "__main__":
    # Test
    api = setup_moodle_connection()
    if api:
        data = api.get_full_course_data()
        
        # Veriyi kaydet
        with open('moodle_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print("\n📁 Veriler 'moodle_data.json' dosyasına kaydedildi")