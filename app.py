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

if st.button("Scrape WhatsApp Numbers", key="scrape_button"):
    st.info(f"Scraping {max_pages} page(s) from {location.replace('-', ' ').title()}... please wait.")
    scraper = BayutPlaywrightScraper()
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
        import json
        import pandas as pd
        
        json_data = json.dumps(agents, indent=2)
        st.download_button(
            label="Download as JSON",
            data=json_data,
            file_name=f"bayut_agents_{location}_{max_pages}pages.json",
            mime="application/json"
        )
        
        # Convert to CSV for Excel
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
