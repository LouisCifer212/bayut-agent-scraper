import { Actor, Dataset } from 'apify';
import { PlaywrightCrawler } from 'crawlee';

await Actor.init();
const { startPage = 1, endPage = 10 } = await Actor.getInput() ?? {};

const startRequests = [];
for (let p = startPage; p <= endPage; p++) {
    startRequests.push({ url: `https://www.bayut.com/brokers/?page=${p}`, label: 'LIST' });
}

const crawler = new PlaywrightCrawler({
    headless: true,
    maxConcurrency: 1,              // un browser alla volta → RAM ‹ 500 MB
    navigationTimeoutSecs: 90,
    proxyConfiguration: await Actor.createProxyConfiguration(),
    preNavigationHooks: [
        async ({ page }) => {
            // blocca immagini / video
            await page.route('**/*.{png,jpg,jpeg,svg,gif,webp,mp4}', r => r.abort());
            // header e webdriver stealth
            await page.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => false }));
        },
    ],
    requestHandler: async ({ request, page, enqueueLinks, log }) => {
        if (request.label === 'LIST') {
            // link dei broker presenti nel listato
            await page.waitForSelector('a[data-testid="broker-card-link"]', { timeout: 15000 });
            await enqueueLinks({
                selector: 'a[data-testid="broker-card-link"]',
                baseUrl: 'https://www.bayut.com',
                label: 'DETAIL',
            });
            return;
        }

        if (request.label === 'DETAIL') {
            await page.waitForSelector('a[href^="tel:"]', { timeout: 15000 });

            const data = await page.evaluate(() => {
                const pick = sel => document.querySelector(sel)?.textContent?.trim() || '';
                return {
                    name:  pick('h1') || pick('[data-testid="agency-name"]'),
                    phone: document.querySelector('a[href^="tel:"]')?.textContent?.trim() || '',
                    city:  pick('[data-testid="agency-location"]'),
                    listings: pick('[data-testid="listing-count"]'),
                    profileUrl: location.href,
                };
            });

            if (data.name && data.phone) {
                await Dataset.pushData(data);
                log.info(`Saved: ${data.name}`);
            }
            await page.close();      // libera memoria subito
        }
    },
});

await crawler.run(startRequests);
await Actor.exit();
