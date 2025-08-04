import streamlit as st
import asyncio
from bayut_whatsapp_scraper import BayutPlaywrightScraper

st.title("Bayut WhatsApp Scraper (Playwright)")

# Location selector
location = st.selectbox(
    "Select Location:",
    ["ras-al-khaimah", "dubai", "abu-dhabi", "sharjah", "ajman", "fujairah", "umm-al-quwain"],
    index=0,
    key="location_select"
)

max_pages = st.slider("How many pages to scrape?", 1, 10, 1)

if st.button("Scrape WhatsApp Numbers"):
    st.info(f"Scraping {max_pages} page(s) from {location.replace('-', ' ').title()}... please wait.")
    scraper = BayutPlaywrightScraper()
    agents = asyncio.run(scraper.scrape_whatsapp_numbers(location=location, max_pages=max_pages))
    st.success(f"Found {len(agents)} agents with WhatsApp numbers!")
    st.json(agents)
