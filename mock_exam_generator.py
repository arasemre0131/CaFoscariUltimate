#!/usr/bin/env python3
"""
Mock Sınav Oluşturucu - Claude AI ile Akıllı Soru Üretimi
Ders materyallerinden otomatik mock sınavlar oluşturur
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import anthropic

class MockExamGenerator:
    def __init__(self, claude_api_key: str = None):
        """
        Mock sınav oluşturucu başlatıcısı
        Args:
            claude_api_key: Claude API anahtarı
        """
        self.claude_api_key = claude_api_key or os.getenv('CLAUDE_API_KEY')
        
        if self.claude_api_key:
            self.claude = anthropic.Anthropic(api_key=self.claude_api_key)
        else:
            self.claude = None
            print("⚠️  Claude API key bulunamadı. Basit sorular kullanılacak.")
        
        # Computer Architecture için temel sorular
        self.default_questions = {
            'processor_architecture': [
                {
                    'type': 'multiple_choice',
                    'question': 'CPU\'nun temel bileşenleri nelerdir?',
                    'options': ['ALU, Control Unit, Registers', 'Cache, RAM, ROM', 'Input, Output, Storage', 'Bus, Clock, Power'],
                    'correct': 0,
                    'difficulty': 'easy'
                },
                {
                    'type': 'short_answer',
                    'question': 'RISC ve CISC mimarileri arasındaki temel farkları açıklayın.',
                    'answer': 'RISC: Basit komutlar, sabit uzunluk, az adres modu. CISC: Karmaşık komutlar, değişken uzunluk, çok adres modu.',
                    'difficulty': 'medium'
                }
            ],
            'memory_system': [
                {
                    'type': 'multiple_choice',
                    'question': 'Cache\'in amacı nedir?',
                    'options': ['Hızlı veri erişimi', 'Daha fazla storage', 'Güvenlik', 'Enerji tasarrufu'],
                    'correct': 0,
                    'difficulty': 'easy'
                },
                {
                    'type': 'long_answer',
                    'question': 'Virtual memory sisteminin çalışma prensibini detaylarıyla açıklayın.',
                    'answer': 'Virtual memory, fiziksel bellekten daha büyük adres alanı sağlar. Paging ve segmentation kullanır.',
                    'difficulty': 'hard'
                }
            ],
            'pipelining': [
                {
                    'type': 'multiple_choice',
                    'question': 'Pipeline hazard türleri nelerdir?',
                    'options': ['Structural, Data, Control', 'Read, Write, Execute', 'Fetch, Decode, Store', 'Cache, Memory, Disk'],
                    'correct': 0,
                    'difficulty': 'medium'
                }
            ]
        }
    
    def load_content_data(self) -> Dict:
        """İçerik analizi verilerini yükle"""
        data = {}
        
        # İçerik analizi
        if os.path.exists('content_analysis.json'):
            with open('content_analysis.json', 'r', encoding='utf-8') as f:
                data['content_analysis'] = json.load(f)
        
        # Moodle verileri
        if os.path.exists('moodle_data.json'):
            with open('moodle_data.json', 'r', encoding='utf-8') as f:
                data['moodle_data'] = json.load(f)
        
        return data
    
    def extract_topics_from_content(self, content_data: Dict) -> List[str]:
        """İçerik verilerinden konuları çıkar"""
        topics = []
        
        # İçerik analizinden konular
        if 'content_analysis' in content_data:
            summary = content_data['content_analysis'].get('summary', {})
            common_topics = summary.get('common_topics', [])
            topics.extend(common_topics)
        
        # Varsayılan konular
        default_topics = [
            'processor_architecture',
            'memory_system', 
            'instruction_set',
            'performance',
            'pipelining',
            'cache_design',
            'parallel_processing'
        ]
        
        # Benzersiz konuları döndür
        all_topics = list(set(topics + default_topics))
        return all_topics[:10]  # İlk 10 konu
    
    def generate_ai_questions(self, topic: str, question_count: int = 5, difficulty: str = 'medium') -> List[Dict]:
        """Claude AI ile soru oluştur"""
        if not self.claude:
            return []
        
        prompt = f"""
