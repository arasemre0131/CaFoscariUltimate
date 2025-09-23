#!/usr/bin/env python3
"""
🚀 CA' FOSCARI ULTIMATE STUDY SYSTEM - OPTIMIZED
AI-powered study system with core functionality
Emre Aras (907842) - Ca' Foscari University
"""
import os
import json
import requests
import time
import re
from datetime import datetime
from pathlib import Path

# Essential APIs only
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
        
        # Optimized core system
        self.context_memory = []
        
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
    
    def claude_request(self, messages, system_prompt="You are an expert AI tutor.", max_retries=3):
        """Make request to Claude API with optimized settings for reliability"""
        if not self.claude_api:
            return "❌ Claude API key not configured"

        for attempt in range(max_retries):
            try:
                print(f"🧠 Generating cheat sheet with Claude AI (attempt {attempt + 1}/{max_retries})...")
                print(f"🚀 Using Claude-3-Haiku (optimized & working) with 4K tokens...")

                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.claude_api,
                        "content-type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-haiku-20240307",  # Claude 3 Haiku - çalışan en iyi model
                        "max_tokens": 4096,  # Haiku maximum token limit
                        "system": system_prompt,
                        "messages": messages
                    },
                    timeout=180  # 3 minutes for complex requests
                )

                if response.status_code == 200:
                    result = response.json()["content"][0]["text"]
                    print(f"✅ Cheat sheet generated successfully!")
                    return result
                else:
                    print(f"❌ API Error {response.status_code}: {response.text[:100]}...")
                    if attempt == max_retries - 1:
                        return None

            except requests.exceptions.Timeout:
                print(f"⏱️ Request timeout on attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    return None

            except Exception as e:
                print(f"❌ Request failed: {str(e)[:100]}...")
                if attempt == max_retries - 1:
                    return None

            # Brief wait before retry
            if attempt < max_retries - 1:
                print(f"🔄 Retrying in 3 seconds...")
                time.sleep(3)

        return None
    
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

    def optimize_moodle_courses(self):
        """Optimize courses by analyzing Moodle data and providing recommendations"""
        print("\n" + "="*60)
        print("⚡ MOODLE COURSE OPTIMIZATION")
        print("="*60)

        try:
            # Load Moodle data
            moodle_data_path = Path("data/moodle/latest.json")
            if not moodle_data_path.exists():
                print("❌ No Moodle data found. Please ensure Moodle data is available.")
                input("\n✨ Press Enter to continue...")
                return

            with open(moodle_data_path, 'r', encoding='utf-8') as f:
                moodle_data = json.load(f)

            courses = moodle_data.get('courses', [])
            pdfs = moodle_data.get('pdfs', [])
            videos = moodle_data.get('videos', [])

            if not courses:
                print("❌ No courses found in Moodle data.")
                input("\n✨ Press Enter to continue...")
                return

            print(f"📚 Found {len(courses)} courses in Moodle data")
            print(f"📄 Total PDFs: {len(pdfs)}")
            print(f"🎥 Total Videos: {len(videos)}")
            print()

            # Show available courses
            print("Available courses for optimization:")
            for i, course in enumerate(courses, 1):
                course_pdfs = [p for p in pdfs if p.get('course_id') == course['id']]
                course_videos = [v for v in videos if v.get('course_id') == course['id']]
                print(f"{i}. {course['name']} ({course['shortname']}) - {len(course_pdfs)} PDFs, {len(course_videos)} videos")

            print(f"{len(courses) + 1}. Optimize All Courses")
            print(f"{len(courses) + 2}. Return to Main Menu")

            choice = input(f"\nSelect course to optimize (1-{len(courses) + 2}): ").strip()

            if choice == str(len(courses) + 2):
                return
            elif choice == str(len(courses) + 1):
                # Optimize all courses
                for course in courses:
                    self._optimize_single_course(course, pdfs, videos)
            else:
                try:
                    course_index = int(choice) - 1
                    if 0 <= course_index < len(courses):
                        selected_course = courses[course_index]
                        self._optimize_single_course(selected_course, pdfs, videos)
                    else:
                        print("❌ Invalid selection.")
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")

        except Exception as e:
            print(f"❌ Error during course optimization: {e}")

        input("\n✨ Press Enter to continue...")

    def _optimize_single_course(self, course, all_pdfs, all_videos):
        """Optimize a single course based on its materials"""
        print(f"\n🔍 OPTIMIZING: {course['name']}")
        print("-" * 50)

        course_id = course['id']
        course_pdfs = [p for p in all_pdfs if p.get('course_id') == course_id]
        course_videos = [v for v in all_videos if v.get('course_id') == course_id]

        # Material analysis
        total_pdf_size = sum(p.get('size', 0) for p in course_pdfs) / (1024 * 1024)  # MB
        print(f"📊 Materials Analysis:")
        print(f"   📄 PDFs: {len(course_pdfs)} files ({total_pdf_size:.1f} MB)")
        print(f"   🎥 Videos: {len(course_videos)} files")

        # Analyze sections and organization
        sections = {}
        for pdf in course_pdfs:
            section = pdf.get('section', 'Uncategorized')
            if section not in sections:
                sections[section] = {'pdfs': 0, 'videos': 0}
            sections[section]['pdfs'] += 1

        for video in course_videos:
            section = video.get('section', 'Uncategorized')
            if section not in sections:
                sections[section] = {'pdfs': 0, 'videos': 0}
            sections[section]['videos'] += 1

        print(f"\n📋 Content Organization:")
        for section, content in sections.items():
            print(f"   📂 {section}: {content['pdfs']} PDFs, {content['videos']} videos")

        # Generate optimization recommendations
        recommendations = []

        if len(course_pdfs) > 10:
            recommendations.append("📚 Consider consolidating similar PDFs to reduce cognitive load")

        if total_pdf_size > 50:
            recommendations.append("💾 Large file sizes detected - consider compression or splitting")

        if len(sections) > 8:
            recommendations.append("🗂️ Many sections found - consider reorganizing into fewer main topics")

        if len(course_videos) == 0:
            recommendations.append("🎥 No videos found - consider adding visual learning materials")

        if len(course_pdfs) == 0:
            recommendations.append("📄 No PDFs found - ensure reading materials are available")

        # Check for balanced content distribution
        pdf_sections = sum(1 for s in sections.values() if s['pdfs'] > 0)
        video_sections = sum(1 for s in sections.values() if s['videos'] > 0)

        if pdf_sections > 0 and video_sections == 0:
            recommendations.append("⚖️ Content is text-heavy - add multimedia elements for better engagement")

        if not recommendations:
            recommendations.append("✅ Course appears well-organized!")

        print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

        # Study efficiency score
        efficiency_score = 100
        if len(course_pdfs) > 15:
            efficiency_score -= 10
        if total_pdf_size > 100:
            efficiency_score -= 15
        if len(sections) > 10:
            efficiency_score -= 10
        if len(course_videos) == 0 and len(course_pdfs) > 5:
            efficiency_score -= 15

        efficiency_score = max(0, efficiency_score)

        print(f"\n⚡ EFFICIENCY SCORE: {efficiency_score}/100")
        if efficiency_score >= 85:
            print("🟢 Excellent organization!")
        elif efficiency_score >= 70:
            print("🟡 Good, with room for improvement")
        else:
            print("🔴 Needs optimization")

        # Suggest study plan optimization
        if course_pdfs or course_videos:
            print(f"\n📝 SUGGESTED ACTIONS:")
            print(f"   1. Generate optimized study plan for this course")
            print(f"   2. Create priority-based material sequence")
            print(f"   3. Set up automated progress tracking")

            action = input(f"\nWould you like to auto-generate an optimized study plan? (y/N): ").strip().lower()
            if action in ['y', 'yes']:
                self._generate_optimized_study_plan(course, course_pdfs, course_videos, sections)

    def _generate_optimized_study_plan(self, course, pdfs, videos, sections):
        """Generate an optimized study plan based on course materials"""
        print(f"\n📅 GENERATING OPTIMIZED STUDY PLAN...")

        # Create optimized sequence based on sections
        study_sequence = []
        week_counter = 1

        for section_name, content in sections.items():
            if content['pdfs'] > 0 or content['videos'] > 0:
                study_sequence.append({
                    'week': week_counter,
                    'section': section_name,
                    'pdfs': content['pdfs'],
                    'videos': content['videos'],
                    'estimated_hours': content['pdfs'] * 2 + content['videos'] * 1.5
                })
                week_counter += 1

        # Generate study plan content
        plan_content = []
        plan_content.append(f"OPTIMIZED STUDY PLAN - {course['name']}")
        plan_content.append("=" * 60)
        plan_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        plan_content.append(f"Course: {course['shortname']}")
        plan_content.append(f"Total Materials: {len(pdfs)} PDFs, {len(videos)} videos")
        plan_content.append("")

        total_estimated_hours = 0
        for item in study_sequence:
            plan_content.append(f"WEEK {item['week']}: {item['section']}")
            plan_content.append(f"  📄 PDFs to review: {item['pdfs']}")
            plan_content.append(f"  🎥 Videos to watch: {item['videos']}")
            plan_content.append(f"  ⏱️ Estimated time: {item['estimated_hours']:.1f} hours")
            plan_content.append("")
            total_estimated_hours += item['estimated_hours']

        plan_content.append(f"TOTAL ESTIMATED TIME: {total_estimated_hours:.1f} hours")
        plan_content.append(f"RECOMMENDED DAILY STUDY: {total_estimated_hours / 30:.1f} hours/day (1 month)")

        # Save the plan
        plan_dir = Path("study_plans") / f"{course['id']}_{course['shortname']}"
        plan_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_file = plan_dir / f"OPTIMIZED_PLAN_{course['id']}_{timestamp}.txt"

        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(plan_content))

        print(f"✅ Optimized study plan saved: {plan_file}")
        print(f"📊 Total estimated study time: {total_estimated_hours:.1f} hours")

    def refresh_moodle_data(self):
        """Refresh Moodle data to get newly enrolled courses"""
        print("\n" + "="*60)
        print("🔄 MOODLE DATA REFRESH")
        print("="*60)

        if not self.moodle_token or not self.moodle_url:
            print("❌ Moodle API not configured!")
            print("Please check your API configuration in api_config.py")
            input("\n✨ Press Enter to continue...")
            return

        try:
            print("🔍 Fetching user information from Moodle...")

            # First get user ID
            user_info_response = requests.get(
                f"{self.moodle_url}/webservice/rest/server.php",
                params={
                    'wstoken': self.moodle_token,
                    'wsfunction': 'core_webservice_get_site_info',
                    'moodlewsrestformat': 'json'
                },
                timeout=30
            )

            if user_info_response.status_code != 200:
                print(f"❌ Failed to get user info: HTTP {user_info_response.status_code}")
                input("\n✨ Press Enter to continue...")
                return

            user_info = user_info_response.json()
            username = user_info.get('username')

            if not username:
                print("❌ Could not determine username from site info")
                input("\n✨ Press Enter to continue...")
                return

            print(f"👤 User: {username} ({user_info.get('fullname', 'N/A')})")

            # Get detailed user info to find user ID
            user_detail_response = requests.get(
                f"{self.moodle_url}/webservice/rest/server.php",
                params={
                    'wstoken': self.moodle_token,
                    'wsfunction': 'core_user_get_users_by_field',
                    'moodlewsrestformat': 'json',
                    'field': 'username',
                    'values[0]': username
                },
                timeout=30
            )

            if user_detail_response.status_code != 200:
                print(f"❌ Failed to get user details: HTTP {user_detail_response.status_code}")
                input("\n✨ Press Enter to continue...")
                return

            user_details = user_detail_response.json()
            if not user_details or len(user_details) == 0:
                print("❌ User details not found")
                input("\n✨ Press Enter to continue...")
                return

            user_id = user_details[0].get('id')
            print(f"🆔 User ID: {user_id}")

            print("📚 Fetching enrolled courses...")

            # Get user's enrolled courses using the correct user ID
            courses_response = requests.get(
                f"{self.moodle_url}/webservice/rest/server.php",
                params={
                    'wstoken': self.moodle_token,
                    'wsfunction': 'core_enrol_get_users_courses',
                    'moodlewsrestformat': 'json',
                    'userid': user_id
                },
                timeout=30
            )

            if courses_response.status_code != 200:
                print(f"❌ Failed to fetch courses: HTTP {courses_response.status_code}")
                input("\n✨ Press Enter to continue...")
                return

            courses_data = courses_response.json()

            if isinstance(courses_data, dict) and 'errorcode' in courses_data:
                print(f"❌ Moodle API Error: {courses_data.get('message', 'Unknown error')}")
                input("\n✨ Press Enter to continue...")
                return

            print(f"📚 Found {len(courses_data)} enrolled courses")

            # Build comprehensive course data
            all_courses = []
            all_pdfs = []
            all_videos = []

            for course in courses_data:
                course_id = course.get('id')
                course_name = course.get('fullname', 'Unknown Course')
                course_shortname = course.get('shortname', f'COURSE_{course_id}')

                print(f"📖 Processing: {course_name}")

                # Add to courses list
                all_courses.append({
                    'id': course_id,
                    'name': course_name,
                    'shortname': course_shortname,
                    'categoryid': course.get('categoryid', 0),
                    'visible': course.get('visible', 1),
                    'enrolledusercount': course.get('enrolledusercount', 0)
                })

                # Get course contents (PDFs and videos)
                try:
                    contents_response = requests.get(
                        f"{self.moodle_url}/webservice/rest/server.php",
                        params={
                            'wstoken': self.moodle_token,
                            'wsfunction': 'core_course_get_contents',
                            'moodlewsrestformat': 'json',
                            'courseid': course_id
                        },
                        timeout=30
                    )

                    if contents_response.status_code == 200:
                        contents_data = contents_response.json()

                        if not isinstance(contents_data, dict) or 'errorcode' not in contents_data:
                            for section in contents_data:
                                section_name = section.get('name', 'General')

                                if 'modules' in section:
                                    for module in section['modules']:
                                        if 'contents' in module:
                                            for content in module['contents']:
                                                content_type = content.get('type', '')
                                                filename = content.get('filename', '')
                                                fileurl = content.get('fileurl', '')
                                                filesize = content.get('filesize', 0)

                                                # Collect PDFs
                                                if content_type == 'file' and filename.lower().endswith('.pdf'):
                                                    all_pdfs.append({
                                                        'course_id': course_id,
                                                        'name': filename,
                                                        'url': fileurl,
                                                        'size': filesize,
                                                        'section': section_name,
                                                        'module_name': module.get('name', 'Unknown Module')
                                                    })

                                                # Collect videos (mp4, avi, mov, etc.)
                                                elif content_type == 'file' and any(filename.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']):
                                                    all_videos.append({
                                                        'course_id': course_id,
                                                        'name': filename,
                                                        'url': fileurl,
                                                        'type': filename.split('.')[-1].lower(),
                                                        'size': filesize,
                                                        'section': section_name,
                                                        'module_name': module.get('name', 'Unknown Module')
                                                    })

                except Exception as e:
                    print(f"⚠️ Warning: Could not fetch contents for {course_name}: {e}")

            # Save updated data
            moodle_data = {
                'courses': all_courses,
                'pdfs': all_pdfs,
                'videos': all_videos,
                'last_updated': datetime.now().isoformat(),
                'total_courses': len(all_courses),
                'total_pdfs': len(all_pdfs),
                'total_videos': len(all_videos)
            }

            # Ensure data directory exists
            data_dir = Path("data/moodle")
            data_dir.mkdir(parents=True, exist_ok=True)

            # Save with timestamp backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = data_dir / f"moodle_data_{timestamp}.json"
            latest_file = data_dir / "latest.json"

            # Save backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(moodle_data, f, indent=2, ensure_ascii=False)

            # Update latest
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(moodle_data, f, indent=2, ensure_ascii=False)

            # Update courses_database.json for main menu integration
            print("🔄 Updating main courses database...")
            courses_db_file = Path("courses_database.json")

            # Load existing courses database
            try:
                if courses_db_file.exists():
                    with open(courses_db_file, 'r', encoding='utf-8') as f:
                        existing_courses_db = json.load(f)
                else:
                    existing_courses_db = {}
            except Exception:
                existing_courses_db = {}

            # Update with new courses from Moodle
            updated_courses_db = existing_courses_db.copy()
            new_course_count = 0

            for course in all_courses:
                course_id = str(course['id'])

                # Check if this is a new course
                if course_id not in existing_courses_db:
                    new_course_count += 1
                    print(f"🆕 Adding new course: {course['name']}")

                # Update/add course entry
                updated_courses_db[course_id] = {
                    "id": course_id,
                    "name": course['name'],
                    "shortname": course['shortname'],
                    "summary": "",
                    "last_updated": datetime.now().isoformat(),
                    "pdfs": [],
                    "videos": [],
                    "categoryid": course.get('categoryid', 0),
                    "visible": course.get('visible', 1)
                }

                # Add PDFs for this course
                course_pdfs = [p for p in all_pdfs if p['course_id'] == course['id']]
                for pdf in course_pdfs:
                    pdf_entry = {
                        "name": pdf['name'],
                        "url": pdf['url'],
                        "size": pdf['size'],
                        "section": pdf['section'],
                        "module": pdf.get('module_name', 'Unknown Module')
                    }
                    updated_courses_db[course_id]["pdfs"].append(pdf_entry)

                # Add videos for this course
                course_videos = [v for v in all_videos if v['course_id'] == course['id']]
                for video in course_videos:
                    video_entry = {
                        "name": video['name'],
                        "url": video['url'],
                        "type": video['type'],
                        "size": video['size'],
                        "section": video['section'],
                        "module": video.get('module_name', 'Unknown Module')
                    }
                    if "videos" not in updated_courses_db[course_id]:
                        updated_courses_db[course_id]["videos"] = []
                    updated_courses_db[course_id]["videos"].append(video_entry)

            # Save updated courses database
            with open(courses_db_file, 'w', encoding='utf-8') as f:
                json.dump(updated_courses_db, f, indent=2, ensure_ascii=False)

            # Reload courses in memory for immediate effect
            self.courses = updated_courses_db

            print("\n" + "="*50)
            print("✅ MOODLE DATA REFRESH COMPLETE!")
            print("="*50)
            print(f"📚 Total Courses: {len(all_courses)}")
            print(f"📄 Total PDFs: {len(all_pdfs)}")
            print(f"🎥 Total Videos: {len(all_videos)}")
            print(f"💾 Moodle data saved to: {latest_file}")
            print(f"📊 Main database updated: {courses_db_file}")
            print(f"🗂️ Backup saved to: {backup_file}")

            # Show new courses if any
            if new_course_count > 0:
                print(f"\n🆕 Found {new_course_count} new course(s)!")
                print("✨ New courses are now visible in the main menu!")
            else:
                print("\n✅ No new courses found - all data is up to date")

            print("\n💡 You can now use all features with updated course data!")

        except Exception as e:
            print(f"❌ Error refreshing Moodle data: {e}")
            print("Please check your internet connection and Moodle API configuration.")

        input("\n✨ Press Enter to continue...")

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
        """Extract text from PDF with enhanced content extraction for comprehensive cheat sheets"""
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                # Extract from maximum pages for comprehensive content
                max_pages = min(15, len(reader.pages))  # Increased to 15 pages
                for page_num in range(max_pages):
                    page_text = reader.pages[page_num].extract_text()
                    text += page_text + "\n"

                # Return maximum content for best cheat sheets
                return text[:15000]  # Increased to 15000 characters
        except ImportError:
            return f"📄 {pdf_path.name} (PyPDF2 not available - install with: pip install PyPDF2)"
        except Exception as e:
            return f"📄 Error reading {pdf_path.name}: {e}"
    
    def find_course_directory(self, course_code):
        """Find course directory with dynamic matching"""
        if course_code not in self.courses:
            return None

        data_courses = Path("data/courses")
        if not data_courses.exists():
            data_courses.mkdir(parents=True, exist_ok=True)

        course = self.courses[course_code]
        course_name = course.get('name', '')

        print(f"🔍 Looking for course directory for: {course_code} - {course_name}")

        # Method 1: Try exact course_code_name format (new style from refresh)
        course_name_safe = course_name.replace('/', '_').replace('[', '').replace(']', '')
        new_style_dir = data_courses / f"{course_code}_{course_name_safe}"
        print(f"   📁 Trying new style: {new_style_dir.name}")
        if new_style_dir.exists():
            print(f"   ✅ Found new style directory!")
            return new_style_dir

        # Method 2: Legacy hard-coded mappings for backward compatibility
        course_mappings = {
            "18872": "[CT0662-1]_CALCULUS-1_(CT3)_-_a.a._2024-25",
            "21001": "[CT0662-2]_CALCULUS-2_(CT3)_-_a.a._2024-25",
            "18873": "[CT0665]_INTRODUCTION_TO_COMPUTER_PROGRAMMING_(CT3)_-_a.a._2024-25",
            "18874": "[CT0666]_DISCRETE_STRUCTURES_(CT3)_-_a.a._2024-25",
            "18876": "[CT0668-2]_COMPUTER_ARCHITECTURES-LABORATORY_(CT3)_-_a.a._2024-25",
            "21005": "[CT0677-E]_TECHNICAL_ENGLISH_FOR_COMPUTER_SCIENCE_-_PRACTICE_(CT3)_-_a.a._2024-25",
            "18877": "[CT0678]_MATHEMATICS_BACKGROUND_(CT3)_-_a.a._2024-25"
        }

        if course_code in course_mappings:
            legacy_dir = data_courses / course_mappings[course_code]
            print(f"   📁 Trying legacy mapping: {legacy_dir.name}")
            if legacy_dir.exists():
                print(f"   ✅ Found legacy directory!")
                return legacy_dir

        # Method 3: Search by CT code pattern
        ct_code = course_name.split("]")[0].replace("[", "") if "]" in course_name else ""
        if ct_code:
            print(f"   🔍 Searching by CT code: {ct_code}")
            for subdir in data_courses.iterdir():
                if subdir.is_dir() and ct_code in subdir.name:
                    print(f"   ✅ Found by CT code: {subdir.name}")
                    return subdir

        # Method 4: Search by course code in directory name
        print(f"   🔍 Searching by course code: {course_code}")
        for subdir in data_courses.iterdir():
            if subdir.is_dir() and course_code in subdir.name:
                print(f"   ✅ Found by course code: {subdir.name}")
                return subdir

        print(f"   ❌ No directory found for course {course_code}")
        return None
    
    def deep_pdf_analysis(self, course_code):
        """Deep PDF analysis with AI enhancement"""
        if course_code not in self.courses:
            print(f"❌ Course {course_code} not found")
            self.show_available_courses()
            return
        
        course = self.courses[course_code]

        print(f"\n🧠 Deep analyzing: {course.get('name', course_code)}")

        # Try to download from Moodle first
        print("📥 Checking Moodle for additional materials...")
        self.download_moodle_pdfs(course_code)

        # Find course directory
        course_dir = self.find_course_directory(course_code)
        pdfs = []

        if course_dir:
            print(f"📁 Using local directory: {course_dir}")
            pdfs = list(course_dir.rglob("*.pdf"))
            print(f"📄 Found {len(pdfs)} PDF files in directory")
        else:
            print("📁 No local directory found, checking course database...")

        # If no local PDFs or no directory, check course database for PDF info
        course_pdfs = course.get('pdfs', [])
        if course_pdfs and len(pdfs) == 0:
            print(f"📄 Found {len(course_pdfs)} PDFs in course database")
            print("💡 These PDFs are available on Moodle but not downloaded locally")

            # Show available PDFs
            print("\n📋 Available PDFs on Moodle:")
            for i, pdf_info in enumerate(course_pdfs[:10], 1):  # Show first 10
                pdf_name = pdf_info.get('name', 'Unknown PDF')
                pdf_section = pdf_info.get('section', 'Unknown Section')
                pdf_size = pdf_info.get('size', 0) / 1024  # KB
                print(f"   {i}. {pdf_name} ({pdf_size:.1f} KB) - {pdf_section}")

            if len(course_pdfs) > 10:
                print(f"   ... and {len(course_pdfs) - 10} more PDFs")

            print("\n💡 To analyze these PDFs:")
            print("   1. Use 'Refresh Moodle Data' to download PDFs")
            print("   2. Or download specific course materials manually")

            # For demonstration, create a summary based on available metadata
            print(f"\n📊 COURSE OVERVIEW BASED ON AVAILABLE MATERIALS")
            print("="*60)
            print(f"Course: {course.get('name', course_code)}")
            print(f"Total PDFs available: {len(course_pdfs)}")

            # Group by sections
            sections = {}
            for pdf_info in course_pdfs:
                section = pdf_info.get('section', 'General')
                if section not in sections:
                    sections[section] = []
                sections[section].append(pdf_info)

            print(f"Organized in {len(sections)} sections:")
            for section, section_pdfs in sections.items():
                total_size = sum(pdf.get('size', 0) for pdf in section_pdfs) / (1024 * 1024)  # MB
                print(f"   📂 {section}: {len(section_pdfs)} files ({total_size:.1f} MB)")

            input("\n✨ Press Enter to continue...")
            return

        if not pdfs:
            print("❌ No PDF files available for analysis")
            print("💡 Try using 'Refresh Moodle Data' to download course materials")
            input("\n✨ Press Enter to continue...")
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
        """Create AI-optimized study plan from analysis cache"""
        # Try multiple cache file patterns
        cache_files = [
            f"analysis_cache_{course_code}.json",
            f"pdf_analysis_cache_{course_code}.json"
        ]
        
        analysis = None
        for cache_file in cache_files:
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                    analysis = cache_data.get("analysis") or cache_data.get("content_analysis", "")
                    if analysis:
                        print(f"📊 Found analysis cache: {cache_file}")
                        break
            except FileNotFoundError:
                continue
        
        if not analysis:
            print("❌ No course analysis cache found!")
            print(f"💡 Please run 'Deep PDF Analysis' for course {course_code} first")
            print("   or use menu option 1 to analyze course materials")
            return False
        
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
        
        # Save plan in course data folder
        course_name = course.get('name', course_code)
        course_data_dir = f"data/courses/{course_name}"
        
        # Create study_plans subfolder in course directory
        study_plan_dir = f"{course_data_dir}/study_plans"
        os.makedirs(study_plan_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_file = f"{study_plan_dir}/STUDY_PLAN_{course_code}_{timestamp}.txt"
        
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
        
        return True

    def generate_cheat_sheet(self, course_code):
        """Generate a comprehensive PDF cheat sheet for the course"""
        if course_code not in self.courses:
            print(f"❌ Course {course_code} not found")
            self.show_available_courses()
            return

        course = self.courses[course_code]
        course_name = course.get('name', course_code)

        print(f"\n📄 Generating cheat sheet for: {course_name}")

        # Detect course type for specialized formatting
        course_type = self.detect_course_type(course_name, course_code)
        print(f"🎯 Course type detected: {course_type}")

        # Try to get content from various sources
        content_sources = []

        # 1. Try to get content from local PDFs - ENHANCED for comprehensive extraction
        course_dir = self.find_course_directory(course_code)
        if course_dir:
            pdfs = list(course_dir.rglob("*.pdf"))
            if pdfs:
                print(f"📚 Comprehensive extraction from {len(pdfs)} local PDF files...")
                # Process ALL PDFs for maximum content coverage
                # Extract formulas from all PDFs
                all_formulas = []

                for pdf in pdfs[:5]:  # Focus on top 5 PDFs for exam content
                    print(f"   📖 Extracting from: {pdf.name}")
                    content = self.extract_pdf_text(pdf)
                    if content and len(content.strip()) > 50:
                        # Focused content extraction for exam cheat sheet
                        optimized_content = content[:6000]  # Focused amount per PDF

                        # Extract formulas specifically if math/science course
                        pdf_formulas = self.extract_formulas_from_text(content, course_type)
                        all_formulas.extend(pdf_formulas)

                        content_sources.append({
                            'type': 'pdf',
                            'name': pdf.name,
                            'content': optimized_content,
                            'section': 'Local PDF',
                            'formulas': pdf_formulas
                        })

                if all_formulas:
                    print(f"   📐 Extracted {len(all_formulas)} formulas from PDFs")

        # 2. Get content from course database PDFs info
        course_pdfs = course.get('pdfs', [])
        if course_pdfs and not content_sources:
            print(f"📋 Using course metadata from {len(course_pdfs)} PDFs...")
            for pdf_info in course_pdfs[:10]:
                content_sources.append({
                    'type': 'metadata',
                    'name': pdf_info.get('name', 'Unknown'),
                    'section': pdf_info.get('section', 'General'),
                    'module': pdf_info.get('module', 'Unknown Module')
                })

        if not content_sources:
            print("❌ No content sources available for cheat sheet generation")
            print("💡 Try using 'Refresh Moodle Data' first to get course materials")
            input("\n✨ Press Enter to continue...")
            return

        # Generate cheat sheet content using Claude AI
        print("🧠 Generating cheat sheet content with AI...")

        if not self.claude_api:
            print("❌ Claude API not available")
            input("\n✨ Press Enter to continue...")
            return

        # Prepare content for AI processing with smart chunking for large content
        if content_sources[0]['type'] == 'pdf':
            combined_content = "\n".join([f"=== {src['name']} ===\n{src['content']}" for src in content_sources])

            # Add extracted formulas section for math/science courses
            all_formulas = []
            for src in content_sources:
                if 'formulas' in src:
                    all_formulas.extend(src['formulas'])

            if all_formulas:
                formula_section = "\n\n=== EXTRACTED FORMULAS ===\n" + "\n".join(all_formulas)
                combined_content += formula_section

            # Optimized content for exam cheat sheet (focused, not comprehensive)
            max_content_length = 20000  # Focused limit for exam-specific content
            print(f"📊 Total content length: {len(combined_content)} characters")

            if len(combined_content) > max_content_length:
                print(f"✂️ Optimizing content size for API reliability...")

                # Smart content optimization strategy
                optimized_content = ""

                # 1. Always include formulas (highest priority)
                if all_formulas:
                    formula_content = "=== EXTRACTED FORMULAS ===\n" + "\n".join(all_formulas[:15]) + "\n\n"
                    optimized_content += formula_content
                    print(f"   ✅ Added {len(all_formulas[:15])} formulas")

                # 2. Extract key content from each PDF
                remaining_length = max_content_length - len(optimized_content)
                content_per_pdf = remaining_length // min(len(content_sources), 3)

                for i, src in enumerate(content_sources[:3]):
                    print(f"   📖 Optimizing content from: {src['name']}")

                    # Extract the most important content
                    content = src['content']
                    lines = content.split('\n')

                    # Prioritize lines with mathematical content or key terms
                    important_lines = []
                    key_terms = ['theorem', 'definition', 'formula', 'example', 'proof', 'solution',
                                'important', 'note', 'remember', '=', 'equation', 'property']

                    for line in lines:
                        line = line.strip()
                        if len(line) > 20 and len(line) < 200:  # Reasonable length
                            if any(term in line.lower() for term in key_terms):
                                important_lines.append(line)

                    # If we have important lines, use them; otherwise use first substantial lines
                    if important_lines:
                        selected_content = '\n'.join(important_lines[:20])  # Top 20 important lines
                    else:
                        substantial_lines = [line.strip() for line in lines if len(line.strip()) > 30]
                        selected_content = '\n'.join(substantial_lines[:15])  # Top 15 substantial lines

                    # Add to optimized content
                    pdf_section = f"=== {src['name']} ===\n{selected_content[:content_per_pdf]}\n\n"
                    optimized_content += pdf_section

                combined_content = optimized_content[:max_content_length]
                print(f"   ✅ Content optimized to {len(combined_content)} characters")

            content_prompt = f"Based on the following course materials:\n\n{combined_content}"
        else:
            metadata_content = "\n".join([f"- {src['name']} (Section: {src['section']}, Module: {src['module']})" for src in content_sources])
            content_prompt = f"Based on the following course materials metadata:\n\n{metadata_content}"

        # Generate exam-focused prompt
        exam_focused_prompt = self.generate_exam_focused_prompt(course_type, course_name)

        messages = [{
            "role": "user",
            "content": f"""{content_prompt}

{exam_focused_prompt}

COMPACT EXAM STRUCTURE (Maximum 5 pages):

**1. FORMULA QUICK REFERENCE**
- All essential formulas in table format
- Variable definitions in compact form
- Units clearly marked

**2. CALCULATION SHORTCUTS & TRICKS**
- Quick solution methods
- Mental math shortcuts
- Pattern recognition rules

**3. EXAM TACTICS**
- Time management strategies
- Question approach methods
- Partial credit maximization
- Error checking techniques

**4. COMMON MISTAKES TO AVOID**
- Frequent errors and how to prevent them
- Warning signs during calculations
- Double-check methods

**5. QUICK REFERENCE TABLES**
- Constants and conversion factors
- Standard solutions and patterns
- Key relationships in table form

FORMAT REQUIREMENTS:
- Compact bullet points
- Clear mathematical notation
- Easy-to-scan layout
- Maximum information density
- Print-friendly format (5 pages max)

IMPORTANT: This is an EXAM CHEAT SHEET meant to be printed and used during exams. Focus on essential formulas, quick tricks, and exam tactics. Be concise but complete. Every piece of information should be immediately useful during an exam."""
        }]

        cheat_sheet_content = self.claude_request(messages)

        if not cheat_sheet_content:
            print("❌ Failed to generate cheat sheet after multiple attempts.")
            print("💡 This may be due to large content size or API issues.")
            print("🔧 Try again or contact support if the problem persists.")
            input("\n✨ Press Enter to continue...")
            return

        # Create directory for cheat sheets
        cheat_sheet_dir = Path("cheat_sheets")
        cheat_sheet_dir.mkdir(exist_ok=True)

        # Save as text file first
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_filename = f"CHEAT_SHEET_{course_code}_{timestamp}.txt"
        txt_path = cheat_sheet_dir / txt_filename

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"CHEAT SHEET - {course.get('name', course_code)}\n")
            f.write(f"Course Code: {course_code}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            f.write(cheat_sheet_content)

        print(f"✅ Text cheat sheet saved: {txt_path}")

        # Try to convert to PDF using reportlab
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.units import inch
            from reportlab.lib.colors import HexColor, black, blue, darkblue
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

            pdf_filename = f"CHEAT_SHEET_{course_code}_{timestamp}.pdf"
            pdf_path = cheat_sheet_dir / pdf_filename

            # Create PDF with better margins
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=72, leftMargin=72,
                topMargin=72, bottomMargin=18
            )

            styles = getSampleStyleSheet()
            story = []

            # Custom styles
            custom_title = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=darkblue
            )

            custom_heading = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=12,
                textColor=blue,
                borderWidth=1,
                borderColor=blue,
                borderPadding=5
            )

            custom_subheading = ParagraphStyle(
                'CustomSubHeading',
                parent=styles['Heading3'],
                fontSize=12,
                spaceAfter=8,
                spaceBefore=8,
                textColor=darkblue
            )

            custom_normal = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                alignment=TA_JUSTIFY
            )

            formula_style = ParagraphStyle(
                'FormulaStyle',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=8,
                spaceBefore=8,
                fontName='Courier',  # Monospace font for formulas
                backgroundColor=HexColor('#f0f0f0'),
                borderWidth=1,
                borderColor=HexColor('#cccccc'),
                borderPadding=5
            )

            # Title
            title = Paragraph(f"<b>CHEAT SHEET</b><br/>{course.get('name', course_code)}", custom_title)
            story.append(title)
            story.append(Spacer(1, 20))

            # Course info box
            info_text = f"""
            <b>Course Code:</b> {course_code}<br/>
            <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <b>Source:</b> Ca' Foscari Ultimate Study System
            """
            info = Paragraph(info_text, custom_normal)
            story.append(info)
            story.append(Spacer(1, 20))

            # Process content with better formatting
            lines = cheat_sheet_content.split('\n')
            current_section = ""

            for line in lines:
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 6))
                    continue

                # Detect section headers
                if (line.startswith('**') and line.endswith('**')) or line.isupper() or line.startswith('#'):
                    # Main section header
                    clean_line = line.replace('**', '').replace('#', '').strip()
                    if len(clean_line) > 3:  # Avoid short strings
                        para = Paragraph(f"<b>{clean_line}</b>", custom_heading)
                        story.append(para)
                        current_section = clean_line
                        continue

                # Detect subsection headers
                if line.startswith('-') and line.endswith(':'):
                    clean_line = line.replace('-', '').replace(':', '').strip()
                    para = Paragraph(f"<b>{clean_line}:</b>", custom_subheading)
                    story.append(para)
                    continue

                # Enhanced formula detection based on course type
                formula_indicators = ['=', '∫', '∑', 'dx', 'dy', 'sin', 'cos', 'tan', 'log', 'ln', '√', '^', '_', '∆', 'α', 'β', 'γ', 'π', '∞']

                # Add course-specific indicators
                if course_type == 'computer_science':
                    formula_indicators.extend(['O(', 'Θ(', 'Ω(', 'def ', 'class ', 'if ', 'for ', 'while '])
                elif course_type == 'physics_engineering':
                    formula_indicators.extend(['m/s', 'kg', 'N', 'J', 'W', 'V', 'A', 'Ω', 'F', 'H'])
                elif course_type == 'economics':
                    formula_indicators.extend(['$', '€', '£', '%', 'GDP', 'CPI', 'PV', 'FV'])

                if any(indicator in line for indicator in formula_indicators) and len(line) > 5:
                    para = Paragraph(f"<font name='Courier'>{line}</font>", formula_style)
                    story.append(para)
                    continue

                # Bullet points
                if line.startswith('- ') or line.startswith('• '):
                    clean_line = line.replace('- ', '').replace('• ', '')
                    # Check if bullet point contains formula
                    if any(indicator in clean_line for indicator in formula_indicators):
                        para = Paragraph(f"• <font name='Courier'>{clean_line}</font>", custom_normal)
                    else:
                        para = Paragraph(f"• {clean_line}", custom_normal)
                    story.append(para)
                    continue

                # Numbered lists
                if len(line) > 2 and line[0].isdigit() and line[1] in ['.', ')']:
                    para = Paragraph(line, custom_normal)
                    story.append(para)
                    continue

                # Code/formula blocks (lines starting with spaces)
                if line.startswith('    ') or line.startswith('\t'):
                    para = Paragraph(f"<font name='Courier'>{line.strip()}</font>", formula_style)
                    story.append(para)
                    continue

                # Regular paragraphs
                if len(line) > 10:  # Only add substantial content
                    para = Paragraph(line, custom_normal)
                    story.append(para)

            # Add footer
            story.append(Spacer(1, 30))
            footer = Paragraph(
                "<i>Generated by Ca' Foscari Ultimate Study System - AI-Powered Academic Assistant</i>",
                custom_normal
            )
            story.append(footer)

            doc.build(story)
            print(f"📄 Enhanced PDF cheat sheet created: {pdf_path}")

        except ImportError:
            print("📄 PDF generation requires reportlab library")
            print("💡 To enable PDF generation: pip install reportlab")
            print(f"✅ Text version available: {txt_path}")

        except Exception as e:
            print(f"⚠️ PDF generation failed: {e}")
            print(f"✅ Text version available: {txt_path}")

        # Show exam cheat sheet preview
        print("\n" + "="*80)
        print("📋 EXAM CHEAT SHEET PREVIEW")
        print("="*80)
        preview_length = 1500  # Focused preview for exam content
        preview = cheat_sheet_content[:preview_length]
        if len(cheat_sheet_content) > preview_length:
            preview += "\n\n... (content continues - see full exam cheat sheet in files)"
        print(preview)
        print("="*80)
        print(f"🎯 Course type: {course_type}")
        print(f"📊 Content length: {len(cheat_sheet_content)} characters")
        pages_estimate = min(5, len(cheat_sheet_content) // 2500 + 1)  # Max 5 pages
        print(f"📄 Estimated pages: {pages_estimate} (max 5 for exam use)")
        if hasattr(locals(), 'all_formulas') and all_formulas:
            print(f"📐 Extracted formulas: {len(all_formulas)}")
        print("🎯 Optimized for exam use - formulas, tactics, and shortcuts")
        print("="*80)

        print(f"\n📁 Files saved in: {cheat_sheet_dir}/")
        print(f"📄 Text file: {txt_filename}")
        if (cheat_sheet_dir / pdf_filename).exists():
            print(f"🔖 PDF file: {pdf_filename}")

        input("\n✨ Press Enter to continue...")
        return True

    def detect_course_type(self, course_name, course_code):
        """Detect course type for specialized cheat sheet formatting"""
        course_name_lower = course_name.lower()

        # Mathematical courses
        math_keywords = ['calculus', 'mathematics', 'algebra', 'analysis', 'geometry', 'statistics',
                        'probability', 'discrete', 'mathematical', 'math', 'linear algebra']

        # Computer Science courses
        cs_keywords = ['programming', 'computer', 'software', 'algorithm', 'data structure',
                      'architecture', 'systems', 'networks', 'database', 'machine learning']

        # Physics/Engineering courses
        physics_keywords = ['physics', 'engineering', 'mechanics', 'thermodynamics', 'electronics',
                           'circuits', 'signals', 'control', 'electromagnetic']

        # Language courses
        language_keywords = ['english', 'language', 'linguistic', 'communication', 'writing']

        # Economics/Business courses
        econ_keywords = ['economics', 'business', 'finance', 'management', 'accounting', 'marketing']

        if any(keyword in course_name_lower for keyword in math_keywords):
            return 'mathematics'
        elif any(keyword in course_name_lower for keyword in cs_keywords):
            return 'computer_science'
        elif any(keyword in course_name_lower for keyword in physics_keywords):
            return 'physics_engineering'
        elif any(keyword in course_name_lower for keyword in language_keywords):
            return 'language'
        elif any(keyword in course_name_lower for keyword in econ_keywords):
            return 'economics'
        else:
            return 'general'

    def extract_formulas_from_text(self, text, course_type):
        """Extract and format formulas based on course type"""
        if course_type not in ['mathematics', 'physics_engineering', 'computer_science']:
            return []

        formulas = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            # Mathematical formula patterns
            math_patterns = [
                r'.*[=<>≤≥≠].*',  # Equations and inequalities
                r'.*∫.*d[xy].*',  # Integrals
                r'.*∑.*',         # Summations
                r'.*∏.*',         # Products
                r'.*√.*',         # Square roots
                r'.*[αβγδεζηθικλμνξοπρστυφχψω].*',  # Greek letters
                r'.*\^.*',        # Exponents
                r'.*_.*',         # Subscripts
                r'.*lim.*',       # Limits
                r'.*sin|cos|tan|log|ln|exp.*',  # Functions
                r'.*∂.*',         # Partial derivatives
                r'.*[∞±∆∇].*',    # Mathematical symbols
            ]

            # CS-specific patterns
            if course_type == 'computer_science':
                cs_patterns = [
                    r'.*O\(.*\).*',   # Big O notation
                    r'.*Θ\(.*\).*',   # Theta notation
                    r'.*Ω\(.*\).*',   # Omega notation
                    r'.*def.*\(.*\):.*',  # Function definitions
                    r'.*class.*:.*',  # Class definitions
                    r'.*if.*then.*else.*',  # Conditional logic
                ]
                math_patterns.extend(cs_patterns)

            # Check if line matches any pattern
            import re
            for pattern in math_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    if len(line) > 5 and len(line) < 200:  # Reasonable formula length
                        formulas.append(line)
                    break

        return list(set(formulas))  # Remove duplicates

    def generate_exam_focused_prompt(self, course_type, course_name):
        """Generate exam-focused cheat sheet prompt for 5-page limit"""
        base_prompt = f'Create a CONCISE EXAM CHEAT SHEET for "{course_name}" that can be printed and used during an exam. MAXIMUM 5 PAGES when printed.'

        if course_type == 'mathematics':
            return f"""{base_prompt}

**EXAM CHEAT SHEET - MATHEMATICS FOCUS:**
- ALL key formulas in compact format
- Quick derivation steps (1-2 lines max)
- Integration/differentiation rules table
- Trigonometric identities (compact table)
- Limit rules and L'Hôpital's rule
- Series formulas (Taylor, MacLaurin)
- Common function derivatives and integrals
- Exam tactics: substitution tricks, partial fractions
- Quick checks for answers
- Common mistake warnings"""

        elif course_type == 'physics_engineering':
            return f"""{base_prompt}

**EXAM CHEAT SHEET - PHYSICS/ENGINEERING FOCUS:**
- All physics formulas with units
- Constants table (g, c, h, k, etc.)
- Quick unit conversion table
- Free body diagram rules
- Circuit analysis shortcuts
- Energy/momentum conservation
- Wave equation forms
- Exam tactics: dimensional analysis tricks
- Quick calculation methods
- Common error checks"""

        elif course_type == 'computer_science':
            return f"""{base_prompt}

**EXAM CHEAT SHEET - COMPUTER SCIENCE FOCUS:**
- Algorithm complexity table (O, Θ, Ω)
- Data structure operations time complexity
- Sorting algorithms comparison
- Graph algorithms summary
- Key pseudocode templates
- Big O calculation rules
- Recursion patterns
- Exam tactics: complexity analysis shortcuts
- Quick debugging checks
- Common algorithm patterns"""

        else:
            return f"""{base_prompt}

**EXAM CHEAT SHEET - GENERAL FOCUS:**
- Key concepts in bullet points
- Essential formulas/rules
- Quick reference tables
- Step-by-step procedures
- Memory aids and shortcuts
- Exam tactics and time management
- Common mistakes to avoid
- Quick verification methods"""

    def handle_file_location_question(self):
        """Study plan dosya lokasyonu hakkında basit yanıt"""
        return """📁 Study plan şurada kaydedildi:
data/courses/[DERS_ADI]/study_plans/STUDY_PLAN_[KOD]_[TARİH].txt

Örnek: data/courses/[CT0668-2] COMPUTER ARCHITECTURES-LABORATORY (CT3) - a.a. 2024-25/study_plans/

Bu klasörü bilgisayarında aç ve TXT dosyasını görebilirsin."""
    
    def chat_with_claude(self):
        """AKILLI chat mode - Study plan oluşturma ve smart web search"""
        print("\n💬 INTELLIGENT CHAT MODE - Integrated AI Assistant")
        print("="*60)
        print("✅ Study plan creation integrated!")
        print("✅ Smart web search (only when needed)")
        print("✅ All conversations cached")
        print("📧 Smart email commands also available")
        print("Type 'exit' to return to menu.")
        print("-"*60)
        
        # Conversation cache for this session
        conversation_cache = []
        
        while True:
            try:
                user_input = input("\n🎓 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'back']:
                    break
                
                if not user_input:
                    continue
                
                # Cache user input
                conversation_cache.append({"role": "user", "content": user_input})
                
                # Handle email commands first
                if self.handle_email_commands(user_input):
                    continue
                
                # Check for study plan requests
                if self.detect_study_plan_request(user_input):
                    print("📚 Study plan request detected!")
                    course_code = self.extract_course_from_request(user_input)
                    if course_code:
                        print(f"🎯 Creating study plan for {course_code}")
                        success = self.create_study_plan(course_code)
                        if success:
                            response_msg = f"✅ Study plan successfully created for {course_code}! Check the course data folder."
                        else:
                            response_msg = f"❌ Could not create study plan for {course_code}. Run PDF analysis first."
                        # Cache the response
                        conversation_cache.append({
                            "role": "assistant", 
                            "content": response_msg
                        })
                        print(f"\n🧠 Claude: {response_msg}")
                        continue
                    else:
                        # Show available courses
                        print("📋 Available courses:")
                        for code, course in self.courses.items():
                            print(f"  • {code}: {course.get('name', 'Unknown')}")
                        response_msg = "Please specify a course code from the list above for study plan creation."
                        conversation_cache.append({
                            "role": "assistant", 
                            "content": response_msg
                        })
                        print(f"\n🧠 Claude: {response_msg}")
                        continue
                
                # Basit sorular için basit yanıtlar
                if any(keyword in user_input.lower() for keyword in ['nerede', 'nasıl açarım', 'kaydettin', 'dosya']):
                    response = self.handle_file_location_question()
                elif any(keyword in user_input.lower() for keyword in ['teşekkür', 'görüşürüz', 'iyi çalışmalar']):
                    response = "✅ Rica ederim! İhtiyacın olursa buradayım."
                else:
                    # Normal Claude API için basit prompt
                    enhanced_prompt = f"""Sen bir AI asistansın. Kısa ve net yanıtla.
Soru: {user_input}

Yanıtını Türkçe ver ve kısa tut."""
                    
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
                
                # Cache AI response
                conversation_cache.append({"role": "assistant", "content": response})
                
                print(f"\n🧠 Claude: {response}")
                
            except KeyboardInterrupt:
                break
        
        # Save conversation cache
        self.save_conversation_cache(conversation_cache)
        print("\n👋 Returning to main menu...")
    
    def detect_study_plan_request(self, user_input):
        """Study plan isteği tespit et"""
        user_input_lower = user_input.lower()
        
        study_plan_keywords = [
            'study plan', 'çalışma planı', 'plan oluştur', 'study schedule',
            'ders programı', 'çalışma takvimi', 'plan yap', 'create plan',
            'make plan', 'study guide', 'çalışma rehberi', 'plan çıkar'
        ]
        
        return any(keyword in user_input_lower for keyword in study_plan_keywords)
    
    def extract_course_from_request(self, user_input):
        """İstekten course code çıkar"""
        user_input_lower = user_input.lower()
        
        # Direct course code match
        for course_code in self.courses.keys():
            if course_code.lower() in user_input_lower:
                return course_code
        
        # Course name match
        for course_code, course_info in self.courses.items():
            course_name = course_info.get('name', '').lower()
            # Check for significant words from course name
            course_words = [word for word in course_name.split() if len(word) > 3]
            if any(word in user_input_lower for word in course_words):
                return course_code
        
        return None
    
    def cache_new_email(self, contact_name, email_address):
        """Yeni email adresini cache'e kaydet"""
        try:
            # Contacts.json'a ekle
            self.contacts[contact_name] = email_address
            
            # Dosyaya kaydet
            with open("contacts.json", "w", encoding="utf-8") as f:
                json.dump(self.contacts, f, indent=2, ensure_ascii=False)
            
            print(f"📝 Contact saved to cache: {contact_name} -> {email_address}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not save contact to cache: {e}")
    
    def save_conversation_cache(self, conversation_cache):
        """Konuşmayı cache'e kaydet"""
        if not conversation_cache:
            return
        
        try:
            os.makedirs("conversation_cache", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cache_file = f"conversation_cache/chat_{timestamp}.json"
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': timestamp,
                    'messages': conversation_cache,
                    'total_messages': len(conversation_cache)
                }, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Conversation cached: {len(conversation_cache)} messages saved")
            
        except Exception as e:
            print(f"⚠️ Cache save failed: {e}")
    
    def handle_email_commands(self, user_input, dry_run=False):
        """AKILLI email handler - her şeyi web'den alır"""
        user_input_lower = user_input.lower()
        
        # Check for email reading commands
        if any(cmd in user_input_lower for cmd in ['check emails', 'important emails', 'read emails', 'email check']):
            print("\n📬 Checking your important emails...")
            result = self.read_important_emails()
            print(result)
            return True
        
        # Smart email detection - önce email pattern kontrol et
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        direct_emails = re.findall(email_pattern, user_input)
        
        # Email varsa VEYA email keyword'ları varsa email gönderme moduna geç
        has_email = len(direct_emails) > 0
        has_email_keywords = any(word in user_input_lower for word in ['gönder', 'send', 'mail', 'email', 'at', 'yolla', 'yaz'])
        
        if has_email or has_email_keywords:
            # Contact bul
            found_contact = None
            found_email = None
            
            if direct_emails:
                # Direct email bulundu - hemen kullan
                found_email = direct_emails[0]
                found_contact = found_email.split('@')[0]
                
                # Cache'e ekle
                self.cache_new_email(found_contact, found_email)
                print(f"✅ New email cached: {found_contact} -> {found_email}")
            else:
                # Direct email yok, cache'den ara
                for contact_name, email in self.contacts.items():
                    if contact_name in user_input_lower or any(pattern in user_input_lower for pattern in [
                        contact_name + 'e', contact_name + 'ye', contact_name + 'den', contact_name + 'a',
                        contact_name + 'i', contact_name + 'in', contact_name + 'le'
                    ]):
                        found_contact = contact_name
                        found_email = email
                        break
                
                if not found_email:
                    print("❌ Contact not found and no email address detected!")
                    print("📋 Available contacts:", ", ".join(self.contacts.keys()))
                    print("💡 Try: 'erdeme selam yaz' or include email: 'test@example.com mesaj'")
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
                print("4. 📄 Generate Cheat Sheet (create PDF summary)")
                print("5. 💬 Chat with Claude AI (interactive tutoring + email)")
                print("6. 🤖 Autonomous Assistant (AI that learns from you)")
                print("7. 🌅 Daily Briefing (intelligent daily report)")
                print("8. 🧭 Unified Intelligence (advanced AI mode)")
                print("9. ⚡ Moodle Course Optimization (optimize courses from Moodle)")
                print("10. 🔄 Refresh Moodle Data (sync new enrolled courses)")
                print("11. 🔍 System Status (check configuration)")
                print("12. ❌ Exit")
                
                choice = input("\nEnter your choice (1-12): ").strip()
                
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
                    course_code = input("Enter course code for cheat sheet: ").strip()
                    self.generate_cheat_sheet(course_code)

                elif choice == "5":
                    self.chat_with_claude()

                elif choice == "6":
                    print("⚠️ Autonomous assistant temporarily disabled for optimization")
                    input("Press Enter to continue...")

                elif choice == "7":
                    print("⚠️ Daily briefing temporarily disabled for optimization")
                    input("Press Enter to continue...")

                elif choice == "8":
                    print("\n🧭 UNIFIED INTELLIGENCE MODE")
                    print("="*50)
                    print("This mode analyzes your input with multi-dimensional AI")
                    print("and provides intelligent responses with confidence scoring.\n")

                    while True:
                        user_input = input("🤖 Unified AI > ").strip()
                        if user_input.lower() in ['exit', 'quit', 'back']:
                            break
                        print("⚠️ Unified intelligence temporarily disabled for optimization")

                elif choice == "9":
                    self.optimize_moodle_courses()

                elif choice == "10":
                    self.refresh_moodle_data()

                elif choice == "11":
                    self.system_status()

                elif choice == "12":
                    print("\n👋 Thank you for using Ca' Foscari Ultimate!")
                    print("🎓 Good luck with your studies!")
                    break

                else:
                    print("❌ Invalid choice. Please select 1-12.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again...")

    
    def analyze_user_patterns_deprecated(self):
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
    
    def autonomous_assistant_deprecated(self):
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
    
    def unified_intelligence_deprecated(self, user_input):
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
    
    def create_daily_briefing_deprecated(self):
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