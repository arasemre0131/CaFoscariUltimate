# 📁 CA' FOSCARI ULTIMATE - DOSYA ORGANİZASYONU

## 🏗️ Klasör Yapısı

Sistem tüm dosyaları otomatik olarak organize eder ve her dersin kendi klasör yapısını oluşturur.

### 📂 Ana Klasörler

```
CaFoscariUltimate/
├── data/                          # Tüm veri dosyaları
│   ├── moodle/                   # Moodle API verileri
│   ├── gmail/                    # Gmail analiz verileri
│   ├── content/                  # İçerik analiz sonuçları
│   └── courses/                  # Ders bazlı organizasyon
│       ├── [Ders_Adi]/
│       │   ├── pdfs/             # Ders PDF'leri
│       │   ├── videos/           # Ders videoları
│       │   ├── documents/        # Diğer dökümanlar
│       │   ├── analysis/         # İçerik analizleri
│       │   ├── mock_exams/       # Ders mock sınavları
│       │   ├── pdf_list.json     # PDF listesi
│       │   ├── video_list.json   # Video listesi
│       │   └── document_list.json # Dokuman listesi
│
├── mock_exams/                    # Mock sınav sistemi
│   ├── created/                  # Oluşturulan sınavlar
│   │   └── [Ders_Adi]/
│   │       ├── exam_*.txt        # Sınav dosyaları
│   │       └── *_meta.json       # Sınav meta verileri
│   ├── completed/                # Tamamlanan sınavlar
│   └── analyses/                 # Sınav analizleri
│       └── [Ders_Adi]/
│           └── analysis_*.json   # Analiz sonuçları
│
├── ai_analyses/                   # AI analiz sonuçları
├── study_plans/                   # Çalışma planları
├── reports/                       # Performans raporları
├── logs/                         # Sistem logları
├── backups/                      # Yedek dosyalar
└── temp/                         # Geçici dosyalar
```

## 📋 Dosya Türleri ve Konumları

### 🎓 Moodle'dan Çekilen Dosyalar

| Dosya Türü | Konum | Format |
|-------------|-------|--------|
| **PDF'ler** | `data/courses/[Ders_Adi]/pdfs/` | PDF |
| **Videolar** | `data/courses/[Ders_Adi]/videos/` | MP4, AVI, vb. |
| **Dökümanlar** | `data/courses/[Ders_Adi]/documents/` | DOC, PPT, vb. |
| **Ders Listeleri** | `data/courses/[Ders_Adi]/` | JSON |

### 📧 Gmail Analiz Verileri

| Veri Türü | Konum | Açıklama |
|-----------|-------|----------|
| **Ham Veriler** | `data/gmail/gmail_data_YYYYMMDD_HHMMSS.json` | Timestampli dosyalar |
| **Son Veriler** | `data/gmail/latest.json` | En güncel analiz |

### 🎯 Mock Sınav Dosyaları

| Dosya Türü | Konum | Açıklama |
|-------------|-------|----------|
| **Sınav Dosyaları** | `mock_exams/created/[Ders_Adi]/` | Oluşturulan sınavlar |
| **Meta Veriler** | `mock_exams/created/[Ders_Adi]/*_meta.json` | Sınav bilgileri |
| **Analiz Sonuçları** | `mock_exams/analyses/[Ders_Adi]/` | Performans analizleri |

## 🔧 Otomatik Organizasyon

Sistem aşağıdaki özellikleri otomatik olarak sağlar:

### ✅ Klasör Oluşturma
- Her ders için otomatik klasör yapısı
- Türkçe karakter ve özel karakter temizliği
- Alt klasör yapısının otomatik oluşturulması

### ✅ Dosya İsimlendirme
- Güvenli dosya isimlendirme (Türkçe karakter dönüşümü)
- Timestamp bazlı benzersiz dosya isimleri
- Metadata dosyaları ile ilişkilendirme

### ✅ Veri Yedekleme
- JSON formatında veri saklama
- `latest.json` dosyalarıyla hızlı erişim
- Timestampli geçmiş veriler

## 📊 Örnek Kullanım

### Sistem Başlattığınızda:
```bash
python3 main.py
```

### Klasör Yapısı Görmek İçin:
```python
from storage_manager import StorageManager
sm = StorageManager()
sm.show_directory_structure()
```

### Ders Klasörü Oluşturmak İçin:
```python
course_paths = sm.create_course_folder("Computer Architecture")
# Otomatik olarak Computer_Architecture/ klasörü oluşur
```

## 🧹 Otomatik Temizlik

Sistem otomatik olarak:
- 30 günden eski geçici dosyaları siler
- Eski backup dosyalarını temizler
- Log dosyalarını organize eder

---
**📝 Not:** Bu organizasyon sistemi tamamen otomatik çalışır. Manuel müdahale gerektirmez.