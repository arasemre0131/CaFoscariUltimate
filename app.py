#!/usr/bin/env python3
"""CA' FOSCARI ULTIMATE - WEB INTERFACE"""
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os, json, requests, time, re
from datetime import datetime
from pathlib import Path
import threading

# Import existing system - handle import errors
try:
    from main import CaFoscariUltimate
except ImportError:
    print("❌ Could not import CaFoscariUltimate from main.py")
    print("Make sure main.py is in the same directory")
    CaFoscariUltimate = None

app = Flask(__name__)
app.secret_key = 'cafoscari_ultimate_2024'

# Global system instance
system = None

def initialize_system():
    global system
    if CaFoscariUltimate is None:
        print("❌ CaFoscariUltimate class not available")
        return

    try:
        system = CaFoscariUltimate()
        print("✅ Ca' Foscari system initialized")
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        system = None

# Initialize system in background
if CaFoscariUltimate is not None:
    threading.Thread(target=initialize_system, daemon=True).start()
else:
    print("⚠️ Skipping system initialization - CaFoscariUltimate not available")

@app.route('/')
def index():
    """Main dashboard"""
    if not system:
        return render_template('loading.html')

    status = {
        'courses': len(system.courses),
        'claude_api': bool(system.claude_api),
        'moodle': bool(system.moodle_token),
        'gmail': bool(system.gmail_service),
        'cached_emails': len(system.email_cache) if hasattr(system, 'email_cache') else 0
    }

    return render_template('dashboard.html',
                         courses=system.courses,
                         status=status,
                         recent_emails=list(system.email_cache.keys())[:5] if hasattr(system, 'email_cache') else [])

@app.route('/courses')
def courses():
    """Courses overview"""
    if not system:
        return redirect(url_for('index'))

    return render_template('courses.html', courses=system.courses)

@app.route('/ai-chat')
def ai_chat():
    """AI Chat interface"""
    return render_template('ai_chat.html',
                         courses=system.courses if system else {},
                         contacts=system.contacts if system else {})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for AI chat"""
    if not system:
        return jsonify({'error': 'System not ready'}), 503

    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    try:
        # Direct pattern matching for common requests
        if re.search(r'\d{5}.*mock.*@.*\.(com|gmail)', user_message, re.I):
            course_match = re.search(r'\b(\d{5})\b', user_message)
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_message)

            if course_match and email_match:
                course_code = course_match.group(1)
                email = email_match.group(0)

                if course_code in system.courses:
                    # Generate and send mock exam
                    if hasattr(system, 'generate_mock_exam_with_pdf'):
                        result = system.generate_mock_exam_with_pdf(course_code)
                    else:
                        # Fallback to regular mock exam generation
                        try:
                            system.generate_mock_exam(course_code)
                            result = True
                        except:
                            result = False

                    if result:
                        if hasattr(system, 'send_mock_exam_email') and hasattr(system, 'cache_email'):
                            system.send_mock_exam_email(email, course_code, result)
                            system.cache_email(email)
                        else:
                            # Fallback to regular email
                            if hasattr(system, 'send_email'):
                                system.send_email(email, f"Mock Exam - {course_code}", "Mock exam generated successfully")
                        return jsonify({
                            'response': f'✅ Mock exam for {course_code} created and sent to {email}',
                            'type': 'success',
                            'action': 'mock_exam_sent'
                        })
                    else:
                        return jsonify({
                            'response': '❌ Failed to create mock exam',
                            'type': 'error'
                        })

        # System prompt for Claude
        system_prompt = f"""You are Claude integrated with Ca' Foscari study system.

Available courses: {', '.join(system.courses.keys())}
Contacts: {', '.join(f'{k}={v}' for k,v in system.contacts.items())}

For system requests, respond with exact formats:
- Study plan: "STUDY_PLAN: course_code"
- Mock exam: "MOCK_EXAM: course_code"
- PDF analysis: "PDF_ANALYSIS: course_code"
- Cheat sheet: "CHEAT_SHEET: course_code"
- Email: "EMAIL_REQUEST: email | subject | message"

