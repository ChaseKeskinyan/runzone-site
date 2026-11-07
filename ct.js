// RunZone attribution. Existing campaign names retained for reporting continuity.
(function () {
  'use strict';
  function hostOf(value) { try { return new URL(value).hostname.toLowerCase(); } catch (_) { return ''; } }
  function domain(host, suffix) { return host === suffix || host.endsWith('.' + suffix); }
  function classify(href, ref, ua) {
    var p = new URL(href).searchParams;
    var source = (p.get('utm_source') || '').toLowerCase();
    var medium = (p.get('utm_medium') || '').toLowerCase();
    var h = hostOf(ref);
    if (p.has('gclid') || p.has('msclkid') || /^(cpc|ppc|paidsearch|paid_search)$/.test(medium)) return 'paid-search';
    if (/^(paid_social|paidsocial)$/.test(medium)) return 'paid-social';
    if (source || medium) {
      if (/^(paid|display|cpm)$/.test(medium)) return 'campaign-other';
      if (medium === 'email') return 'email';
      if (source === 'tiktok') return 'tiktok';
      if (source === 'instagram') return 'instagram';
      if (source === 'google' && medium === 'organic') return 'google';
      if (/^(bing|duckduckgo|yahoo)$/.test(source) && medium === 'organic') return 'search-other';
      return 'campaign-other';
    }
    if (domain(h,'getrunzone.app')) return null;
    if (/musical_ly|BytedanceWebview|TikTok/i.test(ua) || domain(h,'tiktok.com')) return 'tiktok';
    if (/Instagram/i.test(ua) || domain(h,'instagram.com')) return 'instagram';
    if (/^(www\.|m\.)?google\.(com|[a-z]{2}|co\.[a-z]{2}|com\.[a-z]{2})$/.test(h)) return 'google';
    if (['bing.com','duckduckgo.com','search.yahoo.com'].some(function(d){return domain(h,d);})) return 'search-other';
    if (['chatgpt.com','chat.openai.com','perplexity.ai'].some(function(d){return domain(h,d);})) return 'ai-search';
    return h ? 'referral' : null;
  }
  function tagged(href, campaign) {
    var u; try { u = new URL(href); } catch (_) { return href; }
    if (u.hostname !== 'apps.apple.com' || !/\/id6816559417(?:\/|$)/.test(u.pathname)) return href;
    if (!u.searchParams.has('ct')) u.searchParams.set('ct', campaign);
    if (!u.searchParams.has('pt')) u.searchParams.set('pt', '128681280');
    if (!u.searchParams.has('mt')) u.searchParams.set('mt', '8');
    return u.href;
  }
  if (typeof module !== 'undefined' && module.exports) { module.exports = {classify:classify, tagged:tagged}; return; }
  var consent = function(){return window.runzoneAnalyticsConsent === true;};
  var channel = classify(location.href, document.referrer, navigator.userAgent) || 'website';
  var landing = location.pathname;
  // Retain existing session campaign continuity; do not store user identifiers or query strings.
  try {
    var old = JSON.parse(sessionStorage.getItem('rz_attribution_v2') || 'null');
    var fresh = classify(location.href, document.referrer, navigator.userAgent);
    var allowed = ['google','search-other','tiktok','instagram','ai-search','website','paid-search','paid-social','email','referral','campaign-other'];
    if (!fresh && old && allowed.indexOf(old.channel) !== -1 && Date.now()-old.at < 1800000) {
      channel = old.channel; landing = old.landing;
    }
    sessionStorage.setItem('rz_attribution_v2', JSON.stringify({channel:channel,landing:landing,at:Date.now()}));
  } catch (_) {}
  function tag(a) { if(a && a.href) a.href = tagged(a.href,channel); }
  function ready() {
    document.querySelectorAll('a[href]').forEach(tag);
    document.addEventListener('click', function(e) {
      var a = e.target.closest ? e.target.closest('a[href]') : null;
      if (!a) return;
      tag(a);
      var u; try {u = new URL(a.href);} catch(_){return;}
      if(u.hostname !== 'apps.apple.com' || !/\/id6816559417(?:\/|$)/.test(u.pathname)) return;
      // Consent integration and a configured GA4 property are required for events.
      if(consent() && typeof window.gtag === 'function') window.gtag('event','app_store_click',{
        source_channel:channel, content_path:location.pathname, landing_path:landing,
        campaign_token:u.searchParams.get('ct'), cta_id:a.dataset.ctaId || 'download', transport_type:'beacon'
      });
    });
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded',ready); else ready();
})();
