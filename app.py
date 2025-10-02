#!/usr/bin/env python3
"""STUDY ASSISTANT - WEB INTERFACE"""
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, session
import os, json, requests, time, re, uuid
from datetime import datetime
from pathlib import Path
import threading
from werkzeug.utils import secure_filename
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import urllib.parse

# Import existing system - handle import errors
try:
    from main import StudyAssistant
except ImportError:
    print("❌ Could not import StudyAssistant from main.py")
    print("Make sure main.py is in the same directory")
    StudyAssistant = None

app = Flask(__name__)
app.secret_key = 'study_assistant_ultimate_2024'

# Global system instance
system = None

def fetch_moodle_courses(moodle_url, api_token):
    """Fetch courses from Moodle API and create universal course database"""
    try:
        # Clean and validate URL
        moodle_url = moodle_url.rstrip('/')
        if not moodle_url.startswith(('http://', 'https://')):
            moodle_url = 'https://' + moodle_url

        # Moodle Web Service API endpoint for getting courses
        api_url = f"{moodle_url}/webservice/rest/server.php"

        params = {
            'wstoken': api_token,
            'wsfunction': 'core_course_get_courses',
            'moodlewsrestformat': 'json'
        }

        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()

        courses_data = response.json()

        if isinstance(courses_data, dict) and 'exception' in courses_data:
            raise Exception(f"Moodle API error: {courses_data.get('message', 'Unknown error')}")

        # Transform Moodle course data to our format
        courses_db = {}
        for course in courses_data:
            if course.get('id') and course.get('id') != 1:  # Skip site course (id=1)
                course_id = str(course['id'])
                courses_db[course_id] = {
                    'name': course.get('fullname', course.get('shortname', f'Course {course_id}')),
                    'shortname': course.get('shortname', course_id),
                    'category': course.get('categoryname', 'General'),
                    'moodle_url': f"{moodle_url}/course/view.php?id={course['id']}",
                    'moodle_id': course['id'],
                    'summary': course.get('summary', ''),
                    'visible': course.get('visible', 1) == 1
                }

        return courses_db

    except requests.RequestException as e:
        raise Exception(f"Network error connecting to Moodle: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Invalid response from Moodle API")
    except Exception as e:
        raise Exception(f"Failed to fetch courses: {str(e)}")

@app.before_request
def check_setup():
    """Check if setup is completed before processing requests"""
    # Skip setup check for setup-related routes, Gmail OAuth, and static files
    exempt_routes = ['setup', 'api_setup', 'api_test_setup', 'auth_gmail', 'auth_gmail_callback', 'api_gmail_status', 'static']
    if request.endpoint in exempt_routes or request.path.startswith('/static'):
        return

    # Check if setup is completed
    if not is_setup_completed():
        return redirect(url_for('setup'))

# Conversation memory storage
conversations = {}

def get_conversation_id():
    """Get or create conversation ID for session"""
    if 'conversation_id' not in session:
        session['conversation_id'] = str(uuid.uuid4())
    return session['conversation_id']

def get_conversation_history(conv_id):
    """Get conversation history, limit to last 10 messages"""
    if conv_id not in conversations:
        conversations[conv_id] = []
    # Keep only last 10 messages to avoid token limits
    return conversations[conv_id][-10:]

def add_to_conversation(conv_id, role, content):
    """Add message to conversation history"""
    if conv_id not in conversations:
        conversations[conv_id] = []
    conversations[conv_id].append({"role": role, "content": content})

    # Cleanup old conversations (keep only last 50 messages)
    if len(conversations[conv_id]) > 50:
        conversations[conv_id] = conversations[conv_id][-50:]

def initialize_system():
    global system
    if StudyAssistant is None:
        print("❌ StudyAssistant class not available")
        return

    try:
        system = StudyAssistant()
        print("✅ Study system initialized")
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        system = None

# Initialize system in background
if StudyAssistant is not None:
    threading.Thread(target=initialize_system, daemon=True).start()
else:
    print("⚠️ Skipping system initialization - StudyAssistant not available")

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
                         recent_emails=list(system.email_cache.keys())[:5] if hasattr(system, 'email_cache') else [],
                         contacts=get_contacts(),
                         university_name=get_university_name())