Otherwise respond naturally in Turkish."""

        # Check for course name mentions first
        detected_course = None
        for code, course in system.courses.items():
            course_name = course.get('name', '')
            course_keywords = []

            # Extract keywords from course name
            if 'CALCULUS' in course_name.upper():
                course_keywords.extend(['calculus', 'matematik', 'analiz', 'türev', 'integral'])
            if 'LINEAR ALGEBRA' in course_name.upper():
                course_keywords.extend(['linear algebra', 'lineer cebir', 'matris', 'vektör'])
            if 'DISCRETE' in course_name.upper():
                course_keywords.extend(['discrete', 'ayrık', 'matematik'])
            if 'PROGRAMMING' in course_name.upper():
                course_keywords.extend(['programming', 'programlama', 'kod', 'python', 'java'])
            if 'COMPUTER ARCH' in course_name.upper():
                course_keywords.extend(['computer architecture', 'bilgisayar mimarisi', 'işlemci', 'cpu'])
            if 'ENGLISH' in course_name.upper():
                course_keywords.extend(['english', 'ingilizce', 'technical english'])
            if 'MATHEMATICS' in course_name.upper():
                course_keywords.extend(['mathematics', 'matematik', 'background'])

            # Check if any keyword matches
            for keyword in course_keywords:
                if keyword.lower() in user_message.lower():
                    detected_course = code
                    break

            if detected_course:
                break

        # If course detected, add it to message for Claude
        if detected_course:
            user_message_with_code = f"{user_message} {detected_course}"
            messages = [{"role": "user", "content": user_message_with_code}]
        else:
            messages = [{"role": "user", "content": user_message}]

        # Check for requests without course code - show interactive selection
        action_keywords = ['mock exam', 'study plan', 'pdf analiz', 'analiz']
        has_action = any(keyword in user_message.lower() for keyword in action_keywords)
        has_course_code = re.search(r'\d{5}', user_message) or detected_course

        if has_action and not has_course_code:
            action_type = None
            if 'mock exam' in user_message.lower():
                action_type = 'mock_exam'
            elif 'study plan' in user_message.lower():
                action_type = 'study_plan'
            elif 'analiz' in user_message.lower():
                action_type = 'pdf_analysis'

            if action_type:
                return jsonify({
                    'response': 'Hangi ders için? Aşağıdan seçin:',
                    'type': 'course_selection',
                    'action': action_type,
                    'courses': [{'code': code, 'name': course.get('name', code)} for code, course in system.courses.items()]
                })

        # Get Claude response with enhanced system prompt
        enhanced_system_prompt = system_prompt + f"""

IMPORTANT: Course name detection has been applied. If user mentions course names instead of codes, automatically map them:
- Calculus/Matematik/Türev → Use course with CALCULUS in name
- Linear Algebra/Lineer Cebir/Matris → Use course with LINEAR ALGEBRA in name
- Programming/Programlama → Use course with PROGRAMMING in name
- Discrete/Ayrık Matematik → Use course with DISCRETE in name
- Computer Architecture/Bilgisayar Mimarisi → Use course with COMPUTER ARCH in name
- English/İngilizce → Use course with ENGLISH in name
- Mathematics Background → Use course with MATHEMATICS in name

