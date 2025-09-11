# 🚀 Ca' Foscari Ultimate Study System

Complete AI-powered study system for Ca' Foscari University students.  
**Emre Aras (907842) - Ca' Foscari University**

## 📋 Ana Menü İşlevleri

### 1. 🧠 Deep PDF Analysis
- **Ne yapar:** Ders materyallerini (PDF'ler) Claude AI ile analiz eder
- **Nasıl:** Course kodu gir → PDF'leri okur → Analiz sonuçlarını cache'ler
- **Çıktı:** `analysis_cache_[KOD].json` dosyasına kaydeder
- **Örnek:** CT0668-2 dersinin tüm PDF'lerini analiz edip key points çıkarır

### 2. 📝 Generate Mock Exam
- **Ne yapar:** Analiz edilen ders materyallerine dayanarak mock sınav oluşturur
- **Nasıl:** Course kodu gir → Cache'den analiz verilerini alır → Sınav soruları üretir
- **Çıktı:** `mock_exams/` klasörüne sınav dosyası kaydeder
- **Özellik:** Multiple choice, short answer, essay questions

### 3. 📚 Create Study Plan
- **Ne yapar:** 4 haftalık kişiselleştirilmiş çalışma planı oluşturur
- **Nasıl:** Course kodu gir → Cache verilerini kullanır → Günlük goals + exercises
- **Çıktı:** `data/courses/[DERS]/study_plans/` klasörüne kaydeder
- **İçerik:** Daily objectives, self-check questions, resource links

### 4. 💬 Chat with Claude AI
- **Ne yapar:** Interactive AI tutor + email gönderme
- **Özellikler:**
  - "study plan for 18876" → Otomatik study plan oluşturur
  - Email gönderme: "erdeme selam yaz" → Smart email gönderir
  - Conversation memory tutar
- **Akıllı:** Basit sorulara basit yanıtlar, complex sorular için Claude AI

### 5. 🤖 Autonomous Assistant
- **Ne yapar:** Seninle birlikte öğrenen kişisel asistan
- **Özellikler:**
  - Her etkileşimden öğrenir ve seni hatırlar
  - Proactive email monitoring & urgent alerts
  - Study schedule reminders
  - Deadline tracking
  - Context-aware responses
- **Akıllı:** Çalışma saatlerin, stres seviyeni, başarı paternlerini analiz eder

### 6. 🌅 Daily Briefing
- **Ne yapar:** Günlük intelligent rapor oluşturur
- **İçerik:**
  - System status
  - Pending tasks
  - Upcoming deadlines
  - Yesterday's achievements
  - AI suggestions
- **Kullanım:** Tek seferlik rapor görüntüler

### 7. 🧭 Unified Intelligence
- **Ne yapar:** Advanced multi-dimensional AI analysis
- **Özellikler:**
  - NLP + Emotional + Contextual + Historical + Predictive analysis
  - Cross-system data integration
  - Confidence scoring
  - Smart confirmation (< %75 güvende onay ister)
- **Örnek:** "🤔 AI Suggestion: [action] (confidence: 85%) Proceed? (y/n/explain)"

### 8. 🔍 System Status
- **Ne yapar:** Sistem durumu ve configuration check
- **Kontrol eder:**
  - API key durumları (Claude, Gmail, Moodle)
  - Cache files status
  - Error diagnostics
  - Available courses

### 9. ❌ Exit
- **Ne yapar:** Sistemi güvenli şekilde kapatır

## 🔧 Kurulum

1. Repository'yi clone edin
2. `api_keys/` klasörü oluşturun (git'te olmaz)
3. API key'lerinizi ekleyin:
   - `api_keys/claude_api_key.txt`
   - `api_keys/config.json` (Gmail credentials)
4. `python3 main.py` ile başlatın

## 📁 Klasör Yapısı

```
CaFoscariUltimate/
├── main.py                    # Ana program
├── data/courses/              # Course klasörleri
│   └── [CT0668-2] COMPUTER... # Her ders için klasör
│       └── study_plans/       # Study plan'lar burada
├── mock_exams/               # Mock sınavlar
├── *_cache_*.json           # Analiz cache dosyaları
└── api_keys/                # API anahtarları (git'te yok)
```

## 🎯 En Çok Kullanılan

1. **Study Plan:** Chat'te "study plan for 18876" yaz
2. **Email:** Chat'te "erdeme selam nasılsın yaz" 
3. **Analysis:** Menü 1 → Course kodu gir
4. **Mock Exam:** Menü 2 → Course kodu gir

---

### 2. 📚 Moodle Entegrasyonu
**Özellikler:**
- Ders listesi otomatik çekme
- Ödev ve quiz deadline'larını takip
- PDF ve video linklerini toplama
- Takvim etkinliklerini senkronizasyon

**Kullanım:**
1. Moodle Web Services token alın
2. Sistema token'ı girin
3. Otomatik senkronizasyon başlatın

### 3. 📧 Gmail Analizi
**Özellikler:**
- Üniversite maillerini filtreleMe
- Öncelik seviyesi belirleme
- Deadline'ları otomatik çıkarma
- Eylem gerektiren mailleri sınıflandırma

### 4. 🤖 AI Çalışma Planı
**Özellikler:**
- 14 günlük detaylı program
- Zayıf konulara odaklanma
- Pomodoro tekniği entegrasyonu
- Mock sınav zamanları planlama

### 5. 📝 Mock Sınav Sistemi
**Soru Türleri:**
- Çoktan seçmeli (15 soru)
- Kısa cevap (3 soru) 
- Uzun cevap (2 soru)

**Özellikler:**
- Konuya göre soru üretimi
- Zorluk seviyesi ayarlama
- Otomatik cevap anahtarı
- Performans takibi

### 6. 🔔 Bildirim Sistemi
**Bildirim Türleri:**
- Kritik ödev hatırlatmaları
- Sınav tarihi yaklaştığında uyarı
- Yüksek öncelikli mail bildirimi
- Günlük çalışma planı hatırlatması

**Bildirim Kanalları:**
- macOS desktop bildirimi
- Email bildirimi
- Ses uyarısı
- Log dosyası

---

## 📊 VERİ YÖNETİMİ

### Otomatik Oluşturulan Dosyalar
```
📁 CaFoscariUltimate/
├── 📄 system_config.json          # Ana sistem ayarları
├── 📄 moodle_data.json            # Moodle'dan çekilen veriler  
├── 📄 gmail_analysis.json         # Gmail analiz sonuçları
├── 📄 content_analysis.json       # PDF/Video analiz sonuçları
├── 📄 comprehensive_study_plan.json # AI çalışma planı
├── 📄 manual_exams.json           # Manuel eklenen sınav tarihleri
├── 📄 notification_history.json   # Bildirim geçmişi
├── 📁 downloads/                  # İndirilen ders materyalleri
├── 📁 backup_YYYYMMDD/           # Günlük yedekler
└── 📝 mock_exam_*.json           # Oluşturulan mock sınavlar
```

### Yedekleme
- **Otomatik:** Her gece 00:00'da
- **Manuel:** Ana menüden tetiklenebilir
- **Saklama süresi:** 30 gün (ayarlanabilir)

---

## ⚙️ MODÜL DETAYLARI

### 1. `moodle_api.py`
**Moodle Web Services API Entegrasyonu**
- Resmi API endpoint'leri kullanım
- OAuth2 authentication  
- Rate limiting ve error handling
- Course, assignment, event data çekme

### 2. `gmail_analyzer.py`  
**Gmail API ile Mail Analizi**
- IMAP over SSL bağlantı
- Üniversite domain filtresi
- NLP ile öncelik belirleme
- Deadline extraction

### 3. `content_analyzer.py`
**PDF ve Video İçerik Analizi** 
- PyPDF2 ile PDF okuma
- OCR ile metin çıkarma  
- Video metadata analizi
- Keyword extraction ve kategorilendirme

### 4. `study_planner.py`
**AI Destekli Çalışma Planlama**
- Claude API entegrasyonu
- Kişiselleştirilmiş plan üretimi
- Pomodoro tekniği entegrasyonu
- Progress tracking

### 5. `mock_exam_generator.py`
**Mock Sınav Oluşturucu**
- AI powered soru üretimi
- Multiple question types
- Difficulty scaling  
- Auto answer key generation

### 6. `notification_system.py`
**Akıllı Bildirim Sistemi**
- Multi-channel notifications
- Priority-based filtering
- Quiet hours support
- Duplicate prevention

### 7. `main.py`
**Ana Orchestrator Sistemi**
- Modül koordinasyonu
- Zamanlanmış görevler
- Error handling ve logging
- Interactive CLI interface

---

## 🔒 GÜVENLİK

### Veri Güvenliği
- API anahtarları local storage
- Şifreli credential yönetimi
- HTTPS only connections
- Rate limiting implementation

### Privacy
- Sadece educational data processing
- No personal data transmission
- Local data processing önceliği
- GDPR compliance

---

## 🤝 DESTEK

### Sorun Giderme
1. **Import Errors:** `pip install -r requirements.txt`
2. **API Errors:** Token'ları kontrol edin
3. **Permission Errors:** File permissions düzeltin
4. **OCR Issues:** Tesseract kurulumunu kontrol edin

### Log Dosyaları
- `notification_history.json` - Bildirim logları
- `system_config.json` - Hata kayıtları
- Console output - Debug bilgileri

### İletişim
- **Öğrenci:** Emre Aras (907842)
- **Email:** [üniversite email adresi]
- **Program:** Computer Architecture - Ca' Foscari

---

## 📝 LİSANS

Bu proje educational purposes için geliştirilmiştir.
Ca' Foscari Üniversitesi Computer Architecture bölümü öğrenci projesi.

**⚠️ Uyarı:** Bu sistem üniversite sistemleri ile entegre çalışır. Kullanımdan önce üniversite IT politikalarını kontrol ediniz.

---

## 🚀 FEATURES ROADMAP

### v2.0 Planned Features
- [ ] Web dashboard interface
- [ ] Mobile app companion  
- [ ] Study group coordination
- [ ] Grade prediction AI
- [ ] Voice note transcription
- [ ] Calendar app integration

### Known Issues
- OCR accuracy varies by document quality
- Gmail API rate limiting during bulk operations
- Mock exam question quality depends on training data

---

**🎓 CA' FOSCARI ULTIMATE STUDY SYSTEM v1.0**
*Built with ❤️ for academic excellence*