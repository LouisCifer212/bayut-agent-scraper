// Bayut Agent Scraper – Apify Actor (Playwright) with Residential proxy

import { Actor, Dataset } from 'apify';
import { PlaywrightCrawler } from 'crawlee';

await Actor.init();
const { startPage = 1, endPage = 10 } = (await Actor.getInput()) ?? {};

// ---------------- proxy ----------------
// Force Apify Residential pool so Cloudflare cannot block easily
const proxyConfiguration = await Actor.createProxyConfiguration({
  useApifyProxy: true,
  apifyProxyGroups: ['RESIDENTIAL'], // requires credits or higher tier
});

// -------------- build list -------------
const startRequests = [];
for (let p = startPage; p <= endPage; p++) {
  startRequests.push({ url: `https://www.bayut.com/brokers/?page=${p}`, label: 'LIST' });
}

// -------------- crawler ---------------
const crawler = new PlaywrightCrawler({
  proxyConfiguration,
  headless: true,
  maxConcurrency: 1,            // keep memory low
  navigationTimeoutSecs: 120,
  requestHandlerTimeoutSecs: 180,
  launchContext: {
    useChrome: true,
  },
  preNavigationHooks: [
    async ({ page }) => {
      // abort heavy assets
      await page.route('**/*.{png,jpg,jpeg,svg,gif,webp,mp4}', r => r.abort());
      // hide webdriver flag
      await page.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => false }));
    },
  ],
  requestHandler: async ({ request, page, enqueueLinks, log }) => {
    if (request.label === 'LIST') {
      await page.waitForSelector('a[data-testid="broker-card-link"]', { timeout: 20000 });
      await enqueueLinks({
        selector: 'a[data-testid="broker-card-link"]',
        baseUrl: 'https://www.bayut.com',
        label: 'DETAIL',
      });
      return;
    }

    if (request.label === 'DETAIL') {
      await page.waitForSelector('a[href^="tel:"]', { timeout: 20000 });
      const data = await page.evaluate(() => {
        const pick = sel => document.querySelector(sel)?.textContent?.trim() || '';
        return {
          name: pick('h1') || pick('[data-testid="agency-name"]'),
          phone: document.querySelector('a[href^="tel:"]')?.textContent?.trim() || '',
          city: pick('[data-testid="agency-location"]'),
          listings: pick('[data-testid="listing-count"]'),
          profileUrl: location.href,
        };
      });
      if (data.name && data.phone) {
        await Dataset.pushData(data);
        log.info(`Saved: ${data.name}`);
      }
      await page.close();
    }
  },
});

await crawler.run(startRequests);
await Actor.exit();
