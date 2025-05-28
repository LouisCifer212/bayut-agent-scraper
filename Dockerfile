FROM apify/actor-node-playwright:latest

COPY package.json ./
# RIMUOVI o COMMENTA la riga sotto
# COPY package-lock.json ./
RUN npm install

COPY . ./

CMD ["node", "main.js"]
