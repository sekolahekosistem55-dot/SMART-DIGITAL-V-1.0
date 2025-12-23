import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class Config:
    # Database
    DATABASE_URL = "sqlite:///data/database.db"
    
    # API Keys (gunakan environment variables)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")
    GEMINI_API_KEY_3 = os.getenv("GEMINI_API_KEY_3")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    
    # OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    
    # Email SMTP
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    OTP_EXPIRY_MINUTES = 3
    OTP_BLOCK_MINUTES = 30
    OTP_COOLDOWN_SECONDS = 60
    RATE_LIMIT_SECONDS = 15
    
    # Subjects
    SUBJECTS = {
        "SD": [
            "PENDIDIKAN PANCASILA", "B.INDONESIA", "B.INGGRIS", "MATEMATIKA",
            "IPA", "IPS", "SENI BUDAYA", "PRAKARYA", "PJOK", "INFORMATIKA",
            "B.DAERAH", "BIMBINGAN KONSELING", "AGAMA"
        ],
        "SMP": [
            "PENDIDIKAN PANCASILA", "B.INDONESIA", "B.INGGRIS", "MATEMATIKA",
            "IPA", "IPS", "SENI BUDAYA", "PRAKARYA", "PJOK", "INFORMATIKA",
            "B.DAERAH", "BIMBINGAN KONSELING", "AGAMA"
        ],
        "SMA": [
            "PENDIDIKAN PANCASILA", "B.INDONESIA", "B.INGGRIS", "MATEMATIKA",
            "IPA", "IPS", "SENI BUDAYA", "PRAKARYA", "PJOK", "INFORMATIKA",
            "B.DAERAH", "BIMBINGAN KONSELING", "AGAMA"
        ]
    }
    
    RELIGIONS = ["ISLAM", "KRISTEN", "BUDHA", "HINDU", "KONGHUCU"]
    
    # AI Models
    AI_PROVIDERS = ["gemini", "openai", "cohere"]
    
    # Cache TTL (seconds)
    CACHE_TTL = 86400  # 24 hours
