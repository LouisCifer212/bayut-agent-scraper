// Bayut Agent Scraper – Apify Actor con Playwright

import { Actor } from 'apify';
import { PlaywrightCrawler, Dataset } from 'crawlee';

await Actor.init();

const input = await Actor.getInput();
const startUrl = input.startUrl || 'https://www.bayut.com/brokers/';
const maxPages = input.maxPages || 10;

const crawler = new PlaywrightCrawler({
    maxRequestsPerCrawl: maxPages,
    maxConcurrency: 5,
    proxyConfiguration: await Actor.createProxyConfiguration(),
    requestHandler: async ({ request, page, enqueueLinks, log }) => {
        const url = request.url;

        if (url.includes('/brokers/') && !url.includes('/page-')) {
            // LIST PAGE – enqueue broker profiles
await enqueueLinks({
    // nuovo selettore, prende tutti i link che iniziano con /brokers/ e NON hanno di nuovo ?page=
    selector: 'a[href^="/brokers/"]:not([href*="?page="])',
    baseUrl: 'https://www.bayut.com',
    label: 'DETAIL',
});

            });
        } else if (request.label === 'DETAIL') {
            // DETAIL PAGE – extract data
            const name = await page.locator('h1[data-testid="agency-profile-name"]').textContent().catch(() => '');
            const phone = await page.locator('a[href^="tel:"]').first().textContent().catch(() => '');
            const listings = await page.locator('span[data-testid="listing-count"]').textContent().catch(() => '');
            const city = await page.locator('span[data-testid="agency-location"]').textContent().catch(() => '');

            const item = {
                name: name?.trim(),
                phone: phone?.trim(),
                city: city?.trim(),
                listings: listings?.trim(),
                profileUrl: request.url,
            };

            log.info(`Extracted: ${item.name}`);
            await Dataset.pushData(item);
        }
    },
});

await crawler.run([startUrl]);

await Actor.exit();
