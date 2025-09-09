#!/usr/bin/env python3
"""
Gmail API ile Üniversite Mail Analizi
OAuth2 ile güvenli erişim
"""

import os
import json
import pickle
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText

class GmailAnalyzer:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_file: str = 'credentials.json'):
        """
        Gmail API başlatıcısı
        Args:
            credentials_file: Google API credentials dosyası
        """
        self.credentials_file = credentials_file
        self.token_file = 'gmail_token.pickle'
        self.service = None
        self._setup_gmail_service()
    
    def _setup_gmail_service(self):
        """Gmail API servisini kur"""
        creds = None
        
        # Token dosyası varsa yükle
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Token yoksa veya geçersizse yeni al
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print(f"❌ {self.credentials_file} dosyası bulunamadı!")
                    print("Google Cloud Console'dan indirip bu dosyaya kaydedin.")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Token'ı kaydet
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail API bağlantısı kuruldu")
        except Exception as e:
            print(f"❌ Gmail API hatası: {e}")
    
    def get_university_emails(self, days_back: int = 7) -> List[Dict]:
        """Üniversite maillerini getir"""
        if not self.service:
            print("❌ Gmail servis bağlantısı yok")
            return []
        
        print(f"📧 Son {days_back} günün üniversite mailleri getiriliyor...")
        
        # Tarih hesapla
        since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
        
        # Arama sorguları
        university_queries = [
            f'from:unive.it after:{since_date}',
            f'from:ca-foscari after:{since_date}',
            f'subject:(exam OR sınav OR assignment OR ödev OR deadline) after:{since_date}',
            f'subject:(university OR universit) after:{since_date}'
        ]
        
        all_emails = []
        
        for query in university_queries:
            try:
                result = self.service.users().messages().list(
                    userId='me', q=query, maxResults=50
                ).execute()
                
                messages = result.get('messages', [])
                
                for message in messages:
                    email_data = self._get_email_details(message['id'])
                    if email_data and email_data not in all_emails:
                        all_emails.append(email_data)
                        
            except HttpError as error:
                print(f"Gmail API hatası: {error}")
        
        # Öncelik sıralaması
        all_emails.sort(key=lambda x: (
            x['priority_score'], 
            datetime.fromisoformat(x['date']) if x['date'] else datetime.min
        ), reverse=True)
        
        print(f"✅ {len(all_emails)} önemli mail bulundu")
        return all_emails
    
    def _get_email_details(self, message_id: str) -> Optional[Dict]:
        """Email detaylarını getir"""
        try:
            message = self.service.users().messages().get(
                userId='me', id=message_id, format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Header bilgilerini çıkar
            subject = ''
            from_email = ''
            date = ''
            
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                elif header['name'] == 'From':
                    from_email = header['value']
                elif header['name'] == 'Date':
                    date = header['value']
            
            # Email içeriğini çıkar
            body = self._extract_email_body(message['payload'])
            
            # Öncelik skorunu hesapla
            priority_score = self._calculate_email_priority(subject, from_email, body)
            priority_level = self._get_priority_level(priority_score)
            
            # Kategorize et
            category = self._categorize_email(subject, from_email, body)
            
            return {
                'id': message_id,
                'subject': subject,
                'from': from_email,
                'date': self._parse_date(date),
                'body_preview': body[:300] + "..." if len(body) > 300 else body,
                'full_body': body,
                'priority_score': priority_score,
                'priority_level': priority_level,
                'category': category,
                'action_required': self._requires_action(subject, body),
                'deadlines': self._extract_deadlines(body),
                'keywords': self._extract_keywords(subject + " " + body)
            }
            
        except Exception as e:
            print(f"Email detay hatası: {e}")
            return None
    
    def _extract_email_body(self, payload: Dict) -> str:
        """Email içeriğini çıkar"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        data = part['body']['data']
                        body += base64.urlsafe_b64decode(data).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        data = part['body']['data']
                        html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                        # HTML'den text çıkar (basit)
                        body += re.sub(r'<[^>]+>', '', html_body)
        else:
            if payload['mimeType'] == 'text/plain':
                if 'data' in payload['body']:
                    data = payload['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body.strip()
    
    def _calculate_email_priority(self, subject: str, from_email: str, body: str) -> int:
        """Email öncelik skorunu hesapla"""
        score = 0
        text = (subject + " " + from_email + " " + body).lower()
        
        # Yüksek öncelik kelimeleri
        high_priority_keywords = [
            'urgent', 'deadline', 'exam', 'sınav', 'test', 'quiz',
            'assignment', 'ödev', 'due date', 'teslim tarihi',
            'important', 'önemli', 'critical', 'kritik',
            'action required', 'işlem gerekli', 'reminder', 'hatırlatma'
        ]
        
        for keyword in high_priority_keywords:
            if keyword in text:
                score += 10
        
        # Üniversite domaini bonusu
        if 'unive.it' in from_email or 'ca-foscari' in from_email:
            score += 15
        
        # Tarih yakınlığı bonusu
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(today|bugün|tomorrow|yarın)',
            r'(this week|bu hafta|next week|gelecek hafta)'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, text):
                score += 5
        
        # Spam azaltıcı
        spam_keywords = ['advertisement', 'reklam', 'promotion', 'unsubscribe']
        for keyword in spam_keywords:
            if keyword in text:
                score -= 20
        
        return max(0, score)
    
    def _get_priority_level(self, score: int) -> str:
        """Skor'dan öncelik seviyesi çıkar"""
        if score >= 30:
            return "CRITICAL"
        elif score >= 20:
            return "HIGH"
        elif score >= 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _categorize_email(self, subject: str, from_email: str, body: str) -> str:
        """Email'i kategorize et"""
        text = (subject + " " + body).lower()
        
        if any(word in text for word in ['exam', 'sınav', 'test', 'quiz']):
            return "EXAM"
        elif any(word in text for word in ['assignment', 'ödev', 'homework']):
            return "ASSIGNMENT"
        elif any(word in text for word in ['deadline', 'due date', 'teslim']):
            return "DEADLINE"
        elif any(word in text for word in ['class', 'ders', 'lecture', 'course']):
            return "COURSE"
        elif any(word in text for word in ['meeting', 'toplantı', 'appointment']):
            return "MEETING"
        else:
            return "GENERAL"
    
    def _requires_action(self, subject: str, body: str) -> bool:
        """Eylem gerektiriyor mu?"""
        action_keywords = [
            'please', 'lütfen', 'submit', 'teslim et', 'complete', 'tamamla',
            'register', 'kayıt ol', 'confirm', 'onayla', 'reply', 'yanıtla'
        ]
        
        text = (subject + " " + body).lower()
        return any(keyword in text for keyword in action_keywords)
    
    def _extract_deadlines(self, text: str) -> List[str]:
        """Metinden tarihleri çıkar"""
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}',
            r'\d{1,2}\s+(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\s+\d{4}'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Önemli kelimeleri çıkar"""
        important_words = []
        
        # Büyük harfli kelimeler (kısaltmalar, önemli terimler)
        uppercase_words = re.findall(r'\b[A-Z]{2,}\b', text)
        important_words.extend(uppercase_words)
        
        # Sayılar ve tarihler
        numbers = re.findall(r'\b\d+\b', text)
        important_words.extend(numbers)
        
        return list(set(important_words))
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Email tarihini parse et"""
        try:
            # Gmail date formatı genellikle RFC 2822
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            return None
    
    def generate_email_summary(self, emails: List[Dict]) -> Dict:
        """Email özetini oluştur"""
        if not emails:
            return {"message": "Önemli mail bulunamadı"}
        
        summary = {
            'total_emails': len(emails),
            'critical_count': len([e for e in emails if e['priority_level'] == 'CRITICAL']),
            'high_count': len([e for e in emails if e['priority_level'] == 'HIGH']),
            'categories': {},
            'action_required_count': len([e for e in emails if e['action_required']]),
            'top_senders': {},
            'recent_deadlines': []
        }
        
        # Kategori dağılımı
        for email in emails:
            category = email['category']
            summary['categories'][category] = summary['categories'].get(category, 0) + 1
        
        # En çok mail gönderen
        for email in emails:
            sender = email['from']
            summary['top_senders'][sender] = summary['top_senders'].get(sender, 0) + 1
        
        # En yakın deadline'lar
        all_deadlines = []
        for email in emails:
            if email['deadlines']:
                for deadline in email['deadlines']:
                    all_deadlines.append({
                        'date': deadline,
                        'subject': email['subject']
                    })
        
        summary['recent_deadlines'] = sorted(all_deadlines, key=lambda x: x['date'])[:5]
        
        return summary