Computer Architecture dersi için {topic} konusunda {question_count} adet sınav sorusu oluştur.

Zorluk seviyesi: {difficulty}
Soru türleri karışık olsun: çoktan seçmeli, kısa cevap, uzun cevap

Her soru için şu formatı kullan:
- Soru türü (multiple_choice, short_answer, long_answer)
- Soru metni
- Seçenekler (çoktan seçmeli için)
- Doğru cevap/cevap anahtarı
- Zorluk seviyesi

JSON formatında döndür. Sorular Türkçe veya İngilizce olabilir.

Konular şunları içerebilir:
- CPU architecture ve design
- Memory hierarchy (cache, RAM, virtual memory)
- Instruction sets (RISC vs CISC)
- Pipelining ve hazards
- Performance metrics
- Parallel processing

Örnek format:
{{
  "questions": [
    {{
      "type": "multiple_choice",
      "question": "Soru metni...",
      "options": ["A", "B", "C", "D"],
      "correct": 0,
      "difficulty": "{difficulty}",
      "topic": "{topic}"
    }}
  ]
}}
        """
        
        try:
            response = self.claude.messages.create(
                model="claude-3-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # JSON'u parse et
            response_text = response.content[0].text
            
            # JSON'u bulup çıkar
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                questions_data = json.loads(json_match.group())
                return questions_data.get('questions', [])
            else:
                print(f"❌ AI yanıtından JSON parse edilemedi: {topic}")
                return []
                
        except Exception as e:
            print(f"❌ AI soru üretim hatası ({topic}): {e}")
            return []
    
    def get_default_questions(self, topic: str, count: int = 5) -> List[Dict]:
        """Varsayılan sorulardan seç"""
        if topic in self.default_questions:
            questions = self.default_questions[topic].copy()
            # Konu adını ekle
            for q in questions:
                q['topic'] = topic
            
            # İstenen sayıya kadar random seç
            if len(questions) >= count:
                return random.sample(questions, count)
            else:
                # Yetersizse tekrarla
                result = questions.copy()
                while len(result) < count:
                    result.extend(questions)
                return result[:count]
        else:
            # Genel sorular oluştur
            return self.generate_generic_questions(topic, count)
    
    def generate_generic_questions(self, topic: str, count: int) -> List[Dict]:
        """Genel sorular oluştur"""
        generic_templates = [
            {
                'type': 'multiple_choice',
                'question': f'{topic.replace("_", " ").title()} konusunda en önemli kavram nedir?',
                'options': ['Performans', 'Verimlilik', 'Güvenilirlik', 'Ölçeklenebilirlik'],
                'correct': 0,
                'difficulty': 'medium'
            },
            {
                'type': 'short_answer',
                'question': f'{topic.replace("_", " ").title()} sisteminin avantajları nelerdir?',
                'answer': 'Hız, verimlilik ve güvenilirlik sağlar.',
                'difficulty': 'easy'
            },
            {
                'type': 'long_answer',
                'question': f'{topic.replace("_", " ").title()} konusunu detaylarıyla açıklayın.',
                'answer': 'Bu konu computer architecture\'da önemli bir yere sahiptir.',
                'difficulty': 'hard'
            }
        ]
        
        questions = []
        for i in range(count):
            template = generic_templates[i % len(generic_templates)].copy()
            template['topic'] = topic
            questions.append(template)
        
        return questions
    
    def create_mock_exam(self, 
                        course: str = "Computer Architecture",
                        total_questions: int = 20,
                        difficulty: str = 'medium',
                        topics: List[str] = None,
                        duration_minutes: int = 90) -> Dict:
        """Tek mock sınav oluştur"""
        
        print(f"📝 {course} mock sınavı oluşturuluyor...")
        
        # İçerik verilerini yükle
        content_data = self.load_content_data()
        
        # Konuları belirle
        if not topics:
            topics = self.extract_topics_from_content(content_data)
        
        # Soru dağılımı
        questions_per_topic = max(1, total_questions // len(topics))
        remaining_questions = total_questions % len(topics)
        
        all_questions = []
        
        for i, topic in enumerate(topics):
            # Her konudan kaç soru
            topic_question_count = questions_per_topic
            if i < remaining_questions:
                topic_question_count += 1
            
            if topic_question_count <= 0:
                continue
            
            print(f"   📚 {topic}: {topic_question_count} soru")
            
            # AI ile soru üret
            ai_questions = self.generate_ai_questions(topic, topic_question_count, difficulty)
            
            if ai_questions:
                all_questions.extend(ai_questions)
            else:
                # AI çalışmazsa varsayılan sorular
                default_questions = self.get_default_questions(topic, topic_question_count)
                all_questions.extend(default_questions)
        
        # Soruları karıştır
        random.shuffle(all_questions)
        
        # Soru numaralarını ekle
        for i, question in enumerate(all_questions):
            question['question_number'] = i + 1
        
        # Sınav verilerini hazırla
        exam_data = {
            'exam_id': f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'course': course,
            'title': f"{course} Mock Exam",
            'creation_date': datetime.now().isoformat(),
            'difficulty': difficulty,
            'duration_minutes': duration_minutes,
            'total_questions': len(all_questions),
            'topics_covered': topics,
            'question_distribution': {
                'multiple_choice': len([q for q in all_questions if q.get('type') == 'multiple_choice']),
                'short_answer': len([q for q in all_questions if q.get('type') == 'short_answer']),
                'long_answer': len([q for q in all_questions if q.get('type') == 'long_answer'])
            },
            'questions': all_questions,
            'instructions': [
                f"Bu sınav {duration_minutes} dakikadır",
                "Tüm soruları cevaplayın",
                "Çoktan seçmeli sorularda sadece bir seçenek işaretleyin",
                "Kısa cevap soruları için 2-3 cümle yeterlidir",
                "Uzun cevap soruları için detaylı açıklama yapın"
            ],
            'grading_scheme': {
                'multiple_choice': 5,  # puan
                'short_answer': 10,
                'long_answer': 15
            }
        }
        
        return exam_data
    
    def create_exam_series(self, 
                          course: str = "Computer Architecture",
                          exam_count: int = 5,
                          days_interval: int = 3) -> Dict:
        """Mock sınav serisi oluştur"""
        
        print(f"📋 {course} için {exam_count} mock sınav serisi oluşturuluyor...")
        
        exam_series = {
            'series_id': f"series_{datetime.now().strftime('%Y%m%d')}",
            'course': course,
            'creation_date': datetime.now().isoformat(),
            'total_exams': exam_count,
            'exam_schedule': [],
            'progress_tracking': {}
        }
        
        # Her sınav için farklı zorluk ve odak
        difficulties = ['easy', 'medium', 'hard']
        base_date = datetime.now()
        
        for i in range(exam_count):
            exam_date = base_date + timedelta(days=i * days_interval)
            difficulty = difficulties[i % len(difficulties)]
            
            print(f"\n📝 Sınav {i+1}/{exam_count} ({difficulty})")
            
            # Her sınavda farklı konu ağırlığı
            content_data = self.load_content_data()
            all_topics = self.extract_topics_from_content(content_data)
            
            # İlk sınavlar temel konular, sonrakiler daha spesifik
            if i == 0:
                exam_topics = all_topics[:3]  # Temel konular
            elif i == exam_count - 1:
                exam_topics = all_topics  # Tüm konular
            else:
                exam_topics = all_topics[:5]  # Orta seviye
            
            # Mock sınavı oluştur
            mock_exam = self.create_mock_exam(
                course=course,
                total_questions=20 + (i * 2),  # Giderek artan soru sayısı
                difficulty=difficulty,
                topics=exam_topics,
                duration_minutes=60 + (i * 15)  # Giderek artan süre
            )
            
            # Programlama zamanını ekle
            mock_exam['scheduled_date'] = exam_date.strftime('%Y-%m-%d')
            mock_exam['scheduled_time'] = "19:00"  # Akşam sınavı
            mock_exam['exam_number'] = i + 1
            mock_exam['series_position'] = f"{i+1}/{exam_count}"
            
            exam_series['exam_schedule'].append(mock_exam)
            
            # İlerleme takibi şablonu
            exam_series['progress_tracking'][mock_exam['exam_id']] = {
                'status': 'scheduled',  # scheduled, completed, skipped
                'score': None,
                'time_taken': None,
                'completion_date': None,
                'notes': '',
                'weak_areas': [],
                'strong_areas': []
            }
        
        # Seriyi kaydet
        series_filename = f"mock_exam_series_{exam_series['series_id']}.json"
        with open(series_filename, 'w', encoding='utf-8') as f:
            json.dump(exam_series, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Mock sınav serisi oluşturuldu: {series_filename}")
        return exam_series
    
    def create_single_exam_file(self, exam_data: Dict) -> str:
        """Tek sınav için ayrı dosya oluştur"""
        filename = f"mock_exam_{exam_data['exam_id']}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(exam_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def generate_answer_key(self, exam_data: Dict) -> Dict:
        """Cevap anahtarı oluştur"""
        answer_key = {
            'exam_id': exam_data['exam_id'],
            'course': exam_data['course'],
            'title': exam_data['title'] + " - CEVAP ANAHTARI",
            'answers': []
        }
        
        for question in exam_data['questions']:
            answer_entry = {
                'question_number': question['question_number'],
                'question_type': question.get('type'),
                'topic': question.get('topic'),
                'question': question['question']
            }
            
            if question.get('type') == 'multiple_choice':
                correct_index = question.get('correct', 0)
                answer_entry['correct_answer'] = question['options'][correct_index]
                answer_entry['correct_option'] = chr(65 + correct_index)  # A, B, C, D
            else:
                answer_entry['sample_answer'] = question.get('answer', 'Detaylı açıklama beklenir.')
            
            answer_key['answers'].append(answer_entry)
        
        # Cevap anahtarını kaydet
        answer_filename = f"answer_key_{exam_data['exam_id']}.json"
        with open(answer_filename, 'w', encoding='utf-8') as f:
            json.dump(answer_key, f, indent=2, ensure_ascii=False)
        
        return answer_key
    
    def create_study_focused_exam(self, focus_topics: List[str], weak_areas: List[str] = None) -> Dict:
        """Belirli konulara odaklanmış sınav oluştur"""
        print("🎯 Odaklanmış mock sınav oluşturuluyor...")
        
        # Zayıf alanlara daha fazla ağırlık ver
        all_topics = focus_topics.copy()
        if weak_areas:
            all_topics.extend(weak_areas * 2)  # Zayıf alanları 2 kez ekle
        
        exam = self.create_mock_exam(
            course="Computer Architecture - Focused Study",
            total_questions=15,
            difficulty='medium',
            topics=all_topics,
            duration_minutes=60
        )
        
        exam['exam_type'] = 'focused'
        exam['focus_areas'] = focus_topics
        exam['weak_areas_targeted'] = weak_areas or []
        
        return exam

def interactive_mock_exam_generator():
    """Etkileşimli mock sınav oluşturucu"""
    print("""