@app.route('/courses')
def courses():
    """Courses overview"""
    if not system:
        return redirect(url_for('index'))

    return render_template('courses.html', courses=system.courses, university_name=get_university_name())

@app.route('/ai-chat')
def ai_chat():
    """AI Chat interface"""
    return render_template('ai_chat.html',
                         courses=system.courses if system else {},
                         contacts=get_contacts(),
                         university_name=get_university_name())

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
        # Get conversation ID first
        conv_id = get_conversation_id()

        # Check for email confirmation
        if 'pending_email' in session and user_message.lower().strip() in ['evet', 'yes', 'e', 'y']:
            pending_email = session['pending_email']
            del session['pending_email']  # Clear pending email

            # Send the email
            if hasattr(system, 'send_email'):
                success = system.send_email(pending_email['to'], f"📧 {pending_email['subject']}", pending_email['message'])
                if success:
                    response_msg = f"✅ Email başarıyla gönderildi: {pending_email['to']}"
                    add_to_conversation(conv_id, "user", user_message)
                    add_to_conversation(conv_id, "assistant", response_msg)

                    return jsonify({
                        'response': response_msg,
                        'type': 'system',
                        'action': 'email_sent'
                    })
                else:
                    response_msg = f"❌ Email gönderilemedi: {pending_email['to']}"
                    add_to_conversation(conv_id, "user", user_message)
                    add_to_conversation(conv_id, "assistant", response_msg)

                    return jsonify({
                        'response': response_msg,
                        'type': 'error'
                    })

        # Check for email cancellation
        elif 'pending_email' in session and user_message.lower().strip() in ['hayır', 'no', 'h', 'n', 'iptal', 'cancel']:
            del session['pending_email']  # Clear pending email
            response_msg = "❌ Email gönderimi iptal edildi."
            add_to_conversation(conv_id, "user", user_message)
            add_to_conversation(conv_id, "assistant", response_msg)

            return jsonify({
                'response': response_msg,
                'type': 'system'
            })

        # System prompt for Claude
        system_prompt = f"""You are Claude, an AI assistant with access to current information and research capabilities.

Available courses: {', '.join(system.courses.keys())}
Contacts: {', '.join(f'{k}={v}' for k,v in system.contacts.items())}

CRITICAL EMAIL RULES:
When user asks you to send an email about ANY topic (except mock exams) OR asks you to modify/improve a previous email:
1. You must research and write detailed, informative content about the requested topic
2. Use this exact format: EMAIL_REQUEST: email | subject | message
3. The message must contain actual information, research, current events, or detailed content about what was requested
4. Do NOT write template emails like "Dear X, hope you're well..."
5. Write substantial, informative content relevant to the request
6. If user asks for "more detailed", "çok daha detaylı", etc. - send a NEW EMAIL_REQUEST with improved content

MOCK EXAM EMAIL RULES:
If user asks for mock exam AND mentions an email address:
- Use MOCK_EXAM_EMAIL: course_code | email@domain.com
- Do NOT use EMAIL_REQUEST for mock exam requests

EXAMPLE FORMAT:
EMAIL_REQUEST: user_provided_email | Appropriate Subject | [Your detailed, researched content here - NOT a placeholder]

For system requests, respond with exact formats:
- Study plan: "STUDY_PLAN: course_code"
- Mock exam (without email): "MOCK_EXAM: course_code"
- Mock exam with email: "MOCK_EXAM_EMAIL: course_code | email@domain.com"
- PDF analysis: "PDF_ANALYSIS: course_code"
- Cheat sheet: "CHEAT_SHEET: course_code"

IMPORTANT: When using EMAIL_REQUEST, respond ONLY with the command, NO additional text."""

        # Check for email first - if email exists, skip course detection for general messages
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        has_email = re.search(email_pattern, user_message)

        # Skip course detection if it's an email request (unless it's specifically about courses)
        detected_course = None
        course_specific_words = ['mock exam', 'study plan', 'pdf analiz', 'ders', 'course']
        is_course_request = any(word in user_message.lower() for word in course_specific_words)

        if not has_email or is_course_request:
            # Check for course name mentions
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

        # Get conversation history (conv_id already obtained above)
        conversation_history = get_conversation_history(conv_id)

        # Prepare current message
        if detected_course:
            current_message = f"{user_message} {detected_course}"
        else:
            current_message = user_message

        # Build messages with conversation history
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": current_message})

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
        if "EMAIL_REQUEST:" in response:
            # Process email request: EMAIL_REQUEST: email@domain.com | subject | message
            # Extract the EMAIL_REQUEST part (can be multiline)
            email_content = response.split("EMAIL_REQUEST:")[1].strip()

            # Split by | but only first two splits (email and subject)
            parts = email_content.split(" | ", 2)
            if len(parts) >= 3:
                email = parts[0].strip()
                subject = parts[1].strip()
                message = parts[2].strip()

                # Send email using system's send_email method
                if hasattr(system, 'send_email'):
                    # Show email preview and ask for confirmation
                    email_preview = f"""📧 **Email Preview**

**To:** {email}
**Subject:** {subject}
**Message:**
{message}

Bu email'i göndermek istiyor musunuz?
*"evet" yazarsanız gönderilecek, "hayır" yazarsanız iptal edilecek.*"""

                    # Save the pending email data in session for confirmation
                    session['pending_email'] = {
                        'to': email,
                        'subject': subject,
                        'message': message
                    }

                    # Save conversation
                    add_to_conversation(conv_id, "user", current_message)
                    add_to_conversation(conv_id, "assistant", email_preview)

                    return jsonify({
                        'response': email_preview,
                        'type': 'email_preview',
                        'action': 'email_confirmation_needed'
                    })
                else:
                    return jsonify({
                        'response': '❌ Email functionality not available',
                        'type': 'error'
                    })

        elif "STUDY_PLAN:" in response:
            course_code = response.split("STUDY_PLAN:")[1].strip()
            if course_code in system.courses:
                return jsonify({
                    'response': f'Creating study plan for {course_code}...',
                    'type': 'system',
                    'action': 'study_plan',
                    'course_code': course_code
                })

        elif "MOCK_EXAM_EMAIL:" in response:
            # Process mock exam email request: MOCK_EXAM_EMAIL: course_code | email@domain.com
            parts = response.split("MOCK_EXAM_EMAIL:")[1].strip().split(" | ")
            if len(parts) >= 2:
                course_code = parts[0].strip()
                email = parts[1].strip()

                if course_code in system.courses:
                    # Generate mock exam and send via email directly
                    try:
                        print(f"🎯 Generating mock exam for: {get_course_name(course_code)}")
                        if hasattr(system, 'generate_mock_exam_with_pdf'):
                            result = system.generate_mock_exam_with_pdf(course_code)
                        else:
                            system.generate_mock_exam(course_code)
                            exam_dir = Path(f"mock_exams/{course_code}")
                            if exam_dir.exists():
                                pdf_files = list(exam_dir.glob("EXAM_*.pdf"))
                                result = pdf_files[-1] if pdf_files else None
                            else:
                                result = None
                    except Exception as e:
                        print(f"❌ Mock exam generation failed: {e}")
                        result = None

                    if result:
                        if hasattr(system, 'send_mock_exam_email') and hasattr(system, 'cache_email'):
                            pdf_path = result if isinstance(result, (str, Path)) else None
                            email_result = system.send_mock_exam_email(email, course_code, pdf_path)
                            system.cache_email(email)

                        # Save conversation for mock exam email
                        add_to_conversation(conv_id, "user", current_message)
                        add_to_conversation(conv_id, "assistant", f"✅ Mock exam for {course_code} created and sent to {email}")

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
        # Save conversation
        add_to_conversation(conv_id, "user", current_message)
        add_to_conversation(conv_id, "assistant", response)

        return jsonify({
            'response': response,
            'type': 'chat'
        })

    except Exception as e:
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500

