"""
Advanced Bayut Scraper with Selenium - Clicks WhatsApp buttons to extract mobile numbers
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--single-process")
chrome_options.add_argument("--disable-software-rasterizer")
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import json
from typing import List, Dict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BayutWhatsAppScraper:
    def __init__(self, headless=True):
        self.setup_driver(headless)
        self.agents_data = []

    def setup_driver(self, headless=True):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_bayut_brokers(self, location="ras-al-khaimah", max_pages=5):
        """Scrape brokers from Bayut with WhatsApp number extraction"""
        base_url = f"https://www.bayut.com/brokers/{location}/"

        try:
            logger.info(f"Starting scrape of {base_url}")
            self.driver.get(base_url)
            time.sleep(3)  # Let page load

            page = 1
            while page <= max_pages:
                logger.info(f"Scraping page {page}")

                # Get all broker cards on current page
                broker_cards = self.get_broker_cards()

                for i, card in enumerate(broker_cards):
                    try:
                        agent_data = self.extract_agent_from_card(card, i)
                        if agent_data:
                            self.agents_data.append(agent_data)
                            logger.info(f"✓ Extracted: {agent_data.get('name')} - {agent_data.get('whatsapp_number')}")
                    except Exception as e:
                        logger.warning(f"Error processing card {i}: {str(e)}")
                        continue

                # Try to go to next page
                if not self.go_to_next_page():
                    logger.info("No more pages found")
                    break

                page += 1
                time.sleep(2)

        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
        finally:
            self.driver.quit()

        return self.agents_data

    def get_broker_cards(self):
        """Get all broker cards on current page"""
        try:
            # Wait for broker cards to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='broker-card']")))
            cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='broker-card']")
            logger.info(f"Found {len(cards)} broker cards on page")
            return cards
        except TimeoutException:
            logger.warning("No broker cards found on page")
            return []

    def extract_agent_from_card(self, card, card_index):
        """Extract agent data from a single broker card"""
        agent_data = {
            'name': '',
            'agency': '',
            'whatsapp_number': '',
            'profile_link': '',
            'location': 'Ras Al Khaimah',
            'source': 'Bayut'
        }

        try:
            # Extract name
            name_elem = card.find_element(By.CSS_SELECTOR, "h3, h4, .broker-name, [data-testid='broker-name']")
            agent_data['name'] = name_elem.text.strip()
        except NoSuchElementException:
            logger.warning(f"No name found for card {card_index}")

        try:
            # Extract agency
            agency_elem = card.find_element(By.CSS_SELECTOR, ".agency-name, .company-name, [data-testid='agency-name']")
            agent_data['agency'] = agency_elem.text.strip()
        except NoSuchElementException:
            pass

        try:
            # Extract profile link
            profile_link = card.find_element(By.CSS_SELECTOR, "a[href*='/brokers/']")
            agent_data['profile_link'] = profile_link.get_attribute('href')
        except NoSuchElementException:
            pass

        # Extract WhatsApp number - this is the key part!
        whatsapp_number = self.extract_whatsapp_number(card, card_index)
        agent_data['whatsapp_number'] = whatsapp_number

        # Only return if we have name and WhatsApp number
        if agent_data['name'] and agent_data['whatsapp_number']:
            return agent_data

        return None

    def extract_whatsapp_number(self, card, card_index):
        """Extract WhatsApp number by finding and processing WhatsApp links"""
        try:
            # Method 1: Look for existing WhatsApp links in the HTML
            whatsapp_links = card.find_elements(By.CSS_SELECTOR, "a[href*='api.whatsapp.com']")

            for link in whatsapp_links:
                href = link.get_attribute('href')
                number = self.parse_whatsapp_url(href)
                if number:
                    return number

            # Method 2: Look for WhatsApp buttons and click them
            whatsapp_buttons = card.find_elements(By.CSS_SELECTOR, 
                "button[aria-label*='WhatsApp'], button[title*='WhatsApp'], .whatsapp-btn, [data-testid*='whatsapp']")

            for button in whatsapp_buttons:
                try:
                    # Scroll to button and click
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(0.5)
                    button.click()
                    time.sleep(1)

                    # Check if a WhatsApp link appeared
                    whatsapp_links = card.find_elements(By.CSS_SELECTOR, "a[href*='api.whatsapp.com']")
                    for link in whatsapp_links:
                        href = link.get_attribute('href')
                        number = self.parse_whatsapp_url(href)
                        if number:
                            return number

                except Exception as e:
                    logger.debug(f"Error clicking WhatsApp button: {str(e)}")
                    continue

            # Method 3: Look for phone number patterns in onclick handlers or data attributes
            clickable_elements = card.find_elements(By.CSS_SELECTOR, "[onclick*='whatsapp'], [data-phone], .phone-btn")

            for elem in clickable_elements:
                onclick = elem.get_attribute('onclick') or ''
                data_phone = elem.get_attribute('data-phone') or ''

                # Look for phone numbers in these attributes
                for text in [onclick, data_phone]:
                    if text:
                        phone_match = re.search(r'971\d{9}', text)
                        if phone_match:
                            return '+' + phone_match.group()

        except Exception as e:
            logger.debug(f"Error extracting WhatsApp number from card {card_index}: {str(e)}")

        return ''

    def parse_whatsapp_url(self, url):
        """Parse phone number from WhatsApp URL"""
        if not url:
            return ''

        # Extract phone number from URL like: https://api.whatsapp.com/send/?phone=971545695868&text=...
        match = re.search(r'phone=(\d+)', url)
        if match:
            phone = match.group(1)
            # Ensure it starts with +
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        return ''

    def go_to_next_page(self):
        """Navigate to next page if available"""
        try:
            # Look for next page button
            next_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "a[aria-label='Next'], button[aria-label='Next'], .pagination-next, [data-testid='pagination-next']")

            for button in next_buttons:
                if button.is_enabled() and button.is_displayed():
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(3)
                    return True

            return False

        except Exception as e:
            logger.debug(f"Error navigating to next page: {str(e)}")
            return False

    def save_results(self, filename="bayut_agents_whatsapp.json"):
        """Save results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.agents_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.agents_data)} agents to {filename}")
        return filename

# Usage example
def main():
    scraper = BayutWhatsAppScraper(headless=False)  # Set to True for headless mode

    try:
        agents = scraper.scrape_bayut_brokers(location="ras-al-khaimah", max_pages=3)

        print(f"\n🎉 Successfully scraped {len(agents)} agents with WhatsApp numbers!")

        # Show sample results
        for i, agent in enumerate(agents[:5]):  # Show first 5
            print(f"\n{i+1}. {agent['name']}")
            print(f"   Agency: {agent['agency']}")
            print(f"   WhatsApp: {agent['whatsapp_number']}")
            print(f"   Profile: {agent['profile_link']}")

        # Save results
        filename = scraper.save_results()
        print(f"\n💾 Results saved to: {filename}")

    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")

if __name__ == "__main__":
    main()
