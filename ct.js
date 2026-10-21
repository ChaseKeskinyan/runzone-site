// Tag App Store links with an App Store Connect campaign (Analytics > Campaigns) by visitor source.
(function () {
  var ua = navigator.userAgent || '', ref = document.referrer || '', ct = 'website';
  try { ct = sessionStorage.getItem('rz_ct') || ''; } catch (e) { ct = ''; }
  if (!ct) {
    if (/musical_ly|BytedanceWebview|TikTok/i.test(ua) || /tiktok\./i.test(ref)) ct = 'tiktok';
    else if (/Instagram/i.test(ua) || /instagram\./i.test(ref)) ct = 'instagram';
    else if (/google\./i.test(ref)) ct = 'google';
    else if (/bing\.|duckduckgo\.|yahoo\./i.test(ref)) ct = 'search-other';
    else if (/chatgpt\.|openai\.|perplexity\./i.test(ref)) ct = 'ai-search';
    else ct = 'website';
    try { sessionStorage.setItem('rz_ct', ct); } catch (e) {}
  }
  var url = 'https://apps.apple.com/app/apple-store/id6816559417?pt=128681280&ct=' + ct + '&mt=8';
  function tag() { document.querySelectorAll('a[href*="apps.apple.com"]').forEach(function (a) { a.href = url; }); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', tag); else tag();
})();
