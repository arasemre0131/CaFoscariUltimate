#!/usr/bin/env python3
"""
Advanced Mock Exam System
Comprehensive exam creation, analysis and adaptive learning
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
from pathlib import Path

class MockExamSystem:
    def __init__(self):
        """Initialize mock exam system with persistent storage"""
        self.courses_db_path = "courses_database.json"
        self.exam_history_path = "exam_history.json"
        self.courses = self.load_courses_database()
        self.exam_history = self.load_exam_history()
        
    def load_courses_database(self) -> Dict:
        """Load persistent courses database"""
        if os.path.exists(self.courses_db_path):
            with open(self.courses_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Moodle latest verilerini kontrol et
        try:
            from storage_manager import StorageManager
            sm = StorageManager()
            latest_moodle = os.path.join(sm.get_path('moodle_data'), 'latest.json')
            if os.path.exists(latest_moodle):
                with open(latest_moodle, 'r', encoding='utf-8') as f:
                    moodle_data = json.load(f)
                    print("🔄 Moodle latest verilerinden kurslar yükleniyor...")
                    self.sync_with_moodle(moodle_data)
                    return self.courses
        except Exception as e:
            print(f"⚠️  Latest Moodle verileri yüklenirken hata: {e}")
        
        return {}
    
    def save_courses_database(self):
        """Save courses database persistently"""
        with open(self.courses_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.courses, f, indent=2, ensure_ascii=False, default=str)
    
    def load_exam_history(self) -> List[Dict]:
        """Load exam history for adaptive learning"""
        if os.path.exists(self.exam_history_path):
            with open(self.exam_history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_exam_history(self):
        """Save exam history"""
        with open(self.exam_history_path, 'w', encoding='utf-8') as f:
            json.dump(self.exam_history, f, indent=2, ensure_ascii=False, default=str)
    
    def sync_with_moodle(self, moodle_data: Dict):
        """Sync and update courses database from Moodle"""
        print("🔄 Moodle verileri senkronize ediliyor...")
        
        # İlk olarak kursları oluştur
        for course in moodle_data.get('courses', []):
            course_id = str(course['id'])
            course_name = course['name']
            
            # Update course data
            self.courses[course_id] = {
                'id': course_id,
                'name': course_name,
                'shortname': course.get('shortname', ''),
                'summary': course.get('summary', ''),
                'last_updated': datetime.now().isoformat(),
                'pdfs': [],
                'videos': [],
                'documents': [],
                'total_content': 0
            }
        
        # Eğer kurs bilgileri yoksa PDF'lerden kurs oluştur
        if not moodle_data.get('courses', []) and moodle_data.get('pdfs', []):
            print("📄 Kurs bilgisi yok, PDF'lerden kurslar oluşturuluyor...")
            course_ids = set()
            for pdf in moodle_data.get('pdfs', []):
                course_id = str(pdf.get('course_id', 'unknown'))
                if course_id != 'unknown':
                    course_ids.add(course_id)
            
            for course_id in course_ids:
                self.courses[course_id] = {
                    'id': course_id,
                    'name': f'Ders {course_id}',
                    'shortname': f'COURSE_{course_id}',
                    'summary': 'PDF içeriğinden oluşturulan kurs',
                    'last_updated': datetime.now().isoformat(),
                    'pdfs': [],
                    'videos': [],
                    'documents': [],
                    'total_content': 0
                }
        
        # Add PDFs
        for pdf in moodle_data.get('pdfs', []):
            course_id = str(pdf['course_id'])
            if course_id in self.courses:
                self.courses[course_id]['pdfs'].append({
                    'name': pdf['name'],
                    'url': pdf['url'],
                    'size': pdf.get('size', 0),
                    'section': pdf.get('section', ''),
                    'module': pdf.get('module', '')
                })
        
        # Add videos
        for video in moodle_data.get('videos', []):
            course_id = str(video['course_id'])
            if course_id in self.courses:
                self.courses[course_id]['videos'].append({
                    'name': video['name'],
                    'url': video['url'],
                    'type': video.get('type', ''),
                    'section': video.get('section', ''),
                    'module': video.get('module', '')
                })
        
        # Add documents
        for doc in moodle_data.get('documents', []):
            course_id = str(doc['course_id'])
            if course_id in self.courses:
                self.courses[course_id]['documents'].append({
                    'name': doc['name'],
                    'url': doc['url'],
                    'type': doc.get('type', ''),
                    'section': doc.get('section', ''),
                    'module': doc.get('module', '')
                })
        
        # Calculate totals
        for course_id in self.courses:
            course = self.courses[course_id]
            course['total_content'] = (
                len(course['pdfs']) + 
                len(course['videos']) + 
                len(course['documents'])
            )
        
        self.save_courses_database()
        print(f"✅ {len(self.courses)} ders senkronize edildi")
        
    def display_course_selection(self) -> List[Tuple[str, str, int]]:
        """Display available courses for mock exam selection"""
        print("\n📚 MOCK SINAV İÇİN DERS SEÇİMİ:")
        print("=" * 50)
        
        available_courses = []
        index = 1
        
        for course_id, course in self.courses.items():
            if course['total_content'] > 0:  # Only courses with content
                available_courses.append((str(index), course_id, course))
                print(f"[{index}] {course['name']}")
                print(f"    📄 {len(course['pdfs'])} PDF")
                print(f"    🎥 {len(course['videos'])} video")
                print(f"    📋 {len(course['documents'])} doküman")
                print(f"    📊 Toplam içerik: {course['total_content']}")
                print()
                index += 1
        
        return available_courses
    
    def select_course_for_exam(self) -> Optional[str]:
        """Interactive course selection for mock exam"""
        available_courses = self.display_course_selection()
        
        if not available_courses:
            print("❌ İçerik bulunan ders yok. Önce Moodle senkronizasyonu yapın.")
            return None
        
        try:
            choice = input("Hangi ders için mock sınav oluşturmak istiyorsunuz? (1-{}): ".format(len(available_courses)))
            choice_index = int(choice) - 1
            
            if 0 <= choice_index < len(available_courses):
                selected_course_id = available_courses[choice_index][1]
                course_name = self.courses[selected_course_id]['name']
                print(f"\n✅ Seçilen ders: {course_name}")
                return selected_course_id
            else:
                print("❌ Geçersiz seçim!")
                return None
                
        except ValueError:
            print("❌ Lütfen geçerli bir sayı girin!")
            return None
    
    def analyze_course_content(self, course_id: str) -> Dict:
        """Analyze course content for exam generation"""
        course = self.courses.get(course_id)
        if not course:
            return {}
        
        print(f"🤖 {course['name']} dersi içerikleri analiz ediliyor...")
        
        analysis = {
            'course_name': course['name'],
            'topics': [],
            'difficulty_levels': ['Basic', 'Intermediate', 'Advanced'],
            'question_types': ['Multiple Choice', 'True/False', 'Short Answer', 'Problem Solving'],
            'content_summary': {}
        }
        
        # Analyze PDFs
        pdf_topics = []
        for pdf in course['pdfs']:
            # Extract potential topics from filename and section
            topic_hints = self.extract_topics_from_text(pdf['name'] + ' ' + pdf.get('section', ''))
            pdf_topics.extend(topic_hints)
        
        # Analyze videos  
        video_topics = []
        for video in course['videos']:
            topic_hints = self.extract_topics_from_text(video['name'] + ' ' + video.get('section', ''))
            video_topics.extend(topic_hints)
        
        # Combine and deduplicate topics
        all_topics = list(set(pdf_topics + video_topics))
        analysis['topics'] = all_topics[:10]  # Top 10 topics
        
        analysis['content_summary'] = {
            'pdf_count': len(course['pdfs']),
            'video_count': len(course['videos']),
            'document_count': len(course['documents']),
            'estimated_topics': len(analysis['topics'])
        }
        
        return analysis
    
    def extract_topics_from_text(self, text: str) -> List[str]:
        """Extract potential topics from text using simple NLP"""
        # Common academic terms and patterns
        topics = []
        text_lower = text.lower()
        
        # Programming terms
        programming_terms = [
            'algorithm', 'data structure', 'programming', 'coding', 'function',
            'class', 'object', 'inheritance', 'polymorphism', 'recursion',
            'sorting', 'searching', 'graph', 'tree', 'array', 'linked list'
        ]
        
        # Math/Engineering terms  
        math_terms = [
            'linear', 'algebra', 'calculus', 'statistics', 'probability',
            'matrix', 'vector', 'derivative', 'integral', 'equation',
            'optimization', 'regression', 'neural network', 'machine learning'
        ]
        
        # Architecture terms
        arch_terms = [
            'processor', 'cpu', 'memory', 'cache', 'pipeline', 'instruction',
            'assembly', 'architecture', 'performance', 'benchmark', 'hardware'
        ]
        
        all_terms = programming_terms + math_terms + arch_terms
        
        for term in all_terms:
            if term in text_lower:
                topics.append(term.title())
        
        # Extract capitalized words (potential proper nouns/topics)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', text)
        topics.extend(capitalized)
        
        return list(set(topics))
    
    def generate_mock_exam_content(self, course_id: str, difficulty: str = "Mixed") -> Dict:
        """Generate mock exam content based on course analysis"""
        analysis = self.analyze_course_content(course_id)
        
        if not analysis:
            return {}
        
        # Get previous performance for this course
        course_history = [exam for exam in self.exam_history if exam.get('course_id') == course_id]
        weak_topics = self.identify_weak_topics(course_history)
        
        print(f"📝 Mock sınav oluşturuluyor...")
        
        exam_content = {
            'exam_id': f"EXAM_{course_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'course_id': course_id,
            'course_name': analysis['course_name'],
            'created_at': datetime.now().isoformat(),
            'difficulty': difficulty,
            'questions': [],
            'total_questions': 25,
            'time_limit': 90,  # minutes
            'topics_covered': analysis['topics'],
            'adaptive_focus': weak_topics
        }
        
        # Generate questions (placeholder - would use actual content analysis)
        question_templates = self.generate_question_templates(analysis, weak_topics)
        
        for i, template in enumerate(question_templates[:25], 1):
            question = {
                'question_number': i,
                'question_text': template['text'],
                'question_type': template['type'],
                'topic': template['topic'],
                'difficulty': template['difficulty'],
                'points': template['points'],
                'options': template.get('options', []),
                'correct_answer': template.get('correct_answer', ''),
                'explanation': template.get('explanation', '')
            }
            exam_content['questions'].append(question)
        
        return exam_content
    
    def generate_question_templates(self, analysis: Dict, weak_topics: List[str]) -> List[Dict]:
        """Generate question templates based on course content"""
        templates = []
        topics = analysis['topics']
        
        # Focus more on weak topics if any
        focus_topics = weak_topics if weak_topics else topics
        
        for i, topic in enumerate(focus_topics[:25]):
            # Vary question types and difficulty
            question_types = ['multiple_choice', 'true_false', 'short_answer']
            difficulties = ['Basic', 'Intermediate', 'Advanced']
            
            template = {
                'text': f"Question about {topic} - [This would be generated from actual course content]",
                'type': question_types[i % len(question_types)],
                'topic': topic,
                'difficulty': difficulties[i % len(difficulties)],
                'points': 4 if difficulties[i % len(difficulties)] == 'Advanced' else 3 if difficulties[i % len(difficulties)] == 'Intermediate' else 2
            }
            
            if template['type'] == 'multiple_choice':
                template['options'] = ['Option A', 'Option B', 'Option C', 'Option D']
                template['correct_answer'] = 'A'
            
            template['explanation'] = f"Explanation for {topic} concept"
            templates.append(template)
        
        return templates
    
    def create_mock_exam_pdf(self, exam_content: Dict) -> str:
        """Create PDF file for mock exam"""
        pdf_filename = f"Mock_Exam_{exam_content['course_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        pdf_path = os.path.join("mock_exams", pdf_filename)
        
        # Create directory if it doesn't exist
        os.makedirs("mock_exams", exist_ok=True)
        
        # Create text version for now (would use actual PDF library)
        text_content = f"""
