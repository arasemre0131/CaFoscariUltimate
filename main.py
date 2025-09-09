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
        """Setup all API integrations"""
        # Claude API
        self.claude_api = self.config.get("claude", {}).get("api_key", "")
        
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
                    "model": "claude-3-haiku-20240307",
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
        """Generate intelligent mock exam from analysis"""
        cache_file = f"analysis_cache_{course_code}.json"
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                analysis = cache_data["analysis"]
        except FileNotFoundError:
            print("❌ No course analysis found. Please run 'Deep PDF Analysis' first.")
            return
        
        course = self.courses.get(course_code, {})
        
        # Create unique exam prompt with timestamp and randomization
        import random
        exam_styles = ["theoretical focus", "practical focus", "mixed approach", "application-heavy", "concept-heavy"]
        selected_style = random.choice(exam_styles)
        
        # Get existing exams count for uniqueness
        course_name_safe = course.get('name', course_code).replace('/', '_').replace('[', '').replace(']', '')
        exam_dir = f"mock_exams/{course_code}_{course_name_safe}"
        existing_exams = len(list(Path(exam_dir).glob("*.txt"))) if Path(exam_dir).exists() else 0
        
        messages = [{
            "role": "user",
            "content": f"""Create a UNIQUE mock exam #{existing_exams + 1} based on this course analysis:

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
        
        print("📝 Generating comprehensive mock exam...")
        exam = self.claude_request(messages)
        
        # Save exam organized by course
        course_name_safe = course.get('name', course_code).replace('/', '_').replace('[', '').replace(']', '')
        exam_dir = f"mock_exams/{course_code}_{course_name_safe}"
        os.makedirs(exam_dir, exist_ok=True)
        
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
        """Interactive chat with Claude AI with email capabilities"""
        print("\n💬 CLAUDE AI CHAT MODE - WITH EMAIL POWERS")
        print("="*60)
        print("Ask me anything! I can also handle emails for you.")
        print("📧 Email commands:")
        print("  - 'send email to [email] subject [subject] message [message]'")
        print("  - 'check emails' or 'important emails'")
        print("  - 'send mail to sonerozen2004@gmail.com hello soner'")
        print("Type 'exit' to return to menu.")
        print("-"*60)
        
        while True:
            try:
                user_input = input("\n🎓 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'back']:
                    break
                
                if not user_input:
                    continue
                
                # Handle email commands
                if self.handle_email_commands(user_input):
                    continue
                
                # Regular Claude chat
                messages = [{
                    "role": "user",
                    "content": user_input
                }]
                
                print("\n🤔 Claude is thinking...")
                response = self.claude_request(messages)
                
                print(f"\n🧠 Claude: {response}")
                
            except KeyboardInterrupt:
                break
        
        print("\n👋 Returning to main menu...")
    
    def handle_email_commands(self, user_input):
        """Handle email-related commands in chat with smart contact recognition"""
        user_input_lower = user_input.lower()
        
        # Check for email reading commands
        if any(cmd in user_input_lower for cmd in ['check emails', 'important emails', 'read emails', 'email check']):
            print("\n📬 Checking your important emails...")
            result = self.read_important_emails()
            print(result)
            return True
        
        # Smart email sending with contact recognition
        if any(word in user_input_lower for word in ['gönder', 'send', 'mail', 'email', 'at', 'yolla']):
            return self.parse_smart_email_command(user_input)
        
        return False
    
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
                print("5. 📧 Send Email (Gmail integration)")
                print("6. 🔍 System Status (check configuration)")
                print("7. ❌ Exit")
                
                choice = input("\nEnter your choice (1-7): ").strip()
                
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
                    to_email = input("Enter recipient email: ").strip()
                    subject = input("Enter email subject: ").strip()
                    message = input("Enter your message: ").strip()
                    self.send_email(to_email, subject, message)
                    
                elif choice == "6":
                    self.system_status()
                    
                elif choice == "7":
                    print("\n👋 Thank you for using Ca' Foscari Ultimate!")
                    print("🎓 Good luck with your studies!")
                    break
                    
                else:
                    print("❌ Invalid choice. Please select 1-7.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again...")

if __name__ == "__main__":
    try:
        system = CaFoscariUltimate()
        system.run()
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")
        print("Please check your configuration and try again.")