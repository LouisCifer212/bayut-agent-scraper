import os
import subprocess
import sys

# Forza il path di Playwright
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/render/.cache/ms-playwright"

# Installa Chromium al runtime se manca
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        p.chromium.launch(headless=True)
except Exception:
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

import streamlit as st
import asyncio
from bayut_whatsapp_scraper import BayutPlaywrightScraper as BayutScraper

st.set_page_config(
    page_title="Bayut WhatsApp Scraper",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Bayut WhatsApp Scraper")
st.markdown("Extract WhatsApp numbers from Bayut real estate agents")

# Sidebar controls
st.sidebar.header("Settings")
location = st.sidebar.selectbox(
    "Select Location:",
    ["ras-al-khaimah", "dubai", "abu-dhabi", "sharjah", "ajman", "fujairah", "umm-al-quwain"],
    key="location_select"
)

max_pages = st.sidebar.slider("Max Pages to Scrape:", 1, 10, 3)

if st.sidebar.button("Scarica HTML pagina 1 (debug)"):
    try:
        with open("page_1.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        st.download_button("Download page_1.html", html_content, file_name="page_1.html")
    except Exception as e:
        st.error(f"Errore nel download: {e}")
    with st.spinner("Scraping WhatsApp numbers..."):
        try:
            scraper = BayutScraper()
            agents = asyncio.run(scraper.scrape_whatsapp_numbers(location=location, max_pages=max_pages))
            
            if agents:
                st.success(f"Found {len(agents)} agents with WhatsApp numbers!")
                
                # Display results
                for i, agent in enumerate(agents, 1):
                    with st.expander(f"Agent {i}: {agent['name']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Name:** {agent['name']}")
                            st.write(f"**Phone:** {agent['phone']}")
                            st.write(f"**WhatsApp:** {agent['whatsapp']}")
                        with col2:
                            if agent['image']:
                                st.image(agent['image'], width=100)
                
                # Download CSV
                import pandas as pd
                df = pd.DataFrame(agents)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"bayut_agents_{location}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No agents with WhatsApp numbers found.")
                
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
            st.error("Please check the logs for more details.")

# Instructions
st.markdown("---")
st.markdown("""
### How to use:
1. Select a location from the dropdown
2. Choose how many pages to scrape (1-10)
3. Click "Start Scraping"
4. Wait for results and download CSV if needed

### Supported Locations:
- Ras Al Khaimah
- Dubai
- Abu Dhabi
- Sharjah
- Ajman
- Fujairah
- Umm Al Quwain
""")
