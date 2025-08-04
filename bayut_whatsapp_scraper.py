import asyncio
from playwright.async_api import async_playwright
import json
import re

class BayutPlaywrightScraper:
    def __init__(self):
        self.agents = []
    
    async def scrape_whatsapp_numbers(self, location="ras-al-khaimah", max_pages=1):
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True, channel="chrome")
            page = await browser.new_page()
            
            try:
                for page_num in range(1, max_pages + 1):
                    if page_num == 1:
                        url = f"https://www.bayut.com/brokers/{location}/"
                    else:
                        url = f"https://www.bayut.com/brokers/{location}/page-{page_num}/"
                    
                    print(f"Scraping page {page_num}: {url}")
                    
                    await page.goto(url, wait_until="networkidle")
                    
                    # Wait for the main content to load
                    await page.wait_for_selector("main", timeout=10000)
                    
                    # Find all agent listings following your path
                    agent_articles = await page.query_selector_all("main ul li article")
                    print(f"Found {len(agent_articles)} agent articles on page {page_num}")
                    
                    if len(agent_articles) == 0:
                        print(f"No agents found on page {page_num}, stopping pagination")
                        break
                    
                    for i, article in enumerate(agent_articles):
                        try:
                            # Get agent name and link
                            agent_link = await article.query_selector("a[href*='/brokers/']")
                            if not agent_link:
                                continue
                                
                            agent_name = await agent_link.text_content()
                            agent_url = await agent_link.get_attribute("href")
                            
                            # Try multiple selectors for WhatsApp button
                            whatsapp_selectors = [
                                "div[data-testid*='contact'] button[aria-label*='WhatsApp']",
                                "button[href*='whatsapp']",
                                "a[href*='whatsapp']",
                                "button[aria-label*='WhatsApp']",
                                "[data-testid*='whatsapp']"
                            ]
                            
                            whatsapp_button = None
                            for selector in whatsapp_selectors:
                                whatsapp_button = await article.query_selector(selector)
                                if whatsapp_button:
                                    break
                            
                            if whatsapp_button:
                                # Get WhatsApp URL
                                whatsapp_url = await whatsapp_button.get_attribute("href")
                                
                                if whatsapp_url and "whatsapp" in whatsapp_url.lower():
                                    # Extract phone number from WhatsApp URL
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
                                        # Get agency name if available
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
                    
                    # Small delay between pages
                    await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Error during scraping: {e}")
            
            finally:
                await browser.close()
        
        return self.agents

# Streamlit app
import streamlit as st

st.title("Bayut WhatsApp Scraper (Playwright)")

# Location selector
location = st.selectbox(
    "Select Location:",
    ["ras-al-khaimah", "dubai", "abu-dhabi", "sharjah", "ajman", "fujairah", "umm-al-quwain"],
    index=0
)

# Pages slider
max_pages = st.slider("How many pages to scrape?", 1, 10, 1)

if st.button("Scrape WhatsApp Numbers"):
    st.info(f"Scraping {max_pages} page(s) from {location.replace('-', ' ').title()}... please wait.")
    
    scraper = BayutPlaywrightScraper()
    
    # Run async function in Streamlit
    agents = asyncio.run(scraper.scrape_whatsapp_numbers(location=location, max_pages=max_pages))
    
    st.success(f"Found {len(agents)} agents with WhatsApp numbers!")
    
    if agents:
        # Show summary
        st.write(f"**Summary:**")
        st.write(f"- Total agents: {len(agents)}")
        st.write(f"- Location: {location.replace('-', ' ').title()}")
        st.write(f"- Pages scraped: {max_pages}")
        
        # Show results
        st.json(agents)
        
        # Download options
        json_data = json.dumps(agents, indent=2)
        st.download_button(
            label="Download as JSON",
            data=json_data,
            file_name=f"bayut_agents_{location}_{max_pages}pages.json",
            mime="application/json"
        )
        
        # Convert to CSV for Excel
        import pandas as pd
        df = pd.DataFrame(agents)
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv_data,
            file_name=f"bayut_agents_{location}_{max_pages}pages.csv",
            mime="text/csv"
        )
    else:
        st.warning("No agents found. Try a different location or check if the website structure has changed.")
