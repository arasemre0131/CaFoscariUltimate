#!/usr/bin/env python3
"""
Claude API ile Akıllı Çalışma Planı Üreticisi
Moodle verileri, mail analizi ve içerik analizini birleştirerek kişiselleştirilmiş çalışma planı oluşturur
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import anthropic

class StudyPlanner:
    def __init__(self, claude_api_key: str = None):
        """
        Çalışma planı üreticisi başlatıcısı
        Args:
            claude_api_key: Claude API anahtarı
        """
        self.claude_api_key = claude_api_key or os.getenv('CLAUDE_API_KEY')
        
        if self.claude_api_key:
            self.claude = anthropic.Anthropic(api_key=self.claude_api_key)
        else:
            self.claude = None
            print("⚠️  Claude API key bulunamadı. AI analizi yapılamayacak.")
        
        self.student_profile = self._load_or_create_profile()
        
    def _load_or_create_profile(self) -> Dict:
        """Öğrenci profilini yükle veya oluştur"""
        profile_file = 'student_profile.json'
        
        if os.path.exists(profile_file):
            with open(profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Varsayılan profil
        profile = {
            'name': 'Emre Aras',
            'student_id': '907842',
            'university': 'Ca\' Foscari',
            'study_preferences': {
                'daily_study_hours': 4,
                'preferred_study_times': ['09:00-12:00', '14:00-17:00'],
                'break_interval': 25,  # Pomodoro
                'difficulty_preference': 'challenging_first'  # easy_first, challenging_first, mixed
            },
            'performance_history': {
                'strong_subjects': ['Computer Architecture', 'Programming'],
                'weak_subjects': ['Mathematics'],
                'average_study_time_per_page': 3,  # dakika
                'retention_rate': 0.7
            }
        }
        
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        return profile
    
    def load_all_data(self) -> Dict:
        """Tüm mevcut verileri yükle"""
        data = {
            'moodle_data': {},
            'gmail_analysis': {},
            'content_analysis': {},
            'manual_exams': []
        }
        
        # Moodle verileri
        if os.path.exists('moodle_data.json'):
            with open('moodle_data.json', 'r', encoding='utf-8') as f:
                data['moodle_data'] = json.load(f)
        
        # Gmail analizi
        if os.path.exists('gmail_analysis.json'):
            with open('gmail_analysis.json', 'r', encoding='utf-8') as f:
                data['gmail_analysis'] = json.load(f)
        
        # İçerik analizi
        if os.path.exists('content_analysis.json'):
            with open('content_analysis.json', 'r', encoding='utf-8') as f:
                data['content_analysis'] = json.load(f)
        
        # Manuel sınav tarihleri
        if os.path.exists('manual_exams.json'):
            with open('manual_exams.json', 'r', encoding='utf-8') as f:
                data['manual_exams'] = json.load(f)
        
        return data
    
    def add_manual_exam(self, course: str, exam_name: str, exam_date: str, exam_time: str = "09:00", notes: str = ""):
        """Manuel sınav tarihi ekle"""
        manual_exams_file = 'manual_exams.json'
        
        if os.path.exists(manual_exams_file):
            with open(manual_exams_file, 'r', encoding='utf-8') as f:
                exams = json.load(f)
        else:
            exams = []
        
        exam_entry = {
            'course': course,
            'exam_name': exam_name,
            'exam_date': exam_date,
            'exam_time': exam_time,
            'notes': notes,
            'added_date': datetime.now().isoformat(),
            'priority': self._calculate_exam_priority(exam_date)
        }
        
        exams.append(exam_entry)
        
        with open(manual_exams_file, 'w', encoding='utf-8') as f:
            json.dump(exams, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Sınav eklendi: {course} - {exam_name} ({exam_date})")
        return exam_entry
    
    def _calculate_exam_priority(self, exam_date: str) -> str:
        """Sınav tarihine göre öncelik hesapla"""
        try:
            exam_dt = datetime.strptime(exam_date, '%Y-%m-%d')
            days_until = (exam_dt - datetime.now()).days
            
            if days_until <= 3:
                return "CRITICAL"
            elif days_until <= 7:
                return "HIGH"
            elif days_until <= 14:
                return "MEDIUM"
            else:
                return "LOW"
        except:
            return "LOW"
    
    def generate_comprehensive_study_plan(self, days_ahead: int = 14) -> Dict:
        """Kapsamlı çalışma planı oluştur"""
        print("📊 Çalışma planı oluşturuluyor...")
        
        # Tüm verileri yükle
        all_data = self.load_all_data()
        
        # Temel analiz
        basic_analysis = self._analyze_current_situation(all_data)
        
        # Claude ile AI analizi
        ai_analysis = None
        if self.claude:
            ai_analysis = self._generate_ai_analysis(all_data, basic_analysis)
        
        # Haftalık plan oluştur
        weekly_plan = self._generate_weekly_plan(all_data, basic_analysis, days_ahead)
        
        # Günlük detaylar
        daily_schedule = self._generate_daily_schedules(all_data, weekly_plan, days_ahead)
        
        # Final plan
        study_plan = {
            'creation_date': datetime.now().isoformat(),
            'student_profile': self.student_profile,
            'plan_duration_days': days_ahead,
            'data_summary': basic_analysis,
            'ai_insights': ai_analysis,
            'weekly_overview': weekly_plan,
            'daily_schedules': daily_schedule,
            'recommendations': self._generate_recommendations(all_data, basic_analysis),
            'progress_tracking': self._create_progress_template(daily_schedule)
        }
        
        # Planı kaydet
        with open('comprehensive_study_plan.json', 'w', encoding='utf-8') as f:
            json.dump(study_plan, f, indent=2, ensure_ascii=False, default=str)
        
        return study_plan
    
    def _analyze_current_situation(self, data: Dict) -> Dict:
        """Mevcut durumu analiz et"""
        analysis = {
            'assignments_count': 0,
            'critical_assignments': 0,
            'upcoming_exams': 0,
            'high_priority_emails': 0,
            'total_study_materials': 0,
            'estimated_workload': 0,
            'urgent_deadlines': []
        }
        
        # Moodle ödevleri
        moodle_assignments = data.get('moodle_data', {}).get('assignments', [])
        analysis['assignments_count'] = len(moodle_assignments)
        
        critical_assignments = []
        for assignment in moodle_assignments:
            if assignment.get('priority') in ['CRITICAL', 'HIGH']:
                analysis['critical_assignments'] += 1
                critical_assignments.append(assignment)
        
        # Manuel sınavlar
        manual_exams = data.get('manual_exams', [])
        upcoming_exams = []
        for exam in manual_exams:
            try:
                exam_date = datetime.strptime(exam['exam_date'], '%Y-%m-%d')
                days_until = (exam_date - datetime.now()).days
                if days_until <= 30:  # 30 gün içindeki sınavlar
                    upcoming_exams.append(exam)
                    analysis['upcoming_exams'] += 1
            except:
                continue
        
        # Gmail analizi
        gmail_data = data.get('gmail_analysis', [])
        if isinstance(gmail_data, list):
            for email in gmail_data:
                if email.get('priority_level') in ['CRITICAL', 'HIGH']:
                    analysis['high_priority_emails'] += 1
        
        # İçerik analizi
        content_data = data.get('content_analysis', {})
        if 'summary' in content_data:
            analysis['total_study_materials'] = (
                content_data['summary'].get('total_pdfs', 0) +
                content_data['summary'].get('total_videos', 0)
            )
            analysis['estimated_workload'] = content_data['summary'].get('total_study_time_estimate', 0)
        
        # Acil deadline'lar
        all_deadlines = []
        
        # Ödev deadline'ları
        for assignment in critical_assignments:
            if assignment.get('due_date'):
                all_deadlines.append({
                    'type': 'assignment',
                    'name': assignment['name'],
                    'course': assignment['course'],
                    'date': assignment['due_date'],
                    'priority': assignment.get('priority', 'LOW')
                })
        
        # Sınav tarihleri
        for exam in upcoming_exams:
            all_deadlines.append({
                'type': 'exam',
                'name': exam['exam_name'],
                'course': exam['course'],
                'date': exam['exam_date'],
                'priority': exam.get('priority', 'LOW')
            })
        
        # Deadline'ları tarihe göre sırala
        analysis['urgent_deadlines'] = sorted(
            all_deadlines, 
            key=lambda x: x['date'] if isinstance(x['date'], str) else str(x['date'])
        )[:10]
        
        return analysis
    
    def _generate_ai_analysis(self, data: Dict, basic_analysis: Dict) -> Optional[str]:
        """Claude AI ile derinlemesine analiz"""
        if not self.claude:
            return None
        
        prompt = f"""
