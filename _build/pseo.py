#!/usr/bin/env python3
"""RunZone programmatic SEO pages.

Usage (from repo root):
  python3 _build/pseo.py --release 10     # publish the next 10 queued pages
  python3 _build/pseo.py --status         # show how many are published / queued

Two page families, each with real, page-specific numbers:
  /zone-2-heart-rate-for-<age>-year-old/   (ages 20-65)
  /<goal>-pace-chart/                       (5K, 10K, half and marathon goal times)
Hubs: /zone-2-heart-rate-by-age/ and /running-pace-charts/ list whatever is published.
State lives in _build/published.json. Sitemap, llms.txt and hubs are updated on each release.
"""
import argparse, html, json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "_build", "published.json")
DOMAIN = "https://getrunzone.app"
APP = "https://apps.apple.com/us/app/runzone-run-coach/id6816559417"
TODAY = datetime.date.today().isoformat()
MONTH = datetime.date.today().strftime("%B %Y")
esc = lambda s: html.escape(s, quote=True)
LIVE = set()  # slugs that are published (links only go to these)

# ------------------------------------------------------------------ shell (header/footer copied from a live page)
_ref = open(os.path.join(ROOT, "zone-2-calculator", "index.html")).read()
HEADER = _ref[_ref.index("<body>"):_ref.index('<main class="wrap">')]
FOOTER = _ref[_ref.index("<footer>"):_ref.index("</footer>") + len("</footer>")]
FAVICON = re.search(r'<link rel="icon" href="([^"]+)">', _ref).group(1)
APPLE = re.search(r'<svg viewBox="0 0 24 24".*?</svg>', _ref, re.S).group(0)


def shell(slug, title, desc, h1, body, schema, crumb, crumb_url):
    url = f"{DOMAIN}/{slug}/"
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "RunZone", "item": DOMAIN + "/"},
        {"@type": "ListItem", "position": 2, "name": crumb, "item": DOMAIN + crumb_url},
        {"@type": "ListItem", "position": 3, "name": h1, "item": url}]}
    lds = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>\n' for s in (schema if isinstance(schema, list) else [schema]) + [bc])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="apple-itunes-app" content="app-id=6816559417">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta name="theme-color" content="#0E0E0E">
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="/style.css">
<script defer src="https://track.datalyr.com/dl.js" data-workspace-id="G58dbYMy9i"></script>
{lds}</head>
{HEADER}<main class="wrap">
<div class="crumbs"><a href="/">RunZone</a> / <a href="{crumb_url}">{esc(crumb)}</a></div>
<h1>{esc(h1)}</h1>
<div class="meta">By the RunZone team · Updated {MONTH}</div>
{body}
{FOOTER}
</main>
</body>
</html>
'''


def cta(t, s):
    return f'<div class="card cta"><h3>{esc(t)}</h3><p>{esc(s)}</p><a class="btn" href="{APP}">{APPLE}Download RunZone</a></div>'


def faq_block(pairs):
    return "<h2>FAQ</h2>" + "".join(f"<h3>{esc(q)}</h3><p>{a}</p>" for q, a in pairs)


def faq_schema(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in pairs]}


# ------------------------------------------------------------------ heart rate by age
def band_note(age):
    if age < 30:
        return ("In your 20s, recovery is fast, so the main risk is running every run too hard. "
                "Most runners this age can handle 3–5 Zone 2 runs a week plus one harder session.")
    if age < 40:
        return ("In your 30s, work and life stress often push resting heart rate up. Zone 2 is the "
                "easiest way to keep building fitness without adding fatigue. Aim for 3–4 Zone 2 runs a week.")
    if age < 50:
        return ("In your 40s, recovery takes a little longer, so keeping most runs in Zone 2 matters more. "
                "Pair 3–4 easy runs a week with 2 short strength sessions.")
    if age < 60:
        return ("In your 50s, Zone 2 lets you build aerobic fitness while protecting your joints. "
                "3–4 easy sessions a week, mixed with walking or cycling, works well for many people.")
    return ("In your 60s, steady Zone 2 work is one of the best ways to maintain cardiovascular fitness. "
            "Start with brisk walking or walk-run sessions, and check with your doctor before starting a new program.")


def hr_page(age):
    mx = 220 - age
    tan = round(208 - 0.7 * age)
    z = lambda m, a, b: (round(m * a), round(m * b))
    zones = [("Zone 1 · Recovery", .5, .6), ("Zone 2 · Easy aerobic", .6, .7), ("Zone 3 · Tempo", .7, .8),
             ("Zone 4 · Threshold", .8, .9), ("Zone 5 · Max", .9, 1.0)]
    z2 = z(mx, .6, .7)
    k = lambda r: (round(r + (mx - r) * .6), round(r + (mx - r) * .7))
    rows = "".join(f"<tr><td>{n}</td><td>{z(mx,a,b)[0]}–{z(mx,a,b)[1]} bpm</td><td>{z(tan,a,b)[0]}–{z(tan,a,b)[1]} bpm</td></tr>" for n, a, b in zones)
    krows = "".join(f"<tr><td>{r} bpm</td><td>{k(r)[0]}–{k(r)[1]} bpm</td></tr>" for r in (50, 55, 60, 65, 70, 75))
    slug = f"zone-2-heart-rate-for-{age}-year-old"
    pairs = [
        (f"What is Zone 2 heart rate for a {age}-year-old?",
         f"Using the common 220-minus-age estimate, max heart rate is about {mx} bpm, so Zone 2 (60–70% of max) is about {z2[0]}–{z2[1]} bpm. Adding your resting heart rate gives a more personal range."),
        (f"Is {z2[1]} bpm too high for Zone 2 at {age}?",
         f"Not necessarily. {z2[1]} bpm is the top of the estimated range for age {age}. Max heart rate varies by 10–15 bpm between people, so use the talk test as a check: if you can speak in full sentences, you're close to Zone 2."),
        ("How do I find my exact Zone 2?",
         'Add your resting heart rate to the <a href="/zone-2-calculator/">Zone 2 calculator</a> (Karvonen method), or get a lab test. The talk test is a good free cross-check.'),
    ]
    body = f'''
