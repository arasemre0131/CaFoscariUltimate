#!/usr/bin/env python3
"""STUDY ASSISTANT SYSTEM - OPTIMIZED"""
import os, json, requests, time, re
from datetime import datetime
from pathlib import Path

try:
    import pickle
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request as GoogleRequest
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class StudyAssistant:
    def __init__(self):
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  🚀 STUDY ASSISTANT SYSTEM                                      ║
║  Multi-University Support with Moodle Integration               ║
╚══════════════════════════════════════════════════════════════════╝
        """)

        self.courses = self._load_json("courses_database.json", {})
        self.config = self._load_json("api_keys/config.json", {})
        self.contacts = self._load_default_contacts()
        self.email_cache = self._load_json("email_cache.json", {})
        self.context_memory = []
        self.setup_apis()

        print(f"📚 {len(self.courses)} courses loaded")

    def _load_json(self, path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return default

    def _save_json(self, path, data):
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except: return False

    def _load_default_contacts(self):
        defaults = {
            "erdem": "erdem@example.com",
            "soner": "sonerozen2004@gmail.com",
            "tolgay": "tlga.yavuz@gmail.com",
            "tolga": "tlga.yavuz@gmail.com"
        }
        contacts = self._load_json("contacts.json", {})
        defaults.update(contacts)
        if not contacts:
            self._save_json("contacts.json", defaults)
        return defaults

    def setup_apis(self):
        self.claude_api = self.config.get("claude", {}).get("api_key", "")
        if not self.claude_api:
            try:
                with open("api_keys/claude_api_key.txt", 'r') as f:
                    self.claude_api = f.read().strip()
            except: pass

        self.moodle_token = self.config.get("moodle", {}).get("token", "")
        self.moodle_url = self.config.get("moodle", {}).get("url", "https://moodle.unive.it")

        credentials_path = self.config.get("gmail", {}).get("credentials_file", "api_keys/credentials.json")
        self.gmail_enabled = GMAIL_AVAILABLE and os.path.exists(credentials_path)
        self.gmail_service = self.setup_gmail_service() if self.gmail_enabled else None

    def claude_request(self, messages, system_prompt="You are an expert AI tutor.", max_retries=3):
        if not self.claude_api: return "❌ Claude API not configured"

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.claude_api,
                        "content-type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 4096,
                        "system": system_prompt,
                        "messages": messages
                    },
                    timeout=180
                )

                if response.status_code == 200:
                    response_data = response.json()
                    if "content" in response_data and response_data["content"]:
                        if isinstance(response_data["content"], list):
                            return response_data["content"][0]["text"]
                        else:
                            return response_data["content"]
                    elif "message" in response_data:
                        return response_data["message"]
                    else:
                        return "❌ Unexpected response format"
                else:
                    return "❌ HTTP Error"
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, Exception):
                pass

            if attempt < max_retries-1:
                time.sleep(3)

        return "❌ All attempts failed - check API key and connection"

    def setup_gmail_service(self):
        if not GMAIL_AVAILABLE:
            return None
        try:
            SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']
            creds = None
            token_file = self.config.get("gmail", {}).get("token_file", "api_keys/gmail_token.json")
            credentials_file = self.config.get("gmail", {}).get("credentials_file", "api_keys/credentials.json")
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(GoogleRequest())
                else:
                    if os.path.exists(credentials_file):
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                        creds = flow.run_local_server(port=0)
                    else:
                        return None

                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)

            return build('gmail', 'v1', credentials=creds)
        except Exception:
            return None

    def send_email(self, to_email, subject, message):
        if not self.gmail_service:
            return False
        try:
            import base64
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg['To'] = to_email  # Capital T for Gmail API
            msg['Subject'] = subject
            msg['From'] = "me"

            formatted_message = message.replace('\n', '<br>')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px;">
                        <h2 style="color: #2c5aa0;">📧 Ca' Foscari Ultimate System</h2>
                        <div style="background-color: white; padding: 15px; border-radius: 5px; margin-top: 10px;">
                            <p style="line-height: 1.6;">{formatted_message}</p>
                        </div>
                        <hr style="margin: 20px 0; border: 1px solid #ddd;">
                        <p style="color: #666; font-size: 12px;">
                            🎓 Sent from Ca' Foscari Ultimate Study System<br>
                            📅 {timestamp}
                        </p>
                    </div>
                </body>
            </html>
            """

            msg.attach(MIMEText(html_message, 'html'))

            result = self.gmail_service.users().messages().send(
                userId="me",
                body={'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
            ).execute()

            return True

        except Exception:
            return False

    def send_smart_email(self, user_input):
        """Extract email, content and send intelligently"""
        import re

        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', user_input)
        if not email_match:
            return False

        to_email = email_match.group(1)

        content_pattern = r'adresine\s+(.+?)(?:\s+mail|$)'
        content_match = re.search(content_pattern, user_input.lower())

        if content_match:
            message_topic = content_match.group(1).strip()
        else:
            message_topic = "genel bilgi"

        prompt = f"Write a professional email in Turkish about: {message_topic}. Include proper greeting, detailed content, and closing."

        messages = [{"role": "user", "content": prompt}]
        email_content = self.claude_request(messages)

        if not email_content or "❌" in str(email_content):
            return False

        clean_content = str(email_content).strip()
        if clean_content.startswith('"') and clean_content.endswith('"'):
            clean_content = clean_content[1:-1]

        subject = f"📧 {message_topic.title()}"

        return self.send_email(to_email, subject, clean_content)

    def find_course_directory(self, course_code):
        if course_code not in self.courses:
            return None
        course = self.courses[course_code]
        data_courses = Path("data/courses")
        data_courses.mkdir(parents=True, exist_ok=True)

        course_name_safe = course.get('name', '').replace('/', '_').replace('[', '').replace(']', '')
        patterns = [
            f"{course_code}_{course_name_safe}",
            course.get('directory_mapping', ''),
            course_code
        ]

        for pattern in patterns:
            if pattern:
                for subdir in data_courses.iterdir():
                    if subdir.is_dir() and pattern in subdir.name:
                        return subdir
        return None

    def extract_pdf_text(self, pdf_path, max_pages=15):
        if not PDF_AVAILABLE: return f"📄 {pdf_path.name} (PyPDF2 not available)"
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(min(max_pages, len(reader.pages))):
                    text += reader.pages[page_num].extract_text() + "\n"
                return text[:15000]
        except Exception as e:
            return f"📄 Error reading {pdf_path.name}: {e}"

    def deep_pdf_analysis(self, course_code):
        if course_code not in self.courses:
            print(f"❌ Course {course_code} not found")
            self.show_available_courses()
            return

        course = self.courses[course_code]

        course_dir = self.find_course_directory(course_code)
        if not course_dir:
            return

        pdfs = list(course_dir.rglob("*.pdf"))
        if not pdfs:
            return

        combined_content = "\n".join([
            f"=== {pdf.name} ===\n{self.extract_pdf_text(pdf)}\n"
            for pdf in pdfs[:3]
        ])

        messages = [{
            "role": "user",
            "content": f"""Analyze course materials:
COURSE: {course.get('name', course_code)}
CONTENT: {combined_content[:10000]}

Provide comprehensive analysis:
1. Core concepts
2. Key formulas
3. Study recommendations
4. Exam focus areas"""
        }]

        analysis = self.claude_request(messages)

        cache_data = {
            "course_code": course_code,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        self._save_json(f"analysis_cache_{course_code}.json", cache_data)

        return analysis

    def extract_exam_patterns(self, exam_files):
        patterns = {
            'exercises': [], 'points': [], 'structure': [],
            'keywords': [], 'time': [], 'instructions': []
        }

        for exam_file in exam_files[:3]:
            try:
                text = self.extract_pdf_text(exam_file, max_pages=3)

                exercises = re.findall(r'(Exercise|Problem|Question|Esercizio)\s+(\d+)', text, re.I)
                patterns['exercises'].append(len(set(exercises)))

                points = re.findall(r'\(?\s*(\d+)\s*(points?|punti|pts)\s*\)?', text, re.I)
                if points:
                    patterns['points'].extend([int(p[0]) for p in points])

                time = re.search(r'(\d+)\s*(hours?|ore|minutes?|minuti)', text, re.I)
                if time:
                    patterns['time'].append(f"{time.group(1)} {time.group(2)}")

                for keyword in ['prove', 'compute', 'calculate', 'solve', 'find', 'determine']:
                    if keyword in text.lower():
                        patterns['keywords'].append(keyword)

                inst = re.search(r'(Instructions?|Istruzioni):?(.{0,300})', text, re.I)
                if inst:
                    patterns['instructions'].append(inst.group(2).strip())

            except: continue

        return {
            'exercise_count': max(patterns['exercises']) if patterns['exercises'] else 5,
            'total_points': sum(patterns['points'][:5]) if patterns['points'] else 30,
            'time_limit': patterns['time'][0] if patterns['time'] else '2 hours',
            'question_types': list(set(patterns['keywords']))[:5] or ['solve', 'compute', 'prove'],
            'instructions': patterns['instructions'][0][:200] if patterns['instructions'] else None
        }

    def download_previous_exams(self, course_code):

        if not self.moodle_token:
            return []

        exam_dir = Path(f"previous_exams/{course_code}")
        exam_dir.mkdir(parents=True, exist_ok=True)

        try:
            params = {
                'wstoken': self.moodle_token,
                'wsfunction': 'core_course_get_contents',
                'moodlewsrestformat': 'json',
                'courseid': course_code
            }

            response = requests.get(f"{self.moodle_url}/webservice/rest/server.php", params=params)
            sections = response.json()

            exam_files = []
            exam_keywords = ['exam', 'esame', 'prova', 'test', 'midterm', 'final', 'quiz', 'solution']
            exclude_years = ['2020', '2021', '2022', '2023']

            for section in sections:
                if 'modules' not in section:
                    continue

                for module in section['modules']:
                    if 'contents' in module:
                        for content in module['contents']:
                            filename = content.get('filename', '').lower()

                            if any(year in filename for year in exclude_years):
                                continue

                            if any(keyword in filename for keyword in exam_keywords) and filename.endswith('.pdf'):
                                fileurl = content['fileurl'] + f"&token={self.moodle_token}"
                                filepath = exam_dir / content['filename']

                                if not filepath.exists():
                                    pdf_response = requests.get(fileurl)
                                    with open(filepath, 'wb') as f:
                                        f.write(pdf_response.content)
                                    exam_files.append(filepath)
                                else:
                                    exam_files.append(filepath)

            return exam_files

        except Exception:
            return []

    def generate_mock_exam(self, course_code):
        if course_code not in self.courses:
            return

        course = self.courses[course_code]

        exam_files = self.download_previous_exams(course_code)

        if not exam_files:
            exam_dir = Path(f"previous_exams/{course_code}")
            if exam_dir.exists():
                all_files = list(exam_dir.glob("*.pdf"))
                exclude_years = ['2020', '2021', '2022', '2023']
                exam_files = [f for f in all_files if not any(year in f.name for year in exclude_years)]

        if exam_files:
            format_info = self.extract_exam_patterns(exam_files)
            exam_examples = "\n".join([
                f"Example from {f.name}:\n{self.extract_pdf_text(f, 2)[:1500]}\n"
                for f in exam_files[:2]
            ])
        else:
            format_info = {
                'exercise_count': 5, 'total_points': 30,
                'time_limit': '2 hours', 'question_types': ['solve', 'compute', 'prove']
            }
            exam_examples = ""

        cache = self._load_json(f"analysis_cache_{course_code}.json", {})
        if cache:
            course_content = cache.get('analysis', '')[:3000]
        else:
            course_dir = self.find_course_directory(course_code)
            if course_dir:
                pdfs = list(course_dir.rglob("*.pdf"))[:3]
                course_content = "\n".join([self.extract_pdf_text(pdf, 5)[:2000] for pdf in pdfs])
            else:
                course_content = ""

        prompt = f"""Create a Ca' Foscari University mock exam in ENGLISH using EXACT same format as previous exams.

COURSE: {course.get('name', course_code)}
FORMAT REQUIREMENTS: {format_info['exercise_count']} exercises, {format_info['total_points']} points, {format_info['time_limit']}

PREVIOUS EXAM EXAMPLES (COPY THIS FORMAT EXACTLY):
{exam_examples[:3000]}

COURSE CONTENT:
{course_content}

CRITICAL INSTRUCTIONS:
1. Copy the EXACT structure, layout, and formatting from the examples above
2. Keep the same headers, footers, instructions, and point distributions
3. Keep the same exercise numbering and spacing
4. Only change the actual question content - everything else stays identical
5. Maintain the same difficulty level and question style
6. Use the same mathematical notation and symbols as in examples
7. Write entirely in ENGLISH
8. Make sure each exercise has the same point value as in the original format"""

        messages = [{"role": "user", "content": prompt}]
        exam = self.claude_request(messages, "You are a Ca' Foscari professor creating an authentic exam.")

        if not exam:
            return

        exam_dir = Path(f"mock_exams/{course_code}")
        exam_dir.mkdir(parents=True, exist_ok=True)

        pdf_file = self.create_exam_pdf(course_code, course.get('name', course_code), exam, format_info)
        if not pdf_file:
            return

        return pdf_file

    def generate_mock_exam_with_pdf(self, course_code):
        if course_code not in self.courses:
            return None

        course = self.courses[course_code]
        print(f"🎯 Generating mock exam for: {course.get('name', course_code)}")

        exam_files = self.download_previous_exams(course_code)
        if not exam_files:
            exam_dir = Path(f"previous_exams/{course_code}")
            if exam_dir.exists():
                all_files = list(exam_dir.glob("*.pdf"))
                exclude_years = ['2020', '2021', '2022', '2023']
                exam_files = [f for f in all_files if not any(year in f.name for year in exclude_years)]

        if exam_files:
            format_info = self.extract_exam_patterns(exam_files)
            exam_examples = "\n".join([
                f"Example from {f.name}:\n{self.extract_pdf_text(f, 2)[:1500]}\n"
                for f in exam_files[:2]
            ])
        else:
            format_info = {
                'exercise_count': 5, 'total_points': 30,
                'time_limit': '2 hours', 'question_types': ['solve', 'compute', 'prove']
            }
            exam_examples = ""

        cache = self._load_json(f"analysis_cache_{course_code}.json", {})
        if cache:
            course_content = cache.get('analysis', '')[:3000]
        else:
            course_dir = self.find_course_directory(course_code)
            if course_dir:
                pdfs = list(course_dir.rglob("*.pdf"))[:3]
                course_content = "\n".join([self.extract_pdf_text(pdf, 5)[:2000] for pdf in pdfs])
            else:
                course_content = ""

        prompt = f"""Create a Ca' Foscari University mock exam in ENGLISH using EXACT same format as previous exams.

COURSE: {course.get('name', course_code)}
FORMAT REQUIREMENTS: {format_info['exercise_count']} exercises, {format_info['total_points']} points, {format_info['time_limit']}

PREVIOUS EXAM EXAMPLES (COPY THIS FORMAT EXACTLY):
{exam_examples[:3000]}

COURSE CONTENT:
{course_content}

CRITICAL INSTRUCTIONS:
1. Copy the EXACT structure, layout, and formatting from the examples above
2. Keep the same headers, footers, instructions, and point distributions
3. Keep the same exercise numbering and spacing
4. Only change the actual question content - everything else stays identical
5. Maintain the same difficulty level and question style
6. Use the same mathematical notation and symbols as in examples
7. Write entirely in ENGLISH
8. Make sure each exercise has the same point value as in the original format"""

        messages = [{"role": "user", "content": prompt}]
        exam = self.claude_request(messages, "You are a Ca' Foscari professor creating an authentic exam.")

        if not exam:
            return None

        exam_dir = Path(f"mock_exams/{course_code}")
        exam_dir.mkdir(parents=True, exist_ok=True)

        return self.create_exam_pdf(course_code, course.get('name', course_code), exam, format_info)

    def create_exam_pdf(self, course_code, course_name, content, format_info):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.lib.enums import TA_CENTER

            exam_dir = Path(f"mock_exams/{course_code}")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_path = exam_dir / f"EXAM_{course_code}_{timestamp}.pdf"

            doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
            styles = getSampleStyleSheet()
            story = []

            header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, fontName='Times-Bold', spaceAfter=3)
            story.append(Paragraph("Ca' Foscari University of Venice", header_style))
            story.append(Paragraph(course_name, header_style))
            story.append(Paragraph("Mock Exam", header_style))
            story.append(Spacer(1, 10*mm))

            info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, spaceAfter=15)
            story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", info_style))
            story.append(Paragraph(f"Time: {format_info['time_limit']} | Points: {format_info['total_points']}", info_style))

            story.append(Paragraph("Name: ________________________  ID: ____________", info_style))
            story.append(Spacer(1, 15*mm))

            content_style = ParagraphStyle('Content', parent=styles['Normal'], fontSize=11, spaceAfter=8)
            exercise_style = ParagraphStyle('Exercise', parent=styles['Normal'], fontSize=11, fontName='Times-Bold', spaceAfter=8, spaceBefore=12)

            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 6))
                    continue

                if any(line.lower().startswith(prefix) for prefix in ['exercise', 'problem', 'question']):
                    story.append(Paragraph(line, exercise_style))
                else:
                    story.append(Paragraph(line, content_style))

            doc.build(story)

            metadata = {
                'course_code': course_code,
                'course_name': course_name,
                'timestamp': timestamp,
                'format_info': format_info
            }
            metadata_path = exam_dir / f"EXAM_{course_code}_{timestamp}_metadata.json"
            self._save_json(str(metadata_path), metadata)

            return pdf_path

        except ImportError:
            print("⚠️ Install reportlab: pip install reportlab")
            return None
        except Exception as e:
            return None

    def create_study_plan(self, course_code):
        cache_data = self._load_json(f"analysis_cache_{course_code}.json", None)
        if not cache_data:
            return False

        messages = [{
            "role": "user",
            "content": f"""Create 4-week study plan for {self.courses[course_code].get('name', course_code)}
Based on: {cache_data['analysis'][:2000]}

Include daily objectives, resources, and practice exercises."""
        }]

        plan = self.claude_request(messages)

        plan_dir = Path(f"study_plans/{course_code}")
        plan_dir.mkdir(parents=True, exist_ok=True)
        plan_file = plan_dir / f"PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(plan)

        return plan_file

    def generate_cheat_sheet(self, course_code):
        if course_code not in self.courses:
            return

        course = self.courses[course_code]
        course_dir = self.find_course_directory(course_code)

        if not course_dir:
            return

        pdfs = list(course_dir.rglob("*.pdf"))[:5]
        if not pdfs:
            return

        content = "\n".join([self.extract_pdf_text(pdf)[:3000] for pdf in pdfs])

        messages = [{
            "role": "user",
            "content": f"""Create EXAM CHEAT SHEET (max 5 pages):
{course.get('name', course_code)}
Content: {content[:10000]}

Include:
1. ALL formulas
2. Quick tricks
3. Common mistakes
4. Reference tables

Make it print-ready and exam-optimized."""
        }]

        cheat_sheet = self.claude_request(messages)
        if not cheat_sheet: return

        cs_dir = Path("cheat_sheets")
        cs_dir.mkdir(exist_ok=True)
        cs_file = cs_dir / f"CHEAT_{course_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(cs_file, 'w', encoding='utf-8') as f:
            f.write(cheat_sheet)

        return cs_file


    def cache_email(self, email):
        """Cache email address with timestamp"""
        from datetime import datetime

        if email not in self.email_cache:
            self.email_cache[email] = {
                'first_used': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat(),
                'usage_count': 1
            }
        else:
            self.email_cache[email]['last_used'] = datetime.now().isoformat()
            self.email_cache[email]['usage_count'] += 1

        self._save_json("email_cache.json", self.email_cache)

    def get_cached_emails(self):
        """Get list of cached emails for autocomplete"""
        return list(self.email_cache.keys())

    def get_cached_emails_info(self):
        """Get cached email info for web interface"""
        if not self.email_cache:
            return []

        result = []
        for email, data in self.email_cache.items():
            result.append({
                'email': email,
                'usage_count': data.get('usage_count', 1),
                'last_used': data.get('last_used', 'Unknown')[:10]
            })
        return result

    def send_contact_email(self, user_input, contact_name):
        """Send email to contact by name"""
        to_email = self.contacts[contact_name]

        content = user_input.lower()
        for keyword in ['mail', 'email', 'gönder', 'send']:
            content = content.replace(keyword, '')
        content = content.replace(contact_name.lower(), '').strip()

        if not content:
            content = "merhaba, nasılsın?"

        prompt = f"Write a friendly email in Turkish: {content}"
        messages = [{"role": "user", "content": prompt}]
        email_content = self.claude_request(messages)

        subject = f"📧 {contact_name.title()} için mesaj"

        return self.send_email(to_email, subject, email_content)

    def send_mock_exam_email(self, recipient, course_code, pdf_file):
        """Send mock exam PDF as email attachment"""

        if not self.gmail_service:
            return False

        try:
            import base64
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.application import MIMEApplication

            course_name = self.courses[course_code].get('name', course_code)
            subject = f"Mock Exam - {course_name}"  # Remove emoji from subject
            msg = MIMEMultipart()
            msg['To'] = recipient.strip()  # Capital T for Gmail API
            msg['Subject'] = subject
            msg['From'] = "me"

            simple_body = f"""
Mock Exam - {course_name}

Course: {course_name}
Course Code: {course_code}

Please find your mock exam attached as PDF.
Good luck with your studies!

Generated by Ca' Foscari Ultimate Study System
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """

            msg.attach(MIMEText(simple_body, 'plain'))

            if pdf_file and Path(pdf_file).exists():
                with open(pdf_file, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    pdf_attachment.add_header('Content-Disposition', 'attachment', filename=Path(pdf_file).name)
                    msg.attach(pdf_attachment)

            result = self.gmail_service.users().messages().send(
                userId="me",
                body={'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
            ).execute()

            return True

        except Exception:
            return False

    def get_available_courses(self):
        """Return courses list for web interface"""
        return {code: course.get('name', 'Unknown') for code, course in self.courses.items()}

    def get_system_status(self):
        """Return system status as dict for web interface"""
        creds_path = self.config.get("gmail", {}).get("credentials_file", "api_keys/credentials.json")
        token_path = self.config.get("gmail", {}).get("token_file", "api_keys/gmail_token.json")

        return {
            'courses_count': len(self.courses),
            'claude_api': bool(self.claude_api),
            'moodle_api': bool(self.moodle_token),
            'gmail_enabled': self.gmail_enabled,
            'gmail_service': bool(self.gmail_service),
            'gmail_libs': GMAIL_AVAILABLE,
            'credentials_file': os.path.exists(creds_path),
            'token_file': os.path.exists(token_path)
        }

def main():
    """CLI Interface for Ca' Foscari Ultimate System"""
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║  🎓 CA' FOSCARI ULTIMATE - STUDY ASSISTANT                    ║")
    print("║  Advanced AI-Powered Academic Support System                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    try:
        system = StudyAssistant()

        while True:
            print("\n" + "="*60)
            print("📚 MAIN MENU")
            print("="*60)
            print("1. 🤖 AI Chat Assistant")
            print("2. 📝 Generate Mock Exam")
            print("3. 📅 Create Study Plan")
            print("4. 📊 PDF Analysis")
            print("5. 🔧 System Status")
            print("6. ❌ Exit")
            print("="*60)

            choice = input("\n🎯 Select option (1-6): ").strip()

            if choice == '1':
                print("\n🤖 AI Chat Assistant")
                print("-" * 30)
                while True:
                    user_input = input("\n💬 You: ").strip()
                    if user_input.lower() in ['exit', 'quit', 'back']:
                        break

                    response = system.ai_chat(user_input)
                    print(f"\n🎓 Assistant: {response}")

            elif choice == '2':
                print("\n📝 Mock Exam Generator")
                print("-" * 30)

                # List available courses
                courses = system.courses
                if not courses:
                    print("❌ No courses available")
                    continue

                print("Available courses:")
                for i, (code, course) in enumerate(courses.items(), 1):
                    print(f"{i}. {code} - {course.get('name', 'Unknown')}")

                try:
                    course_idx = int(input("\nSelect course number: ")) - 1
                    course_code = list(courses.keys())[course_idx]

                    pdf_file = system.generate_mock_exam_with_pdf(course_code)
                    if pdf_file:
                        print(f"✅ Mock exam generated: {pdf_file}")

                        send_email = input("📧 Send via email? (y/n): ").lower() == 'y'
                        if send_email:
                            email = input("📧 Enter email address: ").strip()
                            if system.send_mock_exam_email(email, course_code, pdf_file):
                                print("✅ Email sent successfully!")
                            else:
                                print("❌ Failed to send email")
                    else:
                        print("❌ Failed to generate mock exam")

                except (ValueError, IndexError):
                    print("❌ Invalid course selection")

            elif choice == '3':
                print("\n📅 Study Plan Creator")
                print("-" * 30)

                # List available courses
                courses = system.courses
                if not courses:
                    print("❌ No courses available")
                    continue

                print("Available courses:")
                for i, (code, course) in enumerate(courses.items(), 1):
                    print(f"{i}. {code} - {course.get('name', 'Unknown')}")

                try:
                    course_idx = int(input("\nSelect course number: ")) - 1
                    course_code = list(courses.keys())[course_idx]

                    plan_file = system.create_study_plan(course_code)
                    if plan_file:
                        print(f"✅ Study plan created: {plan_file}")
                    else:
                        print("❌ Failed to create study plan")

                except (ValueError, IndexError):
                    print("❌ Invalid course selection")

            elif choice == '4':
                print("\n📊 PDF Analysis")
                print("-" * 30)

                # List available courses
                courses = system.courses
                if not courses:
                    print("❌ No courses available")
                    continue

                print("Available courses:")
                for i, (code, course) in enumerate(courses.items(), 1):
                    print(f"{i}. {code} - {course.get('name', 'Unknown')}")

                try:
                    course_idx = int(input("\nSelect course number: ")) - 1
                    course_code = list(courses.keys())[course_idx]

                    analysis = system.analyze_course_pdfs(course_code)
                    print(f"\n📊 Analysis Results:\n{analysis}")

                except (ValueError, IndexError):
                    print("❌ Invalid course selection")

            elif choice == '5':
                print("\n🔧 System Status")
                print("-" * 30)
                status = system.get_status()

                print(f"📚 Courses loaded: {status['courses_count']}")
                print(f"🤖 Claude API: {'✅ Ready' if status['claude_api'] else '❌ Not configured'}")
                print(f"🌐 Moodle API: {'✅ Connected' if status['moodle_api'] else '❌ Not configured'}")
                print(f"📧 Gmail: {'✅ Ready' if status['gmail_service'] else '❌ Not configured'}")

                if status.get('gmail_libs'):
                    print(f"📧 Gmail Libraries: ✅ Available")
                    print(f"📧 Credentials File: {'✅' if status.get('credentials_file') else '❌'}")
                    print(f"📧 Token File: {'✅' if status.get('token_file') else '❌'}")
                else:
                    print(f"📧 Gmail Libraries: ❌ Not available")

            elif choice == '6':
                print("\n👋 Goodbye!")
                break

            else:
                print("❌ Invalid option. Please select 1-6.")

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ System error: {e}")

if __name__ == "__main__":
    main()