@app.route('/mock-exam')
def mock_exam():
    """Mock exam generator interface"""
    return render_course_template('mock_exam.html')

@app.route('/api/generate-mock-exam', methods=['POST'])
def api_generate_mock_exam():
    """Generate mock exam"""
    if not system:
        return jsonify({'error': 'System not ready'}), 503

    data = request.get_json()
    course_code = data.get('course_code')
    email = data.get('email', '').strip()

    error_response = validate_course_code(course_code)
    if error_response:
        return error_response

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
            'course_name': get_course_name(course_code),
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
    return render_course_template('study_plan.html')

@app.route('/api/create-study-plan', methods=['POST'])
def api_create_study_plan():
    """Create study plan"""
    if not system:
        return jsonify({'error': 'System not ready'}), 503

    data = request.get_json()
    course_code = data.get('course_code')

    error_response = validate_course_code(course_code)
    if error_response:
        return error_response

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
                "content": f"Create 4-week study plan for {get_course_name(course_code)}\nBased on: {cache_data.get('analysis', '')[:2000]}\nInclude daily objectives and practice"
            }])
        elif hasattr(system, '_claude_request'):
            plan = system._claude_request([{
                "role": "user",
                "content": f"Create 4-week study plan for {get_course_name(course_code)}\nBased on: {cache_data.get('analysis', '')[:2000]}\nInclude daily objectives and practice"
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
                'course_name': get_course_name(course_code),
                'saved_to': str(plan_file)
            })
        else:
            return jsonify({'error': 'Failed to generate study plan'}), 500

    except Exception as e:
        return jsonify({'error': f'Study plan creation failed: {str(e)}'}), 500

@app.route('/pdf-analysis')
def pdf_analysis():
    """PDF analysis interface"""
    return render_course_template('pdf_analysis.html')

@app.route('/api/analyze-pdfs', methods=['POST'])
def api_analyze_pdfs():
    """Analyze course PDFs"""
    if not system:
        return jsonify({'error': 'System not ready'}), 503

    data = request.get_json()
    course_code = data.get('course_code')

    error_response = validate_course_code(course_code)
    if error_response:
        return error_response

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
COURSE: {get_course_name(course_code)}
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
COURSE: {get_course_name(course_code)}
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
                'course_name': get_course_name(course_code),
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

    return render_template('settings.html', status=status, university_name=get_university_name())

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

@app.route('/setup')
def setup():
    """Setup page for initial configuration"""
    return render_template('setup.html', university_name=get_university_name())

@app.route('/api/setup', methods=['POST'])
def api_setup():
    """Save API configuration"""
    try:
        data = request.json

        # Create directories if they don't exist
        os.makedirs('api_keys', exist_ok=True)
        os.makedirs('config', exist_ok=True)

        # Save Claude API key
        if data.get('claude_api_key'):
            with open('api_keys/claude_api_key.txt', 'w') as f:
                f.write(data['claude_api_key'])

        # Gmail connection is handled via OAuth routes
        # No need to process gmail_credentials here

        # Save University & Moodle config
        moodle_config = {}
        if data.get('university_name'):
            moodle_config['university_name'] = data['university_name']
        if data.get('moodle_url'):
            moodle_config['url'] = data['moodle_url']
        if data.get('moodle_token'):
            moodle_config['token'] = data['moodle_token']

        if moodle_config:
            with open('config/moodle.json', 'w') as f:
                json.dump(moodle_config, f, indent=2)

            # Auto-discover courses from Moodle if URL and token provided
            if data.get('moodle_url') and data.get('moodle_token'):
                try:
                    courses = fetch_moodle_courses(data['moodle_url'], data['moodle_token'])
                    if courses:
                        with open('courses_database.json', 'w') as f:
                            json.dump(courses, f, indent=2)
                except Exception as e:
                    print(f"Warning: Could not auto-discover courses: {e}")

        # Save email settings
        email_config = {
            'default_sender': data.get('default_email', '')
        }
        with open('config/email.json', 'w') as f:
            json.dump(email_config, f, indent=2)

        # Mark setup as complete
        setup_config = {
            'completed': True,
            'setup_date': datetime.now().isoformat()
        }
        with open('config/setup.json', 'w') as f:
            json.dump(setup_config, f, indent=2)

        # Reinitialize system with new config
        global system
        system = None
        initialize_system()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-setup', methods=['POST'])
def api_test_setup():
    """Test API configuration"""
    try:
        data = request.json
        results = {
            'claude': False,
            'gmail': False,
            'moodle': False,
            'errors': []
        }

        # Test Claude API
        if data.get('claude_api_key'):
            try:
                headers = {
                    'x-api-key': data['claude_api_key'],
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                }
                test_data = {
                    'model': 'claude-3-sonnet-20240229',
                    'max_tokens': 10,
                    'messages': [{'role': 'user', 'content': 'Test'}]
                }
                response = requests.post('https://api.anthropic.com/v1/messages',
                                       headers=headers, json=test_data, timeout=10)
                results['claude'] = response.status_code == 200
                if not results['claude']:
                    results['errors'].append(f"Claude API test failed: {response.status_code}")
            except Exception as e:
                results['errors'].append(f"Claude API error: {str(e)}")

        # Test Gmail credentials
        if data.get('gmail_credentials'):
            try:
                gmail_creds = json.loads(data['gmail_credentials'])
                if 'client_id' in gmail_creds and 'client_secret' in gmail_creds:
                    results['gmail'] = True
                else:
                    results['errors'].append("Gmail credentials missing client_id or client_secret")
            except json.JSONDecodeError:
                results['errors'].append("Invalid Gmail credentials JSON")

        # Test Moodle (if provided)
        if data.get('moodle_url') and data.get('moodle_token'):
            try:
                # Simple test request to Moodle
                moodle_url = data['moodle_url'].rstrip('/')
                test_url = f"{moodle_url}/webservice/rest/server.php"
                params = {
                    'wstoken': data['moodle_token'],
                    'wsfunction': 'core_webservice_get_site_info',
                    'moodlewsrestformat': 'json'
                }
                response = requests.get(test_url, params=params, timeout=10)
                results['moodle'] = response.status_code == 200
                if not results['moodle']:
                    results['errors'].append(f"Moodle API test failed: {response.status_code}")
            except Exception as e:
                results['errors'].append(f"Moodle API error: {str(e)}")
        else:
            results['moodle'] = True  # Optional, so mark as OK if not provided

        return jsonify(results)

    except Exception as e:
        return jsonify({'claude': False, 'gmail': False, 'moodle': False, 'errors': [str(e)]})

def is_setup_completed():
    """Check if initial setup is completed"""
    setup_file = Path('config/setup.json')
    if setup_file.exists():
        try:
            with open(setup_file, 'r') as f:
                config = json.load(f)
                return config.get('completed', False)
        except:
            return False
    return False

def get_contacts():
    """Load and return contacts dictionary from cache or config"""
    try:
        contacts_file = Path('email_cache.json')
        if contacts_file.exists():
            with open(contacts_file, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def get_university_name():
    """Get university name from config"""
    moodle_file = Path('config/moodle.json')
    if moodle_file.exists():
        try:
            with open(moodle_file, 'r') as f:
                config = json.load(f)
                return config.get('university_name', 'Study Assistant')
        except:
            return 'Study Assistant'
    return 'Study Assistant'

# Helper functions to reduce code duplication
def render_course_template(template_name, **kwargs):
    """Render template with common course and university data"""
    return render_template(
        template_name,
        courses=system.courses if system else {},
        university_name=get_university_name(),
        **kwargs
    )

def validate_course_code(course_code):
    """Validate course code and return error response if invalid"""
    if not course_code:
        return jsonify({'error': 'Course code required'}), 400
    if not system or course_code not in system.courses:
        return jsonify({'error': f'Course {course_code} not found'}), 404
    return None

def get_course_name(course_code):
    """Get course name from course code"""
    if system and course_code in system.courses:
        return system.courses[course_code].get('name', course_code)
    return course_code

# Gmail OAuth Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
REDIRECT_URI = 'http://localhost:8080/auth/gmail/callback'

def get_credentials_path():
    """Get path to Gmail credentials file"""
    return Path('api_keys/credentials.json')

def get_token_path():
    """Get path to Gmail token file"""
    return Path('api_keys/gmail_token.json')

@app.route('/auth/gmail')
def auth_gmail():
    """Start Gmail OAuth flow"""
    try:
        credentials_path = get_credentials_path()
        if not credentials_path.exists():
            return jsonify({'error': 'Gmail credentials not found. Please add credentials.json first.'}), 400

        flow = Flow.from_client_secrets_file(
            str(credentials_path),
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        session['state'] = state
        return redirect(authorization_url)

    except Exception as e:
        print(f"Gmail OAuth start error: {e}")
        return redirect(url_for('setup') + '?error=gmail_oauth_failed')

@app.route('/api/upload-credentials', methods=['POST'])
def upload_credentials():
    """Upload Gmail credentials JSON file"""
    try:
        if 'credentials' not in request.files:
            return jsonify({'error': 'No credentials file uploaded'}), 400

        file = request.files['credentials']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.endswith('.json'):
            return jsonify({'error': 'File must be a JSON file'}), 400

        # Create api_keys directory if it doesn't exist
        os.makedirs('api_keys', exist_ok=True)

        # Read and validate JSON content
        try:
            content = file.read().decode('utf-8')
            credentials_data = json.loads(content)

            # Basic validation for Google OAuth credentials
            if 'web' in credentials_data or 'installed' in credentials_data:
                # Save to api_keys/credentials.json (consistent with get_credentials_path())
                credentials_path = get_credentials_path()
                with open(credentials_path, 'w') as f:
                    f.write(content)

                return jsonify({'success': True, 'message': 'Credentials uploaded successfully'})
            else:
                return jsonify({'error': 'Invalid credentials format. Must be Google OAuth credentials.'}), 400

        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON file'}), 400

    except Exception as e:
        print(f"Credentials upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/auth/gmail/callback')
def auth_gmail_callback():
    """Handle Gmail OAuth callback"""
    try:
        credentials_path = get_credentials_path()
        if not credentials_path.exists():
            return redirect(url_for('setup') + '?error=credentials_missing')

        flow = Flow.from_client_secrets_file(
            str(credentials_path),
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
            state=session.get('state')
        )

        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials

        # Save token
        token_path = get_token_path()
        os.makedirs(token_path.parent, exist_ok=True)

        with open(token_path, 'w') as token_file:
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            json.dump(token_data, token_file, indent=2)

        # Test Gmail connection
        try:
            service = build('gmail', 'v1', credentials=credentials)
            profile = service.users().getProfile(userId='me').execute()
            print(f"✅ Gmail connected: {profile.get('emailAddress')}")
        except Exception as e:
            print(f"Gmail connection test failed: {e}")

        return redirect(url_for('setup') + '?gmail=connected')

    except Exception as e:
        print(f"Gmail OAuth callback error: {e}")
        return redirect(url_for('setup') + '?error=gmail_oauth_callback_failed')

@app.route('/api/gmail-status')
def api_gmail_status():
    """Check Gmail connection status and credentials"""
    try:
        token_path = get_token_path()
        credentials_path = get_credentials_path()

        # Check if credentials exist (also check root directory for backwards compatibility)
        credentials_exist = credentials_path.exists() or Path('credentials.json').exists()

        if not token_path.exists() or not credentials_exist:
            return jsonify({
                'connected': False,
                'credentials_exist': credentials_exist
            })

        # Load and validate token
        with open(token_path, 'r') as f:
            token_data = json.load(f)

        credentials = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )

        # Refresh if needed
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # Save updated token
            updated_token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            with open(token_path, 'w') as f:
                json.dump(updated_token_data, f, indent=2)

        # Test connection
        service = build('gmail', 'v1', credentials=credentials)
        profile = service.users().getProfile(userId='me').execute()

        return jsonify({
            'connected': True,
            'email': profile.get('emailAddress')
        })

    except Exception as e:
        print(f"Gmail status check error: {e}")
        return jsonify({'connected': False})

if __name__ == '__main__':
    print("\n🚀 Starting Study Assistant Web Interface...")
    print("📱 Access at: http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)