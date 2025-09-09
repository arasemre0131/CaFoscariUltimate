#!/usr/bin/env python3
"""
🚀 CLAUDE ULTIMATE - COMMAND LINE VERSION
Direct PDF analysis with web integration - no interactive loops
Usage: python3 claude_cli.py [analyze|exam|plan] [course_code]
"""
import sys
import os
import json
import requests
from datetime import datetime
from pathlib import Path

class ClaudeUltimateCLI:
    def __init__(self):
        self.courses = self.load_courses()
        self.api_key = self.load_api_key()
        
    def load_courses(self):
        try:
            with open("courses_database.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    
    def load_api_key(self):
        try:
            with open("api_keys/claude_api_key.txt", "r") as f:
                return f.read().strip()
        except Exception:
            return None
    
    def claude_request(self, messages, system_prompt="You are a helpful AI assistant."):
        if not self.api_key:
            return "❌ Claude API key not found"
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
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
                return f"❌ API Error: {response.status_code}"
                
        except Exception as e:
            return f"❌ Request failed: {e}"
    
    def extract_pdf_text(self, pdf_path):
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(min(3, len(reader.pages))):
                    text += reader.pages[page_num].extract_text()
                return text[:2000]
        except ImportError:
            return f"📄 {pdf_path.name} (PyPDF2 not available)"
        except Exception as e:
            return f"📄 Error reading {pdf_path.name}: {e}"
    
    def find_course_directory(self, course_code):
        if course_code not in self.courses:
            return None
            
        course = self.courses[course_code]
        course_name = course.get("name", "")
        
        data_courses = Path("data/courses")
        if not data_courses.exists():
            return None
        
        # Try exact matches first
        for dirname in [course_name, course_code, course.get("full_name", "")]:
            if dirname:
                dir_path = data_courses / dirname
                if dir_path.exists():
                    return dir_path
        
        # Try partial matches
        for subdir in data_courses.iterdir():
            if subdir.is_dir():
                dir_name = subdir.name.upper()
                if (course_code in dir_name or 
                    any(part.upper() in dir_name for part in course_name.split() if len(part) > 3)):
                    return subdir
        
        return None
    
    def analyze_course(self, course_code):
        if course_code not in self.courses:
            print(f"❌ Course {course_code} not found")
            print(f"Available courses: {', '.join(self.courses.keys())}")
            return
        
        course = self.courses[course_code]
        course_dir = self.find_course_directory(course_code)
        
        if not course_dir:
            print(f"❌ No materials found for {course.get('name', course_code)}")
            return
        
        print(f"🧠 Analyzing: {course.get('name', course_code)}")
        print(f"📁 Directory: {course_dir}")
        
        # Find PDFs
        pdfs = list(course_dir.rglob("*.pdf"))
        print(f"📄 Found {len(pdfs)} PDF files")
        
        if not pdfs:
            print("❌ No PDF files found")
            return
        
        # Extract content
        pdf_contents = []
        for pdf in pdfs[:2]:
            print(f"📖 Processing: {pdf.name}")
            content = self.extract_pdf_text(pdf)
            pdf_contents.append(f"=== {pdf.name} ===\n{content}\n")
        
        combined_content = "\n".join(pdf_contents)
        
        # Create analysis request
        messages = [{
            "role": "user",
            "content": f"""Analyze this course material:

Course: {course.get('name', course_code)}
Content from PDFs:
{combined_content}

Provide comprehensive analysis covering:
1. Key concepts and theories
2. Important formulas/definitions  
3. Practical applications
4. Study recommendations
5. Exam focus areas
6. Learning sequence

Format as structured, detailed analysis."""
        }]
        
        print("🤔 Generating AI analysis...")
        analysis = self.claude_request(messages, "You are an expert academic tutor providing detailed course analysis.")
        
        # Save analysis
        cache_file = f"analysis_cache_{course_code}.json"
        cache_data = {
            "course_code": course_code,
            "course_name": course.get('name', course_code),
            "analysis": analysis,
            "pdf_files": [pdf.name for pdf in pdfs[:2]],
            "timestamp": datetime.now().isoformat()
        }
        
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Analysis saved to {cache_file}")
        print("\n" + "="*60)
        print("📊 ANALYSIS RESULTS")
        print("="*60)
        print(analysis)
        
    def generate_exam(self, course_code):
        cache_file = f"analysis_cache_{course_code}.json"
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                analysis = cache_data["analysis"]
        except FileNotFoundError:
            print("❌ No analysis found. Run 'analyze' first.")
            return
        
        course = self.courses.get(course_code, {})
        
        messages = [{
            "role": "user",
            "content": f"""Create a comprehensive mock exam based on this analysis:

Course: {course.get('name', course_code)}
Analysis: {analysis[:1500]}

Generate:
- 8 multiple choice questions (A,B,C,D)
- 4 short answer questions  
- 2 essay questions
- Complete answer key with explanations

Focus on key concepts from the analysis."""
        }]
        
        print("📝 Generating mock exam...")
        exam = self.claude_request(messages, "You are an expert exam creator. Make challenging but fair questions.")
        
        # Save exam
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exam_file = f"mock_exams/EXAM_{course_code}_{timestamp}.txt"
        os.makedirs("mock_exams", exist_ok=True)
        
        with open(exam_file, "w", encoding="utf-8") as f:
            f.write(f"MOCK EXAM - {course.get('name', course_code)}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            f.write(exam)
        
        print(f"💾 Exam saved to {exam_file}")
        print(f"\n{exam}")
        
    def create_plan(self, course_code):
        cache_file = f"analysis_cache_{course_code}.json"
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                analysis = cache_data["analysis"]
        except FileNotFoundError:
            print("❌ No analysis found. Run 'analyze' first.")
            return
        
        course = self.courses.get(course_code, {})
        
        messages = [{
            "role": "user",
            "content": f"""Create a structured study plan:

Course: {course.get('name', course_code)}
Analysis: {analysis[:1500]}

Generate a 4-week study plan with:
- Week-by-week breakdown
- Daily goals (1-2 hours/day)
- Priority topics first
- Review sessions
- Practice checkpoints
- Resource recommendations

Make it practical and achievable."""
        }]
        
        print("📚 Creating study plan...")
        plan = self.claude_request(messages)
        
        # Save plan
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_file = f"study_plans/plan_{course_code}_{timestamp}.txt"
        os.makedirs("study_plans", exist_ok=True)
        
        with open(plan_file, "w", encoding="utf-8") as f:
            f.write(f"STUDY PLAN - {course.get('name', course_code)}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            f.write(plan)
        
        print(f"💾 Plan saved to {plan_file}")
        print(f"\n{plan}")

def main():
    if len(sys.argv) < 3:
        print("🚀 CLAUDE ULTIMATE CLI")
        print("Usage: python3 claude_cli.py [command] [course_code]")
        print("Commands: analyze, exam, plan")
        print("Example: python3 claude_cli.py analyze 18873")
        return
    
    command = sys.argv[1]
    course_code = sys.argv[2]
    
    cli = ClaudeUltimateCLI()
    
    if command == "analyze":
        cli.analyze_course(course_code)
    elif command == "exam":
        cli.generate_exam(course_code)
    elif command == "plan":
        cli.create_plan(course_code)
    else:
        print("❌ Invalid command. Use: analyze, exam, or plan")

if __name__ == "__main__":
    main()