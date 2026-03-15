import os
from dotenv import load_dotenv

load_dotenv()

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "") # App Password

# Database Configuration
# Use SQLite locally, can be easily changed to PostgreSQL for deployment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///leads.db")

# Agent Settings
SEARCH_LIMIT = 20 # Leads per search
RETRY_COUNT = 3
TIMEOUT = 30
