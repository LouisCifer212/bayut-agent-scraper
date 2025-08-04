import streamlit as st
from bayut_whatsapp_scraper import BayutWhatsAppScraper

st.title("Bayut WhatsApp Scraper")

max_pages = st.slider("How many pages to scrape?", 1, 10, 1)

if st.button("Scrape WhatsApp Numbers"):
    st.info("Scraping in progress... please wait.")
    scraper = BayutWhatsAppScraper(headless=True)
    agents = scraper.scrape_bayut_brokers(location="ras-al-khaimah", max_pages=max_pages)
    st.success(f"Found {len(agents)} agents with WhatsApp numbers!")
    st.json(agents)