CA' FOSCARI ULTIMATE - MOCK EXAM
{'='*50}

Course: {exam_content['course_name']}
Exam ID: {exam_content['exam_id']}
Date: {exam_content['created_at'][:10]}
Time Limit: {exam_content['time_limit']} minutes
Total Questions: {exam_content['total_questions']}

INSTRUCTIONS:
1. Answer all questions
2. Mark your answers clearly
3. Show your work for calculation problems
4. Upload the completed PDF back to the system

{'='*50}
QUESTIONS:
{'='*50}

"""
        
        for i, question in enumerate(exam_content['questions'], 1):
            text_content += f"""
Question {i} ({question['points']} points) - Topic: {question['topic']}
Difficulty: {question['difficulty']}

{question['question_text']}

"""
            if question['question_type'] == 'multiple_choice' and question.get('options'):
                for j, option in enumerate(question['options']):
                    text_content += f"   {chr(65+j)}) {option}\n"
                text_content += f"\nAnswer: ____\n"
            elif question['question_type'] == 'true_false':
                text_content += "True / False (Circle one)\n"
            else:
                text_content += "Answer:\n\n\n"
            
            text_content += "-" * 50 + "\n"
        
        # Save as text file for now (would convert to PDF)
        txt_path = pdf_path.replace('.pdf', '.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        print(f"✅ Mock sınav oluşturuldu: {txt_path}")
        print(f"📤 Sınavı çözüp geri yükleyin!")
        
        return txt_path
    
    def identify_weak_topics(self, course_history: List[Dict]) -> List[str]:
        """Identify weak topics from previous exam history"""
        if not course_history:
            return []
        
        topic_scores = {}
        for exam in course_history:
            for result in exam.get('topic_results', []):
                topic = result['topic']
                score = result['score_percentage']
                
                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(score)
        
        # Find topics with average score < 70%
        weak_topics = []
        for topic, scores in topic_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 70:
                weak_topics.append(topic)
        
        return weak_topics
    
    def create_mock_exam_interactive(self):
        """Interactive mock exam creation"""
        print("\n🎯 MOCK SINAV OLUŞTURUCU")
        print("=" * 40)
        
        # Check if courses are loaded
        if not self.courses:
            print("❌ Önce Moodle senkronizasyonu yapın (Ana Menü → 1)")
            return
        
        # Course selection
        course_id = self.select_course_for_exam()
        if not course_id:
            return
        
        # Difficulty selection
        print("\n📊 Zorluk seviyesi seçin:")
        print("1. Temel (Basic)")
        print("2. Orta (Intermediate)")  
        print("3. İleri (Advanced)")
        print("4. Karışık (Mixed - Önerilen)")
        
        try:
            diff_choice = input("Zorluk seviyesi (1-4): ").strip()
            difficulties = {'1': 'Basic', '2': 'Intermediate', '3': 'Advanced', '4': 'Mixed'}
            difficulty = difficulties.get(diff_choice, 'Mixed')
        except:
            difficulty = 'Mixed'
        
        # Generate exam
        exam_content = self.generate_mock_exam_content(course_id, difficulty)
        
        if not exam_content:
            print("❌ Sınav oluşturulamadı!")
            return
        
        # Create PDF
        pdf_path = self.create_mock_exam_pdf(exam_content)
        
        # Save exam for tracking
        exam_record = {
            'exam_id': exam_content['exam_id'],
            'course_id': course_id,
            'course_name': exam_content['course_name'],
            'created_at': exam_content['created_at'],
            'difficulty': difficulty,
            'file_path': pdf_path,
            'status': 'created',
            'completed_at': None,
            'score': None
        }
        
        # Add to history
        if not hasattr(self, 'pending_exams'):
            self.pending_exams = []
        self.pending_exams.append(exam_record)
        
        print(f"\n✅ Mock sınav başarıyla oluşturuldu!")
        print(f"📁 Dosya: {pdf_path}")
        print(f"🎯 Zorluk: {difficulty}")
        print(f"⏱️  Süre: {exam_content['time_limit']} dakika")
        print(f"❓ Soru sayısı: {exam_content['total_questions']}")
        print(f"\n📤 Sınavı çözüp 'Mock Exam Analysis' menüsünden yükleyin!")

def setup_mock_exam_system():
    """Setup and return mock exam system instance"""
    return MockExamSystem()

if __name__ == "__main__":
    # Test the system
    mock_system = setup_mock_exam_system()
    mock_system.create_mock_exam_interactive()