<p class="lead">For a {age}-year-old, Zone 2 heart rate is roughly <strong>{z2[0]}–{z2[1]} bpm</strong>, based on an estimated max heart rate of {mx} bpm. If you know your resting heart rate, the Karvonen table below gives a more personal range.</p>
<h2>All 5 heart rate zones at age {age}</h2>
<table><tr><th>Zone</th><th>220 − age (max {mx})</th><th>Tanaka formula (max {tan})</th></tr>{rows}</table>
<p class="note">Two common max heart rate estimates: 220 minus age, and the Tanaka formula (208 − 0.7 × age). Real max heart rate can differ from both by 10–15 bpm.</p>
<h2>Zone 2 at age {age} by resting heart rate</h2>
<p>The Karvonen method uses your heart rate reserve (max minus resting), so fitter people with lower resting heart rates get a range that fits them better. Zone 2 = resting + 60–70% of reserve.</p>
<table><tr><th>Resting heart rate</th><th>Zone 2 (Karvonen)</th></tr>{krows}</table>
<p>Want it exact? Use the <a href="/zone-2-calculator/">Zone 2 calculator</a> with your own numbers.</p>
<h2>Zone 2 training at {age}</h2>
<p>{band_note(age)}</p>
<ul>
<li><strong>Talk test:</strong> full sentences means you're in Zone 2.</li>
<li><strong>Expect to slow down:</strong> many runners need to run 1–2 minutes per mile slower at first.</li>
<li><strong>Track progress:</strong> your pace at the same heart rate should improve over 4–8 weeks. <a href="/how-long-until-zone-2-works/">How long Zone 2 takes</a>.</li>
</ul>
<p class="note">General fitness information, not medical advice. If you have a heart condition or take medication that affects heart rate, ask your doctor before training by heart rate.</p>
''' + cta("Your Zone 2, coached live", "RunZone calculates your zones and tells you in your ear when you drift out of Zone 2 while the app is open. Works with Apple Watch through Apple Health, or by pace with just your phone.") + faq_block(pairs)
    nb = sorted([a for a in sorted(range(20, 66), key=lambda a: abs(a - age)) if a != age and f"zone-2-heart-rate-for-{a}-year-old" in LIVE][:4])
    body += "<h2>Other ages</h2><p>" + "".join(f'<a href="/zone-2-heart-rate-for-{a}-year-old/">Age {a}</a> · ' for a in nb) + '<a href="/zone-2-heart-rate-by-age/">All ages</a></p>'
    title = f"Zone 2 Heart Rate for a {age}-Year-Old ({z2[0]}–{z2[1]} bpm) | RunZone"
    desc = f"Zone 2 heart rate for a {age}-year-old is about {z2[0]}–{z2[1]} bpm. See all 5 zones at age {age}, Karvonen ranges by resting heart rate, and how to train."
    schema = [{"@context": "https://schema.org", "@type": "Article", "headline": f"Zone 2 heart rate for a {age}-year-old", "datePublished": TODAY, "dateModified": TODAY,
               "author": {"@type": "Organization", "name": "RunZone"}, "publisher": {"@type": "Organization", "name": "RunZone", "url": DOMAIN}}, faq_schema(pairs)]
    return slug, title, desc, shell(slug, title, desc, f"Zone 2 heart rate for a {age}-year-old", body, schema, "Heart rate by age", "/zone-2-heart-rate-by-age/")


# ------------------------------------------------------------------ pace charts
DIST = {"5k": (5.0, "5K"), "10k": (10.0, "10K"), "half-marathon": (21.0975, "half marathon"), "marathon": (42.195, "marathon")}
GOALS = [("5k", 20 * 60), ("5k", 22 * 60), ("5k", 25 * 60), ("5k", 28 * 60), ("5k", 30 * 60), ("5k", 35 * 60),
         ("10k", 45 * 60), ("10k", 50 * 60), ("10k", 55 * 60), ("10k", 60 * 60),
         ("half-marathon", 105 * 60), ("half-marathon", 110 * 60), ("half-marathon", 120 * 60), ("half-marathon", 135 * 60), ("half-marathon", 150 * 60),
         ("marathon", 210 * 60), ("marathon", 225 * 60), ("marathon", 240 * 60), ("marathon", 270 * 60), ("marathon", 300 * 60)]


def fmt(t, hours=None):
    t = round(t); h, m, s = t // 3600, t % 3600 // 60, t % 60
    return f"{h}:{m:02d}:{s:02d}" if (h or hours) else f"{m}:{s:02d}"


def goal_label(sec):
    h, m = sec // 3600, sec % 3600 // 60
    return f"{h}:{m:02d}" if h else f"{m}"


def goal_slug(sec):
    h, m = sec // 3600, sec % 3600 // 60
    return f"{h}-{m:02d}" if h else f"{m}"


def pace_page(dkey, sec):
    km, dname = DIST[dkey]
    miles = km / 1.609344
    pkm, pmi = sec / km, sec / km * 1.609344
    lab = goal_label(sec)
    unit = "" if sec >= 3600 else " minutes"
    slug = f"sub-{goal_slug(sec)}-{dkey}-pace-chart"
    use_km = km <= 10
    if use_km:
        splits = "".join(f"<tr><td>{i} km</td><td>{fmt(pkm*i)}</td></tr>" for i in range(1, int(km) + 1))
        split_head = "Kilometer"
    else:
        marks = [i for i in range(1, int(miles) + 1)] + [round(miles, 1)]
        splits = "".join(f"<tr><td>Mile {m}</td><td>{fmt(pmi*m)}</td></tr>" for m in marks)
        split_head = "Mile"
    eq = "".join(f"<tr><td>{n}</td><td>{fmt(sec*(d/km)**1.06)}</td></tr>" for k2, (d, n) in DIST.items() if k2 != dkey)
    easy_lo, easy_hi = pmi + 60, pmi + 120
    weekly = {"5k": "15–25 miles", "10k": "20–30 miles", "half-marathon": "25–40 miles", "marathon": "35–55 miles"}[dkey]
    long_run = {"5k": "5–7 miles", "10k": "7–9 miles", "half-marathon": "10–13 miles", "marathon": "16–20 miles"}[dkey]
    nice = f"sub-{lab}{unit} {dname}"
    pairs = [
        (f"What pace do I need for a {nice}?", f"About {fmt(pmi)} per mile ({fmt(pkm)} per km), held for the full {dname}."),
        (f"How fast should my easy runs be for a {nice}?", f"Roughly {fmt(easy_lo)}–{fmt(easy_hi)} per mile, or whatever keeps you in Zone 2. Easy runs should feel conversational."),
        (f"How much should I run per week for a {nice}?", f"Many runners aiming for this goal run around {weekly} a week, with a long run of {long_run}. Build up gradually, about 10% a week at most."),
    ]
    body = f'''