def setup_gmail_api():
    """Gmail API kurulumunu yap"""
    print("🔧 Gmail API Kurulumu")
    print("-" * 30)
    print("1. Google Cloud Console'a gidin: https://console.cloud.google.com/")
    print("2. Yeni proje oluşturun veya mevcut birini seçin")
    print("3. Gmail API'yi etkinleştirin")
    print("4. OAuth 2.0 kimlik bilgileri oluşturun (Desktop application)")
    print("5. JSON dosyasını 'credentials.json' olarak kaydedin")
    print()
    
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json dosyası bulunamadı!")
        print("Lütfen Google Cloud Console'dan indirip bu klasöre kaydedin.")
        return None
    
    analyzer = GmailAnalyzer()
    return analyzer

if __name__ == "__main__":
    # Test
    analyzer = setup_gmail_api()
    if analyzer:
        emails = analyzer.get_university_emails(days_back=14)
        
        # Analiz sonuçlarını kaydet
        with open('gmail_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(emails, f, indent=2, ensure_ascii=False)
        
        # Özet oluştur
        summary = analyzer.generate_email_summary(emails)
        
        print("\n📊 EMAIL ANALİZ ÖZETİ")
        print("=" * 40)
        print(f"Toplam mail: {summary['total_emails']}")
        print(f"Kritik: {summary['critical_count']}")
        print(f"Yüksek öncelik: {summary['high_count']}")
        print(f"Eylem gerekli: {summary['action_required_count']}")
        
        print("\n📁 Kategoriler:")
        for cat, count in summary['categories'].items():
            print(f"   {cat}: {count}")
        
        if summary['recent_deadlines']:
            print("\n📅 Yakın Deadline'lar:")
            for dl in summary['recent_deadlines']:
                print(f"   {dl['date']}: {dl['subject']}")
        
        print("\n📁 Veriler 'gmail_analysis.json' dosyasına kaydedildi")