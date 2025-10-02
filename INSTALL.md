# 📦 CA' FOSCARI ULTIMATE SYSTEM - KURULUM REHBERİ

## 🚀 HIZLI KURULUM

### 1. Repository'yi Klonlayın
```bash
git clone https://github.com/emrearas/CaFoscariUltimate.git
cd CaFoscariUltimate
```

### 2. Virtual Environment Oluşturun (Önerilen)
```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Bağımlılıkları Kurun
```bash
pip install -r requirements.txt
```

### 4. Sistemi Başlatın
```bash
python main.py
```

---

## 🔧 DETAYLI KURULUM

### Sistem Gereksinimleri
- **Python:** 3.8 veya üstü
- **İşletim Sistemi:** macOS, Linux, Windows
- **RAM:** Minimum 4GB (8GB önerilen)
- **Disk:** 2GB boş alan

### İsteğe Bağlı Bileşenler

#### OCR Desteği için Tesseract
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-tur

# Windows
# https://github.com/UB-Mannheim/tesseract/wiki adresinden indirin
```

#### Video Analizi için FFmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian  
sudo apt-get install ffmpeg

# Windows
# https://ffmpeg.org/download.html adresinden indirin
```

---

## ⚙️ API YAPILANDIRMASI

### 1. Claude API (AI Özellikleri)
1. [console.anthropic.com](https://console.anthropic.com) adresine gidin
2. API key oluşturun
3. Sistemi başlattığınızda key'i girin

### 2. Google Gmail API
1. [console.cloud.google.com](https://console.cloud.google.com) adresine gidin
2. Yeni proje oluşturun
3. Gmail API'yi etkinleştirin
4. OAuth 2.0 credentials oluşturun
5. JSON dosyasını `credentials.json` olarak kaydedin

### 3. Moodle Web Services
1. Moodle'a giriş yapın
2. User menu > Preferences > User account > Security keys
3. 'Create token for service' seçin
4. Service: 'Moodle mobile web service' seçin
5. Token'ı kopyalayın

---

## 🔍 SORUN GİDERME

### Yaygın Hatalar

#### ImportError: No module named 'X'
```bash
pip install --upgrade -r requirements.txt
```

#### Permission Denied Hatası
```bash
# macOS/Linux
sudo chmod +x main.py

# Veya
python main.py
```

#### Tesseract Not Found
```bash
# PATH'i kontrol edin
which tesseract

# macOS'ta Homebrew ile kurduysanız
export PATH="/opt/homebrew/bin:$PATH"
```

#### Gmail API Hatası
- `credentials.json` dosyasının doğru yerde olduğundan emin olun
- OAuth consent screen'i yapılandırın
- Gmail API'nin etkin olduğunu kontrol edin

---

## 🎯 İLK ÇALIŞTIRMA

1. **Sistemi başlatın:** `python main.py`
2. **İlk kurulum ekranı** otomatik açılacak
3. **API anahtarlarını** girin (Claude isteğe bağlı)
4. **Moodle entegrasyonu** kurun
5. **Gmail entegrasyonu** kurun  
6. **Otomatik senkronizasyon** başlatın

### Örnek İlk Kurulum
```
🔧 SİSTEM BİLEŞENLERİ KURULUYOR...
--------------------------------------------------
Claude API Key (isteğe bağlı): sk-ant-xxxxx
Moodle entegrasyonu kurmak istiyor musunuz? (y/n): y
Moodle URL (https://moodle.unive.it): 
Moodle Web Services Token: xxxxxxxxxxxxx
✅ Moodle entegrasyonu kuruldu
Gmail entegrasyonu kurmak istiyor musunuz? (y/n): y
✅ Gmail entegrasyonu kuruldu
✅ Sistem bileşenleri hazır!
```

---

## 📁 KLASÖR YAPISI

Kurulum sonrası oluşacak yapı:
```
CaFoscariUltimate/
├── main.py                    # Ana program
├── moodle_api.py             # Moodle entegrasyonu
├── gmail_analyzer.py         # Gmail analizi
├── content_analyzer.py       # İçerik analizi
├── study_planner.py          # Çalışma planı
├── mock_exam_generator.py    # Mock sınav
├── notification_system.py    # Bildirimler
├── requirements.txt          # Bağımlılıklar
├── README.md                 # Dökümantasyon
├── .gitignore               # Git ignore
├── system_config.json       # Sistem ayarları (otomatik)
├── credentials.json         # Gmail API (manuel)
├── downloads/               # İndirilen dosyalar
└── backup_YYYYMMDD/        # Yedekler (otomatik)
```

---

## 🔒 GÜVENLİK NOTLARI

- **API anahtarları** asla GitHub'a yüklenmez (`.gitignore`)
- **Tüm veriler** local olarak işlenir
- **HTTPS** bağlantıları kullanılır
- **Rate limiting** uygulanır

---

## 💡 İPUÇLARI

### Performans İyileştirme
- SSD kullanın (video/PDF analizi için)
- En az 8GB RAM önerilen
- Stabil internet bağlantısı gerekli

### Kullanım Önerileri
- İlk çalıştırmada `downloads/` klasörüne PDF'leri koyun
- Sınav tarihlerini manuel olarak ekleyin
- Otomatik senkronizasyonu açık tutun

### Yedekleme
- Otomatik yedekleme her gece yapılır
- Manuel yedekleme menüden yapılabilir
- 30 gün boyunca saklanır

---

## 📞 YARDIM

### Debug Modu
```bash
python main.py --debug
```

### Log Dosyaları
- `notification_history.json` - Bildirim logları
- Console output - Hata mesajları

### Destek
- GitHub Issues açın
- Email: 907842@stud.unive.it
- Discord: emrearas#1234

---

**✅ Kurulum tamamlandıktan sonra `README.md` dosyasını okuyun!**