# Bayut Agent Scraper (Apify Actor)

Scrapes the Bayut broker directory and extracts:

- Agent / agency name
- Phone number
- City (if available)
- Number of listings
- Profile URL

## How it works
Runs a Playwright crawler:
1. Visits paginated broker list ( ?page=1 … N )
2. Enqueues every broker profile link
3. Extracts the data and pushes it to the default dataset

## Input
```json
{
  "startUrl": "https://www.bayut.com/brokers/",
  "maxPages": 20
}