╔══════════════════════════════════════════════════╗
║           MOCK SINAV ÜRETİCİSİ                   ║
║      Computer Architecture - Ca' Foscari        ║
╚══════════════════════════════════════════════════╝
    """)
    
    # Claude API key al
    claude_key = input("Claude API Key (isteğe bağlı, Enter=varsayılan sorular): ").strip()
    
    generator = MockExamGenerator(claude_key if claude_key else None)
    
    while True:
        print("\n🎯 MOCK SINAV MENÜSÜ:")
        print("1. 📝 Tek mock sınav oluştur")
        print("2. 📋 Mock sınav serisi oluştur (5 sınav)")
        print("3. 🎯 Odaklanmış sınav oluştur")
        print("4. 📊 Mevcut sınavları listele")
        print("5. ❌ Çıkış")
        
        choice = input("\nSeçiminiz (1-5): ").strip()
        
        if choice == "1":
            print("\n📝 TEK MOCK SINAV OLUŞTUR")
            course = input("Ders adı (varsayılan: Computer Architecture): ").strip() or "Computer Architecture"
            
            try:
                question_count = int(input("Soru sayısı (varsayılan: 20): ").strip() or "20")
                duration = int(input("Süre (dakika, varsayılan: 90): ").strip() or "90")
            except:
                question_count, duration = 20, 90
            
            difficulty = input("Zorluk (easy/medium/hard, varsayılan: medium): ").strip() or "medium"
            
            print("\n🔄 Sınav oluşturuluyor...")
            exam = generator.create_mock_exam(course, question_count, difficulty, duration_minutes=duration)
            
            # Dosyaya kaydet
            exam_file = generator.create_single_exam_file(exam)
            answer_key = generator.generate_answer_key(exam)
            
            print(f"\n✅ Mock sınav oluşturuldu!")
            print(f"📁 Sınav dosyası: {exam_file}")
            print(f"🔑 Cevap anahtarı: answer_key_{exam['exam_id']}.json")
            print(f"📊 Soru dağılımı: {exam['question_distribution']}")
            
        elif choice == "2":
            print("\n📋 MOCK SINAV SERİSİ OLUŞTUR")
            course = input("Ders adı (varsayılan: Computer Architecture): ").strip() or "Computer Architecture"
            
            try:
                exam_count = int(input("Sınav sayısı (varsayılan: 5): ").strip() or "5")
                interval = int(input("Sınavlar arası gün (varsayılan: 3): ").strip() or "3")
            except:
                exam_count, interval = 5, 3
            
            print(f"\n🔄 {exam_count} mock sınav serisi oluşturuluyor...")
            series = generator.create_exam_series(course, exam_count, interval)
            
            print(f"\n✅ Mock sınav serisi oluşturuldu!")
            print(f"📁 Seri dosyası: mock_exam_series_{series['series_id']}.json")
            print(f"📅 İlk sınav: {series['exam_schedule'][0]['scheduled_date']}")
            print(f"📅 Son sınav: {series['exam_schedule'][-1]['scheduled_date']}")
            
        elif choice == "3":
            print("\n🎯 ODAKLANMIŞ SINAV OLUŞTUR")
            print("Odaklanmak istediğiniz konuları girin (virgülle ayırın):")
            topics_input = input("Konular: ").strip()
            focus_topics = [t.strip() for t in topics_input.split(',') if t.strip()]
            
            if not focus_topics:
                focus_topics = ['processor_architecture', 'memory_system']
            
            weak_input = input("Zayıf olduğunuz alanlar (isteğe bağlı): ").strip()
            weak_areas = [w.strip() for w in weak_input.split(',') if w.strip()] if weak_input else None
            
            print("\n🔄 Odaklanmış sınav oluşturuluyor...")
            exam = generator.create_study_focused_exam(focus_topics, weak_areas)
            
            exam_file = generator.create_single_exam_file(exam)
            answer_key = generator.generate_answer_key(exam)
            
            print(f"\n✅ Odaklanmış mock sınav oluşturuldu!")
            print(f"📁 Sınav dosyası: {exam_file}")
            print(f"🎯 Odak konular: {', '.join(focus_topics)}")
            
        elif choice == "4":
            print("\n📊 MEVCUT SINAVLAR")
            
            # JSON dosyalarını tara
            json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'mock_exam' in f]
            
            if json_files:
                for file in json_files:
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        if 'exam_id' in data:
                            print(f"📝 {data.get('title', 'Unknown')} ({file})")
                            print(f"   📅 {data.get('creation_date', '')}")
                            print(f"   📊 {data.get('total_questions', 0)} soru, {data.get('duration_minutes', 0)} dk")
                            print()
                    except:
                        continue
            else:
                print("Henüz mock sınav oluşturulmamış.")
            
        elif choice == "5":
            print("👋 Mock sınavlarda başarılar! 🚀")
            break
        
        else:
            print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    interactive_mock_exam_generator()