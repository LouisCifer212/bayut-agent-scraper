# Usa l'immagine con Playwright già installato
FROM apify/actor-node-playwright:20

# Copia tutto il contenuto della repo dentro il container
COPY . ./

# Installa solo le dipendenze di produzione, senza quelle opzionali
RUN npm install --quiet --only=prod --no-optional && (npm list || true)

# Specifica il comando che verrà eseguito all'avvio
CMD ["node", "main.js"]
