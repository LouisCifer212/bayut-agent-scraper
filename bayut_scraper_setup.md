# Bayut WhatsApp Scraper Setup

## Installation

1. Install Chrome browser (if not already installed)
2. Install Python dependencies:
   ```bash
   pip install -r requirements_selenium.txt
   ```

3. Install ChromeDriver automatically:
   ```python
   from webdriver_manager.chrome import ChromeDriverManager
   ChromeDriverManager().install()
   ```

## Usage

### Basic Usage
```python
from bayut_whatsapp_scraper import BayutWhatsAppScraper

# Create scraper (headless=False to see browser, True for background)
scraper = BayutWhatsAppScraper(headless=False)

# Scrape agents from Ras Al Khaimah (max 3 pages)
agents = scraper.scrape_bayut_brokers(location="ras-al-khaimah", max_pages=3)

print(f"Found {len(agents)} agents with WhatsApp numbers!")
```

### What It Does
1. **Opens Bayut brokers page** for Ras Al Khaimah
2. **Finds broker cards** on each page
3. **Extracts agent info**: name, agency, profile link
4. **Clicks WhatsApp buttons** or finds WhatsApp links
5. **Extracts mobile numbers** from WhatsApp URLs
6. **Handles pagination** automatically
7. **Saves results** to JSON file

### Output Format
```json
{
  "name": "Afreen Naaz",
  "agency": "Some Real Estate Agency",
  "whatsapp_number": "+971545695868",
  "profile_link": "https://www.bayut.com/brokers/afreen-naaz-2401461/...",
  "location": "Ras Al Khaimah",
  "source": "Bayut"
}
```

## Features
- ✅ **Clicks WhatsApp buttons** to reveal hidden numbers
- ✅ **Extracts mobile numbers** (not landlines)
- ✅ **Handles multiple pages** automatically
- ✅ **Robust error handling** - continues if one agent fails
- ✅ **Rate limiting** - respectful scraping
- ✅ **Headless or visible** browser mode
- ✅ **JSON export** for easy processing

## Tips
- Start with `headless=False` to see what's happening
- Use `max_pages=1` for testing, then increase
- Check the JSON output to verify data quality
- The scraper is designed to be respectful with delays