Sen Ca' Foscari Üniversitesi Computer Architecture bölümü öğrencisi Emre Aras (907842) için kişisel çalışma danışmanısın.

MEVCUT DURUM ANALİZİ:
- Toplam ödev sayısı: {basic_analysis['assignments_count']}
- Kritik ödevler: {basic_analysis['critical_assignments']}
- Yaklaşan sınavlar: {basic_analysis['upcoming_exams']}
- Yüksek öncelikli mailler: {basic_analysis['high_priority_emails']}
- Çalışma materyali: {basic_analysis['total_study_materials']} dosya
- Tahmini çalışma süresi: {basic_analysis['estimated_workload']} dakika

YAKLAŞAN DEADLINE'LAR:
{json.dumps(basic_analysis['urgent_deadlines'][:5], indent=2)}

ÖĞRENCİ PROFİLİ:
- Günlük çalışma süresi: {self.student_profile['study_preferences']['daily_study_hours']} saat
- Çalışma saatleri: {self.student_profile['study_preferences']['preferred_study_times']}
- Güçlü konular: {self.student_profile['performance_history']['strong_subjects']}
- Zayıf konular: {self.student_profile['performance_history']['weak_subjects']}

LÜTFEN ŞUNLARI YAP:
1. Mevcut durumu değerlendir ve stres seviyesini belirle (1-10)
2. En kritik konulara odaklanma stratejisi öner
3. Haftalık çalışma dağılımı öner
4. Performans artırma önerileri ver
5. Zaman yönetimi taktikleri öner

