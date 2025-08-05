import asyncio
from playwright.async_api import async_playwright
import json
import re

class BayutPlaywrightScraper:
    def __init__(self):
        self.agents = []
    
    async def scrape_whatsapp_numbers(self, location="ras-al-khaimah", max_pages=1):
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            page = await browser.new_page()
            # User-Agent "umano"
            await page.set_user_agent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            try:
                for page_num in range(1, max_pages + 1):
                    if page_num == 1:
                        url = f"https://www.bayut.com/brokers/{location}/"
                    else:
                        url = f"https://www.bayut.com/brokers/{location}/page-{page_num}/"
                    
                    print(f"Scraping page {page_num}: {url}")
                    
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    await asyncio.sleep(3)  # Attendi un po' di più per caricamento
                    
                    # Salva la pagina per debug
                    content = await page.content()
                    with open(f"page_{page_num}.html", "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Salvata page_{page_num}.html per debug")
                    
                    # Wait for the main content to load
                    try:
                        await page.wait_for_selector("main", timeout=20000)
                    except Exception as e:
                        print(f"Main selector non trovato: {e}")
                        continue
                    
                    agent_articles = await page.query_selector_all("main ul li article")
                    print(f"Found {len(agent_articles)} agent articles on page {page_num}")
                    
                    if len(agent_articles) == 0:
                        print(f"No agents found on page {page_num}, stopping pagination")
                        break
                    
                    for i, article in enumerate(agent_articles):
                        try:
                            agent_link = await article.query_selector("a[href*='/brokers/']")
                            if not agent_link:
                                continue
                                
                            agent_name = await agent_link.text_content()
                            agent_url = await agent_link.get_attribute("href")
                            
                            whatsapp_selectors = [
                                "div[data-testid*='contact'] button[aria-label*='WhatsApp']",
                                "button[href*='whatsapp']",
                                "a[href*='whatsapp']",
                                "button[aria-label*='WhatsApp']",
                                "[data-testid*='whatsapp']",
                                "button[data-testid*='whatsapp']",
                                "a[data-testid*='whatsapp']"
                            ]
                            
                            whatsapp_button = None
                            for selector in whatsapp_selectors:
                                whatsapp_button = await article.query_selector(selector)
                                if whatsapp_button:
                                    break
                            
                            if whatsapp_button:
                                whatsapp_url = await whatsapp_button.get_attribute("href")
                                
                                if whatsapp_url and "whatsapp" in whatsapp_url.lower():
                                    phone_patterns = [
                                        r'phone=(\+?\d+)',
                                        r'wa\.me/(\+?\d+)',
                                        r'whatsapp\.com/send\?phone=(\+?\d+)',
                                        r'(\+971\d{9})',
                                        r'(\d{10,})'
                                    ]
                                    
                                    phone_number = None
                                    for pattern in phone_patterns:
                                        phone_match = re.search(pattern, whatsapp_url)
                                        if phone_match:
                                            phone_number = phone_match.group(1)
                                            break
                                    
                                    if phone_number:
                                        agency_element = await article.query_selector("[data-testid*='agency'], .agency-name, [class*='agency']")
                                        agency_name = await agency_element.text_content() if agency_element else "Unknown Agency"
                                        
                                        agent_data = {
                                            "name": agent_name.strip() if agent_name else "Unknown",
                                            "agency": agency_name.strip() if agency_name else "Unknown Agency",
                                            "whatsapp_number": phone_number,
                                            "profile_link": f"https://www.bayut.com{agent_url}" if agent_url else "",
                                            "location": location.replace("-", " ").title(),
                                            "source": "Bayut",
                                            "page": page_num
                                        }
                                        
                                        self.agents.append(agent_data)
                                        print(f"Found agent: {agent_name} - {phone_number}")
                            
                        except Exception as e:
                            print(f"Error processing agent {i} on page {page_num}: {e}")
                            continue
                    
                    await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Error during scraping: {e}")
            
            finally:
                await browser.close()
        
        return self.agents
