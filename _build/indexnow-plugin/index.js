// After each successful Netlify deploy, tell IndexNow (Bing, Yandex, Seznam, Naver)
// about sitemap URLs whose <lastmod> is within the last 3 days. Never fails the build.
const fs = require('fs');
const https = require('https');
const KEY = '9ab149e2c4e78929d747bb11d62971d4';
const HOST = 'getrunzone.app';

module.exports = {
  onSuccess: async ({ constants }) => {
    try {
      const xml = fs.readFileSync(require('path').join(constants.PUBLISH_DIR, 'sitemap.xml'), 'utf8');
      const cutoff = Date.now() - 3 * 864e5;
      const urls = [...xml.matchAll(/<loc>([^<]+)<\/loc>\s*<lastmod>([^<]+)<\/lastmod>/g)]
        .filter(m => Date.parse(m[2]) >= cutoff).map(m => m[1]);
      if (!urls.length) { console.log('IndexNow: no recently updated URLs'); return; }
      const body = JSON.stringify({ host: HOST, key: KEY, keyLocation: 'https://' + HOST + '/' + KEY + '.txt', urlList: urls });
      const status = await new Promise((res) => {
        const r = https.request({ hostname: 'api.indexnow.org', path: '/indexnow', method: 'POST',
          headers: { 'Content-Type': 'application/json; charset=utf-8', 'Content-Length': Buffer.byteLength(body) } },
          (resp) => { resp.resume(); res(resp.statusCode); });
        r.on('error', (e) => res('error ' + e.message));
        r.setTimeout(15000, () => { r.destroy(); res('timeout'); });
        r.write(body); r.end();
      });
      console.log('IndexNow: submitted ' + urls.length + ' URLs, status ' + status);
    } catch (e) { console.log('IndexNow skipped: ' + e.message); }
  },
};