Türkçe, pratik ve actionable öneriler ver. Maksimum 500 kelime.
        """
        
        try:
            response = self.claude.messages.create(
                model="claude-3-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"❌ Claude AI analiz hatası: {e}")
            return None
    
    def _generate_weekly_plan(self, data: Dict, analysis: Dict, days: int) -> Dict:
        """Haftalık çalışma planı oluştur"""
        weeks = {}
        current_date = datetime.now()
        
        # Haftalık gruplandırma
        for day_offset in range(days):
            target_date = current_date + timedelta(days=day_offset)
            week_key = f"Week_{target_date.strftime('%Y-%W')}"
            
            if week_key not in weeks:
                weeks[week_key] = {
                    'week_start': target_date.strftime('%Y-%m-%d'),
                    'focus_areas': [],
                    'major_deadlines': [],
                    'total_study_hours': 0
                }
        
        # Deadline'ları haftalara dağıt
        for deadline in analysis['urgent_deadlines']:
            try:
                if isinstance(deadline['date'], str):
                    deadline_date = datetime.strptime(deadline['date'], '%Y-%m-%d')
                else:
                    deadline_date = datetime.fromisoformat(str(deadline['date']))
                
                week_key = f"Week_{deadline_date.strftime('%Y-%W')}"
                
                if week_key in weeks:
                    weeks[week_key]['major_deadlines'].append(deadline)
                    
                    # Focus area ekle
                    if deadline['course'] not in weeks[week_key]['focus_areas']:
                        weeks[week_key]['focus_areas'].append(deadline['course'])
                        
            except:
                continue
        
        # Haftalık çalışma saatlerini hesapla
        daily_hours = self.student_profile['study_preferences']['daily_study_hours']
        for week_key in weeks:
            weeks[week_key]['total_study_hours'] = daily_hours * 7  # 7 gün
        
        return weeks
    
    def _generate_daily_schedules(self, data: Dict, weekly_plan: Dict, days: int) -> List[Dict]:
        """Günlük çalışma programları oluştur"""
        daily_schedules = []
        current_date = datetime.now()
        
        # İçerik analizi verilerini hazırla
        content_data = data.get('content_analysis', {})
        priority_files = content_data.get('summary', {}).get('priority_files', [])
        common_topics = content_data.get('summary', {}).get('common_topics', [])
        
        for day_offset in range(days):
            target_date = current_date + timedelta(days=day_offset)
            day_name = target_date.strftime('%A')
            date_str = target_date.strftime('%Y-%m-%d')
            
            # Bu günün deadline'larını bul
            day_deadlines = []
            for deadline in data.get('manual_exams', []):
                if deadline.get('exam_date') == date_str:
                    day_deadlines.append(deadline)
            
            # Çalışma bloklarını oluştur
            study_blocks = self._create_daily_study_blocks(
                target_date, day_deadlines, priority_files, common_topics
            )
            
            daily_schedule = {
                'date': date_str,
                'day_name': day_name,
                'day_type': self._get_day_type(target_date, day_deadlines),
                'deadlines': day_deadlines,
                'study_blocks': study_blocks,
                'total_study_time': sum(block.get('duration_minutes', 0) for block in study_blocks),
                'priority_level': self._calculate_day_priority(day_deadlines),
                'notes': self._generate_daily_notes(target_date, day_deadlines)
            }
            
            daily_schedules.append(daily_schedule)
        
        return daily_schedules
    
    def _create_daily_study_blocks(self, date: datetime, deadlines: List, priority_files: List, topics: List) -> List[Dict]:
        """Günlük çalışma bloklarını oluştur"""
        blocks = []
        study_times = self.student_profile['study_preferences']['preferred_study_times']
        
        # Her çalışma saati için blok oluştur
        for time_slot in study_times:
            start_time, end_time = time_slot.split('-')
            duration = self._calculate_duration(start_time, end_time)
            
            # İçerik belirleme
            if deadlines and len(deadlines) > 0:
                # Deadline varsa ona odaklan
                subject = deadlines[0]['course']
                topic = f"Sınav hazırlığı: {deadlines[0]['exam_name']}"
                priority = "HIGH"
            elif priority_files and len(priority_files) > 0:
                # Öncelikli dosyalar varsa
                file_info = priority_files[0]
                subject = "Computer Architecture"  # Varsayılan
                topic = f"PDF çalışması: {file_info.get('file', 'Unknown')}"
                priority = "MEDIUM"
            elif topics and len(topics) > 0:
                # Genel konular
                subject = "Computer Architecture"
                topic = f"Konu çalışması: {topics[0]}"
                priority = "MEDIUM"
            else:
                # Varsayılan çalışma
                subject = "Computer Architecture"
                topic = "Genel tekrar"
                priority = "LOW"
            
            block = {
                'time_slot': time_slot,
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': duration,
                'subject': subject,
                'topic': topic,
                'priority': priority,
                'study_method': self._suggest_study_method(topic),
                'break_schedule': self._calculate_breaks(duration)
            }
            
            blocks.append(block)
        
        return blocks
    
    def _calculate_duration(self, start: str, end: str) -> int:
        """İki zaman arasındaki süreyi dakika cinsinden hesapla"""
        try:
            start_time = datetime.strptime(start, '%H:%M').time()
            end_time = datetime.strptime(end, '%H:%M').time()
            
            start_dt = datetime.combine(datetime.today(), start_time)
            end_dt = datetime.combine(datetime.today(), end_time)
            
            return int((end_dt - start_dt).total_seconds() / 60)
        except:
            return 120  # Varsayılan 2 saat
    
    def _get_day_type(self, date: datetime, deadlines: List) -> str:
        """Günün tipini belirle"""
        if deadlines:
            return "EXAM_DAY"
        elif date.weekday() == 6:  # Pazar
            return "LIGHT_STUDY"
        elif date.weekday() == 5:  # Cumartesi
            return "REVIEW_DAY"
        else:
            return "REGULAR_STUDY"
    
    def _calculate_day_priority(self, deadlines: List) -> str:
        """Günün öncelik seviyesini hesapla"""
        if any(d.get('priority') == 'CRITICAL' for d in deadlines):
            return "CRITICAL"
        elif any(d.get('priority') == 'HIGH' for d in deadlines):
            return "HIGH"
        elif deadlines:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_daily_notes(self, date: datetime, deadlines: List) -> str:
        """Günlük notlar oluştur"""
        notes = []
        
        if deadlines:
            notes.append(f"🎯 Sınav günü: {', '.join([d['exam_name'] for d in deadlines])}")
        
        if date.weekday() == 6:  # Pazar
            notes.append("😌 Hafta sonu - Rahat çalışma günü")
        elif date.weekday() == 0:  # Pazartesi
            notes.append("💪 Haftanın başlangıcı - Enerjik başla!")
        
        return " | ".join(notes) if notes else "Düzenli çalışma günü"
    
    def _suggest_study_method(self, topic: str) -> str:
        """Konuya göre çalışma yöntemi öner"""
        topic_lower = topic.lower()
        
        if 'sınav' in topic_lower or 'exam' in topic_lower:
            return "Mock exam + Active recall"
        elif 'pdf' in topic_lower:
            return "Active reading + Note taking"
        elif 'video' in topic_lower:
            return "Watch + Pause + Practice"
        elif 'tekrar' in topic_lower or 'review' in topic_lower:
            return "Spaced repetition + Flashcards"
        else:
            return "Pomodoro technique + Active learning"
    
    def _calculate_breaks(self, duration_minutes: int) -> List[str]:
        """Mola programı hesapla"""
        break_interval = self.student_profile['study_preferences']['break_interval']
        breaks = []
        
        current_time = 0
        while current_time + break_interval < duration_minutes:
            current_time += break_interval
            breaks.append(f"{current_time} dakika sonra 5 dk mola")
        
        return breaks
    
    def _generate_recommendations(self, data: Dict, analysis: Dict) -> Dict:
        """Genel öneriler oluştur"""
        recommendations = {
            'priority_actions': [],
            'study_tips': [],
            'time_management': [],
            'performance_boosters': []
        }
        
        # Öncelikli eylemler
        if analysis['critical_assignments'] > 0:
            recommendations['priority_actions'].append(
                f"🔥 {analysis['critical_assignments']} kritik ödev var - bunlara öncelik ver!"
            )
        
        if analysis['upcoming_exams'] > 0:
            recommendations['priority_actions'].append(
                f"📚 {analysis['upcoming_exams']} yaklaşan sınav için hazırlık yap"
            )
        
        # Çalışma ipuçları
        recommendations['study_tips'].extend([
            "📖 Aktif okuma tekniği kullan (özetleme, soru sorma)",
            "🧠 Her 25 dakikada bir 5 dakika mola ver (Pomodoro)",
            "✍️ Anladıklarını kendi kelimelerinle yaz",
            "🔄 Konuları düzenli aralıklarla tekrar et"
        ])
        
        # Zaman yönetimi
        recommendations['time_management'].extend([
            "⏰ En zor konuları enerjinin yüksek olduğu saatlerde çalış",
            "📅 Büyük görevleri küçük parçalara böl",
            "🎯 Her çalışma seansı için net hedef belirle",
            "📝 Günlük to-do list hazırla ve tamamladıklarını işaretle"
        ])
        
        # Performans artırıcılar
        strong_subjects = self.student_profile['performance_history']['strong_subjects']
        if strong_subjects:
            recommendations['performance_boosters'].append(
                f"💪 Güçlü olduğun {', '.join(strong_subjects)} konularını diğer alanlara bağla"
            )
        
        recommendations['performance_boosters'].extend([
            "🏃‍♂️ Düzenli egzersiz yap (konsantrasyon artırır)",
            "💧 Bol su iç ve beslenme saatlerine dikkat et",
            "😴 Kaliteli uyku al (7-8 saat)",
            "🧘‍♂️ Stres yönetimi için nefes egzersizleri yap"
        ])
        
        return recommendations
    
    def _create_progress_template(self, daily_schedules: List) -> Dict:
        """İlerleme takibi şablonu oluştur"""
        template = {
            'tracking_start': datetime.now().isoformat(),
            'daily_progress': {},
            'weekly_summaries': {},
            'completion_rates': {
                'assignments': 0.0,
                'study_hours': 0.0,
                'reading_materials': 0.0
            },
            'notes': []
        }
        
        # Günlük takip şablonları
        for schedule in daily_schedules:
            date = schedule['date']
            template['daily_progress'][date] = {
                'planned_hours': schedule['total_study_time'] / 60,
                'actual_hours': 0.0,
                'completed_tasks': [],
                'mood_rating': 0,  # 1-10
                'energy_level': 0,  # 1-10
                'notes': "",
                'challenges': []
            }
        
        return template

    def create_mock_exam_schedule(self, course: str = "Computer Architecture") -> Dict:
        """Mock sınav programı oluştur"""
        print(f"📋 {course} için mock sınav programı oluşturuluyor...")
        
        # İçerik analizinden konuları al
        content_data = self.load_all_data().get('content_analysis', {})
        topics = content_data.get('summary', {}).get('common_topics', [])
        
        if not topics:
            topics = [
                'processor_architecture',
                'memory_system', 
                'instruction_set',
                'performance',
                'pipelining'
            ]
        
        mock_exams = []
        base_date = datetime.now()
        
        for i, topic in enumerate(topics[:5]):  # İlk 5 konu
            exam_date = base_date + timedelta(days=(i+1)*3)  # 3 gün arayla
            
            mock_exam = {
                'exam_id': f"mock_{i+1}",
                'course': course,
                'topic': topic,
                'date': exam_date.strftime('%Y-%m-%d'),
                'time': "19:00",
                'duration_minutes': 60,
                'question_count': 20,
                'difficulty': "medium",
                'question_types': {
                    'multiple_choice': 15,
                    'short_answer': 3,
                    'long_answer': 2
                }
            }
            
            mock_exams.append(mock_exam)
        
        # Mock exam programını kaydet
        with open('mock_exam_schedule.json', 'w', encoding='utf-8') as f:
            json.dump(mock_exams, f, indent=2, ensure_ascii=False)
        
        return {
            'course': course,
            'total_exams': len(mock_exams),
            'schedule': mock_exams,
            'recommendations': [
                "Her mock sınav sonrası yanlış cevapları analiz et",
                "Zayıf konuları tespit et ve ek çalışma planla",
                "Gerçek sınav koşullarında çöz (zaman sınırı)",
                "Sonuçları takip et ve gelişimi gözlemle"
            ]
        }

def interactive_setup():
    """Etkileşimli kurulum"""
    print("""
