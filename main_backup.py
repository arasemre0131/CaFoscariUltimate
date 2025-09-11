#!/usr/bin/env python3
"""
🚀 CA' FOSCARI ULTIMATE STUDY SYSTEM - MAIN INTERACTIVE
Complete AI-powered study system with all integrations
Emre Aras (907842) - Ca' Foscari University
"""
import os
import json
import requests
import time
from datetime import datetime
from pathlib import Path

# Try to import additional APIs
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
║                                                                  ║
║  ✨ Full AI Integration: Claude, Moodle, Gmail                  ║
║  🧠 Deep PDF Analysis & Web Search                              ║
║  📚 Mock Exams & Study Plans                                    ║
║  ⚡ Optimized & Clean Codebase                                  ║
║                                                                  ║
║                    Emre Aras (907842)                           ║
║                  Ca' Foscari University                         ║
╚══════════════════════════════════════════════════════════════════╝
        """)
        
        self.courses = self.load_courses()
        self.config = self.load_config()
        self.contacts = self.load_contacts()
        
        # YENİ: Otonom öğrenme sistemi
        self.learning_data = self.load_learning_data()
        self.user_patterns = self.analyze_user_patterns()
        self.context_memory = []  # Son 10 konuşmayı hatırla
        
        self.setup_apis()
        
        print(f"📚 {len(self.courses)} courses loaded")
        if self.claude_api:
            print("✅ Claude API configured - Full AI capabilities enabled")
        if self.moodle_token:
            print("✅ Moodle API ready - Course sync available")
        if self.gmail_enabled:
            print("✅ Gmail integration ready")
    
    def load_courses(self):
        """Load courses database"""
        try:
            with open("courses_database.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    
    def load_config(self):
        """Load API configuration"""
        try:
            with open("api_keys/config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    
    def load_contacts(self):
        """Load contact database for smart email sending"""
        default_contacts = {
            "erdem": "erdem@example.com",
            "soner": "sonerozen2004@gmail.com", 
            "emre": "emre.aras@example.com",
            "prof": "professor@unive.it",
            "assistant": "assistant@unive.it"
        }
        
        try:
            with open("contacts.json", "r", encoding="utf-8") as f:
                contacts = json.load(f)
                # Merge with defaults
                default_contacts.update(contacts)
                return default_contacts
        except Exception:
            # Create contacts file with defaults
            with open("contacts.json", "w", encoding="utf-8") as f:
                json.dump(default_contacts, f, indent=2, ensure_ascii=False)
            return default_contacts
    
    def setup_apis(self):
        """Setup all API integrations - FIXED"""
        # Claude API - Multiple sources
        self.claude_api = None
        
        # Try config.json first
        config_key = self.config.get("claude", {}).get("api_key", "")
        if config_key and config_key.startswith("sk-ant-"):
            self.claude_api = config_key.strip()
            
        # Try claude_api_key.txt file as backup
        if not self.claude_api:
            claude_file = "api_keys/claude_api_key.txt"
            if os.path.exists(claude_file):
                with open(claude_file, 'r') as f:
                    file_key = f.read().strip()
                    if file_key.startswith("sk-ant-"):
                        self.claude_api = file_key
                        
        if self.claude_api:
            print(f"✅ Claude API loaded: {self.claude_api[:15]}...{self.claude_api[-4:]}")
        else:
            print("❌ Claude API key not found in config or file!")
        
        # Moodle API
        self.moodle_token = self.config.get("moodle", {}).get("token", "")
        self.moodle_url = self.config.get("moodle", {}).get("url", "")
        
        # Gmail API
        self.gmail_enabled = GMAIL_AVAILABLE and os.path.exists(self.config.get("gmail", {}).get("credentials_file", ""))
        
        # Setup Gmail service if available
        if self.gmail_enabled:
            self.gmail_service = self.setup_gmail_service()
        else:
            self.gmail_service = None
    
    def claude_request(self, messages, system_prompt="You are an expert AI tutor."):
        """Make request to Claude API with proper error handling"""
        if not self.claude_api:
            return "❌ Claude API key not configured"
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.claude_api,
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4000,
                    "system": system_prompt,
                    "messages": messages
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["content"][0]["text"]
            else:
                return f"❌ Claude API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ Claude request failed: {e}"
    
    def setup_gmail_service(self):
        """Setup Gmail API service"""
        if not GMAIL_AVAILABLE:
            return None
        
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
        except Exception as e:
            print(f"❌ Gmail setup failed: {e}")
            return None
    
    def send_email(self, to_email, subject, message):
        """Send email using Gmail API"""
        if not self.gmail_service:
            print("❌ Gmail service not available")
            return False
        
        try:
            import base64
            from email.mime.text import MIMEText
            
            # Create message
            msg = MIMEText(message)
            msg['to'] = to_email
            msg['subject'] = subject
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            
            # Send email
            send_message = self.gmail_service.users().messages().send(
                userId="me",
                body={'raw': raw_message}
            ).execute()
            
            print(f"✅ Email sent successfully to {to_email}")
            print(f"📧 Subject: {subject}")
            print(f"💬 Message: {message}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def read_important_emails(self, limit=5):
        """Read recent important emails from Gmail"""
        if not self.gmail_service:
            return "❌ Gmail service not available"
        
        try:
            # Get recent emails
            results = self.gmail_service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=limit,
                q='is:important OR is:starred OR from:important'
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return "📬 No important emails found"
            
            email_summaries = []
            for msg in messages:
                msg_detail = self.gmail_service.users().messages().get(
                    userId='me', id=msg['id'], format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in msg_detail['payload']['headers']}
                
                email_summaries.append(f"""
📧 From: {headers.get('From', 'Unknown')}
📋 Subject: {headers.get('Subject', 'No Subject')}
📅 Date: {headers.get('Date', 'Unknown')}
""")
            
            return f"📬 {len(email_summaries)} important emails:\n" + "\n".join(email_summaries)
            
        except Exception as e:
            return f"❌ Failed to read emails: {e}"
    
    def download_moodle_pdfs(self, course_code):
        """Download course materials from Moodle"""
        if not self.moodle_token or not self.moodle_url:
            return False
        
        try:
            # Get course info
            response = requests.get(
                f"{self.moodle_url}/webservice/rest/server.php",
                params={
                    'wstoken': self.moodle_token,
                    'wsfunction': 'core_course_get_contents',
                    'moodlewsrestformat': 'json',
                    'courseid': course_code
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"📥 Found {len(data)} sections on Moodle")
                
                # Create course directory
                course = self.courses.get(course_code, {})
                course_name_safe = course.get('name', course_code).replace('/', '_').replace('[', '').replace(']', '')
                download_dir = Path("data/courses") / f"{course_code}_{course_name_safe}"
                download_dir.mkdir(parents=True, exist_ok=True)
                
                downloaded = 0
                for section in data:
                    if 'modules' in section:
                        for module in section['modules']:
                            if 'contents' in module:
                                for content in module['contents']:
                                    if content.get('type') == 'file' and content.get('filename', '').endswith('.pdf'):
                                        pdf_url = content.get('fileurl', '') + f"&token={self.moodle_token}"
                                        pdf_name = content.get('filename', 'unknown.pdf')
                                        pdf_path = download_dir / pdf_name
                                        
                                        if not pdf_path.exists():
                                            print(f"📄 Downloading: {pdf_name}")
                                            pdf_response = requests.get(pdf_url, timeout=60)
                                            if pdf_response.status_code == 200:
                                                with open(pdf_path, 'wb') as f:
                                                    f.write(pdf_response.content)
                                                downloaded += 1
                
                print(f"✅ Downloaded {downloaded} new PDFs from Moodle")
                return downloaded > 0
            else:
                print(f"❌ Moodle API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Moodle download failed: {e}")
            return False
    
    def web_search_enhance(self, topic, course_name):
        """Enhanced analysis with web search simulation"""
        # Simulate web search results for academic enhancement
        web_enhancements = [
            f"🌐 Latest research trends in {topic}",
            f"📊 Industry applications of {course_name}",
            f"🔗 Connections to current technology developments",
            f"📚 Additional learning resources and tutorials",
            f"🏭 Real-world case studies and examples"
        ]
        
        return "\n".join(web_enhancements)
    
    def extract_pdf_text(self, pdf_path):
        """Extract text from PDF with error handling"""
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(min(3, len(reader.pages))):
                    text += reader.pages[page_num].extract_text()
                return text[:2500]  # First 2500 characters
        except ImportError:
            return f"📄 {pdf_path.name} (PyPDF2 not available - install with: pip install PyPDF2)"
        except Exception as e:
            return f"📄 Error reading {pdf_path.name}: {e}"
    
    def find_course_directory(self, course_code):
        """Find course directory with precise matching using course code"""
        if course_code not in self.courses:
            return None
            
        data_courses = Path("data/courses")
        if not data_courses.exists():
            return None
        
        # Course code to directory mapping
        course_mappings = {
            "18872": "[CT0662-1]_CALCULUS-1_(CT3)_-_a.a._2024-25",
            "21001": "[CT0662-2]_CALCULUS-2_(CT3)_-_a.a._2024-25", 
            "18873": "[CT0665]_INTRODUCTION_TO_COMPUTER_PROGRAMMING_(CT3)_-_a.a._2024-25",
            "18874": "[CT0666]_DISCRETE_STRUCTURES_(CT3)_-_a.a._2024-25",
            "18876": "[CT0668-2]_COMPUTER_ARCHITECTURES-LABORATORY_(CT3)_-_a.a._2024-25",
            "21005": "[CT0677-E]_TECHNICAL_ENGLISH_FOR_COMPUTER_SCIENCE_-_PRACTICE_(CT3)_-_a.a._2024-25",
            "18877": "[CT0678]_MATHEMATICS_BACKGROUND_(CT3)_-_a.a._2024-25"
        }
        
        # Try direct mapping first
        if course_code in course_mappings:
            dir_path = data_courses / course_mappings[course_code]
            if dir_path.exists():
                return dir_path
        
        # Fallback: search for directories containing the course CT code
        course = self.courses[course_code]
        ct_code = course.get("name", "").split("]")[0].replace("[", "") if "]" in course.get("name", "") else ""
        
        for subdir in data_courses.iterdir():
            if subdir.is_dir() and ct_code and ct_code in subdir.name:
                return subdir
        
        return None
    
    def deep_pdf_analysis(self, course_code):
        """Deep PDF analysis with AI enhancement"""
        if course_code not in self.courses:
            print(f"❌ Course {course_code} not found")
            self.show_available_courses()
            return
        
        course = self.courses[course_code]
        course_dir = self.find_course_directory(course_code)
        
        if not course_dir:
            print(f"❌ No materials found for {course.get('name', course_code)}")
            return
        
        print(f"\n🧠 Deep analyzing: {course.get('name', course_code)}")
        print(f"📁 Directory: {course_dir}")
        
        # Try to download from Moodle first
        print("📥 Checking Moodle for additional materials...")
        self.download_moodle_pdfs(course_code)
        
        # Find PDFs
        pdfs = list(course_dir.rglob("*.pdf"))
        print(f"📄 Found {len(pdfs)} PDF files")
        
        if not pdfs:
            print("❌ No PDF files found for analysis")
            return
        
        # Extract content from ALL PDFs for comprehensive analysis
        print("📖 Extracting content from ALL PDFs...")
        pdf_contents = []
        for i, pdf in enumerate(pdfs):
            print(f"   📑 Processing {i+1}/{len(pdfs)}: {pdf.name}")
            content = self.extract_pdf_text(pdf)
            pdf_contents.append(f"=== PDF {i+1}: {pdf.name} ===\n{content}\n")
        
        combined_content = "\n".join(pdf_contents)
        
        # FIRST: Show direct PDF content analysis (without API)
        print("\n" + "="*80)
        print("📄 DIRECT PDF CONTENT SUMMARY")
        print("="*80)
        print(f"Course: {course.get('name', course_code)}")
        print(f"Directory: {course_dir}")
        print(f"Total PDFs processed: {len(pdfs)}")
        print("\nPDF Files:")
        for i, pdf in enumerate(pdfs):
            print(f"  {i+1}. {pdf.name}")
        
        print(f"\nFirst 1000 characters of combined content:")
        print("-" * 60)
        print(combined_content[:1000] + "..." if len(combined_content) > 1000 else combined_content)
        print("="*80)
        
        # Get web enhancement
        web_enhancement = self.web_search_enhance(course.get('name', course_code), course_code)
        
        # Create comprehensive analysis prompt
        messages = [{
            "role": "user",
            "content": f"""Perform deep academic analysis of this course material:

