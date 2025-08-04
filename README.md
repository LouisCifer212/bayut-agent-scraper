# Bayut WhatsApp Scraper (Playwright)

A cloud-friendly Python web app to extract real estate agent WhatsApp numbers from Bayut’s brokers directory, using Playwright and Streamlit.

## 🚀 Features

- Scrapes WhatsApp numbers from Bayut agent listings
- Supports all major UAE locations (Dubai, Abu Dhabi, Ras Al Khaimah, etc.)
- Scrapes up to 50 pages per location (configurable)
- Download results as JSON or CSV
- Runs on Render, no Chrome/Selenium headaches

## 📦 Files

- `app.py` — Streamlit web app
- `bayut_whatsapp_scraper.py` — Playwright-based scraper logic
- `requirements.txt` — Python dependencies
- `render.yaml` — Render deployment config
- `README.md` — This documentation

## 🛠️ Setup

### 1. **Clone the Repo**

```bash
git clone https://github.com/yourusername/bayut-agent-scraper.git
cd bayut-agent-scraper
2. Install Python Dependencies
bash
Copy
pip install -r requirements.txt
playwright install chromium
3. Run the App Locally
bash
Copy
streamlit run app.py
4. Deploy to Render
Make sure your repo includes render.yaml with the following build command:
pip install -r requirements.txt
playwright install chromium
Set the start command to:
streamlit run app.py --server.port $PORT
⚡ Usage
Select the location and number of pages in the web app.
Click "Scrape WhatsApp Numbers".
Download the results as JSON or CSV.
📝 Output Example
json
Copy
[
  {
    "name": "Afreen Naaz",
    "agency": "Some Real Estate Agency",
    "whatsapp_number": "+971545695868",
    "profile_link": "https://www.bayut.com/brokers/afreen-naaz-2401461/...",
    "location": "Ras Al Khaimah",
    "source": "Bayut",
    "page": 1
  }
]
💡 Tips
If you get empty results, try a different location or more pages.
If the site structure changes, update the selectors in bayut_whatsapp_scraper.py.
For large scrapes, start with a small number of pages to test.
⚠️ Disclaimer
For personal/research use only.
Respect Bayut’s terms of service and robots.txt.
Do not use for spam or unsolicited contact.
Happy scraping!
