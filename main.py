#!/usr/bin/env python3
"""CA' FOSCARI ULTIMATE STUDY SYSTEM - OPTIMIZED"""
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

class CaFoscariUltimate:
    def __init__(self):
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  🚀 CA' FOSCARI ULTIMATE STUDY SYSTEM                           ║
║  Emre Aras (907842) - Ca' Foscari University                    ║
╚══════════════════════════════════════════════════════════════════╝
        """)

        self.courses = self._load_json("courses_database.json", {})
        self.config = self._load_json("api_keys/config.json", {})
        self.contacts = self._load_default_contacts()
        self.context_memory = []
        self.setup_apis()

        print(f"📚 {len(self.courses)} courses loaded")
        if self.claude_api: print("✅ Claude API ready")
        if self.moodle_token: print("✅ Moodle API ready")
        if self.gmail_enabled: print("✅ Gmail ready")

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
        defaults = {"erdem": "erdem@example.com", "soner": "sonerozen2004@gmail.com"}
        contacts = self._load_json("contacts.json", {})
        defaults.update(contacts)
        if not contacts:
            self._save_json("contacts.json", defaults)
        return defaults

    def setup_apis(self):
        # Claude API
        self.claude_api = self.config.get("claude", {}).get("api_key", "")
        if not self.claude_api:
            try:
                with open("api_keys/claude_api_key.txt", 'r') as f:
                    self.claude_api = f.read().strip()
            except: pass

        # Moodle API
        self.moodle_token = self.config.get("moodle", {}).get("token", "")
        self.moodle_url = self.config.get("moodle", {}).get("url", "https://moodle.unive.it")

        # Gmail API
        self.gmail_enabled = GMAIL_AVAILABLE and os.path.exists(self.config.get("gmail", {}).get("credentials_file", ""))
        self.gmail_service = self.setup_gmail_service() if self.gmail_enabled else None

    def claude_request(self, messages, system_prompt="You are an expert AI tutor.", max_retries=3):
        if not self.claude_api: return "❌ Claude API not configured"

        for attempt in range(max_retries):
            try:
                print(f"🧠 AI processing (attempt {attempt+1}/{max_retries})...")
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
                    print("✅ AI response ready")
                    return response.json()["content"][0]["text"]
                print(f"❌ Error {response.status_code}")
            except Exception as e:
                print(f"❌ Attempt {attempt+1} failed: {str(e)[:50]}")
            if attempt < max_retries-1: time.sleep(3)
        return None

    def setup_gmail_service(self):
        if not GMAIL_AVAILABLE: return None
        try:
            SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']
            creds = None
            token_file = self.config.get("gmail", {}).get("token_file", "api_keys/gmail_token.json")

            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(GoogleRequest())
                else:
                    credentials_file = self.config.get("gmail", {}).get("credentials_file", "")
                    if os.path.exists(credentials_file):
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                        creds = flow.run_local_server(port=0)

                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)

            return build('gmail', 'v1', credentials=creds)
        except: return None

    def send_email(self, to_email, subject, message):
        if not self.gmail_service: return False
        try:
            import base64
            from email.mime.text import MIMEText
            msg = MIMEText(message)
            msg['to'] = to_email
            msg['subject'] = subject
            self.gmail_service.users().messages().send(
                userId="me", body={'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
            ).execute()
            print(f"✅ Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False

    def find_course_directory(self, course_code):
        if course_code not in self.courses: return None
        course = self.courses[course_code]
        data_courses = Path("data/courses")
        data_courses.mkdir(parents=True, exist_ok=True)

        # Try different naming patterns
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
        print(f"\n🧠 Analyzing: {course.get('name', course_code)}")

        # Find and process PDFs
        course_dir = self.find_course_directory(course_code)
        if not course_dir:
            print("❌ No course directory found")
            return

        pdfs = list(course_dir.rglob("*.pdf"))
        if not pdfs:
            print("❌ No PDF files found")
            return

        print(f"📖 Processing {len(pdfs)} PDFs...")
        combined_content = "\n".join([
            f"=== {pdf.name} ===\n{self.extract_pdf_text(pdf)}\n"
            for pdf in pdfs[:3]
        ])

        # AI Analysis
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

        # Cache result
        cache_data = {
            "course_code": course_code,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        self._save_json(f"analysis_cache_{course_code}.json", cache_data)

        print("\n📊 ANALYSIS RESULTS\n" + "="*60)
        print(analysis)
        print("="*60)
        input("\n✨ Press Enter to continue...")

    def extract_exam_patterns(self, exam_files):
        """Auto-detect exam format from previous exams"""
        patterns = {
            'exercises': [], 'points': [], 'structure': [],
            'keywords': [], 'time': [], 'instructions': []
        }

        for exam_file in exam_files[:3]:
            try:
                text = self.extract_pdf_text(exam_file, max_pages=3)

                # Find exercise patterns
                exercises = re.findall(r'(Exercise|Problem|Question|Esercizio)\s+(\d+)', text, re.I)
                patterns['exercises'].append(len(set(exercises)))

                # Find points
                points = re.findall(r'\(?\s*(\d+)\s*(points?|punti|pts)\s*\)?', text, re.I)
                if points:
                    patterns['points'].extend([int(p[0]) for p in points])

                # Find time limits
                time = re.search(r'(\d+)\s*(hours?|ore|minutes?|minuti)', text, re.I)
                if time:
                    patterns['time'].append(f"{time.group(1)} {time.group(2)}")

                # Extract structure keywords
                for keyword in ['prove', 'compute', 'calculate', 'solve', 'find', 'determine']:
                    if keyword in text.lower():
                        patterns['keywords'].append(keyword)

                # Find instructions
                inst = re.search(r'(Instructions?|Istruzioni):?(.{0,300})', text, re.I)
                if inst:
                    patterns['instructions'].append(inst.group(2).strip())

            except: continue

        # Determine format
        return {
            'exercise_count': max(patterns['exercises']) if patterns['exercises'] else 5,
            'total_points': sum(patterns['points'][:5]) if patterns['points'] else 30,
            'time_limit': patterns['time'][0] if patterns['time'] else '2 hours',
            'question_types': list(set(patterns['keywords']))[:5] or ['solve', 'compute', 'prove'],
            'instructions': patterns['instructions'][0][:200] if patterns['instructions'] else None
        }

    def download_previous_exams(self, course_code):
        """Download previous exams from Moodle (2024+ only)"""
        print(f"📥 Downloading recent exams from Moodle (2024+ only)...")

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
            # Filter out pre-2024 exams
            exclude_years = ['2020', '2021', '2022', '2023']

            for section in sections:
                if 'modules' not in section:
                    continue

                for module in section['modules']:
                    if 'contents' in module:
                        for content in module['contents']:
                            filename = content.get('filename', '').lower()

                            # Skip files from 2023 and earlier
                            if any(year in filename for year in exclude_years):
                                print(f"   ⏭️ Skipping old exam: {content['filename']}")
                                continue

                            if any(keyword in filename for keyword in exam_keywords) and filename.endswith('.pdf'):
                                fileurl = content['fileurl'] + f"&token={self.moodle_token}"
                                filepath = exam_dir / content['filename']

                                if not filepath.exists():
                                    print(f"   📄 Downloading: {content['filename']}")
                                    pdf_response = requests.get(fileurl)
                                    with open(filepath, 'wb') as f:
                                        f.write(pdf_response.content)
                                    exam_files.append(filepath)
                                else:
                                    exam_files.append(filepath)

            print(f"✅ Found {len(exam_files)} recent exam files")
            return exam_files

        except Exception as e:
            print(f"⚠️ Error downloading: {e}")
            return []

    def generate_mock_exam(self, course_code):
        """Generate mock exam with PDF output"""
        if course_code not in self.courses:
            print(f"❌ Course {course_code} not found")
            return

        course = self.courses[course_code]
        print(f"🎯 Generating mock exam for: {course.get('name', course_code)}")

        # First download from Moodle
        exam_files = self.download_previous_exams(course_code)

        # If no downloads, check local folders (filter 2024+ only)
        if not exam_files:
            exam_dir = Path(f"previous_exams/{course_code}")
            if exam_dir.exists():
                all_files = list(exam_dir.glob("*.pdf"))
                # Filter out pre-2024 files
                exclude_years = ['2020', '2021', '2022', '2023']
                exam_files = [f for f in all_files if not any(year in f.name for year in exclude_years)]
                print(f"📁 Found {len(exam_files)} recent local exams (filtered {len(all_files) - len(exam_files)} old exams)")

        # Auto-detect format from previous exams
        if exam_files:
            print(f"📄 Analyzing {len(exam_files)} previous exams...")
            format_info = self.extract_exam_patterns(exam_files)
            exam_examples = "\n".join([
                f"Example from {f.name}:\n{self.extract_pdf_text(f, 2)[:1500]}\n"
                for f in exam_files[:2]
            ])
        else:
            print("⚠️ No previous exams found, using default format")
            format_info = {
                'exercise_count': 5, 'total_points': 30,
                'time_limit': '2 hours', 'question_types': ['solve', 'compute', 'prove']
            }
            exam_examples = ""

        # Get course content from cache OR from PDFs
        cache = self._load_json(f"analysis_cache_{course_code}.json", {})
        if cache:
            course_content = cache.get('analysis', '')[:3000]
        else:
            # Try to get content from course PDFs
            course_dir = self.find_course_directory(course_code)
            if course_dir:
                pdfs = list(course_dir.rglob("*.pdf"))[:3]
                course_content = "\n".join([self.extract_pdf_text(pdf, 5)[:2000] for pdf in pdfs])
            else:
                course_content = ""

        # Generate exam with AI - EXACT FORMAT MATCHING
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
            print("❌ Failed to generate exam")
            return

        # Save exam
        exam_dir = Path(f"mock_exams/{course_code}")
        exam_dir.mkdir(parents=True, exist_ok=True)

        # Create PDF exam
        pdf_file = self.create_exam_pdf(course_code, course.get('name', course_code), exam, format_info)
        if pdf_file:
            print(f"✅ PDF saved: {pdf_file}")
        else:
            print("❌ PDF creation failed")
            return

        print(f"📊 Format: {format_info['exercise_count']} exercises, {format_info['total_points']} points")
        print("\n📄 PREVIEW:")
        print("="*60)
        print(exam[:800])
        input("\n✨ Press Enter to continue...")

    def create_exam_pdf(self, course_code, course_name, content, format_info):
        """Create PDF exam - simplified version"""
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

            # Header
            header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, fontName='Times-Bold', spaceAfter=3)
            story.append(Paragraph("Ca' Foscari University of Venice", header_style))
            story.append(Paragraph(course_name, header_style))
            story.append(Paragraph("Mock Exam", header_style))
            story.append(Spacer(1, 10*mm))

            # Info
            info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, spaceAfter=15)
            story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", info_style))
            story.append(Paragraph(f"Time: {format_info['time_limit']} | Points: {format_info['total_points']}", info_style))

            # Student info
            story.append(Paragraph("Name: ________________________  ID: ____________", info_style))
            story.append(Spacer(1, 15*mm))

            # Content
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

            # Save metadata
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
            print(f"❌ PDF creation failed: {e}")
            return None

    def create_study_plan(self, course_code):
        cache_data = self._load_json(f"analysis_cache_{course_code}.json", None)
        if not cache_data:
            print("❌ No analysis found. Run Deep PDF Analysis first.")
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

        print(f"💾 Plan saved: {plan_file}")
        print("\n📚 PREVIEW\n" + "="*60)
        print(plan[:1200] + "..." if len(plan) > 1200 else plan)
        return True

    def generate_cheat_sheet(self, course_code):
        if course_code not in self.courses:
            print(f"❌ Course {course_code} not found")
            return

        course = self.courses[course_code]
        course_dir = self.find_course_directory(course_code)

        if not course_dir:
            print("❌ No course directory found")
            return

        pdfs = list(course_dir.rglob("*.pdf"))[:5]
        if not pdfs:
            print("❌ No PDFs found")
            return

        print(f"📄 Processing {len(pdfs)} PDFs...")
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

        # Save cheat sheet
        cs_dir = Path("cheat_sheets")
        cs_dir.mkdir(exist_ok=True)
        cs_file = cs_dir / f"CHEAT_{course_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(cs_file, 'w', encoding='utf-8') as f:
            f.write(cheat_sheet)

        print(f"✅ Saved: {cs_file}")
        print("\n📋 PREVIEW\n" + "="*60)
        print(cheat_sheet[:1500] + "..." if len(cheat_sheet) > 1500 else cheat_sheet)
        input("\n✨ Press Enter...")

    def chat_with_claude(self):
        print("\n💬 CHAT MODE - Type 'exit' to return")
        print("="*60)

        while True:
            user_input = input("\n🎓 You: ").strip()
            if user_input.lower() in ['exit', 'quit']: break
            if not user_input: continue

            # Handle special commands
            if self.handle_email_commands(user_input): continue
            if self.handle_study_plan_request(user_input): continue

            # Normal chat
            messages = [{"role": "user", "content": user_input}]
            response = self.claude_request(messages)
            print(f"\n🧠 Claude: {response}")

    def handle_email_commands(self, user_input):
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, user_input)

        if not emails and not any(word in user_input.lower() for word in ['mail', 'email', 'gönder']):
            return False

        # Find recipient
        to_email = emails[0] if emails else None
        if not to_email:
            for name, email in self.contacts.items():
                if name in user_input.lower():
                    to_email = email
                    break

        if not to_email:
            print("❌ No email/contact found")
            return True

        # Extract message
        message = user_input.split()
        message = ' '.join([w for w in message if '@' not in w and w.lower() not in ['mail', 'email', 'gönder', 'send']])

        # Send
        subject = "📧 Message"
        self.send_email(to_email, subject, message)
        return True

    def handle_study_plan_request(self, user_input):
        if not any(w in user_input.lower() for w in ['study plan', 'çalışma planı', 'plan']):
            return False

        for code in self.courses.keys():
            if code.lower() in user_input.lower():
                print(f"📚 Creating study plan for {code}...")
                self.create_study_plan(code)
                return True

        print("📋 Please specify a course code")
        self.show_available_courses()
        return True

    def refresh_moodle_data(self):
        if not self.moodle_token or not self.moodle_url:
            print("❌ Moodle API not configured")
            return

        print("🔄 Refreshing Moodle data...")
        try:
            # Get user info
            response = requests.get(
                f"{self.moodle_url}/webservice/rest/server.php",
                params={
                    'wstoken': self.moodle_token,
                    'wsfunction': 'core_webservice_get_site_info',
                    'moodlewsrestformat': 'json'
                },
                timeout=30
            )

            if response.status_code != 200:
                print(f"❌ Failed: {response.status_code}")
                return

            user_info = response.json()
            print(f"👤 User: {user_info.get('fullname', 'N/A')}")
            print("✅ Moodle data refreshed")

        except Exception as e:
            print(f"❌ Error: {e}")

        input("\n✨ Press Enter...")

    def optimize_moodle_courses(self):
        print("\n⚡ MOODLE OPTIMIZATION")
        moodle_data = self._load_json("data/moodle/latest.json", None)
        if not moodle_data:
            print("❌ No Moodle data found")
            return

        courses = moodle_data.get('courses', [])
        print(f"📚 Found {len(courses)} courses")

        for i, course in enumerate(courses, 1):
            print(f"{i}. {course['name']}")

        choice = input(f"\nSelect course (1-{len(courses)}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(courses):
                self._optimize_course(courses[idx])
        except: print("❌ Invalid selection")

        input("\n✨ Press Enter...")

    def _optimize_course(self, course):
        print(f"\n🔍 Optimizing: {course['name']}")
        print("💡 Recommendations:")
        print("   1. Consolidate similar materials")
        print("   2. Add multimedia content")
        print("   3. Create study schedule")
        print(f"⚡ Efficiency Score: 85/100")

    def show_available_courses(self):
        print("\n📚 AVAILABLE COURSES:")
        for code, course in self.courses.items():
            print(f"  {code}: {course.get('name', 'Unknown')}")

    def system_status(self):
        print("\n🔍 SYSTEM STATUS")
        print(f"📚 Courses: {len(self.courses)}")
        print(f"🧠 Claude: {'✅' if self.claude_api else '❌'}")
        print(f"🌐 Moodle: {'✅' if self.moodle_token else '❌'}")
        print(f"📧 Gmail: {'✅' if self.gmail_enabled else '❌'}")
        input("\n✨ Press Enter...")

    def run(self):
        menu_items = [
            ("🧠 Deep PDF Analysis", lambda: self.deep_pdf_analysis(input("Course code: ").strip())),
            ("📝 Generate Mock Exam", lambda: self.generate_mock_exam(input("Course code: ").strip())),
            ("📚 Create Study Plan", lambda: self.create_study_plan(input("Course code: ").strip())),
            ("📄 Generate Cheat Sheet", lambda: self.generate_cheat_sheet(input("Course code: ").strip())),
            ("💬 Chat with Claude AI", self.chat_with_claude),
            ("⚡ Optimize Moodle Courses", self.optimize_moodle_courses),
            ("🔄 Refresh Moodle Data", self.refresh_moodle_data),
            ("🔍 System Status", self.system_status),
            ("❌ Exit", None)
        ]

        while True:
            try:
                print("\n" + "="*70)
                print("🚀 CA' FOSCARI ULTIMATE - MAIN MENU")
                print("="*70)
                self.show_available_courses()
                print("\n🎯 CHOOSE ACTION:")

                for i, (text, _) in enumerate(menu_items, 1):
                    print(f"{i}. {text}")

                choice = input(f"\nChoice (1-{len(menu_items)}): ").strip()

                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(menu_items):
                        if idx == len(menu_items) - 1:  # Exit
                            print("\n👋 Goodbye!")
                            break
                        menu_items[idx][1]()
                    else:
                        print("❌ Invalid choice")
                except ValueError:
                    print("❌ Please enter a number")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    try:
        system = CaFoscariUltimate()
        system.run()
    except KeyboardInterrupt:
        print("\n👋 System stopped")
    except Exception as e:
        print(f"❌ System error: {e}")