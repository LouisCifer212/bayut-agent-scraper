import { PlaywrightCrawler, Dataset, log } from 'crawlee';

const startUrls = ['https://www.bayut.com/brokers/?page=1'];

const crawler = new PlaywrightCrawler({
    requestHandlerTimeoutSecs: 180,
    navigationTimeoutSecs: 120,
    maxConcurrency: 2,
    headless: true,

    requestHandler: async ({ request, page, enqueueLinks }) => {
        log.info(`Processing: ${request.url}`);

        // Header realistici
        await page.route('**/*', (route, request) => {
            const headers = {
                ...request.headers(),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
                              '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            };
            route.continue({ headers });
        });

        // Disabilita "navigator.webdriver"
        await page.addInitScript(() => {
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
        });

        await page.goto(request.url, { waitUntil: 'domcontentloaded' });

        const agents = await page.$$eval('.b7f530b3', (elements) =>
            elements.map((el) => {
                const name = el.querySelector('h2')?.innerText || '';
                const phone = el.querySelector('a[href^="tel:"]')?.innerText || '';
                const agency = el.querySelector('.c0df3811')?.innerText || '';
                return { name, phone, agency };
            })
        );

        await Dataset.pushData(agents);

        // Pagine successive
        const currentPage = Number(new URL(request.url).searchParams.get('page')) || 1;
        if (currentPage < 10) {
            const nextPage = currentPage + 1;
            await crawler.addRequests([`https://www.bayut.com/brokers/?page=${nextPage}`]);
        }
    },
});

await crawler.run(startUrls);
