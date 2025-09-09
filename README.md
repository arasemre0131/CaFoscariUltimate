# 🎓 CA' FOSCARI ULTIMATE STUDY SYSTEM

**Emre Aras (907842) - Computer Architecture**  
**Ca' Foscari Üniversitesi**

---

## 🚀 SİSTEM ÖZELLİKLERİ

### 📚 Ana Özellikler
- **Moodle API Entegrasyonu** - Resmi Web Services ile güvenli veri çekme
- **Gmail Analiz Sistemi** - Üniversite maillerini otomatik sınıflandırma
- **PDF/Video İçerik Analizi** - Ders materyallerini OCR ile analiz etme
- **AI Powered Çalışma Planı** - Claude API ile kişiselleştirilmiş planlar
- **Mock Sınav Oluşturucu** - Otomatik soru üretimi ve değerlendirme
- **Akıllı Bildirim Sistemi** - Kritik deadline ve görev hatırlatmaları
- **Otomatik Senkronizasyon** - Zamanlanmış veri güncellemeleri

### 🤖 AI Özellikleri
- **Claude 3 Sonnet** entegrasyonu
- Zayıf konulara odaklanmış mock sınavlar
- Performans bazlı çalışma önerileri
- Otomatik içerik analizi ve özetleme
- Akıllı deadline yönetimi

---

## 📦 KURULUM

### Gereksinimler
```bash
pip install requests anthropic google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client schedule PyPDF2 pdfplumber pytesseract pillow opencv-python moviepy
```

### İsteğe Bağlı (OCR ve Video için)
```bash
# macOS
brew install tesseract

# Ubuntu/Debian  
sudo apt-get install tesseract-ocr

# Windows
# Tesseract'ı manuel olarak indirin
```

### Kurulum Adımları
1. **Repoyu klonlayın**
   ```bash
   git clone <repo-url>
   cd CaFoscariUltimate
   ```

2. **Gerekli Python paketlerini kurun**
   ```bash
   pip install -r requirements.txt
   ```

3. **API anahtarlarını hazırlayın**
   - Claude API key: [console.anthropic.com](https://console.anthropic.com)
   - Gmail API credentials: [console.cloud.google.com](https://console.cloud.google.com)
   - Moodle Web Services token: Moodle > User preferences > Security keys

4. **Sistemi başlatın**
   ```bash
   python main.py
   ```

---

## 🔧 YAPILANDIRMA

### İlk Kurulum
Sistem ilk çalıştırıldığında otomatik kurulum başlar:
- Claude API key girişi
- Moodle entegrasyonu kurulumu
- Gmail API yapılandırması
- Bildirim ayarları

### Manuel Yapılandırma Dosyaları
- `system_config.json` - Ana sistem ayarları
- `notification_config.json` - Bildirim kuralları
- `student_profile.json` - Öğrenci profili ve tercihler

---

## 📖 KULLANIM KILAVUZU

### 1. 🏠 Ana Menü
```
1. 🔄 Şimdi tam senkronizasyon yap
2. 🤖 AI analizi ve plan güncellemesi  
3. ⚙️ Sistem bileşenlerini yapılandır
4. 🔔 Bildirim sistemi
5. 📝 Mock sınav oluşturucu
6. 📚 Çalışma planı sistemi
7. ⏰ Otomatik senkronizasyon başlat/durdur
8. 📊 Sistem durumu ve istatistikler
9. 💾 Manuel backup oluştur
10. ❌ Çıkış
```

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