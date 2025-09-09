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
        """Tüm ders verilerini toplu getir"""
        print("📚 Moodle verileri çekiliyor...")
        
        # Dersleri getir
        courses = self.get_user_courses()
        course_ids = [c['id'] for c in courses]
        
        # Her ders için içerik getir
        for course in courses:
            print(f"   📖 {course['name']} içerikleri getiriliyor...")
            course['contents'] = self.get_course_contents(course['id'])
        
        # Ödevleri getir
        assignments = self.get_assignments(course_ids)
        
        # Takvim etkinliklerini getir
        events = self.get_calendar_events()
        
        # PDF ve video linklerini topla
        pdfs = []
        videos = []
        
        for course in courses:
            for section in course.get('contents', []):
                for module in section.get('modules', []):
                    for content in module.get('contents', []):
                        if content.get('mimetype', '').startswith('application/pdf'):
                            pdfs.append({
                                'course': course['name'],
                                'name': content['filename'],
                                'url': content['fileurl'],
                                'size': content['filesize']
                            })
                        elif any(video_type in content.get('mimetype', '') for video_type in ['video/', 'audio/']):
                            videos.append({
                                'course': course['name'],
                                'name': content['filename'],
                                'url': content['fileurl'],
                                'type': content['mimetype']
                            })
        
        result = {
            'courses': courses,
            'assignments': assignments,
            'events': events,
            'pdfs': pdfs,
            'videos': videos,
            'last_updated': datetime.now().isoformat()
        }
        
        print(f"✅ Veri çekme tamamlandı:")
        print(f"   🎓 {len(courses)} ders")
        print(f"   📝 {len(assignments)} ödev")
        print(f"   📅 {len(events)} etkinlik")
        print(f"   📄 {len(pdfs)} PDF")
        print(f"   🎥 {len(videos)} video/ses dosyası")
        
        return result

def setup_moodle_connection():
    """Moodle bağlantısını kur"""
    print("🔧 Moodle API kurulumu")
    print("-" * 30)
    
    moodle_url = input("Moodle URL (https://moodle.unive.it): ").strip() or "https://moodle.unive.it"
    
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