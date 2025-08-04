import streamlit as st
import asyncio
from bayut_whatsapp_scraper import BayutPlaywrightScraper

st.title("Bayut WhatsApp Scraper (Playwright)")

location = st.selectbox(
    "Select Location:",
    ["ras-al-khaimah", "dubai", "abu-dhabi", "sharjah", "ajman", "fujairah", "umm-al-quwain"],
    index=0,
    key="location_select"
)

max_pages = st.selectbox(
    "How many pages to scrape?",
    options=[str(i) for i in range(1, 51)],
    index=0,
    key="max_pages_select"
)
max_pages = int(max_pages)

    st.info(f"Scraping {max_pages} page(s) from {location.replace('-', ' ').title()}... please wait.")
    scraper = BayutPlaywrightScraper()
    agents = asyncio.run(scraper.scrape_whatsapp_numbers(location=location, max_pages=max_pages))
    st.success(f"Found {len(agents)} agents with WhatsApp numbers!")
    st.json(agents)
