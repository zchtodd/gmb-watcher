const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");

puppeteer.use(StealthPlugin());

const proxyUrl = "http://us.smartproxy.com:10000";

async function crawl(browser) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });

    await page.goto(process.argv[3]);
    await page.waitForNavigation();

    await page.waitFor("h1");

    const name = await page.evaluate(() => {
        return document.querySelector("h1").textContent;
    });

    let data = "";
    if (name != process.argv[2]) {
        data = await page.screenshot({
            path: null,
            encoding: "base64"
        });
    }

    console.log(JSON.stringify({ name: name, data: data }));

    await browser.close();
}

puppeteer
    .launch({
        headless: false,
        ignoreHTTPSErrors: true,
        args: [
            `--proxy-server=${proxyUrl}`,
            "--start-fullscreen",
            "--no-sandbox",
            "--disable-setuid-sandbox"
        ]
    })
    .then(crawl)
    .catch(err => {
        console.error(err);
        process.exit(1);
    });
