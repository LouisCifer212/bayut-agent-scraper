// Bayut Agent Scraper – Playwright *Stealth* version
// Uses playwright-extra + stealth plugin to bypass Cloudflare on bayut.com

import { Actor, Dataset } from 'apify';
import { PlaywrightCrawler } from 'crawlee';
// --- STEALTH imports ---
import { chromium } from 'playwright-extra';
import StealthPlugin from 'playwright-extra-plugin-stealth';
chromium.use(StealthPlugin());

await Actor.init();
const { startPage = 1, endPage = 5 } = (await Actor.getInput()) ?? {};

const proxyConfiguration = await Actor.createProxyConfiguration({
  useApifyProxy: true,
  apifyProxyGroups: ['RESIDENTIAL'],
});

const startRequests = Array.from({ length: endPage - startPage + 1 }, (_, i) => ({
  url: `https://www.bayut.com/brokers/?page=${startPage + i}`,
  label: 'LIST',
}));

const crawler = new PlaywrightCrawler({
  // 👉 inject stealth-enabled playwright instance
  launcher: chromium,
  proxyConfiguration,
  headless: true,
  maxConcurrency: 1,
  navigationTimeoutSecs: 150,
  requestHandlerTimeoutSecs: 240,
  launchContext: {
    useChrome: true,
  },
  preNavigationHooks: [
    async ({ page }) => {
      // block heavy assets
      await page.route(/.*\.(png|jpg|jpeg|svg|gif|webp|mp4)$/i, r => r.abort());
    },
  ],
  requestHandler: async ({ request, page, enqueueLinks, log }) => {
    if (request.label === 'LIST') {
      await page.waitForSelector('a[data-testid="broker-card-link"]', { timeout: 30000 });
      await enqueueLinks({
        selector: 'a[data-testid="broker-card-link"]',
        baseUrl: 'https://www.bayut.com',
        label: 'DETAIL',
      });
      return;
    }

    if (request.label === 'DETAIL') {
      await page.waitForSelector('a[href^="tel:"]', { timeout: 30000 });
      const data = await page.evaluate(() => {
        const pick = sel => document.querySelector(sel)?.textContent?.trim() || '';
        return {
          name: pick('h1, [data-testid="agency-name"]'),
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