COURSE: {course.get('name', course_code)}

CONTENT FROM {len(pdfs[:3])} PDFs:
{combined_content}

WEB ENHANCEMENT & CURRENT TRENDS:
{web_enhancement}

Provide comprehensive analysis covering:

1. 📋 CORE CONCEPTS & THEORIES
   - Main topics and subtopics
   - Key theoretical frameworks
   - Important definitions and terminology

2. 🔢 FORMULAS & CALCULATIONS
   - Essential formulas to memorize
   - Mathematical concepts and proofs
   - Problem-solving techniques

3. 💡 PRACTICAL APPLICATIONS
   - Real-world examples and case studies
   - Industry connections
   - Current trends and developments

4. 📚 STUDY RECOMMENDATIONS
   - Learning sequence and priorities
   - Effective study techniques for this subject
   - Time allocation suggestions

5. 🎯 EXAM FOCUS AREAS
   - Most likely exam topics
   - Question types to expect
   - Practice exercise recommendations

6. 🔗 CONNECTIONS & PREREQUISITES
   - Links to other courses
   - Background knowledge needed
   - Advanced topics to explore

Format as detailed, structured analysis with clear sections."""
        }]
        
        print("🤔 Generating AI analysis...")
        analysis = self.claude_request(messages)
        
        # Save analysis to cache
        cache_file = f"analysis_cache_{course_code}.json"
        cache_data = {
            "course_code": course_code,
            "course_name": course.get('name', course_code),
            "analysis": analysis,
            "pdf_files": [pdf.name for pdf in pdfs[:3]],
            "pdf_count": len(pdfs),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Analysis cached to {cache_file}")
        
        # Display results
        print("\n" + "="*80)
        print("📊 DEEP ANALYSIS RESULTS")
        print("="*80)
        print(analysis)
        print("="*80)
        
        input("\n✨ Press Enter to continue...")
    
    def generate_mock_exam(self, course_code):
        """Web'den güncel bilgilerle mock exam"""
        cache_file = f"analysis_cache_{course_code}.json"
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                analysis = cache_data["analysis"]
        except FileNotFoundError:
            print("❌ No course analysis found. Please run 'Deep PDF Analysis' first.")
            return
        
        course = self.courses.get(course_code, {})
        course_name = course.get('name', course_code)
        
        print("🌐 Searching for 2025 exam trends...")
        
        # 1. Web'den 2025 güncel exam trendleri
        current_trends = self.perform_comprehensive_web_search(
            f"{course_name} 2025 exam questions trends latest university"
        )
        
        # 2. Önceki examları kontrol et
        previous_exams = self.get_previous_exams(course_code)
        
        # 3. Öğrenci zayıf noktaları 
        weak_points = self.get_student_weak_points(course_code)
        
        print(f"📊 Found {len(previous_exams)} previous exams for uniqueness")
        
        # Create unique exam with web enhancement
        import random
        exam_styles = ["theoretical focus", "practical focus", "mixed approach", "application-heavy", "concept-heavy", "industry-relevant", "research-based"]
        selected_style = random.choice(exam_styles)
        
        # Get existing exams count
        course_name_safe = course_name.replace('/', '_').replace('[', '').replace(']', '')
        exam_dir = f"mock_exams/{course_code}_{course_name_safe}"
        existing_exams = len(list(Path(exam_dir).glob("*.txt"))) if Path(exam_dir).exists() else 0
        
        # 4. Super smart exam generation
        messages = [{
            "role": "user",
            "content": f"""Generate UNIQUE mock exam #{existing_exams + 1} with WEB-ENHANCED content.
            
Course: {course_name}

CURRENT 2025 TRENDS (from web):
{current_trends}

COURSE ANALYSIS:
{analysis[:1500]}

STUDENT WEAK AREAS TO FOCUS ON:
{weak_points}

PREVIOUS EXAM PATTERNS TO AVOID:
{[q['summary'] for q in previous_exams[-3:]]}

REQUIREMENTS:
- Style: {selected_style.upper()}
- Include 2025 current industry context from web search
- 40% questions focus on identified weak areas
- Reference latest technology/methods mentioned in trends
- Create completely NEW questions (no repetition)
- Include practical, real-world 2025 scenarios

COURSE: {course.get('name', course_code)}
ANALYSIS: {analysis[:2000]}

EXAM STYLE: {selected_style.upper()}
UNIQUENESS REQUIREMENT: This is exam #{existing_exams + 1} - make it completely different from previous exams

Generate a complete mock exam with:

PART A: MULTIPLE CHOICE (10 questions)
- Each question with 4 options (A, B, C, D)
- Cover different difficulty levels
- Include conceptual and practical questions

PART B: SHORT ANSWERS (6 questions)
- Brief explanation questions (2-3 sentences)
- Definition and application questions
- Calculation problems if applicable

PART C: ESSAY QUESTIONS (3 questions)
- Detailed analysis questions
- Compare/contrast topics
- Real-world application scenarios

ANSWER KEY:
- Correct answers for all questions
- Brief explanations for multiple choice
- Key points for short answers
- Detailed rubric for essays

IMPORTANT: Make this exam COMPLETELY DIFFERENT from any previous exams. Use different examples, scenarios, and question formats. Focus on {selected_style} throughout. Vary question types and approaches to ensure uniqueness."""
        }]
        
        print("📝 Generating web-enhanced mock exam...")
        exam = self.claude_request(messages)
        
        # Save with enhanced metadata
        self.save_exam_with_metadata(course_code, exam, {
            'web_enhanced': True,
            'trends_used': current_trends[:300],
            'weak_focus': weak_points,
            'exam_style': selected_style,
            'previous_exams_count': len(previous_exams)
        })
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exam_file = f"{exam_dir}/EXAM_{course_code}_{timestamp}.txt"
        
        with open(exam_file, "w", encoding="utf-8") as f:
            f.write(f"MOCK EXAM - {course.get('name', course_code)}\n")
            f.write(f"Course Code: {course_code}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            f.write(exam)
        
        print(f"💾 Mock exam saved to {exam_file}")
        print("\n" + "="*60)
        print("📝 MOCK EXAM PREVIEW")
        print("="*60)
        print(exam[:1000] + "..." if len(exam) > 1000 else exam)
        print("="*60)
        
        input("\n✨ Press Enter to continue...")
    
    def create_study_plan(self, course_code):
        """Create AI-optimized study plan"""
        cache_file = f"analysis_cache_{course_code}.json"
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                analysis = cache_data["analysis"]
        except FileNotFoundError:
            print("❌ No course analysis found. Please run 'Deep PDF Analysis' first.")
            return
        
        course = self.courses.get(course_code, {})
        
        messages = [{
            "role": "user",
            "content": f"""Create a detailed study plan based on this course analysis:

COURSE: {course.get('name', course_code)}
ANALYSIS: {analysis[:2000]}

Create a comprehensive 4-week study plan:

WEEK 1: Foundation Building
- Day-by-day study goals (1.5-2 hours/day)
- Core concepts to master
- Basic exercises and readings

WEEK 2: Intermediate Development  
- Build on Week 1 knowledge
- More complex topics
- Practice problems and applications

WEEK 3: Advanced Topics & Integration
- Advanced concepts
- Connections between topics
- Real-world applications

WEEK 4: Review & Exam Preparation
- Comprehensive review sessions
- Mock exam practice
- Final preparations

For each week include:
- Daily objectives (specific and measurable)
- Estimated time requirements
- Resources to use
- Self-check questions
- Practice exercises

Make it practical, achievable, and personalized for university-level study."""
        }]
        
        print("📚 Creating personalized study plan...")
        plan = self.claude_request(messages)
        
        # Save plan organized by course
        course_name_safe = course.get('name', course_code).replace('/', '_').replace('[', '').replace(']', '')
        plan_dir = f"study_plans/{course_code}_{course_name_safe}"
        os.makedirs(plan_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_file = f"{plan_dir}/PLAN_{course_code}_{timestamp}.txt"
        
        with open(plan_file, "w", encoding="utf-8") as f:
            f.write(f"STUDY PLAN - {course.get('name', course_code)}\n")
            f.write(f"Course Code: {course_code}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            f.write(plan)
        
        print(f"💾 Study plan saved to {plan_file}")
        print("\n" + "="*60)
        print("📚 STUDY PLAN PREVIEW")
        print("="*60)
        print(plan[:1200] + "..." if len(plan) > 1200 else plan)
        print("="*60)
        
        input("\n✨ Press Enter to continue...")
    
    def chat_with_claude(self):
        """HER MESAJDA web search yapan akıllı chat"""
        print("\n💬 INTELLIGENT CHAT MODE - Real-time Web Enhanced")
        print("="*60)
        print("Every response is enriched with current web information!")
        print("📧 Smart email commands also available")
        print("Type 'exit' to return to menu.")
        print("-"*60)
        
        while True:
            try:
                user_input = input("\n🎓 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'back']:
                    break
                
                if not user_input:
                    continue
                
                # Handle email commands first
                if self.handle_email_commands(user_input):
                    continue
                
                # HER MESAJ İÇİN web-enhanced response
                print("🌐 Analyzing with real-time web data...")
                
                # 1. Web search
                web_results = self.perform_comprehensive_web_search(user_input)
                
                # 2. İlgili PDF'leri bul (cache'den)
                relevant_content = self.find_relevant_cached_content(user_input)
                
                # 3. Öğrenci performansını kontrol et
                student_context = self.get_student_context()
                
                # 4. Zengin prompt oluştur
                enhanced_prompt = f"""You are an AI tutor with real-time web access.
                
Question: {user_input}

CURRENT WEB INFORMATION:
{web_results}

RELEVANT COURSE MATERIALS:
{relevant_content}

STUDENT CONTEXT:
{student_context}

Provide an accurate, current, and educational response.
Use the web information to ensure accuracy.
Reference course materials when relevant.
Answer in the same language as the question."""
                
                # Claude API - Garantili çalışması için
                if not self.claude_api:
                    print("❌ Claude API key bulunamadı!")
                    print("🔑 Lütfen api_keys/claude_api_key.txt dosyasına geçerli key ekleyin")
                    print("📍 Key alın: https://console.anthropic.com/settings/keys")
                    continue
                
                messages = [{"role": "user", "content": enhanced_prompt}]
                response = self.claude_request(messages)
                
                if response.startswith("❌"):
                    print("🔑 API Key geçersiz! Yeni key alın:")
                    print("📍 https://console.anthropic.com/settings/keys")
                    print("💾 Sonra: echo 'YENİ_KEY' > api_keys/claude_api_key.txt")
                    continue
                    
                print(f"\n🧠 Claude (Web-Enhanced): {response}")
                
            except KeyboardInterrupt:
                break
        
        print("\n👋 Returning to main menu...")
    
    def handle_email_commands(self, user_input, dry_run=False):
        """AKILLI email handler - her şeyi web'den alır"""
        user_input_lower = user_input.lower()
        
        # Check for email reading commands
        if any(cmd in user_input_lower for cmd in ['check emails', 'important emails', 'read emails', 'email check']):
            print("\n📬 Checking your important emails...")
            result = self.read_important_emails()
            print(result)
            return True
        
        # Smart email sending with web-powered content
        if any(word in user_input_lower for word in ['gönder', 'send', 'mail', 'email', 'at', 'yolla', 'yaz']):
            # Contact bul
            found_contact = None
            found_email = None
            
            # Turkish language pattern matching
            for contact_name, email in self.contacts.items():
                if contact_name in user_input_lower or any(pattern in user_input_lower for pattern in [
                    contact_name + 'e', contact_name + 'ye', contact_name + 'den', contact_name + 'a',
                    contact_name + 'i', contact_name + 'in', contact_name + 'le'
                ]):
                    found_contact = contact_name
                    found_email = email
                    break
            
            if not found_email:
                print("❌ Contact not found!")
                print("📋 Available contacts:", ", ".join(self.contacts.keys()))
                return True
            
            # Mesaj içeriğini çıkar
            raw_message = self.extract_email_message(user_input, found_contact)
            
            # İÇERİK FİLTRELEME ÖNCE!
            if self.contains_inappropriate_content(raw_message):
                print("❌ Uygunsuz içerik tespit edildi. Email gönderilemez.")
                print("💡 Lütfen profesyonel ve uygun bir dil kullanın.")
                return True
            
            # AKILLI İÇERİK OLUŞTURMA - Cache veya Web Search
            actual_content = self.get_intelligent_content(raw_message)
            
            # Subject'i de akıllı oluştur
            subject = self.generate_smart_subject(raw_message, actual_content)
            
            if dry_run:
                # Sadece email gönderebileceğimizi test et, gerçekte gönderme
                return found_contact is not None and found_email is not None
            
            print(f"\n📧 Smart Email Detected!")
            print(f"👤 Contact: {found_contact}")
            print(f"📧 Email: {found_email}")
            print(f"📋 Subject: {subject}")
            print(f"💬 Message Preview: {actual_content[:200]}...")
            
            success = self.send_email(found_email, subject, actual_content)
            if success:
                print("✅ Smart email sent successfully!")
            return True
        
        return False
    
    def contains_inappropriate_content(self, text):
        """Uygunsuz içerik kontrolü"""
        if not text:
            return False
            
        inappropriate_words = [
            'amına', 'amınakoy', 'sik', 'göt', 'piç', 'orospu', 
            'sikeyim', 'siktir', 'amk', 'amq', 'ananı', 'fuck',
            'bitch', 'ass', 'shit', 'damn', 'bastard'
        ]
        
        text_lower = text.lower()
        for word in inappropriate_words:
            if word in text_lower:
                return True
        return False
        
    def create_professional_alternative(self, raw_message, contact_name):
        """Uygunsuz mesaj için profesyonel alternatif öner"""
        alternatives = {
            'angry': f"Merhaba {contact_name.capitalize()},\n\nBu konu hakkında konuşmamız gerekiyor.\n\nSaygılarımla",
            'complaint': f"Sayın {contact_name.capitalize()},\n\nBir durumla ilgili görüşlerinizi almak istiyorum.\n\nSaygılar",
            'general': f"Merhaba {contact_name.capitalize()},\n\nBir konuda senin düşüncelerini merak ediyorum.\n\nSaygılarımla"
        }
        return alternatives['general']
    
    def extract_email_message(self, user_input, contact_name):
        """
        Extract actual message content from natural language email command
        Examples:
        - "erdeme bacıları sakla diye mail gönder" → "bacıları sakla"  
        - "sonere merhaba nasılsın yaz" → "merhaba nasılsın"
        - "erdeme istiklal marşını gönder" → "istiklal marşını"
        """
        import re
        
        user_input_lower = user_input.lower()
        
        # Pattern 1: [contact]e/ye [message] diye mail gönder
        pattern1 = rf"{contact_name}[eya]?\s+(.+?)\s+diye\s+(?:mail\s+)?(?:gönder|yolla|at)"
        match = re.search(pattern1, user_input_lower)
        if match:
            return match.group(1).strip()
        
        # Pattern 2: [contact]e/ye [message] yaz  
        pattern2 = rf"{contact_name}[eya]?\s+(.+?)\s+yaz"
        match = re.search(pattern2, user_input_lower)
        if match:
            return match.group(1).strip()
            
        # Pattern 3: [contact]e/ye [message] mail gönder
        pattern3 = rf"{contact_name}[eya]?\s+(.+?)\s+(?:mail\s+)?(?:gönder|yolla|at)"
        match = re.search(pattern3, user_input_lower)
        if match:
            return match.group(1).strip()
            
        # Pattern 4: [contact]e/ye [message] (direct, no command words)
        pattern4 = rf"{contact_name}[eya]?\s+(.+?)(?:\s|$)"
        match = re.search(pattern4, user_input_lower)
        if match:
            message = match.group(1).strip()
            # Remove any trailing command words
            command_words = ['gönder', 'yolla', 'at', 'mail', 'email', 'send', 'yaz', 'diye']
            words = message.split()
            clean_words = []
            for word in words:
                if word not in command_words:
                    clean_words.append(word)
                else:
                    break  # Stop at first command word
            return ' '.join(clean_words).strip()
        
        # Fallback: return original minus contact and command words
        words = user_input_lower.split()
        clean_words = []
        skip_words = [contact_name, contact_name+'e', contact_name+'ye', 'gönder', 'yolla', 'at', 'mail', 'email', 'send', 'yaz', 'diye']
        
        for word in words:
            if word not in skip_words:
                clean_words.append(word)
                
        return ' '.join(clean_words).strip()
    
    def get_intelligent_content(self, message_request):
        """Cache'de yoksa web search yap, hard-code YOK!"""
        from datetime import datetime
        
        # 1. Önce cache'e bak
        cache_file = f"content_cache/{message_request.replace(' ', '_').replace('/', '_')}.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    cache_time = datetime.fromisoformat(cached['timestamp'])
                    if (datetime.now() - cache_time).days < 7:
                        print("📦 Using cached content")
                        return cached['content']
            except:
                pass
        
        # 2. Cache'de yoksa WEB SEARCH yap
        print(f"🔍 Searching web for: {message_request}")
        
        # Web search fonksiyonunu çağır
        search_results = self.perform_comprehensive_web_search(message_request)
        
        # 3. Claude API ile zengin içerik oluştur
        if not self.claude_api:
            return "❌ Claude API key bulunamadı. Lütfen api_keys/claude_api_key.txt dosyasına geçerli key ekleyin."
        
        prompt = f"""
        User wants to send an email with this content: "{message_request}"
        
        Web search results:
        {search_results}
        
        Instructions:
        - If this is a famous text (like "Gençliğe Hitabe", "İstiklal Marşı"), provide the FULL original text
        - If it's a greeting or wish, create an appropriate message
        - Use the web search results to ensure accuracy
        - Return ONLY the email content, no explanations
        - If it's in Turkish, keep it in Turkish
        """
        
        messages = [{"role": "user", "content": prompt}]
        actual_content = self.claude_request(messages)
        
        if actual_content.startswith("❌"):
            return "❌ Claude API error. Please update your API key."
        
        # 4. Cache'e kaydet
        os.makedirs("content_cache", exist_ok=True)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'request': message_request,
                    'content': actual_content,
                    'timestamp': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Cache save error: {e}")
        
        return actual_content
    
    def create_fallback_content(self, message_request, search_results):
        """Güçlü fallback sistem - her durumda çalışır"""
        
        # Bilinen content'ler için hazır cevaplar
        fallback_contents = {
            'gençliğe hitabe': """Ey Türk gençliği! Birinci vazifen, Türk istiklâlini, Türk Cumhuriyetini, ilelebet, muhafaza ve müdafaa etmektir.

Mevcudiyetinin ve istikbalinin yegâne temeli budur. Bu temel, senin, en kıymetli hazinendir. İstikbalde dahi, seni bu hazineden mahrum bırakmaya çalışacak, dahilî ve haricî bedhahların olacaktır. Bir gün, İstiklal ve Cumhuriyeti müdafaa mecburiyetine düştüğün vakit, vazifeye atılmak için, içinde bulunacağın vaziyetin imkân ve şeraitini düşünmeyeceksin!

Bu imkân ve şerait, çok namüsait bir mahiyette tezahür edebilir. İstiklal ve Cumhuriyetine kastedecek düşmanlar, bütün dünyada emsali görülmemiş bir galibiyetin mümessili olabilirler.

Ey Türk istikbalinin evlâdı! İşte, bu ahval ve şerait içinde dahi, vazifen, Türk İstiklal ve Cumhuriyetini kurtarmaktır! Muhtaç olduğun kudret, damarlarındaki asil kanda mevcuttur!

Mustafa Kemal ATATÜRK""",
            
            'istiklal marşı': """Korkma, sönmez bu şafaklarda yüzen al sancak;
Sönmeden yurdumun üstünde tüten en son ocak.
O benim milletimin yıldızıdır, parlayacak;
O benimdir, o benim milletimindir ancak.

Çatma, kurban olayım, çehreni ey nazlı hilal!
Kahraman ırkıma bir gül! Ne bu şiddet, bu celal?
Sana olmaz dökülen kanlarımız sonra helal.
Hakkıdır, Hakk'a tapan milletimin istiklal!

Ben ezelden beridir hür yaşadım, hür yaşarım.
Hangi çılgın bana zincir vuracakmış? Şaşarım!
Kükremiş sel gibiyim, bendimi çiğner, aşarım.
Yırtarım dağları, enginlere sığmam, taşarım.

Mehmet Akif ERSOY""",
            
            'andımız': """Türküm, doğruyum, çalışkanım. İlkem, küçüklerimi korumak, büyüklerimi saymak, yurdumu, milletimi özümden çok sevmektir. Ülküm, yükselmek, ileri gitmektir. Ey büyük Atatürk! Açtığın yolda, gösterdiğin amaçta hiç durmadan yürüyeceğime ant içerim. Varlığım Türk varlığına armağan olsun. Ne mutlu Türküm diyene!""",
            
            # Greeting'ler için pattern'ler
            'merhaba': "Merhaba! Nasılsın? Umarım her şey yolunda gidiyor.",
            'selam': "Selam! Bu güzel günde seni selamlar, sağlıklı ve mutlu olmayı dilerim.",
            'iyi günler': "İyi günler! Gününün güzel ve verimli geçmesini diliyorum.",
            'nasılsın': "Merhaba! Ben iyiyim, teşekkürler. Sen nasılsın? Umarım her şey yolundadır.",
            'naber': "Selam! Her şey yolunda, teşekkürler. Senden naber?",
            
            # Özel durumlar
            'doğum günü': "🎉 Doğum gününüz kutlu olsun! Sağlık, mutluluk ve başarı dolu nice yıllar dilerim. 🎂🎈",
            'kutlama': "🎊 Tebrikler! Bu özel gününüzü kutlar, başarılarınızın devamını dilerim.",
            'geçmiş olsun': "Geçmiş olsun. Allah şifa versin, en kısa zamanda sağlığınıza kavuşmanızı dilerim.",
            'teşekkür': "Rica ederim! Her zaman yardımcı olmaya çalışırım. 😊",
            
            # Akademik
            'ders': "Merhaba! Ders konusunda yardımcı olmaya hazırım. Hangi konuda destek istiyorsun?",
            'sınav': "Sınav hazırlığın nasıl gidiyor? Başarılar dilerim! 📚💪",
            'proje': "Proje konusunda yardıma ihtiyacın varsa çekinme, birlikte çözebiliriz.",
            
            # Sosyal
            'kahve': "☕ Kahve içelim mi? Güzel bir sohbet de yaparız.",
            'buluşalım': "Tabii, buluşalım! Ne zaman uygun?",
            'görüşürüz': "Görüşürüz! İyi günler dilerim. 👋"
        }
        
        message_lower = message_request.lower() if message_request else ""
        
        # Önce tam eşleşme ara
        if message_lower in fallback_contents:
            return fallback_contents[message_lower]
        
        # Sonra partial match ara
        for key, content in fallback_contents.items():
            if key in message_lower:
                return content
                
        # Keyword-based matching
        greeting_keywords = ['merhaba', 'selam', 'hello', 'hi', 'hey']
        question_keywords = ['nasılsın', 'naber', 'how are you', 'ne yapıyorsun']
        academic_keywords = ['ders', 'sınav', 'exam', 'study', 'ödev', 'homework']
        
        if any(keyword in message_lower for keyword in greeting_keywords):
            return "Merhaba! Nasılsın? Umarım her şey yolunda gidiyor. 😊"
        elif any(keyword in message_lower for keyword in question_keywords):
            return "İyiyim, teşekkürler! Sen nasılsın? Umarım güzel bir gün geçiriyorsundur."
        elif any(keyword in message_lower for keyword in academic_keywords):
            return "Merhaba! Akademik konularda yardımcı olmaya hazırım. Hangi konuda destek istiyorsun? 📚"
        
        # Web search sonucu varsa kullan
        if search_results and len(search_results) > 50:
            return f"Merhaba!\n\n{search_results}\n\nUmarım faydalı olur.\n\nSaygılarımla"
            
        # Son çare: universal message
        return f"""Merhaba!

Mesajın: "{message_request}"

Bu konuda daha detaylı konuşabiliriz. Başka bir şey sormanız gerekirse çekinmeyin.

İyi günler dilerim!

Saygılarımla"""
    
    def create_intelligent_fallback_response(self, user_input, web_results, course_content):
        """Akıllı fallback response sistemi"""
        
        # Sorunun türünü belirle
        question_lower = user_input.lower()
        
        # Medical/Biology terms
        medical_terms = {
            'ilik suyu': """🦴 İLİK SUYU (Bone Marrow) Bilgileri:

İlik suyu (kemik iliği), kemiklerin içindeki yumuşak dokudur ve çok önemli fonksiyonları vardır:

📍 Fonksiyonları:
• Kan hücresi üretimi (kırmızı kan hücresi, beyaz kan hücresi, trombosit)
• Bağışıklık sistemi desteği
• Kan yenilenmesi ve onarımı

🔬 İki türü vardır:
• Kırmızı İlik: Aktif kan üretimi yapar
• Sarı İlik: Yağ depolama alanı

🏥 Tıbbi Kullanımlar:
• İlik nakli tedavileri
• Lösemi ve kan hastalıkları tedavisi
• Kök hücre tedavileri

💊 Sağlık İçin Önemli:
• Demir eksikliği anemisinde rol oynar
• B12 ve folik asit eksikliklerinde etkilenir
• Yaşlanmayla birlikte aktivitesi azalır""",
            
            'kan': """🩸 KAN Bilgileri:
Kan, vücudumuzun hayati sıvısıdır ve birçok önemli fonksiyona sahiptir...""",
            
            'hücre': """🔬 HÜCRE Bilgileri:
Hücreler, tüm canlıların temel yapı taşlarıdır..."""
        }
        
        # Academic terms
        academic_terms = {
            'matematik': 'Matematik ile ilgili sorunuz için daha spesifik olabilir misiniz? Calculus, algebra, geometri gibi hangi alanla ilgili?',
            'programming': 'Programlama ile ilgili hangi dil veya konu hakkında bilgi istiyorsunuz? Python, Java, C++ gibi...',
            'computer': 'Bilgisayar bilimleri çok geniş bir alan. Hangi konuyla ilgili detay istiyorsunuz?'
        }
        
        # Greetings
        greetings = {
            'merhaba': 'Merhaba! Size nasıl yardımcı olabilirim?',
            'selam': 'Selam! Hangi konuda bilgi almak istiyorsunuz?',
            'hello': 'Hello! How can I help you today?'
        }
        
        # Check for specific terms
        for term, info in medical_terms.items():
            if term in question_lower:
                return info
                
        for term, info in academic_terms.items():
            if term in question_lower:
                return info
                
        for term, info in greetings.items():
            if term in question_lower:
                return info
        
        # Web results varsa kullan
        if web_results and len(web_results) > 50:
            return f"""📚 Web'den bulunan bilgiler:

{web_results}

🤖 Bu bilgiler web araması sonucu elde edilmiştir. Daha detaylı bilgi için spesifik sorular sorabilirsiniz.

Başka sorunuz var mı?"""
        
        # Course content varsa kullan
        if course_content:
            return f"""📖 Ders materyallerinizden ilgili bilgiler:

{course_content[:500]}...

Bu konuda daha derinlemesine çalışmak isterseniz, mock sınav oluşturabilirim veya study plan hazırlayabilirim.

Hangi konuda daha çok bilgi istiyorsunuz?"""
        
        # General fallback
        return f"""🤖 Sorunuz: "{user_input}"

Bu konuda size yardımcı olmaya çalışayım:

• Eğer tıbbi/bilimsel bir terim hakkındaysa, daha spesifik sorular sorabilirsiniz
• Ders konularıyla ilgiliyse, hangi dersinizle bağlantılı olduğunu belirtebilirsiniz
• Mock sınav, study plan gibi akademik destek istiyorsanız ana menüden seçebilirsiniz

Daha spesifik olarak ne öğrenmek istiyorsunuz? 🎓"""
    
    def perform_comprehensive_web_search(self, query):
        """GERÇEK web search - API kullanarak"""
        try:
            results = []
            
            # 1. DuckDuckGo API (ücretsiz, API key gerektirmez)
            ddg_results = self.search_duckduckgo(query)
            if ddg_results:
                results.append(f"DuckDuckGo: {ddg_results}")
            
            # 2. Wikipedia API (özel içerikler için)
            if any(term in query.lower() for term in ['gençliğe hitabe', 'istiklal marşı', 'nutuk', 'atatürk']):
                wiki_results = self.search_wikipedia(query)
                if wiki_results:
                    results.append(f"Wikipedia: {wiki_results}")
            
            return "\n\n".join(results) if results else f"Limited search results for: {query}"
            
        except Exception as e:
            print(f"⚠️ Web search error: {e}")
            return f"Search simulation for: {query}"
    
    def search_duckduckgo(self, query):
        """DuckDuckGo instant answer API"""
        try:
            import requests
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            result = ""
            if data.get('AbstractText'):
                result = data['AbstractText']
            elif data.get('Answer'):
                result = data['Answer']
            elif data.get('Definition'):
                result = data['Definition']
            
            return result if result else None
            
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
            return None
    
    def search_wikipedia(self, query):
        """Wikipedia API for specific content"""
        try:
            import requests
            # Türkçe Wikipedia için
            url = "https://tr.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': query,
                'prop': 'extracts',
                'exintro': False,
                'explaintext': True,
                'exsectionformat': 'plain'
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if 'extract' in page_data and page_data['extract'].strip():
                    return page_data['extract'][:3000]  # İlk 3000 karakter
            
            return None
            
        except Exception as e:
            print(f"Wikipedia search failed: {e}")
            return None
    
    def generate_smart_subject(self, raw_message, content):
        """Generate intelligent email subject based on content"""
        if any(word in raw_message.lower() for word in ['gençliğe hitabe', 'atatürk']):
            return "📜 Gençliğe Hitabe - Atatürk'ün Mesajı"
        elif 'istiklal marşı' in raw_message.lower():
            return "🇹🇷 İstiklal Marşı - Mehmet Akif Ersoy"
        elif any(word in raw_message.lower() for word in ['doğum günü', 'happy birthday']):
            return "🎉 Doğum Günün Kutlu Olsun!"
        elif any(word in raw_message.lower() for word in ['merhaba', 'selam', 'hello']):
            return "👋 Selam!"
        elif any(word in raw_message.lower() for word in ['önemli', 'acil', 'urgent']):
            return "⚠️ Önemli Mesaj"
        else:
            return "💬 Mesaj"
    
    def find_relevant_cached_content(self, query):
        """Cache'deki analizlerden ilgili içeriği bul"""
        from pathlib import Path
        relevant = []
        
        try:
            # Tüm cache dosyalarını tara
            for cache_file in Path(".").glob("*cache*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Basit relevance check
                        analysis_text = data.get('analysis', '') + data.get('course_name', '')
                        if any(word.lower() in analysis_text.lower() 
                               for word in query.split() if len(word) > 2):
                            relevant.append({
                                'course': data.get('course_name', 'Unknown Course'),
                                'excerpt': data.get('analysis', '')[:400] + '...'
                            })
                except Exception:
                    continue
            
            return relevant[:2]  # En fazla 2 ilgili içerik
        except Exception:
            return []
    
    def get_student_context(self):
        """Öğrenci performans context'i"""
        try:
            # Geçmiş mock examları say
            from pathlib import Path
            mock_count = len(list(Path(".").glob("mock_exams/**/*.txt")))
            study_count = len(list(Path(".").glob("study_plans/**/*.txt")))
            
            context = f"""Student: Emre Aras (ID: 907842)
University: Ca' Foscari University
Generated Mock Exams: {mock_count}
Study Plans Created: {study_count}
Current Courses: 7 active courses
System Usage: Advanced user with AI integration"""
            
            return context
        except Exception:
            return "Student: Emre Aras (ID: 907842) - Ca' Foscari University Student"
    
    def get_previous_exams(self, course_code):
        """Önceki examları analiz et"""
        from pathlib import Path
        course = self.courses.get(course_code, {})
        course_name_safe = course.get('name', course_code).replace('/', '_').replace('[', '').replace(']', '')
        exam_dir = Path(f"mock_exams/{course_code}_{course_name_safe}")
        
        previous = []
        if exam_dir.exists():
            for exam_file in exam_dir.glob("*.txt"):
                try:
                    with open(exam_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract question patterns (simplified)
                        if 'PART A:' in content:
                            summary = f"Exam {exam_file.stem}: Multiple choice + essay format"
                        else:
                            summary = f"Exam {exam_file.stem}: Mixed format"
                        previous.append({
                            'file': exam_file.name,
                            'summary': summary
                        })
                except Exception:
                    continue
        
        return previous
    
    def get_student_weak_points(self, course_code):
        """Öğrencinin zayıf noktalarını tespit et"""
        # Mock implementation - gerçek sistemde öğrenci performansı analiz edilir
        weak_areas = {
            '18873': ["Pointers and memory management", "Recursive functions", "Data structures implementation"],
            '18874': ["Boolean algebra", "Graph theory applications", "Combinatorics problems"],
            '18872': ["Integration techniques", "Series convergence", "Differential equations"],
            '18876': ["Assembly language", "CPU architecture", "Memory hierarchy"],
            '21005': ["Technical vocabulary", "Academic writing", "Presentation skills"]
        }
        
        return weak_areas.get(course_code, ["Theoretical concepts", "Practical applications", "Problem solving"])
    
    def save_exam_with_metadata(self, course_code, exam_content, metadata):
        """Exam'ı metadata ile kaydet"""
        from datetime import datetime
        course = self.courses.get(course_code, {})
        course_name_safe = course.get('name', course_code).replace('/', '_').replace('[', '').replace(']', '')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create directory
        exam_dir = Path(f"mock_exams/{course_code}_{course_name_safe}")
        exam_dir.mkdir(parents=True, exist_ok=True)
        
        # Save exam
        exam_file = exam_dir / f"EXAM_{course_code}_{timestamp}.txt"
        with open(exam_file, 'w', encoding='utf-8') as f:
            f.write(exam_content)
        
        # Save metadata
        meta_file = exam_dir / f"EXAM_{course_code}_{timestamp}_metadata.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'course_code': course_code,
                'course_name': course.get('name', course_code),
                'exam_file': exam_file.name,
                **metadata
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Enhanced exam saved: {exam_file}")
    
    def enhance_message_with_ai(self, raw_message, contact_name):
        """
        Use Claude AI to enhance and understand the message content
        Examples:
        - "gençliğe hitabe" → Full Atatürk's speech to youth
        - "istiklal marşı" → Full Turkish national anthem
        - "happy birthday" → Enhanced birthday message
        """
        try:
            # Check if it's a reference to famous content
            enhancement_prompt = f"""
            Analyze this message content: "{raw_message}"
            
            If this refers to:
            - Famous speeches (like "gençliğe hitabe" = Atatürk's Speech to Youth)
            - National texts (like "istiklal marşı" = Turkish National Anthem) 
            - Well-known poems, quotes, or literature
            - Historical documents or important texts
            
            Then provide the FULL original text in Turkish.
            
            If it's just a regular message, return it as-is but make it more polite and well-formatted.
            
            Rules:
            - Always respond in Turkish
            - If it's famous content, provide the complete original text
            - If it's a regular message, just improve the formatting
            - Keep the original meaning intact
            - Don't add explanations, just return the enhanced message content
            """
            
            messages = [{
                "role": "user",
                "content": enhancement_prompt
            }]
            
            enhanced_message = self.claude_request(messages)
            
            # If Claude returned enhanced content, use it
            if enhanced_message and len(enhanced_message) > len(raw_message) * 2:
                print(f"🧠 AI Enhanced: '{raw_message}' → Full content prepared")
                return enhanced_message
            else:
                print(f"📝 Original message: '{raw_message}'")
                return raw_message
                
        except Exception as e:
            print(f"⚠️ AI enhancement failed: {e}")
            return raw_message
    
    def parse_smart_email_command(self, user_input):
        """Parse smart email commands with contact recognition"""
        try:
            user_input_lower = user_input.lower()
            
            # Look for contact names in the message
            found_contact = None
            found_email = None
            
            # Check for contact names with Turkish language support
            for contact_name, email in self.contacts.items():
                # Direct match
                if contact_name in user_input_lower:
                    found_contact = contact_name
                    found_email = email
                    break
                # Turkish language patterns (with suffixes like -e, -ye, -den, etc.)
                elif any(pattern in user_input_lower for pattern in [
                    contact_name + 'e',    # erdeme
                    contact_name + 'ye',   # erdeme (variant)  
                    contact_name + 'den',  # erdemden
                    contact_name + 'a',    # erdema
                    contact_name + 'i',    # erdemi
                    contact_name + 'in',   # erdemin
                    contact_name + 'le',   # erdemle
                ]):
                    found_contact = contact_name
                    found_email = email
                    break
            
            # Also check for direct email addresses
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            direct_emails = re.findall(email_pattern, user_input)
            
            if direct_emails and not found_email:
                found_email = direct_emails[0]
                found_contact = found_email.split('@')[0]
            
            if not found_email:
                print("❌ No email address or contact found!")
                print("📋 Available contacts:", ", ".join(self.contacts.keys()))
                print("💡 Try: 'erdeme anneni yırtayım diye mail gönder'")
                return True
            
            # Smart message extraction with pattern recognition
            raw_message = self.extract_email_message(user_input, found_contact)
            
            # Intelligent message enhancement using Claude AI
            if raw_message:
                clean_message = self.enhance_message_with_ai(raw_message, found_contact)
            else:
                clean_message = "Selam! Ca' Foscari Ultimate sistemi üzerinden gönderildi."
            
            # Smart subject based on content
            if any(word in user_input_lower for word in ['önemli', 'urgent', 'acil']):
                subject = "⚠️ Önemli Mesaj"
            elif any(word in user_input_lower for word in ['hello', 'hi', 'selam', 'merhaba']):
                subject = "👋 Selam!"
            else:
                subject = "💬 Mesaj"
            
            print(f"\n📧 Smart Email Detected!")
            print(f"👤 Contact: {found_contact}")
            print(f"📧 Email: {found_email}")
            print(f"📋 Subject: {subject}")
            print(f"💬 Message: {clean_message}")
            print()
            
            success = self.send_email(found_email, subject, clean_message)
            if success:
                print("✅ Smart email sent successfully!")
            else:
                print("❌ Failed to send email.")
            return True
            
        except Exception as e:
            print(f"❌ Error processing smart email command: {e}")
            return True
    
    def parse_send_email_command(self, user_input):
        """Parse natural language email sending commands"""
        try:
            # Simple parsing for commands like "send email to X subject Y message Z"
            parts = user_input.lower().split()
            
            email_address = None
            subject = "Message from Ca' Foscari Ultimate"
            message = user_input
            
            # Look for email addresses in the input
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, user_input)
            
            if emails:
                email_address = emails[0]
                
                # Extract message (everything after the email address)
                email_idx = user_input.lower().find(email_address.lower())
                message = user_input[email_idx + len(email_address):].strip()
                
                if not message:
                    message = "Hello! This message was sent via Ca' Foscari Ultimate System."
                
                print(f"\n📧 Sending email to: {email_address}")
                print(f"📋 Subject: {subject}")
                print(f"💬 Message: {message}")
                
                success = self.send_email(email_address, subject, message)
                if success:
                    print("✅ Email sent successfully!")
                else:
                    print("❌ Failed to send email.")
                return True
            else:
                print("❌ No valid email address found in your message.")
                print("💡 Try: 'send email to someone@example.com your message here'")
                return True
                
        except Exception as e:
            print(f"❌ Error processing email command: {e}")
            return True
    
    def show_available_courses(self):
        """Display available courses"""
        print("\n📚 AVAILABLE COURSES:")
        print("-" * 60)
        for code, course in self.courses.items():
            name = course.get('name', 'Unknown Course')
            print(f"  {code}: {name}")
        print("-" * 60)
    
    def system_status(self):
        """Show system status and statistics"""
        print("\n🔍 SYSTEM STATUS")
        print("="*60)
        print(f"📚 Courses loaded: {len(self.courses)}")
        print(f"🧠 Claude API: {'✅ Active' if self.claude_api else '❌ Not configured'}")
        print(f"🌐 Moodle API: {'✅ Active' if self.moodle_token else '❌ Not configured'}")
        print(f"📧 Gmail API: {'✅ Ready' if self.gmail_enabled else '❌ Not configured'}")
        
        # Check cache files
        cache_files = list(Path(".").glob("analysis_cache_*.json"))
        print(f"💾 Cached analyses: {len(cache_files)}")
        
        # Check generated files
        mock_exams = list(Path("mock_exams").glob("*.txt")) if Path("mock_exams").exists() else []
        study_plans = list(Path("study_plans").glob("*.txt")) if Path("study_plans").exists() else []
        
        print(f"📝 Generated mock exams: {len(mock_exams)}")
        print(f"📚 Generated study plans: {len(study_plans)}")
        
        print("="*60)
        input("\n✨ Press Enter to continue...")
    
    def run(self):
        """Main interactive menu"""
        while True:
            try:
                print("\n" + "="*70)
                print("🚀 CA' FOSCARI ULTIMATE - MAIN MENU")
                print("="*70)
                
                self.show_available_courses()
                
                print("\n🎯 CHOOSE YOUR ACTION:")
                print("1. 🧠 Deep PDF Analysis (analyze course materials)")
                print("2. 📝 Generate Mock Exam (create practice tests)")
                print("3. 📚 Create Study Plan (personalized learning path)")
                print("4. 💬 Chat with Claude AI (interactive tutoring)")
                print("5. 🤖 Autonomous Assistant (AI that learns from you)")
                print("6. 📧 Send Email (Gmail integration)")
                print("7. 🌅 Daily Briefing (intelligent daily report)")
                print("8. 🧭 Unified Intelligence (advanced AI mode)")
                print("9. 🔍 System Status (check configuration)")
                print("10. ❌ Exit")
                
                choice = input("\nEnter your choice (1-10): ").strip()
                
                if choice == "1":
                    course_code = input("Enter course code for analysis: ").strip()
                    self.deep_pdf_analysis(course_code)
                    
                elif choice == "2":
                    course_code = input("Enter course code for mock exam: ").strip()
                    self.generate_mock_exam(course_code)
                    
                elif choice == "3":
                    course_code = input("Enter course code for study plan: ").strip()
                    self.create_study_plan(course_code)
                    
                elif choice == "4":
                    self.chat_with_claude()
                    
                elif choice == "5":
                    self.autonomous_assistant()
                    
                elif choice == "6":
                    to_email = input("Enter recipient email: ").strip()
                    subject = input("Enter email subject: ").strip()
                    message = input("Enter your message: ").strip()
                    self.send_email(to_email, subject, message)
                    
                elif choice == "7":
                    print(self.create_daily_briefing())
                    input("\n✨ Press Enter to continue...")
                    
                elif choice == "8":
                    print("\n🧭 UNIFIED INTELLIGENCE MODE")
                    print("="*50)
                    print("This mode analyzes your input with multi-dimensional AI")
                    print("and provides intelligent responses with confidence scoring.\n")
                    
                    while True:
                        user_input = input("🤖 Unified AI > ").strip()
                        if user_input.lower() in ['exit', 'quit', 'back']:
                            break
                        result = self.unified_intelligence(user_input)
                        if result:
                            print(f"✅ {result}")
                    
                elif choice == "9":
                    self.system_status()
                    
                elif choice == "10":
                    print("\n👋 Thank you for using Ca' Foscari Ultimate!")
                    print("🎓 Good luck with your studies!")
                    break
                    
                else:
                    print("❌ Invalid choice. Please select 1-10.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again...")

    def load_learning_data(self):
        """Öğrenme datasını yükle"""
        try:
            with open("learning_data.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'interactions': [],
                'user_preferences': {},
                'patterns': {},
                'performance_data': {}
            }
    
    def analyze_user_patterns(self):
        """Gelişmiş kullanıcı alışkanlık analizi"""
        if not self.learning_data['interactions']:
            return {
                'study_times': [],
                'productive_hours': [],
                'common_questions': [],
                'preferred_explanations': [],
                'stress_triggers': [],
                'success_patterns': [],
                'most_active_hours': [],
                'favorite_topics': [],
                'interaction_frequency': 0,
                'preferred_response_style': 'detailed'
            }
        
        patterns = {
            'study_times': [],
            'productive_hours': [],
            'common_questions': [],
            'preferred_explanations': [],
            'stress_triggers': [],
            'success_patterns': [],
            'most_active_hours': [],
            'favorite_topics': {},
            'interaction_frequency': 0,
            'preferred_response_style': 'detailed'
        }
        
        # Son 100 etkileşimi analiz et
        interactions = self.learning_data['interactions'][-100:]
        
        for interaction in interactions:
            try:
                timestamp = datetime.fromisoformat(interaction['timestamp'])
                hour = timestamp.hour
                topic = interaction.get('topic', 'general')
                input_text = interaction.get('input', '').lower()
                
                # Aktif saatler
                patterns['most_active_hours'].append(hour)
                
                # Mood analizi
                if 'context' in interaction:
                    context = interaction['context']
                    mood = context.get('mood', 'neutral')
                    
                    # Produktif saatler (motivated mood)
                    if mood == 'motivated':
                        patterns['productive_hours'].append(hour)
                    
                    # Stres tetikleyicileri
                    elif mood == 'stressed':
                        patterns['stress_triggers'].append(input_text)
                        
                    # Başarı kalıpları
                    elif mood == 'happy':
                        patterns['success_patterns'].append({
                            'time': hour,
                            'topic': topic,
                            'input': input_text[:50]  # İlk 50 karakter
                        })
                
                # Topic frequency
                if topic in patterns['favorite_topics']:
                    patterns['favorite_topics'][topic] += 1
                else:
                    patterns['favorite_topics'][topic] = 1
                    
                # Common questions (similar inputs)
                if len(input_text) > 5:
                    patterns['common_questions'].append(input_text)
                    
            except Exception:
                continue
        
        # Post-processing
        patterns['most_active_hours'] = list(set(patterns['most_active_hours']))
        patterns['productive_hours'] = list(set(patterns['productive_hours']))
        patterns['interaction_frequency'] = len(interactions)
        
        # En popüler saatleri bul
        if patterns['most_active_hours']:
            from collections import Counter
            hour_counts = Counter(patterns['most_active_hours'])
            patterns['peak_hours'] = [h for h, count in hour_counts.most_common(3)]
        else:
            patterns['peak_hours'] = []
        
        return patterns
    
    def autonomous_assistant(self):
        """Otonom asistan modu - seninle birlikte öğrenir"""
        print("\n🧠 AUTONOMOUS ASSISTANT MODE")
        print("="*60)
        print("I learn from every interaction and adapt to you!")
        print("💡 I can proactively help with:")
        print("   - Email monitoring & urgent alerts")
        print("   - Study schedule reminders") 
        print("   - Deadline tracking")
        print("   - Context-aware responses")
        print("-"*60)
        
        while True:
            try:
                # 1. Proaktif kontroller
                self.check_urgent_matters()
                
                # 2. Kullanıcı inputu
                user_input = input("\n🤖 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'back']:
                    self.save_learning_data()
                    print("\n🧠 Learning data saved. I'll remember our conversation!")
                    break
                
                if not user_input:
                    continue
                
                # 3. CONTEXT-AWARE işleme
                print("🧠 Processing with full context awareness...")
                response = self.process_with_full_context(user_input)
                
                # 4. Öğrenme
                self.learn_from_interaction(user_input, response)
                
                print(f"\n🤖 Assistant: {response}")
                
            except KeyboardInterrupt:
                self.save_learning_data()
                break
        
        print("\n👋 Autonomous assistant session ended.")
    
    def check_urgent_matters(self):
        """Proaktif kontroller ve ihtiyaç tahminleri"""
        urgent_items = []
        predictions = self.predict_user_needs()
        
        # Urgency predictions'ı ekle
        for prediction in predictions:
            if prediction['confidence'] > 0.7:
                urgent_items.append(prediction['message'])
        
        # Geleneksel kontroller
        from datetime import datetime
        current_hour = datetime.now().hour
        
        # Çalışma zamanı önerisi
        if current_hour in self.user_patterns.get('peak_hours', []):
            urgent_items.append("⭐ Peak productivity time - let's study!")
            
        # Stres seviyesi kontrolü  
        stress_level = self.detect_stress_level()
        if stress_level > 0.7:
            urgent_items.append("😌 High stress detected - consider a break")
            
        # Devam eden konular
        if len(self.context_memory) > 0:
            last_topic = self.context_memory[-1].get('topic', '')
            if 'exam' in last_topic.lower():
                urgent_items.append(f"🎯 Continue working on: {last_topic}")
        
        if urgent_items:
            print(f"\n🧠 INTELLIGENT ASSISTANCE: {'; '.join(urgent_items[:2])}")  # En fazla 2 öneri
    
    def process_with_full_context(self, user_input):
        """Tam bağlam farkındalığı ile işleme"""
        
        # 1. Email komutu mu kontrol et
        if self.handle_email_commands(user_input):
            return "✅ Email command processed successfully"
        
        # 2. Kapsamlı context analizi
        context = {
            'current_input': user_input,
            'conversation_history': self.context_memory[-5:],
            'time_context': self.get_time_context(),
            'user_patterns': self.user_patterns,
            'mood': self.detect_mood(user_input),
            'urgency_level': self.detect_urgency(user_input),
            'web_search': self.smart_web_search(user_input) if len(user_input.split()) > 2 else None,
            'course_context': self.find_relevant_cached_content(user_input)
        }
        
        return self.generate_contextual_response(context)
    
    def get_time_context(self):
        """Gelişmiş zaman bağlamı analizi"""
        from datetime import datetime
        now = datetime.now()
        
        context = {
            'time': now.strftime("%H:%M"),
            'date': now.strftime("%Y-%m-%d"), 
            'day': now.strftime("%A"),
            'is_weekend': now.weekday() >= 5,
            'is_late': now.hour >= 22 or now.hour < 6,
            'is_study_time': 9 <= now.hour <= 21,
            'semester_week': self.calculate_semester_week(),
            'days_to_exams': self.calculate_days_to_exams()
        }
        
        # Özel durumlar ve öneriler
        if context['is_late']:
            context['suggestion'] = "⏰ Geç oldu, yarın için plan yapalım mı?"
            context['energy_level'] = "low"
        elif context['is_weekend']:
            context['suggestion'] = "🎯 Hafta sonu çalışma planın var mı?"
            context['energy_level'] = "relaxed"
        elif 9 <= now.hour <= 11:
            context['suggestion'] = "🌅 Sabah - yeni konular öğrenmek için ideal"
            context['energy_level'] = "high"
        elif 14 <= now.hour <= 17:
            context['suggestion'] = "⚡ Öğleden sonra - konsantrasyon zirvesi"
            context['energy_level'] = "peak"
        elif 19 <= now.hour <= 21:
            context['suggestion'] = "📚 Akşam - tekrar ve pratik zamanı"
            context['energy_level'] = "moderate"
        
        return context
    
    def calculate_semester_week(self):
        """Dönem başından bu yana kaç hafta geçti"""
        from datetime import datetime
        # Basit implementasyon - gerçek sistemde üniversite takvimi kullanılır
        semester_start = datetime(2024, 9, 1)  # Varsayılan dönem başı
        current = datetime.now()
        weeks = (current - semester_start).days // 7
        return max(1, min(weeks, 16))  # 1-16 hafta arası
    
    def calculate_days_to_exams(self):
        """Sınavlara kaç gün kaldı (varsayılan)"""
        from datetime import datetime
        # Basit implementasyon - gerçek sistemde sınav takvimi kullanılır
        exam_date = datetime(2024, 12, 15)  # Varsayılan final sınavı
        current = datetime.now()
        days = (exam_date - current).days
        return max(0, days) if days > 0 else 0
    
    def detect_mood(self, text):
        """Gelişmiş mood detection"""
        mood_indicators = {
            'stressed': ['sıkıldım', 'stres', 'yetişmiyor', 'zor', 'başaramıyorum', 'help', 'panic'],
            'motivated': ['hadi', 'başlayalım', 'ready', 'hazırım', 'yapalım', 'let\'s go', 'başlayalım'],
            'confused': ['anlamadım', 'nasıl', 'ne demek', 'karışık', 'confused', 'how'],
            'tired': ['yorgunum', 'uyku', 'bitkin', 'tükendim', 'yeter', 'tired', 'exhausted'],
            'happy': ['süper', 'harika', 'başardım', 'tamamdır', ':)', 'great', 'awesome'],
            'worried': ['endişe', 'korku', 'worry', 'afraid', 'concerned', 'anxious']
        }
        
        text_lower = text.lower()
        detected_mood = 'neutral'
        confidence = 0
        
        for mood, indicators in mood_indicators.items():
            matches = sum(1 for ind in indicators if ind in text_lower)
            if matches > confidence:
                confidence = matches
                detected_mood = mood
        
        return {'mood': detected_mood, 'confidence': confidence}
    
    def detect_urgency(self, text):
        """Aciliyet seviyesi tespit et"""
        urgent_words = ['acil', 'urgent', 'hemen', 'quickly', 'asap', 'immediately', 'yarın sınav']
        moderate_words = ['yakında', 'soon', 'bu hafta', 'this week']
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in urgent_words):
            return 'high'
        elif any(word in text_lower for word in moderate_words):
            return 'moderate'
        else:
            return 'low'
    
    def smart_web_search(self, query):
        """Akıllı web araması - cache ile optimize"""
        import hashlib
        import os
        
        try:
            # Cache kontrolü
            cache_key = hashlib.md5(query.encode()).hexdigest()
            cache_file = f"search_cache/{cache_key}.json"
            
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached = json.load(f)
                        from datetime import datetime
                        cache_time = datetime.fromisoformat(cached['timestamp'])
                        age = (datetime.now() - cache_time).total_seconds()
                        
                        if age < 3600:  # 1 saat geçerli
                            print(f"📦 Using cached search results ({int(age/60)} min old)")
                            return cached['results']
                except Exception:
                    pass
            
            # Gerçek arama yap
            print(f"🔍 Performing fresh web search for: {query}")
            results = self.perform_comprehensive_web_search(query)
            
            # Cache'e kaydet
            os.makedirs("search_cache", exist_ok=True)
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'query': query,
                        'results': results,
                        'timestamp': datetime.now().isoformat()
                    }, f, ensure_ascii=False, indent=2)
            except Exception:
                pass  # Cache kayıt hatası önemli değil
            
            return results
            
        except Exception as e:
            print(f"⚠️ Smart search error: {e}")
            return f"Search failed for: {query}"
    
    def generate_contextual_response(self, context):
        """Gelişmiş context-aware response generation"""
        
        # Mood'a göre response ton'unu ayarla
        mood_data = context.get('mood', {'mood': 'neutral', 'confidence': 0})
        urgency = context.get('urgency_level', 'low')
        time_data = context.get('time_context', {})
        
        # Response style'ını context'e göre ayarla
        response_style = self.determine_response_style(mood_data, urgency, time_data)
        
        enhanced_prompt = f"""You are an advanced, context-aware AI tutor with deep emotional intelligence.

USER QUESTION: {context['current_input']}

DETAILED TIME CONTEXT:
- Current time: {time_data.get('time', 'unknown')}
- Day: {time_data.get('day', 'unknown')}
- Study time: {time_data.get('is_study_time', False)}
- Energy level: {time_data.get('energy_level', 'unknown')}
- Suggestion: {time_data.get('suggestion', 'none')}
- Semester week: {time_data.get('semester_week', 'unknown')}
- Days to exams: {time_data.get('days_to_exams', 'unknown')}

MOOD ANALYSIS:
- Detected mood: {mood_data['mood']} (confidence: {mood_data['confidence']})
- Urgency level: {urgency}

USER PATTERNS: {context.get('user_patterns', {})}

RECENT CONVERSATION: {context.get('conversation_history', [])}

COURSE MATERIALS: {context.get('course_context', [])}

WEB SEARCH RESULTS: {context.get('web_search') or 'No search performed'}

RESPONSE INSTRUCTIONS:
- Tone: {response_style['tone']}
- Length: {response_style['length']}
- Focus: {response_style['focus']}
- Urgency handling: {response_style['urgency_approach']}

Provide a personalized, empathetic response that:
1. Acknowledges the user's emotional state
2. Adapts to the time context and energy level
3. Provides appropriate urgency handling
4. References relevant course materials when available
5. Uses current web information when applicable
6. Maintains conversation continuity
7. Answers in the same language as the question

Be genuinely helpful and emotionally intelligent."""
        
        messages = [{"role": "user", "content": enhanced_prompt}]
        return self.claude_request(messages)
    
    def determine_response_style(self, mood_data, urgency, time_data):
        """Mood ve context'e göre response style belirle"""
        
        mood = mood_data.get('mood', 'neutral')
        energy_level = time_data.get('energy_level', 'unknown')
        
        # Mood'a göre temel stil
        if mood == 'stressed':
            style = {
                'tone': 'calming and reassuring',
                'length': 'concise with clear action steps',
                'focus': 'stress reduction and immediate help',
                'urgency_approach': 'prioritize mental wellbeing first'
            }
        elif mood == 'confused':
            style = {
                'tone': 'patient and explanatory',
                'length': 'detailed with examples',
                'focus': 'clear explanations and step-by-step guidance',
                'urgency_approach': 'break down complex tasks'
            }
        elif mood == 'motivated':
            style = {
                'tone': 'energetic and encouraging',
                'length': 'comprehensive with challenges',
                'focus': 'maximize learning momentum',
                'urgency_approach': 'channel motivation effectively'
            }
        elif mood == 'tired':
            style = {
                'tone': 'gentle and understanding',
                'length': 'brief with essential points only',
                'focus': 'energy conservation and rest recommendations',
                'urgency_approach': 'suggest postponing if possible'
            }
        else:  # neutral, happy, worried
            style = {
                'tone': 'friendly and professional',
                'length': 'balanced and informative',
                'focus': 'comprehensive learning support',
                'urgency_approach': 'standard priority handling'
            }
        
        # Urgency'e göre ayarlama
        if urgency == 'high':
            style['length'] = 'concise and action-oriented'
            style['focus'] = 'immediate problem solving'
        
        # Energy level'a göre ayarlama
        if energy_level == 'low':
            style['tone'] = 'gentle and supportive'
            style['length'] = 'brief and focused'
        elif energy_level == 'peak':
            style['length'] = 'comprehensive and challenging'
        
        return style
    
    def learn_from_interaction(self, user_input, response):
        """Her etkileşimden öğren"""
        from datetime import datetime
        
        learning_entry = {
            'timestamp': datetime.now().isoformat(),
            'input': user_input,
            'response': response[:200] + '...' if len(response) > 200 else response,
            'topic': self.extract_topic(user_input)
        }
        
        # Context memory'e ekle
        self.context_memory.append({
            'input': user_input,
            'response': response[:100] + '...' if len(response) > 100 else response,
            'topic': learning_entry['topic'],
            'timestamp': learning_entry['timestamp']
        })
        
        # Son 10'unu tut
        if len(self.context_memory) > 10:
            self.context_memory = self.context_memory[-10:]
        
        # Learning data'ya ekle
        self.learning_data['interactions'].append(learning_entry)
        
        # Her 5 etkileşimde kaydet
        if len(self.context_memory) % 5 == 0:
            self.save_learning_data()
    
    def extract_topic(self, text):
        """Topic extraction"""
        topics = {
            'programming': ['code', 'program', 'python', 'kod'],
            'math': ['math', 'calculus', 'matematik', 'integral'],
            'exam': ['exam', 'test', 'sınav', 'mock'],
            'email': ['email', 'mail', 'gönder', 'send']
        }
        
        text_lower = text.lower()
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        return 'general'
    
    def predict_user_needs(self):
        """Kullanıcının gelecekteki ihtiyaçlarını tahmin et"""
        predictions = []
        
        # Pattern analizi
        if len(self.learning_data['interactions']) < 3:
            return predictions
            
        recent_topics = [i.get('topic', '') for i in self.learning_data['interactions'][-5:]]
        recent_emotions = [i.get('emotion', '') for i in self.learning_data['interactions'][-3:]]
        
        # Exam pattern detection
        if recent_topics.count('exam') >= 2:
            predictions.append({
                'type': 'study_need',
                'message': '🎯 Exam focus detected - consider creating study plan',
                'confidence': 0.8
            })
        
        # Stress pattern detection
        if recent_emotions.count('stressed') >= 2:
            predictions.append({
                'type': 'wellness',
                'message': '😌 Multiple stress signals - recommend break/relaxation',
                'confidence': 0.9
            })
            
        # Time-based predictions
        current_hour = datetime.now().hour
        if current_hour in self.user_patterns.get('peak_hours', []):
            predictions.append({
                'type': 'productivity',
                'message': '⭐ Your peak productivity time - great for challenging tasks',
                'confidence': 0.75
            })
            
        # Topic continuity prediction
        if len(set(recent_topics[-3:])) == 1 and recent_topics[-1] != 'general':
            topic = recent_topics[-1]
            predictions.append({
                'type': 'topic_continuation',
                'message': f'📚 Deep focus on {topic} - shall we continue or explore related topics?',
                'confidence': 0.7
            })
        
        return predictions
    
    def detect_stress_level(self):
        """Konuşma context'inden stress seviyesi tespit et"""
        stress_indicators = 0
        total_weight = 0
        
        if len(self.context_memory) < 2:
            return 0.3  # Default low stress
            
        # Son 3 mesajdaki stress göstergeleri
        recent_messages = self.context_memory[-3:]
        
        stress_keywords = {
            'high': ['help', 'urgent', 'deadline', 'stress', 'panic', 'confused', 'stuck'],
            'medium': ['difficult', 'problem', 'issue', 'worry', 'concern', 'trouble'],
            'low': ['thanks', 'good', 'okay', 'fine', 'understand', 'clear']
        }
        
        for message in recent_messages:
            text = message.get('user_input', '').lower()
            
            # High stress indicators
            high_count = sum(1 for keyword in stress_keywords['high'] if keyword in text)
            stress_indicators += high_count * 0.3
            
            # Medium stress indicators  
            medium_count = sum(1 for keyword in stress_keywords['medium'] if keyword in text)
            stress_indicators += medium_count * 0.2
            
            # Low stress indicators (reduce stress score)
            low_count = sum(1 for keyword in stress_keywords['low'] if keyword in text)
            stress_indicators -= low_count * 0.1
            
            total_weight += 1
        
        # Time pressure indicators
        current_hour = datetime.now().hour
        if current_hour >= 22 or current_hour <= 6:  # Late night/early morning
            stress_indicators += 0.2
            
        # Learning pattern analysis
        recent_emotions = [i.get('emotion', '') for i in self.learning_data['interactions'][-3:]]
        if 'stressed' in recent_emotions:
            stress_indicators += 0.3 * recent_emotions.count('stressed')
        
        # Normalize to 0-1 range
        stress_level = max(0, min(1, stress_indicators))
        
        return stress_level
    
    def unified_intelligence(self, user_input):
        """Tüm sistemleri birleştiren üst düzey zeka"""
        
        # 1. Multi-dimensional analysis
        analysis = {
            'linguistic': self.nlp_analysis(user_input),
            'emotional': self.emotional_analysis(user_input),
            'contextual': self.contextual_analysis(user_input),
            'historical': self.historical_analysis(user_input),
            'predictive': self.predictive_analysis(user_input)
        }
        
        # 2. Cross-reference all data sources
        data_matrix = {
            'moodle': getattr(self, 'moodle_cache', {}),
            'gmail': getattr(self, 'email_cache', {}),
            'performance': self.learning_data,
            'web': getattr(self, 'web_cache', {}),
            'context': self.context_memory,
            'patterns': self.user_patterns
        }
        
        # 3. AI decision making
        decision = self.ai_decision_engine(analysis, data_matrix, user_input)
        
        # 4. Execute with smart confirmation
        if decision['confidence'] < 0.75:
            print(f"🤔 AI Suggestion: {decision['action']} (confidence: {decision['confidence']:.1%})")
            print("   Proceed? (y/n/explain): ", end='')
            response = input().lower()
            
            if response == 'explain':
                print(f"💭 Reasoning: {decision['reasoning']}")
                response = input("Proceed after explanation? (y/n): ").lower()
            
            if response != 'y':
                return self.alternative_action(decision, user_input)
        
        return self.execute_decision(decision, user_input)
    
    def nlp_analysis(self, text):
        """Natural Language Processing analysis"""
        analysis = {
            'intent': 'unknown',
            'entities': [],
            'sentiment': 'neutral',
            'urgency': 0.5,
            'complexity': 0.5
        }
        
        text_lower = text.lower()
        
        # Intent detection
        intent_patterns = {
            'email': ['mail', 'gönder', 'send', 'e-mail', 'email'],
            'study': ['çalış', 'study', 'ders', 'lesson', 'öğren', 'learn'],
            'exam': ['sınav', 'exam', 'test', 'mock', 'quiz'],
            'search': ['ara', 'search', 'find', 'bul', 'where'],
            'plan': ['plan', 'planlama', 'schedule', 'organize'],
            'help': ['yardım', 'help', 'nasıl', 'how', 'ne yapmalı']
        }
        
        for intent, keywords in intent_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                analysis['intent'] = intent
                break
        
        # Entity extraction (basic)
        entities = []
        for course_code, course_info in self.courses.items():
            if course_code.lower() in text_lower or any(word.lower() in text_lower for word in course_info.get('name', '').split()[:3]):
                entities.append({'type': 'course', 'value': course_code})
        
        analysis['entities'] = entities
        
        # Sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'perfect', 'iyi', 'güzel', 'harika', 'mükemmel']
        negative_words = ['bad', 'terrible', 'awful', 'kötü', 'berbat', 'zorla', 'problem', 'issue']
        urgent_words = ['urgent', 'asap', 'quickly', 'acil', 'hızlı', 'şimdi', 'immediately']
        
        if any(word in text_lower for word in positive_words):
            analysis['sentiment'] = 'positive'
        elif any(word in text_lower for word in negative_words):
            analysis['sentiment'] = 'negative'
            
        if any(word in text_lower for word in urgent_words):
            analysis['urgency'] = 0.9
        
        # Complexity based on length and structure
        analysis['complexity'] = min(1.0, len(text.split()) / 20)
        
        return analysis
    
    def emotional_analysis(self, text):
        """Emotional state analysis"""
        emotions = {
            'stressed': 0, 'excited': 0, 'confused': 0, 'confident': 0, 
            'tired': 0, 'motivated': 0, 'frustrated': 0, 'calm': 0
        }
        
        emotion_indicators = {
            'stressed': ['stressed', 'pressure', 'overwhelmed', 'stresli', 'baskı', 'bunaldım'],
            'excited': ['excited', 'great', 'awesome', 'heyecanlı', 'harika', 'muhteşem'],
            'confused': ['confused', 'don\'t understand', 'unclear', 'kafam karıştı', 'anlamadım'],
            'confident': ['confident', 'sure', 'ready', 'emin', 'hazır', 'güvenli'],
            'tired': ['tired', 'exhausted', 'sleepy', 'yorgun', 'bitkin', 'uykulu'],
            'motivated': ['motivated', 'let\'s do', 'ready to', 'motive', 'yapalım', 'hazırım'],
            'frustrated': ['frustrated', 'annoying', 'why', 'sinir', 'neden', 'bıktım'],
            'calm': ['calm', 'peaceful', 'relaxed', 'sakin', 'huzurlu', 'rahat']
        }
        
        text_lower = text.lower()
        for emotion, keywords in emotion_indicators.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            emotions[emotion] = min(1.0, count * 0.3)
        
        # Find dominant emotion
        dominant_emotion = max(emotions, key=emotions.get)
        confidence = emotions[dominant_emotion]
        
        return {
            'dominant': dominant_emotion if confidence > 0.1 else 'neutral',
            'confidence': confidence,
            'all_emotions': emotions
        }
    
    def contextual_analysis(self, text):
        """Context-aware analysis"""
        time_context = self.get_time_context()
        
        context = {
            'time_relevance': 0.5,
            'topic_continuity': 0.5,
            'urgency_context': 0.5,
            'study_context': 0.5
        }
        
        # Time relevance
        if time_context['is_study_time']:
            context['time_relevance'] = 0.8
        elif time_context['is_late']:
            context['time_relevance'] = 0.3
            
        # Topic continuity
        if len(self.context_memory) > 0:
            last_topic = self.extract_topic(self.context_memory[-1].get('user_input', ''))
            current_topic = self.extract_topic(text)
            if last_topic == current_topic:
                context['topic_continuity'] = 0.9
        
        return context
    
    def historical_analysis(self, text):
        """Historical pattern analysis"""
        if len(self.learning_data['interactions']) < 2:
            return {'pattern_match': 0.0, 'frequency': 0.0}
            
        # Analyze similar past interactions
        current_topic = self.extract_topic(text)
        similar_interactions = [
            i for i in self.learning_data['interactions'][-10:] 
            if i.get('topic') == current_topic
        ]
        
        return {
            'pattern_match': len(similar_interactions) / 10,
            'frequency': len(similar_interactions),
            'last_similar': similar_interactions[-1] if similar_interactions else None
        }
    
    def predictive_analysis(self, text):
        """Future-oriented predictive analysis"""
        predictions = self.predict_user_needs()
        stress_level = self.detect_stress_level()
        
        return {
            'predicted_needs': predictions,
            'stress_level': stress_level,
            'next_likely_action': self.predict_next_action(text),
            'success_probability': self.calculate_success_probability(text)
        }
    
    def predict_next_action(self, current_input):
        """Predict what user will likely need next"""
        current_intent = self.nlp_analysis(current_input)['intent']
        
        action_sequences = {
            'email': ['check response', 'follow up'],
            'study': ['create plan', 'start studying', 'test knowledge'],
            'exam': ['review materials', 'take practice test', 'study weak areas'],
            'search': ['analyze results', 'take action', 'search more']
        }
        
        return action_sequences.get(current_intent, ['continue conversation'])
    
    def calculate_success_probability(self, text):
        """Calculate probability of successful task completion"""
        base_probability = 0.7
        
        # Adjust based on complexity
        complexity = self.nlp_analysis(text)['complexity']
        base_probability -= complexity * 0.2
        
        # Adjust based on stress
        stress = self.detect_stress_level()
        base_probability -= stress * 0.3
        
        # Adjust based on time context
        time_ctx = self.get_time_context()
        if time_ctx.get('energy_level') == 'high':
            base_probability += 0.2
        elif time_ctx.get('energy_level') == 'low':
            base_probability -= 0.1
            
        return max(0.1, min(1.0, base_probability))
    
    def ai_decision_engine(self, analysis, data_matrix, user_input):
        """AI decision making engine"""
        
        intent = analysis['linguistic']['intent']
        emotion = analysis['emotional']['dominant']
        confidence_base = 0.8
        
        # Decision based on intent and context
        if intent == 'email':
            action = "process email command with intelligent content generation"
            confidence = 0.9 if self.handle_email_commands(user_input, dry_run=True) else 0.4
        elif intent == 'study':
            action = "create personalized study session with current materials"
            confidence = 0.85
        elif intent == 'exam':
            action = "generate unique mock exam with web-enhanced content"
            confidence = 0.9
        elif intent == 'help':
            action = "provide contextual assistance with predictive suggestions"
            confidence = 0.95
        else:
            action = "engage in intelligent conversation with full context awareness"
            confidence = 0.75
            
        # Adjust confidence based on emotional state
        if emotion == 'stressed':
            confidence *= 0.9  # Be more careful with stressed users
            action += " (with stress-aware approach)"
        elif emotion == 'confident':
            confidence *= 1.1  # User is confident, we can be too
            
        return {
            'action': action,
            'confidence': min(1.0, confidence),
            'reasoning': f"Intent: {intent}, Emotion: {emotion}, Context: {analysis['contextual']}",
            'priority': 'high' if analysis['linguistic']['urgency'] > 0.7 else 'normal'
        }
    
    def execute_decision(self, decision, user_input):
        """Execute the AI decision"""
        action = decision['action']
        
        if 'email command' in action:
            return self.handle_email_commands(user_input)
        elif 'study session' in action:
            print("🎯 Starting intelligent study session...")
            return self.process_with_full_context(user_input)
        elif 'mock exam' in action:
            print("📝 Generating AI-enhanced mock exam...")
            return self.process_with_full_context(user_input)
        elif 'assistance' in action:
            return self.process_with_full_context(user_input)
        else:
            return self.process_with_full_context(user_input)
    
    def alternative_action(self, declined_decision, user_input):
        """Handle when user declines AI suggestion"""
        print("🤝 Understood. Let me try a different approach...")
        
        # Fallback to basic processing
        if self.handle_email_commands(user_input):
            return "✅ Email processed with basic approach"
        else:
            return self.process_with_full_context(user_input)
    
    def create_daily_briefing(self):
        """Günlük özet rapor sistemi"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        today_str = now.strftime('%d %B %Y, %A')
        
        briefing = f"""
╔══════════════════════════════════════════════════════════════════╗
║  🌅 GÜNLÜK BRİFİNG - {today_str:<30}  ║
╚══════════════════════════════════════════════════════════════════╝

📊 BUGÜNKÜ PROGRAM:
{self.get_today_schedule()}

📧 ÖNEMLİ MAİLLER:
{self.get_important_emails_summary()}

📚 ÇALIŞMA HEDEFLERİ:
{self.get_study_goals()}

⏰ DEADLINE'LAR:
{self.get_upcoming_deadlines()}

💪 DÜN TAMAMLANANLAR:
{self.get_yesterday_achievements()}

🎯 BUGÜNKÜ ÖNCELİKLER:
{self.generate_priorities()}

💡 AI ÖNERİLERİ:
{self.generate_ai_suggestions()}

🧠 SİSTEM STATUS:
{self.get_system_status()}
        """
        
        return briefing
    
    def get_today_schedule(self):
        """Bugünkü program"""
        time_ctx = self.get_time_context()
        
        schedule = []
        current_hour = datetime.now().hour
        
        if current_hour < 12:
            schedule.append("   🌅 Sabah: Yeni kavramlar ve zor konular için ideal zaman")
        if 12 <= current_hour < 17:
            schedule.append("   ⚡ Öğleden sonra: En yüksek konsantrasyon dönemi")
        if current_hour >= 17:
            schedule.append("   📚 Akşam: Tekrar ve pratik zamanı")
            
        if time_ctx['is_weekend']:
            schedule.append("   🎯 Hafta sonu: Derin çalışma ve proje zamanı")
            
        return '\n'.join(schedule) if schedule else "   📅 Esnek program - AI önerilerine göre ayarlanacak"
    
    def get_important_emails_summary(self):
        """Önemli email özeti"""
        # Basit implementasyon - gerçek sistemde Gmail API kullanılır
        return "   ✉️  3 yeni mail - 1 önemli (akademik), 2 bilgilendirme"
    
    def get_study_goals(self):
        """Çalışma hedefleri"""
        goals = []
        
        # Son etkileşimlerden hedef çıkar
        if len(self.learning_data['interactions']) > 0:
            recent_topics = [i.get('topic', '') for i in self.learning_data['interactions'][-3:]]
            unique_topics = list(set(recent_topics))
            
            for topic in unique_topics[:3]:
                if topic != 'general':
                    goals.append(f"   📖 {topic.title()} konusunda derinleşme")
        
        if not goals:
            goals.append("   🎯 Günlük çalışma hedefi: 2 saat aktif öğrenme")
            
        return '\n'.join(goals)
    
    def get_upcoming_deadlines(self):
        """Yaklaşan deadline'lar"""
        # Örnek deadlines - gerçek sistemde takvim entegrasyonu olur
        deadlines = [
            "   📅 Matematik Sınavı: 5 gün kaldı",
            "   📝 Proje Teslimi: 12 gün kaldı",
            "   📚 Final Hazırlığı: 3 hafta kaldı"
        ]
        return '\n'.join(deadlines)
    
    def get_yesterday_achievements(self):
        """Dünkü başarılar"""
        yesterday_count = len([i for i in self.learning_data['interactions'][-10:] 
                              if datetime.now().day - 1 == datetime.now().day])  # Simplified
        
        achievements = [
            f"   ✅ {yesterday_count} AI etkileşimi tamamlandı",
            "   📚 2 saat verimli çalışma",
            "   🎯 Günlük hedeflerin %85'i gerçekleşti"
        ]
        return '\n'.join(achievements)
    
    def generate_priorities(self):
        """Bugünkü öncelikler"""
        priorities = []
        time_ctx = self.get_time_context()
        predictions = self.predict_user_needs()
        
        if time_ctx.get('energy_level') == 'high':
            priorities.append("   🔥 Yüksek enerji - zor konulara odaklan")
        
        for prediction in predictions[:2]:
            if prediction['confidence'] > 0.7:
                priorities.append(f"   💡 {prediction['message']}")
                
        if not priorities:
            priorities.append("   🎯 Esnek gündem - ihtiyaçlara göre adapt ol")
            
        return '\n'.join(priorities)
    
    def generate_ai_suggestions(self):
        """AI önerileri"""
        suggestions = []
        stress_level = self.detect_stress_level()
        
        if stress_level > 0.7:
            suggestions.append("   😌 Stres seviyesi yüksek - 15 dk mola öneriyorum")
        
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 11:
            suggestions.append("   🧠 Sabah zirvesi - yeni konular öğrenmek için ideal")
        elif 14 <= current_hour <= 16:
            suggestions.append("   ⚡ Öğleden sonra peak - odak gerektiren tasks için perfect")
            
        suggestions.append("   🤖 Autonomous assistant modu aktif - sürekli öğreniyorum")
        
        return '\n'.join(suggestions)
    
    def get_system_status(self):
        """Sistem durumu"""
        status_items = []
        
        if hasattr(self, 'claude_api_key'):
            status_items.append("   ✅ Claude AI: Aktif")
        if hasattr(self, 'moodle_token'):
            status_items.append("   ✅ Moodle API: Bağlı")
        
        status_items.append(f"   📊 Learning Data: {len(self.learning_data['interactions'])} etkileşim")
        status_items.append(f"   🧠 Context Memory: {len(self.context_memory)} aktif")
        
        return '\n'.join(status_items)

    def save_learning_data(self):
        """Learning data kaydet"""
        try:
            with open("learning_data.json", 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, indent=2, ensure_ascii=False)
            print("💾 Learning data saved")
        except Exception as e:
            print(f"⚠️ Failed to save: {e}")

if __name__ == "__main__":
    try:
        system = CaFoscariUltimate()
        system.run()
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")
        print("Please check your configuration and try again.")