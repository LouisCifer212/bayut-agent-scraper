# Bayut WhatsApp Scraper (Playwright)

Web app Python per estrarre numeri WhatsApp degli agenti immobiliari da Bayut, usando Playwright e Streamlit.  
Funziona su Render, senza problemi di Chrome/Selenium.

---

## 🚀 Funzionalità

- Estrae numeri WhatsApp dagli annunci agenti su Bayut
- Supporta tutte le principali città degli Emirati (Dubai, Abu Dhabi, Ras Al Khaimah, ecc.)
- Puoi scegliere quante pagine analizzare (fino a 50 o più)
- Download risultati in JSON o CSV
- Interfaccia web semplice (Streamlit)

---

## 📦 File principali

- `app.py` — Web app Streamlit
- `bayut_whatsapp_scraper.py` — Logica di scraping Playwright
- `requirements.txt` — Dipendenze Python
- `render.yaml` — Configurazione per deploy su Render
- `README.md` — Questo file

---

## 🛠️ Setup rapido

1. **Clona la repo**
   ```bash
   git clone https://github.com/yourusername/bayut-agent-scraper.git
   cd bayut-agent-scraper
Installa le dipendenze
bash
Copy
pip install -r requirements.txt
playwright install chromium
Avvia l'app in locale
bash
Copy
streamlit run app.py
Apri il link che appare nel terminale (di solito http://localhost:8501).
Deploy su Render
Assicurati che la repo abbia il file render.yaml (vedi esempio sopra).
Su Render, collega la repo e deploya come Web Service.
⚡ Uso
Scegli la città e il numero di pagine da analizzare.
Clicca "Scrape WhatsApp Numbers".
Scarica i risultati in JSON o CSV.
📝 Esempio di output
json
Copy
[
  {
    "name": "Afreen Naaz",
    "agency": "Some Real Estate Agency",
    "whatsapp_number": "+971545695868",
    "profile_link": "https://www.bayut.com/brokers/afreen-naaz-2401461/...",
    "location": "Ras Al Khaimah",
    "source": "Bayut",
    "page": 1
  }
]
⚠️ Disclaimer
Solo per uso personale/ricerca.
Rispetta i termini di servizio di Bayut.
Non usare per spam o contatti non richiesti.
Buono scraping!