Detected course for this message: {detected_course if detected_course else 'None'}"""

        if hasattr(system, 'claude_request'):
            response = system.claude_request(messages, enhanced_system_prompt)
        elif hasattr(system, '_claude_request'):
            response = system._claude_request(messages, enhanced_system_prompt)
        else:
            response = "❌ Claude API not available"

        # Process system commands
        if "STUDY_PLAN:" in response:
            course_code = response.split("STUDY_PLAN:")[1].strip()
            if course_code in system.courses:
                return jsonify({
                    'response': f'Creating study plan for {course_code}...',
                    'type': 'system',
                    'action': 'study_plan',
                    'course_code': course_code
                })

        elif "MOCK_EXAM:" in response:
            course_code = response.split("MOCK_EXAM:")[1].strip()
            if course_code in system.courses:
                return jsonify({
                    'response': f'Creating mock exam for {course_code}...',
                    'type': 'system',
                    'action': 'mock_exam',
                    'course_code': course_code
                })

        elif "PDF_ANALYSIS:" in response:
            course_code = response.split("PDF_ANALYSIS:")[1].strip()
            if course_code in system.courses:
                return jsonify({
                    'response': f'Analyzing PDFs for {course_code}...',
                    'type': 'system',
                    'action': 'pdf_analysis',
                    'course_code': course_code
                })

        # Regular Claude response
        return jsonify({
            'response': response,
            'type': 'chat'
        })

    except Exception as e:
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500

@app.route('/mock-exam')
def mock_exam():
    """Mock exam generator interface"""
    return render_template('mock_exam.html', courses=system.courses if system else {})

@app.route('/api/generate-mock-exam', methods=['POST'])
def api_generate_mock_exam():
    """Generate mock exam"""
    if not system:
        return jsonify({'error': 'System not ready'}), 503

    data = request.get_json()
    course_code = data.get('course_code')
    email = data.get('email', '').strip()

    if not course_code or course_code not in system.courses:
        return jsonify({'error': 'Invalid course code'}), 400

    try:
        # Generate mock exam - check available methods
        pdf_file = None

        if hasattr(system, 'generate_mock_exam_with_pdf'):
            pdf_file = system.generate_mock_exam_with_pdf(course_code)
        else:
            # Use original generate_mock_exam method
            try:
                system.generate_mock_exam(course_code)
                # Look for generated PDF in mock_exams directory
                exam_dir = Path(f"mock_exams/{course_code}")
                if exam_dir.exists():
                    pdf_files = list(exam_dir.glob("EXAM_*.pdf"))
                    if pdf_files:
                        pdf_file = pdf_files[-1]  # Get the latest one
            except Exception as e:
                print(f"Error generating mock exam: {e}")

        if not pdf_file:
            return jsonify({'error': 'Failed to generate mock exam'}), 500

        result = {
            'success': True,
            'course_name': system.courses[course_code].get('name', course_code),
            'pdf_file': str(pdf_file),
            'download_url': f'/download-exam/{Path(pdf_file).name}'
        }

        # Send email if provided
        if email:
            email_sent = False

            if hasattr(system, 'send_mock_exam_email'):
                email_sent = system.send_mock_exam_email(email, course_code, pdf_file)
            elif hasattr(system, 'send_email'):
                # Fallback to regular email without attachment
                email_sent = system.send_email(email, f"Mock Exam - {course_code}",
                                               f"Mock exam for {course_code} has been generated. Please download from the system.")

            if email_sent:
                if hasattr(system, 'cache_email'):
                    system.cache_email(email)
                result['email_sent'] = True
                result['email'] = email
            else:
                result['email_error'] = 'Failed to send email'

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'Mock exam generation failed: {str(e)}'}), 500

@app.route('/study-plan')
def study_plan():
    """Study plan interface"""
    return render_template('study_plan.html', courses=system.courses if system else {})

@app.route('/api/create-study-plan', methods=['POST'])
def api_create_study_plan():
    """Create study plan"""
    if not system:
        return jsonify({'error': 'System not ready'}), 503

    data = request.get_json()
    course_code = data.get('course_code')

    if not course_code or course_code not in system.courses:
        return jsonify({'error': 'Invalid course code'}), 400

    try:
        # Check if analysis exists
        cache_file = f"analysis_cache_{course_code}.json"
        abs_cache_path = os.path.abspath(cache_file)

        print(f"Debug: Looking for cache file: {abs_cache_path}")
        print(f"Debug: Cache file exists: {os.path.exists(cache_file)}")

        if not os.path.exists(cache_file):
            # Try to find analysis cache files
            import glob
            cache_files = glob.glob("analysis_cache_*.json")
            print(f"Debug: Found cache files: {cache_files}")

            if not cache_files:
                return jsonify({'error': 'Please run PDF Analysis first. No analysis cache found.'}), 400
            else:
                return jsonify({'error': f'Please run PDF Analysis for course {course_code} first. Available analyses: {[f.replace("analysis_cache_", "").replace(".json", "") for f in cache_files]}'}), 400

        # Create study plan
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
        except:
            cache_data = {}

        # Get Claude response
        if hasattr(system, 'claude_request'):
            plan = system.claude_request([{
                "role": "user",
                "content": f"Create 4-week study plan for {system.courses[course_code].get('name', course_code)}\nBased on: {cache_data.get('analysis', '')[:2000]}\nInclude daily objectives and practice"
            }])
        elif hasattr(system, '_claude_request'):
            plan = system._claude_request([{
                "role": "user",
                "content": f"Create 4-week study plan for {system.courses[course_code].get('name', course_code)}\nBased on: {cache_data.get('analysis', '')[:2000]}\nInclude daily objectives and practice"
            }])
        else:
            return jsonify({'error': 'Claude API not available'}), 500

        if plan:
            # Save plan
            plan_dir = Path(f"study_plans/{course_code}")
            plan_dir.mkdir(parents=True, exist_ok=True)
            plan_file = plan_dir / f"PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            with open(plan_file, 'w', encoding='utf-8') as f:
                f.write(plan)

            return jsonify({
                'success': True,
                'plan': plan,
                'course_name': system.courses[course_code].get('name', course_code),
                'saved_to': str(plan_file)
            })
        else:
            return jsonify({'error': 'Failed to generate study plan'}), 500

    except Exception as e:
        return jsonify({'error': f'Study plan creation failed: {str(e)}'}), 500

@app.route('/pdf-analysis')
def pdf_analysis():
    """PDF analysis interface"""
    return render_template('pdf_analysis.html', courses=system.courses if system else {})

@app.route('/api/analyze-pdfs', methods=['POST'])
def api_analyze_pdfs():
    """Analyze course PDFs"""
    if not system:
        return jsonify({'error': 'System not ready'}), 503

    data = request.get_json()
    course_code = data.get('course_code')

    if not course_code or course_code not in system.courses:
        return jsonify({'error': 'Invalid course code'}), 400

    try:
        # Find course directory
        if hasattr(system, 'find_course_directory'):
            course_dir = system.find_course_directory(course_code)
        elif hasattr(system, '_find_course_dir'):
            course_dir = system._find_course_dir(course_code)
        else:
            # Fallback - look in data/courses
            base_dir = Path("data/courses")
            course_dir = None

            if base_dir.exists():
                # Try different patterns to find course directory
                patterns = [
                    f"{course_code}_*",  # e.g., 21002_CT0663...
                    f"*{course_code}*",  # e.g., contains course code
                    f"*{course.get('name', '').split(' ')[0]}*" if course_code in system.courses else None  # Course name match
                ]

                for pattern in patterns:
                    if pattern:
                        import glob
                        matches = glob.glob(str(base_dir / pattern))
                        if matches:
                            course_dir = Path(matches[0])
                            break

                # If still not found, try exact course name search
                if not course_dir and course_code in system.courses:
                    course_name = system.courses[course_code].get('name', '')
                    for subdir in base_dir.iterdir():
                        if subdir.is_dir():
                            # Check if course name components match
                            if any(part in subdir.name for part in course_name.split() if len(part) > 3):
                                course_dir = subdir
                                break

        print(f"Debug: Found course directory: {course_dir}")

        if not course_dir or not course_dir.exists():
            # List available directories for debug
            base_dir = Path("data/courses")
            if base_dir.exists():
                available_dirs = [d.name for d in base_dir.iterdir() if d.is_dir()]
                print(f"Debug: Available directories: {available_dirs}")
                return jsonify({'error': f'No course directory found for {course_code}. Available: {available_dirs[:3]}...'}), 404
            else:
                return jsonify({'error': 'Course data directory not found'}), 404

        # Get PDFs
        pdfs = list(course_dir.rglob("*.pdf"))[:3]
        if not pdfs:
            return jsonify({'error': 'No PDF files found'}), 404

        # Extract content
        combined_content = ""
        for pdf in pdfs:
            if hasattr(system, 'extract_pdf_text'):
                content = system.extract_pdf_text(pdf)
            elif hasattr(system, '_extract_pdf_text'):
                content = system._extract_pdf_text(pdf)
            else:
                content = f"PDF: {pdf.name} (extraction not available)"
            combined_content += f"=== {pdf.name} ===\n{content}\n"

        # AI Analysis
        if hasattr(system, 'claude_request'):
            analysis = system.claude_request([{
                "role": "user",
                "content": f"""Analyze course materials:
