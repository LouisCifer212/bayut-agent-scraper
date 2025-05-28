FROM apify/actor-node-playwright:latest

COPY package.json ./
COPY package-lock.json ./
RUN npm install

COPY . ./

CMD ["node", "main.js"]