<p class="lead">To run a <strong>{nice}</strong>, you need to average <strong>{fmt(pmi)} per mile</strong> ({fmt(pkm)} per km). Here are your exact splits, equivalent race times and the easy pace to train at.</p>
<h2>Splits</h2>
<table><tr><th>{split_head}</th><th>Time at goal pace</th></tr>{splits}</table>
<h2>Equivalent race times</h2>
<p>Based on the Riegel formula, a {nice} is roughly equivalent to:</p>
<table><tr><th>Distance</th><th>Equivalent time</th></tr>{eq}</table>
<p class="note">Predictions assume you've trained for the distance, so treat longer-distance equivalents as optimistic.</p>
<h2>How to train for a {nice}</h2>
<ul>
<li><strong>Easy pace:</strong> about {fmt(easy_lo)}–{fmt(easy_hi)} per mile, or in <a href="/zone-2-calculator/">Zone 2</a>. Most of your miles should be here.</li>
<li><strong>Weekly volume:</strong> many runners aiming for this goal run around {weekly} a week.</li>
<li><strong>Long run:</strong> build to {long_run}.</li>
<li><strong>One quality session a week:</strong> intervals or a tempo run near goal pace.</li>
<li><strong>Pacing on race day:</strong> start slightly slower than {fmt(pmi)}/mile and speed up in the second half.</li>
</ul>
<p>Not sure what you can run now? Use the <a href="/pace-calculator/">pace calculator</a> with a recent race time.</p>
''' + cta(f"A plan for your {dname} goal", "RunZone builds your weekly plan around your goal and schedule, keeps easy runs in Zone 2 with live voice cues, and charts your pace getting faster at the same heart rate.") + faq_block(pairs)
    sibs = [g for g in GOALS if not (g[0] == dkey and g[1] == sec) and f"sub-{goal_slug(g[1])}-{g[0]}-pace-chart" in LIVE]
    sibs = sorted(sibs, key=lambda g: g[0] != dkey)[:5]
    body += "<h2>Other goal times</h2><p>" + "".join(f'<a href="/sub-{goal_slug(s)}-{dk}-pace-chart/">Sub-{goal_label(s)} {DIST[dk][1]}</a> · ' for dk, s in sibs) + '<a href="/running-pace-charts/">All pace charts</a></p>'
    title = f"Sub-{lab} {dname.title() if dname[0].isalpha() else dname} Pace Chart ({fmt(pmi)}/mi) | RunZone".replace("5K Pace", "5K Pace")
    desc = f"Pace chart for a {nice}: {fmt(pmi)} per mile ({fmt(pkm)}/km), full splits, equivalent race times and the easy pace to train at."
    schema = [{"@context": "https://schema.org", "@type": "Article", "headline": f"{nice} pace chart", "datePublished": TODAY, "dateModified": TODAY,
               "author": {"@type": "Organization", "name": "RunZone"}, "publisher": {"@type": "Organization", "name": "RunZone", "url": DOMAIN}}, faq_schema(pairs)]
    return slug, title, desc, shell(slug, title, desc, f"{nice[0].upper() + nice[1:]} pace chart", body, schema, "Pace charts", "/running-pace-charts/")


# ------------------------------------------------------------------ queue (popular items first, families interleaved)
def queue():
    ages = [30, 40, 35, 45, 50, 25, 55, 60, 28, 32, 38, 42, 48, 52, 33, 36, 44, 46, 27, 29, 31, 34, 37, 39, 41, 43, 47, 49,
            51, 53, 54, 56, 57, 58, 59, 61, 62, 63, 64, 65, 20, 21, 22, 23, 24, 26]
    pace_order = [("half-marathon", 7200), ("5k", 1800), ("marathon", 14400), ("5k", 1500), ("10k", 3600), ("half-marathon", 6300),
                  ("marathon", 12600), ("5k", 1200), ("10k", 3000), ("half-marathon", 6600), ("5k", 1680), ("marathon", 13500),
                  ("10k", 2700), ("5k", 2100), ("half-marathon", 8100), ("marathon", 16200), ("10k", 3300), ("5k", 1320),
                  ("half-marathon", 9000), ("marathon", 18000)]
    q, ai, pi = [], 0, 0
    while ai < len(ages) or pi < len(pace_order):  # 3 ages : 2 pace charts
        for _ in range(3):
            if ai < len(ages): q.append(("hr", ages[ai])); ai += 1
        for _ in range(2):
            if pi < len(pace_order): q.append(("pace",) + pace_order[pi]); pi += 1
    return q


def build(item):
    return hr_page(item[1]) if item[0] == "hr" else pace_page(item[1], item[2])


def slug_of(item):
    return f"zone-2-heart-rate-for-{item[1]}-year-old" if item[0] == "hr" else f"sub-{goal_slug(item[2])}-{item[1]}-pace-chart"


def item_id(item):
    return "-".join(str(x) for x in item)


# ------------------------------------------------------------------ hubs, sitemap, llms, guides link
def write(slug, doc):
    os.makedirs(os.path.join(ROOT, slug), exist_ok=True)
    open(os.path.join(ROOT, slug, "index.html"), "w").write(doc)


def hubs(pub):
    items = [build(tuple(json.loads(p))) for p in pub]
    hr = sorted([i for i in items if i[0].startswith("zone-2-heart-rate-for-")], key=lambda i: int(re.search(r"for-(\d+)-", i[0]).group(1)))
    pc = [i for i in items if i[0].endswith("-pace-chart")]
    card = lambda i: f'<a href="/{i[0]}/">{esc(i[1].split(" (")[0].split(" | ")[0])}<span>{esc(i[2][:80])}…</span></a>'
    out = []
    if hr:
        body = '<p class="lead">Your estimated Zone 2 heart rate at every age, with all 5 zones and Karvonen ranges by resting heart rate.</p><div class="related">' + "".join(card(i) for i in hr) + "</div>" + cta("Your Zone 2, coached live", "RunZone calculates your zones and coaches you in Zone 2 with voice cues while the app is open.")
        write("zone-2-heart-rate-by-age", shell("zone-2-heart-rate-by-age", "Zone 2 Heart Rate by Age (Chart) | RunZone", "Zone 2 heart rate by age: estimated Zone 2 ranges and all 5 heart rate zones for every age from 20 to 65.", "Zone 2 heart rate by age", body, {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Zone 2 heart rate by age"}, "Free tools", "/guides/"))
        out.append(("zone-2-heart-rate-by-age", "Zone 2 heart rate by age", "Zone 2 ranges and all 5 zones for every age"))
    if pc:
        body = '<p class="lead">Exact paces, splits and equivalent times for popular 5K, 10K, half marathon and marathon goals.</p><div class="related">' + "".join(card(i) for i in pc) + "</div>" + cta("A plan for your race goal", "RunZone builds your weekly plan around your goal and keeps easy runs easy.")
        write("running-pace-charts", shell("running-pace-charts", "Running Pace Charts for Every Goal Time | RunZone", "Pace charts for popular 5K, 10K, half marathon and marathon goal times, with splits and equivalent race times.", "Running pace charts", body, {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Running pace charts"}, "Free tools", "/guides/"))
        out.append(("running-pace-charts", "Running pace charts", "Splits for popular race goal times"))
    return out, items


def update_robots():
    p = os.path.join(ROOT, "robots.txt"); s = open(p).read()
    if "/_build/" not in s:
        open(p, "w").write(s.replace("Allow: /\n", "Allow: /\nDisallow: /_build/\n"))


def update_sitemap(slugs):
    p = os.path.join(ROOT, "sitemap.xml"); s = open(p).read()
    for slug in slugs:
        loc = f"{DOMAIN}/{slug}/"
        if loc not in s:
            s = s.replace("</urlset>", f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod></url>\n</urlset>")
    open(p, "w").write(s)


def update_llms(hub_list):
    p = os.path.join(ROOT, "llms.txt"); s = open(p).read()
    for slug, name, d in hub_list:
        line = f"- [{name}]({DOMAIN}/{slug}/): {d}"
        if f"/{slug}/" not in s:
            s = s.replace("## Guides", f"## Reference charts\n{line}\n\n## Guides", 1) if "## Reference charts" not in s else s.replace("## Reference charts\n", f"## Reference charts\n{line}\n", 1)
    open(p, "w").write(s)


def update_guides(hub_list):
    p = os.path.join(ROOT, "guides", "index.html"); s = open(p).read()
    for slug, name, d in hub_list:
        if f'href="/{slug}/"' not in s:
            s = s.replace('<div class="related">', f'<div class="related"><a href="/{slug}/">{esc(name)}<span>{esc(d)}</span></a>', 1)
    open(p, "w").write(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", type=int, default=0)
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    pub = json.load(open(STATE)) if os.path.exists(STATE) else []
    q = [i for i in queue() if json.dumps(list(i)) not in pub]
    if a.status:
        print(f"published {len(pub)}, queued {len(q)}"); return
    new = q[:a.release]
    for item in [tuple(json.loads(p)) for p in pub] + new:
        LIVE.add(slug_of(item))
    for item in new:
        slug, title, desc, doc = build(item)
        write(slug, doc)
        pub.append(json.dumps(list(item)))
        print("released", slug)
    hub_list, items = hubs(pub)
    # rebuild already-published pages too so cross-links stay current
    for slug, title, desc, doc in items:
        write(slug, doc)
    update_sitemap([h[0] for h in hub_list] + [i[0] for i in items])
    update_llms(hub_list)
    update_robots()
    update_guides(hub_list)
    json.dump(pub, open(STATE, "w"), indent=0)
    print(f"done: published {len(pub)}, queued {len(q) - len(new)}")


if __name__ == "__main__":
    main()
