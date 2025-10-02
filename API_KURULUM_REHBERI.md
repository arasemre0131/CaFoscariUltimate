# 🔑 CA' FOSCARI ULTIMATE - API KURULUM REHBERİ

## 🎯 Artık Her Seferinde API Key Sormuyor!

Sistem artık **otomatik** olarak API key'lerini yükler. Bir kez ayarladıktan sonra tekrar sormaz.

## 📁 API Klasörü

Tüm API key'ler şu klasörde saklanır:
```
/Users/eas/Desktop/CaFoscariUltimate/api_keys/
```

## ⚡ HIZLI KURULUM

### ✅ MOODLE (Hazır!)
- **Dosya:** `api_keys/moodle_token.txt` ✅
- **URL:** `https://moodle.unive.it` (otomatik) ✅
- **Token:** Mevcut token otomatik taşındı ✅

### ✅ GMAIL (Hazır!)  
- **Dosya:** `api_keys/credentials.json` ✅
- **Credentials:** Masaüstünden otomatik taşındı ✅

### ❌ CLAUDE API (Opsiyonel)
- **Dosya:** `api_keys/claude_api_key.txt`
- **Nereden:** https://console.anthropic.com/
- **Gerekli mi:** Hayır, sistem Claude olmadan da çalışır

## 🚀 Sistem Artık Nasıl Çalışıyor?

### Eski Sistem (Sinir Bozucu):
```
python3 main.py
> Moodle URL (https://moodle.unive.it): [manuel giriş]
> Moodle Token: [manuel giriş] 
> Gmail kurulsun mu?: [manuel giriş]
> Claude API?: [manuel giriş]
```

### Yeni Sistem (Otomatik):
```
python3 main.py
> ⚙️ Sistem bileşenlerini yapılandır
✅ Moodle token mevcut (api_keys klasöründen yüklendi)
✅ Bağlantı başarılı: Ca' Foscari
✅ Gmail credentials mevcut: api_keys/credentials.json
✅ Gmail API bağlantısı kuruldu
```

## 🔧 API KEY EKLEMEYİ ÇOK KOLAY

### Claude API Key Eklemek İstersen:
1. Anthropic'den API key al
2. Bir dosya oluştur: `api_keys/claude_api_key.txt`
3. API key'i içine yapıştır
4. Kaydet ve kapat
5. **Sistem otomatik yükler!**

### Yeni Gmail Credentials:
1. Google Console'dan `credentials.json` indir
2. `api_keys/credentials.json` olarak kaydet
3. **Sistem otomatik yükler!**

### Yeni Moodle Token:
1. Yeni token al
2. `api_keys/moodle_token.txt` dosyasını aç
3. Eski token'ı sil, yeni token'ı yapıştır
4. **Sistem otomatik yükler!**

## 📊 API DURUMUNU KONTROL ET

```bash
python3 api_config.py
```

Bu komut şunları gösterir:
- ✅ Hangi API'ler hazır
- ❌ Hangi API'ler eksik
- 📋 Eksikler için kurulum talimatları

## 🛡️ GÜVENLİK

- API key'ler sadece `api_keys/` klasöründe
- Git'e yüklenmez (`.gitignore`'da)
- Sadece senin bilgisayarında

## 🎉 SONUÇ

**Artık hiç API key sorulmaz!** Sistem:
- Moodle URL'yi otomatik doldurur
- Token'ları klasörden yükler
- Gmail credentials'ı otomatik bulur
- Claude key varsa otomatik yükler

**Tek seferlik kurulum, sürekli kullanım! 🚀**

---

## 💡 İPUÇLARI

- `api_keys/` klasörünü sil → Sistem yeniden sorar
- Yeni token al → Sadece dosyayı güncelle
- Birden fazla Gmail hesabı → `credentials.json` değiştir

**API key dertleri bitti! 🎯**