╔══════════════════════════════════════════════════╗
║        AKILLI ÇALIŞMA PLANI ÜRETİCİSİ            ║
║           Ca' Foscari - Emre Aras                ║
╚══════════════════════════════════════════════════╝
    """)
    
    # Claude API key kontrol
    claude_key = input("Claude API Key (isteğe bağlı): ").strip()
    
    planner = StudyPlanner(claude_key if claude_key else None)
    
    while True:
        print("\n🎯 MENÜ:")
        print("1. 📊 Kapsamlı çalışma planı oluştur")
        print("2. 📅 Manuel sınav tarihi ekle") 
        print("3. 📋 Mock sınav programı oluştur")
        print("4. 📈 Mevcut durumu analiz et")
        print("5. ❌ Çıkış")
        
        choice = input("\nSeçiminiz (1-5): ").strip()
        
        if choice == "1":
            days = int(input("Kaç günlük plan oluşturayım? (varsayılan 14): ").strip() or "14")
            plan = planner.generate_comprehensive_study_plan(days)
            
            print(f"\n✅ {days} günlük çalışma planı oluşturuldu!")
            print(f"📁 Dosya: comprehensive_study_plan.json")
            print(f"📊 Toplam çalışma saati: {sum(d['total_study_time'] for d in plan['daily_schedules']) // 60} saat")
            
        elif choice == "2":
            course = input("Ders adı: ").strip()
            exam_name = input("Sınav adı: ").strip()
            exam_date = input("Sınav tarihi (YYYY-MM-DD): ").strip()
            exam_time = input("Sınav saati (HH:MM, varsayılan 09:00): ").strip() or "09:00"
            notes = input("Notlar (isteğe bağlı): ").strip()
            
            planner.add_manual_exam(course, exam_name, exam_date, exam_time, notes)
            
        elif choice == "3":
            course = input("Ders adı (varsayılan Computer Architecture): ").strip() or "Computer Architecture"
            mock_schedule = planner.create_mock_exam_schedule(course)
            
            print(f"\n✅ {mock_schedule['total_exams']} mock sınav programı oluşturuldu!")
            print("📁 Dosya: mock_exam_schedule.json")
            
        elif choice == "4":
            data = planner.load_all_data()
            analysis = planner._analyze_current_situation(data)
            
            print("\n📊 MEVCUT DURUM:")
            print(f"📝 Ödevler: {analysis['assignments_count']} (Kritik: {analysis['critical_assignments']})")
            print(f"📚 Yaklaşan sınavlar: {analysis['upcoming_exams']}")
            print(f"📧 Önemli mailler: {analysis['high_priority_emails']}")
            print(f"📄 Çalışma materyali: {analysis['total_study_materials']} dosya")
            print(f"⏱️  Tahmini çalışma: {analysis['estimated_workload']} dakika")
            
        elif choice == "5":
            print("👋 Görüşmek üzere! Başarılar 🚀")
            break
        
        else:
            print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    interactive_setup()