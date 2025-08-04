
# Bayut WhatsApp Scraper

A Python Selenium-based scraper to extract real estate agent WhatsApp mobile numbers from Bayut’s Ras Al Khaimah brokers directory.

## 🚀 Features

- Clicks WhatsApp buttons to reveal hidden mobile numbers
- Extracts agent name, agency, WhatsApp number, and profile link
- Handles pagination to scrape multiple pages automatically
- Exports results to JSON for easy integration with CRMs (like GoHighLevel)
- Headless or visible browser mode for debugging or background runs
- Robust error handling and logging

## 📦 Files

- `bayut_whatsapp_scraper.py` — Main scraper script (Selenium)
- `requirements_selenium.txt` — Python dependencies
- `bayut_scraper_setup.md` — Setup and usage instructions

## 🛠️ Setup

1. Install Chrome browser (if not already installed)
2. Install Python dependencies:
pip install -r requirements_selenium.txt

3. (Optional) Install ChromeDriver automatically:
```python
from webdriver_manager.chrome import ChromeDriverManager
ChromeDriverManager().install()
⚡ Usage
python
Copy
from bayut_whatsapp_scraper import BayutWhatsAppScraper

# Create scraper (set headless=False to watch browser, True for background)
scraper = BayutWhatsAppScraper(headless=False)

# Scrape agents from Ras Al Khaimah (max 3 pages)
agents = scraper.scrape_bayut_brokers(location="ras-al-khaimah", max_pages=3)

print(f"Found {len(agents)} agents with WhatsApp numbers!")
📝 Output Example
json
Copy
{
  "name": "Afreen Naaz",
  "agency": "Some Real Estate Agency",
  "whatsapp_number": "+971545695868",
  "profile_link": "https://www.bayut.com/brokers/afreen-naaz-2401461/...",
  "location": "Ras Al Khaimah",
  "source": "Bayut"
}
💡 Tips
Start with headless=False to see the browser in action.
Use max_pages=1 for quick tests, then increase for full scraping.
Check the JSON output to verify data quality.
The scraper is designed to be respectful with delays and error handling.
📲 Next Steps
Integrate the output with your CRM (e.g., GoHighLevel)
Use the WhatsApp numbers for direct outreach or campaigns
Automate the script for regular data updates
⚠️ Disclaimer
For personal/research use only.
Respect Bayut’s terms of service and robots.txt.
Do not use for spam or unsolicited contact.
Happy scraping!
