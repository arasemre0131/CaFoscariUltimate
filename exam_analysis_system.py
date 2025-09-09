#!/usr/bin/env python3
"""
Mock Exam Analysis System
Advanced answer analysis, scoring and feedback generation
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
from pathlib import Path

class ExamAnalysisSystem:
    def __init__(self, mock_exam_system):
        """Initialize with reference to mock exam system"""
        self.mock_system = mock_exam_system
        self.analysis_history_path = "analysis_history.json"
        self.analysis_history = self.load_analysis_history()
        
    def load_analysis_history(self) -> List[Dict]:
        """Load previous analysis results"""
        if os.path.exists(self.analysis_history_path):
            with open(self.analysis_history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_analysis_history(self):
        """Save analysis history"""
        with open(self.analysis_history_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_history, f, indent=2, ensure_ascii=False, default=str)
    
    def upload_completed_exam(self, exam_file_path: str) -> Optional[Dict]:
        """Process uploaded completed exam file"""
        print(f"📤 Tamamlanmış sınav dosyası analiz ediliyor: {exam_file_path}")
        
        if not os.path.exists(exam_file_path):
            print("❌ Dosya bulunamadı!")
            return None
        
        # Extract exam ID from filename or content
        exam_info = self.extract_exam_info(exam_file_path)
        if not exam_info:
            print("❌ Sınav bilgileri çıkarılamadı!")
            return None
        
        print(f"✅ Sınav tespit edildi: {exam_info['course_name']}")
        return exam_info
    
    def extract_exam_info(self, file_path: str) -> Optional[Dict]:
        """Extract exam information from uploaded file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract exam ID
            exam_id_match = re.search(r'Exam ID: (EXAM_\w+_\d+_\d+)', content)
            if not exam_id_match:
                return None
            
            exam_id = exam_id_match.group(1)
            
            # Extract course name
            course_match = re.search(r'Course: (.+)', content)
            course_name = course_match.group(1) if course_match else "Unknown"
            
            return {
                'exam_id': exam_id,
                'course_name': course_name,
                'file_path': file_path,
                'content': content
            }
            
        except Exception as e:
            print(f"❌ Dosya okuma hatası: {e}")
            return None
    
    def extract_student_answers(self, content: str) -> Dict[int, str]:
        """Extract student answers from exam content"""
        answers = {}
        
        # Look for different answer patterns
        patterns = [
            r'Question (\d+).*?Answer:\s*([^\n-]+)',  # Short answers
            r'Question (\d+).*?Answer:\s*([A-D])',    # Multiple choice
            r'Question (\d+).*?(?:True|False)'        # True/False
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                question_num = int(match.group(1))
                answer = match.group(2).strip() if len(match.groups()) > 1 else "No answer"
                answers[question_num] = answer
        
        return answers
    
    def analyze_answers(self, exam_id: str, student_answers: Dict[int, str]) -> Dict:
        """Comprehensive answer analysis"""
        print("🤖 Cevaplar detaylı olarak analiz ediliyor...")
        
        # This would load the original exam questions
        original_exam = self.load_original_exam(exam_id)
        if not original_exam:
            return {'error': 'Original exam not found'}
        
        analysis = {
            'exam_id': exam_id,
            'course_name': original_exam.get('course_name', ''),
            'analyzed_at': datetime.now().isoformat(),
            'total_questions': len(original_exam.get('questions', [])),
            'answered_questions': len(student_answers),
            'overall_score': 0,
            'max_score': 0,
            'percentage': 0,
            'topic_analysis': {},
            'difficulty_analysis': {},
            'question_type_analysis': {},
            'detailed_feedback': [],
            'recommendations': [],
            'strong_areas': [],
            'weak_areas': [],
            'error_patterns': []
        }
        
        total_score = 0
        max_possible_score = 0
        topic_scores = {}
        difficulty_scores = {}
        type_scores = {}
        
        # Analyze each question
        for question in original_exam.get('questions', []):
            q_num = question['question_number']
            topic = question['topic']
            difficulty = question['difficulty']
            q_type = question['question_type']
            points = question['points']
            
            max_possible_score += points
            
            # Initialize tracking dictionaries
            if topic not in topic_scores:
                topic_scores[topic] = {'correct': 0, 'total': 0, 'points': 0, 'max_points': 0}
            if difficulty not in difficulty_scores:
                difficulty_scores[difficulty] = {'correct': 0, 'total': 0, 'points': 0, 'max_points': 0}
            if q_type not in type_scores:
                type_scores[q_type] = {'correct': 0, 'total': 0, 'points': 0, 'max_points': 0}
            
            # Update totals
            topic_scores[topic]['total'] += 1
            topic_scores[topic]['max_points'] += points
            difficulty_scores[difficulty]['total'] += 1
            difficulty_scores[difficulty]['max_points'] += points
            type_scores[q_type]['total'] += 1
            type_scores[q_type]['max_points'] += points
            
            # Check if student answered
            if q_num in student_answers:
                student_answer = student_answers[q_num]
                is_correct, earned_points, feedback = self.grade_answer(
                    question, student_answer
                )
                
                if is_correct:
                    topic_scores[topic]['correct'] += 1
                    difficulty_scores[difficulty]['correct'] += 1
                    type_scores[q_type]['correct'] += 1
                
                topic_scores[topic]['points'] += earned_points
                difficulty_scores[difficulty]['points'] += earned_points
                type_scores[q_type]['points'] += earned_points
                total_score += earned_points
                
                # Detailed feedback for this question
                analysis['detailed_feedback'].append({
                    'question_number': q_num,
                    'topic': topic,
                    'difficulty': difficulty,
                    'student_answer': student_answer,
                    'correct_answer': question.get('correct_answer', ''),
                    'is_correct': is_correct,
                    'points_earned': earned_points,
                    'points_possible': points,
                    'feedback': feedback,
                    'explanation': question.get('explanation', '')
                })
                
            else:
                # Question not answered
                analysis['detailed_feedback'].append({
                    'question_number': q_num,
                    'topic': topic,
                    'difficulty': difficulty,
                    'student_answer': 'No answer provided',
                    'correct_answer': question.get('correct_answer', ''),
                    'is_correct': False,
                    'points_earned': 0,
                    'points_possible': points,
                    'feedback': 'Question not answered',
                    'explanation': question.get('explanation', '')
                })
        
        # Calculate overall scores
        analysis['overall_score'] = total_score
        analysis['max_score'] = max_possible_score
        analysis['percentage'] = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        # Process topic analysis
        for topic, scores in topic_scores.items():
            percentage = (scores['points'] / scores['max_points'] * 100) if scores['max_points'] > 0 else 0
            analysis['topic_analysis'][topic] = {
                'correct_answers': scores['correct'],
                'total_questions': scores['total'],
                'points_earned': scores['points'],
                'points_possible': scores['max_points'],
                'percentage': percentage,
                'status': self.get_performance_status(percentage)
            }
        
        # Process difficulty analysis
        for difficulty, scores in difficulty_scores.items():
            percentage = (scores['points'] / scores['max_points'] * 100) if scores['max_points'] > 0 else 0
            analysis['difficulty_analysis'][difficulty] = {
                'correct_answers': scores['correct'],
                'total_questions': scores['total'],
                'points_earned': scores['points'],
                'points_possible': scores['max_points'],
                'percentage': percentage,
                'status': self.get_performance_status(percentage)
            }
        
        # Process question type analysis
        for q_type, scores in type_scores.items():
            percentage = (scores['points'] / scores['max_points'] * 100) if scores['max_points'] > 0 else 0
            analysis['question_type_analysis'][q_type] = {
                'correct_answers': scores['correct'],
                'total_questions': scores['total'],
                'points_earned': scores['points'],
                'points_possible': scores['max_points'],
                'percentage': percentage,
                'status': self.get_performance_status(percentage)
            }
        
        # Generate insights
        analysis['strong_areas'] = self.identify_strong_areas(analysis)
        analysis['weak_areas'] = self.identify_weak_areas(analysis)
        analysis['recommendations'] = self.generate_recommendations(analysis)
        analysis['error_patterns'] = self.identify_error_patterns(analysis)
        
        return analysis
    
    def get_performance_status(self, percentage: float) -> str:
        """Get performance status based on percentage"""
        if percentage >= 90:
            return "Excellent"
        elif percentage >= 80:
            return "Good"
        elif percentage >= 70:
            return "Satisfactory"
        elif percentage >= 60:
            return "Needs Improvement"
        else:
            return "Poor"
    
    def grade_answer(self, question: Dict, student_answer: str) -> Tuple[bool, float, str]:
        """Grade individual answer"""
        correct_answer = question.get('correct_answer', '').strip().upper()
        student_answer_clean = student_answer.strip().upper()
        points = question['points']
        q_type = question['question_type']
        
        if q_type == 'multiple_choice':
            is_correct = student_answer_clean == correct_answer
            earned_points = points if is_correct else 0
            feedback = "Correct!" if is_correct else f"Incorrect. Correct answer: {correct_answer}"
            
        elif q_type == 'true_false':
            is_correct = student_answer_clean in correct_answer or correct_answer in student_answer_clean
            earned_points = points if is_correct else 0
            feedback = "Correct!" if is_correct else f"Incorrect. Correct answer: {correct_answer}"
            
        else:  # short_answer or other
            # Simple keyword matching for now (would use more sophisticated NLP)
            similarity = self.calculate_answer_similarity(correct_answer, student_answer_clean)
            
            if similarity >= 0.8:
                is_correct = True
                earned_points = points
                feedback = "Excellent answer!"
            elif similarity >= 0.6:
                is_correct = True
                earned_points = points * 0.8
                feedback = "Good answer, minor issues."
            elif similarity >= 0.4:
                is_correct = False
                earned_points = points * 0.5
                feedback = "Partially correct, needs improvement."
            else:
                is_correct = False
                earned_points = 0
                feedback = "Incorrect or incomplete answer."
        
        return is_correct, earned_points, feedback
    
    def calculate_answer_similarity(self, correct: str, student: str) -> float:
        """Calculate similarity between correct and student answers"""
        # Simple word overlap calculation
        correct_words = set(correct.lower().split())
        student_words = set(student.lower().split())
        
        if not correct_words:
            return 0.0
        
        overlap = len(correct_words.intersection(student_words))
        return overlap / len(correct_words)
    
    def load_original_exam(self, exam_id: str) -> Optional[Dict]:
        """Load original exam questions for comparison"""
        # This would load from saved exam data
        # For now, return a placeholder
        return {
            'exam_id': exam_id,
            'course_name': 'Mock Course',
            'questions': [
                {
                    'question_number': 1,
                    'topic': 'Sample Topic',
                    'difficulty': 'Basic',
                    'question_type': 'multiple_choice',
                    'points': 3,
                    'correct_answer': 'A',
                    'explanation': 'Sample explanation'
                }
            ]
        }
    
    def identify_strong_areas(self, analysis: Dict) -> List[str]:
        """Identify student's strong areas"""
        strong_areas = []
        
        for topic, scores in analysis['topic_analysis'].items():
            if scores['percentage'] >= 80:
                strong_areas.append(f"{topic} ({scores['percentage']:.1f}%)")
        
        return strong_areas
    
    def identify_weak_areas(self, analysis: Dict) -> List[str]:
        """Identify student's weak areas"""
        weak_areas = []
        
        for topic, scores in analysis['topic_analysis'].items():
            if scores['percentage'] < 70:
                weak_areas.append(f"{topic} ({scores['percentage']:.1f}%)")
        
        return weak_areas
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate personalized study recommendations"""
        recommendations = []
        
        # Based on weak areas
        for topic, scores in analysis['topic_analysis'].items():
            if scores['percentage'] < 60:
                recommendations.append(f"🔴 Critical: Review {topic} fundamentals - Score: {scores['percentage']:.1f}%")
            elif scores['percentage'] < 80:
                recommendations.append(f"🟡 Focus on {topic} practice problems - Score: {scores['percentage']:.1f}%")
        
        # Based on difficulty performance
        for difficulty, scores in analysis['difficulty_analysis'].items():
            if scores['percentage'] < 70:
                recommendations.append(f"📚 Work on {difficulty} level problems more")
        
        # Based on question types
        for q_type, scores in analysis['question_type_analysis'].items():
            if scores['percentage'] < 70:
                recommendations.append(f"📝 Practice {q_type.replace('_', ' ')} questions")
        
        return recommendations[:10]  # Top 10 recommendations
    
    def identify_error_patterns(self, analysis: Dict) -> List[str]:
        """Identify common error patterns"""
        patterns = []
        
        # Analyze difficulty progression
        basic_score = analysis['difficulty_analysis'].get('Basic', {}).get('percentage', 0)
        intermediate_score = analysis['difficulty_analysis'].get('Intermediate', {}).get('percentage', 0)
        advanced_score = analysis['difficulty_analysis'].get('Advanced', {}).get('percentage', 0)
        
        if basic_score > intermediate_score + 20:
            patterns.append("Struggles with intermediate concepts despite strong basics")
        
        if intermediate_score > advanced_score + 20:
            patterns.append("Difficulty with advanced applications")
        
        # Question type patterns
        mc_score = analysis['question_type_analysis'].get('multiple_choice', {}).get('percentage', 0)
        sa_score = analysis['question_type_analysis'].get('short_answer', {}).get('percentage', 0)
        
        if mc_score > sa_score + 25:
            patterns.append("Better at recognition than recall/explanation")
        
        return patterns
    
    def generate_detailed_report(self, analysis: Dict) -> str:
        """Generate comprehensive analysis report"""
        report = f"""
{'='*60}
📊 MOCK EXAM DETAILED ANALYSIS REPORT
{'='*60}

Course: {analysis['course_name']}
Exam ID: {analysis['exam_id']}
Analysis Date: {analysis['analyzed_at'][:19]}

{'='*60}
📈 OVERALL PERFORMANCE
{'='*60}

Score: {analysis['overall_score']:.1f} / {analysis['max_score']:.1f}
Percentage: {analysis['percentage']:.1f}%
Grade: {self.get_letter_grade(analysis['percentage'])}
Questions Answered: {analysis['answered_questions']} / {analysis['total_questions']}

{'='*60}
🎯 TOPIC ANALYSIS
{'='*60}

"""
        
        for topic, scores in analysis['topic_analysis'].items():
            status_emoji = "✅" if scores['percentage'] >= 80 else "⚠️" if scores['percentage'] >= 60 else "❌"
            report += f"{status_emoji} {topic}:\n"
            report += f"   Score: {scores['points_earned']:.1f}/{scores['points_possible']:.1f} ({scores['percentage']:.1f}%)\n"
            report += f"   Correct: {scores['correct_answers']}/{scores['total_questions']} questions\n"
            report += f"   Status: {scores['status']}\n\n"
        
        report += f"""
{'='*60}
📊 DIFFICULTY BREAKDOWN
{'='*60}

"""
        
        for difficulty, scores in analysis['difficulty_analysis'].items():
            report += f"{difficulty}: {scores['percentage']:.1f}% ({scores['correct_answers']}/{scores['total_questions']})\n"
        
        report += f"""

{'='*60}
💪 STRENGTHS
{'='*60}

"""
        
        if analysis['strong_areas']:
            for area in analysis['strong_areas']:
                report += f"✅ {area}\n"
        else:
            report += "No areas scoring above 80% - Focus on fundamental review\n"
        
        report += f"""

{'='*60}
⚠️ AREAS NEEDING IMPROVEMENT
{'='*60}

"""
        
        if analysis['weak_areas']:
            for area in analysis['weak_areas']:
                report += f"❌ {area}\n"
        else:
            report += "All topics performing adequately!\n"
        
        report += f"""

{'='*60}
📚 PERSONALIZED RECOMMENDATIONS
{'='*60}

"""
        
        for i, rec in enumerate(analysis['recommendations'], 1):
            report += f"{i}. {rec}\n"
        
        if analysis['error_patterns']:
            report += f"""

{'='*60}
🔍 ERROR PATTERN ANALYSIS
{'='*60}

"""
            for pattern in analysis['error_patterns']:
                report += f"• {pattern}\n"
        
        report += f"""

{'='*60}
📈 NEXT STEPS
{'='*60}

1. Review the detailed feedback for each question
2. Focus study time on topics scoring below 70%
3. Practice the question types you struggled with
4. Retake a similar mock exam in 1-2 weeks

{'='*60}
"""
        
        return report
    
    def get_letter_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
    
    def analyze_uploaded_exam_interactive(self):
        """Interactive exam analysis interface"""
        print("\n📊 MOCK SINAV ANALİZ SİSTEMİ")
        print("=" * 40)
        
        # List pending exams if any
        if hasattr(self.mock_system, 'pending_exams') and self.mock_system.pending_exams:
            print("\n📋 Bekleyen Sınavlar:")
            for i, exam in enumerate(self.mock_system.pending_exams, 1):
                print(f"[{i}] {exam['course_name']} - {exam['created_at'][:16]}")
        
        # Ask for exam file
        exam_file = input("\nTamamlanmış sınav dosyasının yolunu girin: ").strip().strip('"')
        
        if not exam_file:
            print("❌ Dosya yolu girilmedi!")
            return
        
        # Process the exam
        exam_info = self.upload_completed_exam(exam_file)
        if not exam_info:
            return
        
        # Extract student answers
        student_answers = self.extract_student_answers(exam_info['content'])
        print(f"✅ {len(student_answers)} cevap tespit edildi")
        
        # Analyze answers
        analysis = self.analyze_answers(exam_info['exam_id'], student_answers)
        
        # Generate and display report
        report = self.generate_detailed_report(analysis)
        
        # Save report
        report_filename = f"Analysis_{exam_info['exam_id']}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        os.makedirs("exam_analyses", exist_ok=True)
        report_path = os.path.join("exam_analyses", report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ Analiz tamamlandı!")
        print(f"📁 Detaylı rapor: {report_path}")
        
        # Display summary
        print(f"\n📊 ÖZET SONUÇLAR:")
        print(f"Genel Puan: {analysis['overall_score']:.1f}/{analysis['max_score']:.1f} ({analysis['percentage']:.1f}%)")
        print(f"Harf Notu: {self.get_letter_grade(analysis['percentage'])}")
        
        if analysis['strong_areas']:
            print(f"\n💪 Güçlü Alanlar:")
            for area in analysis['strong_areas'][:3]:
                print(f"  ✅ {area}")
        
        if analysis['weak_areas']:
            print(f"\n⚠️ Geliştirilmesi Gereken Alanlar:")
            for area in analysis['weak_areas'][:3]:
                print(f"  ❌ {area}")
        
        # Save to history
        self.analysis_history.append(analysis)
        self.save_analysis_history()
        
        # Update mock system history
        self.mock_system.exam_history.append({
            'exam_id': exam_info['exam_id'],
            'course_id': analysis.get('course_id', ''),
            'analyzed_at': analysis['analyzed_at'],
            'overall_percentage': analysis['percentage'],
            'topic_results': [
                {'topic': topic, 'score_percentage': scores['percentage']}
                for topic, scores in analysis['topic_analysis'].items()
            ]
        })
        self.mock_system.save_exam_history()

if __name__ == "__main__":
    # Test
    from mock_exam_system import MockExamSystem
    mock_system = MockExamSystem()
    analysis_system = ExamAnalysisSystem(mock_system)
    analysis_system.analyze_uploaded_exam_interactive()