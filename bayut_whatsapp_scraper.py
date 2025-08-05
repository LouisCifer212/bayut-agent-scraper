import asyncio
from playwright.async_api import async_playwright
import json
import re

class BayutPlaywrightScraper:
    def __init__(self):
        self.agents = []
    
    async def scrape_whatsapp_numbers(self, location="ras-al-khaimah", max_pages=1):
        async with async_playwright() as p:
            # Launch browser with stealth options
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            
            # Create context with human-like user agent
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                for page_num in range(1, max_pages + 1):
                    if page_num == 1:
                        url = f"https://www.bayut.com/brokers/{location}/"
                    else:
                        url = f"https://www.bayut.com/brokers/{location}/page-{page_num}/"
                    
                    print(f"Scraping page {page_num}: {url}")
                    
                    # Navigate with extended timeout
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    await asyncio.sleep(3)  # Extra wait for dynamic content
                    
                    # Save page content for debugging
                    try:
                        content = await page.content()
                        with open(f"page_{page_num}.html", "w", encoding="utf-8") as f:
                            f.write(content)
                        print(f"Saved page_{page_num}.html for debugging")
                    except Exception as e:
                        print(f"Could not save HTML file: {e}")
                    
                    # Wait for main content
                    try:
                        await page.wait_for_selector("main", timeout=20000)
                        print("Main content loaded successfully")
                    except Exception as e:
                        print(f"Main selector not found: {e}")
                        # Try alternative selectors
                        try:
                            await page.wait_for_selector("body", timeout=10000)
                            print("Body found, continuing...")
                        except:
                            print("Page seems empty or blocked, skipping...")
                            continue
                    
                    # Find agent articles with multiple selectors
                    agent_selectors = [
                        "main ul li article",
                        "article[data-testid*='agent']",
                        ".agent-card",
                        "[data-testid*='broker']",
                        "li article"
                    ]
                    
                    agent_articles = []
                    for selector in agent_selectors:
                        agent_articles = await page.query_selector_all(selector)
                        if agent_articles:
                            print(f"Found {len(agent_articles)} agents using selector: {selector}")
                            break
                    
                    if len(agent_articles) == 0:
                        print(f"No agents found on page {page_num} with any selector")
                        # Log page title and URL for debugging
                        page_title = await page.title()
                        current_url = page.url
                        print(f"Page title: {page_title}")
                        print(f"Current URL: {current_url}")
                        break
                    
                    # Process each agent
                    for i, article in enumerate(agent_articles):
                        try:
                            # Get agent name and profile link
                            agent_link_selectors = [
                                "a[href*='/brokers/']",
                                "a[href*='/agent/']",
                                "h3 a",
                                ".agent-name a",
                                "a[data-testid*='agent']"
                            ]
                            
                            agent_link = None
                            for selector in agent_link_selectors:
                                agent_link = await article.query_selector(selector)
                                if agent_link:
                                    break
                            
                            if not agent_link:
                                print(f"No agent link found for article {i}")
                                continue
                                
                            agent_name = await agent_link.text_content()
                            agent_url = await agent_link.get_attribute("href")
                            
                            # Look for WhatsApp button with comprehensive selectors
                            whatsapp_selectors = [
                                "button[aria-label*='WhatsApp' i]",
                                "a[href*='whatsapp']",
                                "button[href*='whatsapp']",
                                "[data-testid*='whatsapp' i]",
                                "button[data-testid*='whatsapp' i]",
                                "a[data-testid*='whatsapp' i]",
                                ".whatsapp-button",
                                "[class*='whatsapp' i]",
                                "button[title*='WhatsApp' i]",
                                "a[title*='WhatsApp' i]"
                            ]
                            
                            whatsapp_element = None
                            for selector in whatsapp_selectors:
                                whatsapp_element = await article.query_selector(selector)
                                if whatsapp_element:
                                    print(f"Found WhatsApp element with selector: {selector}")
                                    break
                            
                            if whatsapp_element:
                                # Try to get WhatsApp URL
                                whatsapp_url = await whatsapp_element.get_attribute("href")
                                
                                # If no href, try clicking the button to reveal URL
                                if not whatsapp_url or "whatsapp" not in whatsapp_url.lower():
                                    try:
                                        # Click the WhatsApp button and wait for navigation
                                        async with page.expect_popup() as popup_info:
                                            await whatsapp_element.click()
                                        popup = await popup_info.value
                                        whatsapp_url = popup.url
                                        await popup.close()
                                    except Exception as click_error:
                                        print(f"Could not click WhatsApp button: {click_error}")
                                        continue
                                
                                if whatsapp_url and "whatsapp" in whatsapp_url.lower():
                                    # Extract phone number with improved patterns
                                    phone_patterns = [
                                        r'phone=(\+?\d+)',
                                        r'wa\.me/(\+?\d+)',
                                        r'whatsapp\.com/send\?phone=(\+?\d+)',
                                        r'(\+971\d{8,9})',  # UAE numbers
                                        r'(\+\d{10,15})',   # International format
                                        r'(\d{10,})'        # Fallback for long numbers
                                    ]
                                    
                                    phone_number = None
                                    for pattern in phone_patterns:
                                        phone_match = re.search(pattern, whatsapp_url)
                                        if phone_match:
                                            phone_number = phone_match.group(1)
                                            break
                                    
                                    if phone_number:
                                        # Get additional agent info
                                        agency_selectors = [
                                            "[data-testid*='agency']",
                                            ".agency-name",
                                            "[class*='agency']",
                                            ".company-name",
                                            "[data-testid*='company']"
                                        ]
                                        
                                        agency_name = "Unknown Agency"
                                        for selector in agency_selectors:
                                            agency_element = await article.query_selector(selector)
                                            if agency_element:
                                                agency_text = await agency_element.text_content()
                                                if agency_text and agency_text.strip():
                                                    agency_name = agency_text.strip()
                                                    break
                                        
                                        # Get agent image if available
                                        image_element = await article.query_selector("img")
                                        image_url = ""
                                        if image_element:
                                            image_url = await image_element.get_attribute("src") or ""
                                        
                                        agent_data = {
                                            "name": agent_name.strip() if agent_name else "Unknown",
                                            "agency": agency_name,
                                            "phone": phone_number,
                                            "whatsapp": whatsapp_url,
                                            "profile_link": f"https://www.bayut.com{agent_url}" if agent_url and not agent_url.startswith('http') else agent_url or "",
                                            "image": image_url,
                                            "location": location.replace("-", " ").title(),
                                            "source": "Bayut",
                                            "page": page_num
                                        }
                                        
                                        self.agents.append(agent_data)
                                        print(f"✅ Found agent: {agent_name} - {phone_number}")
                                    else:
                                        print(f"Could not extract phone number from: {whatsapp_url}")
                                else:
                                    print(f"No valid WhatsApp URL found for agent: {agent_name}")
                            else:
                                print(f"No WhatsApp button found for agent: {agent_name}")
                            
                        except Exception as e:
                            print(f"Error processing agent {i} on page {page_num}: {e}")
                            continue
                    
                    # Delay between pages
                    await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Critical error during scraping: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                await browser.close()
        
        print(f"Scraping completed. Total agents found: {len(self.agents)}")
        return self.agents
