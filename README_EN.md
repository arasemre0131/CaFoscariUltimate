# 🎓 CA' FOSCARI ULTIMATE STUDY SYSTEM

**Advanced AI-Powered Study Management System for Ca' Foscari University**

Emre Aras (907842) - Computer Architecture Department  
Ca' Foscari University, Venice

## 🚀 Features

### 📚 **Moodle Integration**
- Automatic course data synchronization
- PDF, video, and document extraction
- 169+ PDFs automatically organized
- Real-time course content analysis

### 📧 **Gmail Analysis** 
- University email analysis
- Priority email detection
- Deadline tracking
- Smart categorization

### 🎯 **Advanced Mock Exam System**
- PDF content-based exam generation
- Adaptive difficulty adjustment  
- Performance analysis and reporting
- Topic-wise weakness identification

### 🤖 **AI Study Planning**
- Intelligent study schedule generation
- Performance-based recommendations
- Content difficulty assessment
- Personalized learning paths

### 🔔 **Smart Notifications**
- Assignment deadline alerts
- Exam reminders
- High-priority email notifications
- Study plan reminders

### 📊 **Performance Analytics**
- Detailed study progress tracking
- Mock exam performance analysis
- Topic mastery assessment
- Learning curve visualization

## ⚡ Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/arasemre0131/CaFoscariUltimate.git
cd CaFoscariUltimate
pip install -r requirements.txt
```

### 2. API Configuration
The system uses automatic API key management:

```bash
# Create API keys folder (auto-created)
api_keys/
├── moodle_token.txt       # Moodle Web Services token
├── credentials.json       # Gmail API credentials  
└── claude_api_key.txt     # Claude API key (optional)
```

### 3. Run System
```bash
python3 main.py
```

## 🔧 API Setup Guide

### 🌐 **Moodle API**
1. Login to https://moodle.unive.it
2. User menu → Preferences → Security keys
3. Create token for "Moodle mobile web service"
4. Save token to `api_keys/moodle_token.txt`

**URL is auto-filled:** `https://moodle.unive.it` ✅

### 📧 **Gmail API**
1. Go to https://console.cloud.google.com/
2. Create new project → Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop application)
4. Download `credentials.json` → Save to `api_keys/`
5. Configure OAuth consent screen

### 🤖 **Claude API** (Optional)
1. Get API key from https://console.anthropic.com/
2. Save to `api_keys/claude_api_key.txt`
3. **System works without Claude API**

## 🎯 System Workflow

### 1. **Initial Setup** (Option 3)
- ✅ Auto-loads API keys from `api_keys/` folder
- ✅ Auto-fills Moodle URL
- ✅ One-click configuration

### 2. **Data Synchronization** (Option 1)
- Pulls all course data from Moodle
- Analyzes university emails
- Organizes files automatically
- Creates comprehensive database

### 3. **Mock Exam Creation** (Option 5)
- Select course from synchronized data
- Generate exams from PDF content
- Adaptive difficulty based on performance
- Detailed answer analysis

### 4. **Performance Tracking** (Option 6)
- Track exam scores and progress
- Identify weak topics
- Generate improvement recommendations
- Performance visualization

## 📁 File Organization

```
CaFoscariUltimate/
├── data/
│   ├── courses/           # Course-specific folders
│   │   └── [Course_Name]/
│   │       ├── pdfs/      # Course PDFs
│   │       ├── videos/    # Course videos
│   │       └── documents/ # Course documents
│   ├── moodle/           # Moodle API data
│   └── gmail/            # Gmail analysis data
├── mock_exams/
│   ├── created/          # Generated exams
│   ├── completed/        # Finished exams
│   └── analyses/         # Performance reports
└── api_keys/             # API credentials
```

## 🔥 Key Advantages

### **No More Manual API Entry!**
- **Before:** Enter Moodle URL, token, Gmail setup every time
- **After:** One-time setup, automatic loading forever

### **Smart Content Analysis**
- 169+ PDFs automatically analyzed
- Course content difficulty assessment
- Topic extraction and categorization

### **Adaptive Learning**
- Mock exams adjust to your performance
- Weak topic identification
- Personalized study recommendations

### **Comprehensive Integration**
- Moodle + Gmail + AI analysis
- Real-time notifications
- Automated file organization

## 🛠️ Technical Features

- **Storage Manager:** Automated file organization
- **Error Handling:** Robust timezone and date parsing
- **Performance Optimized:** Efficient data processing
- **Security:** API keys stored locally, not in git
- **Cross-Platform:** Works on macOS, Linux, Windows

## 📊 System Status

Current system handles:
- **169 PDFs** from Moodle courses
- **Multiple course integration**
- **Real-time email analysis**
- **Automated mock exam generation**
- **Performance tracking and reporting**

## 🎯 Perfect for Ca' Foscari Students

- **Computer Architecture** course optimization
- **Multi-language support** (English/Italian)
- **University-specific email analysis**
- **Academic calendar integration**
- **Deadline management**

## 🚀 Getting Started

1. **Clone the repository**
2. **Add your API keys to `api_keys/` folder**
3. **Run `python3 main.py`**
4. **Choose Option 3 → Configure system components**
5. **Choose Option 1 → Full synchronization**
6. **Choose Option 5 → Create your first mock exam!**

## 📈 Performance Results

- **Automated processing of 169+ PDFs**
- **Real-time course synchronization**
- **Smart exam generation from content**
- **Comprehensive performance analytics**

---

**🎓 Built for academic excellence at Ca' Foscari University!**

*This system transforms your study workflow with AI-powered automation, comprehensive content analysis, and adaptive learning features.*