COURSE: {system.courses[course_code].get('name', course_code)}
CONTENT: {combined_content[:10000]}

Provide comprehensive analysis:
1. Core concepts
2. Key formulas
3. Study recommendations
4. Exam focus areas"""
            }])
        elif hasattr(system, '_claude_request'):
            analysis = system._claude_request([{
                "role": "user",
                "content": f"""Analyze course materials:
COURSE: {system.courses[course_code].get('name', course_code)}
CONTENT: {combined_content[:10000]}

Provide comprehensive analysis:
1. Core concepts
2. Key formulas
3. Study recommendations
4. Exam focus areas"""
            }])
        else:
            return jsonify({'error': 'Claude API not available'}), 500

        if analysis:
            # Cache result
            cache_data = {
                "course_code": course_code,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "pdf_files": [pdf.name for pdf in pdfs]
            }

            # Save cache
            try:
                with open(f"analysis_cache_{course_code}.json", 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error saving cache: {e}")

            return jsonify({
                'success': True,
                'analysis': analysis,
                'course_name': system.courses[course_code].get('name', course_code),
                'pdf_count': len(pdfs),
                'pdf_files': [pdf.name for pdf in pdfs]
            })
        else:
            return jsonify({'error': 'Failed to analyze PDFs'}), 500

    except Exception as e:
        return jsonify({'error': f'PDF analysis failed: {str(e)}'}), 500

@app.route('/settings')
def settings():
    """System settings and status"""
    if not system:
        return redirect(url_for('index'))

    status = {
        'courses': len(system.courses),
        'claude_api': bool(system.claude_api),
        'moodle_token': bool(system.moodle_token),
        'gmail_service': bool(system.gmail_service),
        'email_cache': system.email_cache if hasattr(system, 'email_cache') else {}
    }

    return render_template('settings.html', status=status)

@app.route('/download-exam/<filename>')
def download_exam(filename):
    """Download generated exam PDF"""
    try:
        # Find the file in mock_exams directories
        for course_dir in Path("mock_exams").iterdir():
            if course_dir.is_dir():
                pdf_file = course_dir / filename
                if pdf_file.exists():
                    return send_file(pdf_file, as_attachment=True)

        return "File not found", 404
    except Exception as e:
        return f"Download failed: {e}", 500

if __name__ == '__main__':
    print("\n🚀 Starting Ca' Foscari Ultimate Web Interface...")
    print("📱 Access at: http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)