// Bayut Agent Scraper – Apify Actor (Playwright)

import { Actor, Dataset } from 'apify';
import { PlaywrightCrawler } from 'crawlee';

await Actor.init();

// ---------- INPUT ----------
const input        = await Actor.getInput() || {};
const START_URL    = input.startUrl || 'https://www.bayut.com/brokers/';
const MAX_PAGES    = Number(input.maxPages || 10);
const proxyConfig  = await Actor.createProxyConfiguration({ useApifyProxy: true });

// ---------- BUILD REQUEST LIST ----------
const startRequests = Array.from({ length: MAX_PAGES }, (_, i) => ({
    url  : `${START_URL}?page=${i + 1}`,
    label: 'LIST',
}));

// ---------- CRAWLER ----------
const crawler = new PlaywrightCrawler({
    proxyConfiguration : proxyConfig,
    headless           : true,
    maxConcurrency     : 5,
    requestHandler: async ({ request, page, enqueueLinks, log }) => {

        // ------ LIST PAGE ------
        if (request.label === 'LIST') {
            await page.waitForSelector('a[href^="/brokers/"]:not([href*="?page="])', { timeout: 15000 });

            await enqueueLinks({
                selector : 'a[href^="/brokers/"]:not([href*="?page="])',
                baseUrl  : 'https://www.bayut.com',
                label    : 'DETAIL',
            });
            return;
        }

        // ------ DETAIL PAGE ------
        if (request.label === 'DETAIL') {
            await page.waitForSelector('h1[data-testid="agency-profile-name"]', { timeout: 15000 });

            const data = await page.evaluate(() => {
                const pick = sel => document.querySelector(sel)?.textContent?.trim() || '';
                return {
                    name       : pick('h1[data-testid="agency-profile-name"]'),
                    phone      : document.querySelector('a[href^="tel:"]')?.textContent?.trim() || '',
                    city       : pick('span[data-testid="agency-location"]'),
                    listings   : pick('span[data-testid="listing-count"]'),
                    profileUrl : location.href,
                };
            });

            if (data.name) {
                await Dataset.pushData(data);
                log.info(`Saved: ${data.name}`);
            }
        }
    },
});

await crawler.run(startRequests);
await Actor.exit();
