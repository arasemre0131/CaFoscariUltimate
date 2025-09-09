#!/usr/bin/env python3
"""
API Configuration Manager
Tüm API key'leri ve ayarları merkezi olarak yönetir
"""

import os
import json
from typing import Dict, Optional

class APIConfigManager:
    def __init__(self):
        """API Config Manager başlatıcısı"""
        self.config_dir = "api_keys"
        self.config_file = os.path.join(self.config_dir, "config.json")
        self._ensure_config_dir()
        self.config = self._load_config()
    
    def _ensure_config_dir(self):
        """API keys klasörünü oluştur"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            print(f"📁 {self.config_dir} klasörü oluşturuldu")
    
    def _load_config(self) -> Dict:
        """Konfigürasyonu yükle"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Varsayılan config
        default_config = {
            "moodle": {
                "url": "https://moodle.unive.it",
                "token": "",
                "auto_login": True
            },
            "gmail": {
                "credentials_file": "api_keys/credentials.json",
                "token_file": "api_keys/gmail_token.json",
                "auto_setup": True
            },
            "claude": {
                "api_key": "",
                "auto_load": True
            },
            "notifications": {
                "enabled": True,
                "methods": ["desktop", "sound"]
            }
        }
        
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict):
        """Konfigürasyonu kaydet"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get_moodle_config(self) -> Dict:
        """Moodle ayarlarını al"""
        moodle_config = self.config.get('moodle', {})
        
        # Token'ı ayrı dosyadan da kontrol et
        token_file = os.path.join(self.config_dir, "moodle_token.txt")
        if os.path.exists(token_file) and not moodle_config.get('token'):
            with open(token_file, 'r', encoding='utf-8') as f:
                token = f.read().strip()
                if token:
                    moodle_config['token'] = token
                    self.config['moodle']['token'] = token
                    self._save_config(self.config)
        
        return moodle_config
    
    def set_moodle_token(self, token: str):
        """Moodle token'ını kaydet"""
        self.config['moodle']['token'] = token
        self._save_config(self.config)
        
        # Ayrı dosyaya da kaydet
        token_file = os.path.join(self.config_dir, "moodle_token.txt")
        with open(token_file, 'w', encoding='utf-8') as f:
            f.write(token)
        
        print(f"✅ Moodle token kaydedildi: {self.config_dir}/moodle_token.txt")
    
    def get_gmail_config(self) -> Dict:
        """Gmail ayarlarını al"""
        gmail_config = self.config.get('gmail', {})
        
        # credentials.json'ı kontrol et
        creds_file = os.path.join(self.config_dir, "credentials.json")
        if os.path.exists(creds_file):
            gmail_config['credentials_file'] = creds_file
        
        return gmail_config
    
    def get_claude_config(self) -> Dict:
        """Claude ayarlarını al"""
        claude_config = self.config.get('claude', {})
        
        # API key'i ayrı dosyadan kontrol et
        key_file = os.path.join(self.config_dir, "claude_api_key.txt")
        if os.path.exists(key_file) and not claude_config.get('api_key'):
            with open(key_file, 'r', encoding='utf-8') as f:
                api_key = f.read().strip()
                if api_key:
                    claude_config['api_key'] = api_key
                    self.config['claude']['api_key'] = api_key
                    self._save_config(self.config)
        
        return claude_config
    
    def set_claude_api_key(self, api_key: str):
        """Claude API key'ini kaydet"""
        self.config['claude']['api_key'] = api_key
        self._save_config(self.config)
        
        # Ayrı dosyaya da kaydet
        key_file = os.path.join(self.config_dir, "claude_api_key.txt")
        with open(key_file, 'w', encoding='utf-8') as f:
            f.write(api_key)
        
        print(f"✅ Claude API key kaydedildi: {self.config_dir}/claude_api_key.txt")
    
    def copy_gmail_credentials(self, source_path: str) -> bool:
        """Gmail credentials dosyasını kopyala"""
        try:
            import shutil
            dest_path = os.path.join(self.config_dir, "credentials.json")
            shutil.copy2(source_path, dest_path)
            print(f"✅ Gmail credentials kopyalandı: {dest_path}")
            return True
        except Exception as e:
            print(f"❌ Gmail credentials kopyalama hatası: {e}")
            return False
    
    def show_setup_instructions(self):
        """Kurulum talimatlarını göster"""
        print("\n📋 API KURULUM TALİMATLARI")
        print("=" * 50)
        
        print(f"\n📁 API klasörü: {os.path.abspath(self.config_dir)}")
        print("\n🔑 Aşağıdaki dosyaları bu klasöre koyun:")
        
        # Moodle
        print(f"\n1️⃣ MOODLE TOKEN:")
        print(f"   📄 Dosya: {self.config_dir}/moodle_token.txt")
        print(f"   🔗 URL: https://moodle.unive.it (otomatik)")
        print("   💡 Token almak için:")
        print("      • Moodle'a giriş yap")
        print("      • User menu → Preferences → Security keys")
        print("      • 'Create token for service' → 'Moodle mobile web service'")
        
        # Gmail
        print(f"\n2️⃣ GMAIL API:")
        print(f"   📄 Dosya: {self.config_dir}/credentials.json")
        print("   💡 Google Console'dan indirin")
        
        # Claude
        print(f"\n3️⃣ CLAUDE API:")
        print(f"   📄 Dosya: {self.config_dir}/claude_api_key.txt")
        print("   💡 Anthropic'den API key alın")
        
        print(f"\n✅ Bu dosyaları oluşturduktan sonra sistem otomatik yükleyecek!")
    
    def check_all_apis(self) -> Dict[str, bool]:
        """Tüm API'lerin durumunu kontrol et"""
        status = {}
        
        # Moodle
        moodle = self.get_moodle_config()
        status['moodle'] = bool(moodle.get('token'))
        
        # Gmail
        gmail = self.get_gmail_config()
        status['gmail'] = os.path.exists(gmail.get('credentials_file', ''))
        
        # Claude
        claude = self.get_claude_config()
        status['claude'] = bool(claude.get('api_key'))
        
        return status
    
    def show_status(self):
        """API durumlarını göster"""
        status = self.check_all_apis()
        
        print("\n📊 API DURUM:")
        print("=" * 30)
        
        for api_name, is_ready in status.items():
            icon = "✅" if is_ready else "❌"
            print(f"{icon} {api_name.upper()}: {'Hazır' if is_ready else 'Eksik'}")
        
        missing = [name for name, ready in status.items() if not ready]
        if missing:
            print(f"\n⚠️  Eksik API'ler: {', '.join(missing)}")
            self.show_setup_instructions()
        else:
            print("\n🚀 Tüm API'ler hazır!")

# Global instance
api_config = APIConfigManager()

if __name__ == "__main__":
    # Test ve kurulum
    api_config.show_setup_instructions()
    api_config.show_status()