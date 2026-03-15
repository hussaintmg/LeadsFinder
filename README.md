# 🤖 AI Lead Agent - Google Maps Edition

This agent automates the discovery of businesses from Google Maps, analyzes their online presence, extracts contact info, and sends AI-personalized outreach emails.

## 📁 Project Structure
- `app.py`: Streamlit Dashboard (UI)
- `maps_scraper.py`: Playwright-based Google Maps crawler
- `website_analyzer.py`: Checks for "WEAK_WEBSITE" or "NO_WEBSITE"
- `email_extractor.py`: Extracts emails from websites
- `email_generator.py`: Generates pitches using AI (g4f)
- `email_sender.py`: Sends emails via SMTP
- `csv_manager.py`: Manages discovery runs & storage

## 🚀 Setup Instructions
1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
2. **Environment Variables:**
   Create a `.env` file in the project directory:
   ```env
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```
3. **Run the App:**
   ```bash
   streamlit run app.py
   ```

## 🛠 Workflow
1. **Lead Discovery:** Enter industry/location. The agent scrapes Google Maps, analyzes sites, and filters for leads that need help or have emails.
2. **Results History:** View every discovery run in separate tables.
3. **Email Center:** Select leads from any run, generate AI emails, and send them in bulk.
