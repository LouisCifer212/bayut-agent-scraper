## **6. `bayut_scraper_setup.md` (AGGIORNATO)**

```markdown
# Guida Setup — Bayut WhatsApp Scraper

## 1. Prerequisiti

- Python 3.8 o superiore
- pip
- (Opzionale) Git

---

## 2. Clona la repository

```bash
git clone https://github.com/yourusername/bayut-agent-scraper.git
cd bayut-agent-scraper
3. Installa le dipendenze
bash
Copy
pip install -r requirements.txt
playwright install chromium
4. Avvia l'app in locale
bash
Copy
streamlit run app.py
Apri il link che appare nel terminale (di solito http://localhost:8501).

5. Deploy su Render
Assicurati che la repo abbia un file render.yaml così:

yaml
Copy
services:
  - type: web
    name: bayut-agent-scraper
    env: python
    buildCommand: |
      pip install -r requirements.txt
      playwright install chromium
    startCommand: streamlit run app.py --server.port $PORT
    plan: free
Collega la repo su Render, crea un nuovo Web Service e deploya.
6. Usa la web app
Scegli la città e il numero di pagine.
Clicca "Scrape WhatsApp Numbers".
Scarica i risultati in JSON o CSV.
7. Troubleshooting
Nessun risultato? Prova con più pagine o un'altra città.
Errore Playwright? Assicurati che playwright install chromium sia stato eseguito.
Errore Streamlit Duplicate Widget? Ogni widget deve avere un key unico.
8. Aggiornare i selettori
Se Bayut cambia struttura, aggiorna i selettori in bayut_whatsapp_scraper.py.
