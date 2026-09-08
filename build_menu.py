#!/usr/bin/env python3
"""El Rancho Grande menu generator — replicates the Mi Jalapeno menu system
(build.py: sidebar+counts, search+filter pills, category-card grid landing,
per-category item pages + item sheet) in ERG branding. Shared /menu/ (one menu
across all locations). Reads item data from the existing menu/index.html."""
import html, json, re, unicodedata, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
def e(s): return html.escape(str(s), quote=True)
ASSET_DIR = ROOT / "assets" / "images"
def _has(base): return (ASSET_DIR / f"{base}-800.webp").exists()

DOMAIN = "https://elranchogrande.info"
BRAND_SHORT = "El Rancho Grande"
ORDER_URL = "/locations/"   # shared menu -> pick a location to order

# ---------------- categories + items from stable data file (menu_data.json)
CATS_LIST = [c for c in json.loads((ROOT / "menu_data.json").read_text())["categories"] if c["items"]]
CAT_BY_NAME = {c["name"]: c for c in CATS_LIST}

COURSE_GROUPS = [
    ("To Start", ["Appetizers", "Nachos", "Dips", "Salads"]),
    ("From the Grill", ["Combos From The Grill", "Fajitas", "Chicken", "Seafood", "Molcajete / Specialty Bowls", "Combinations", "Rice Bowls"]),
    ("Tacos & More", ["Street Tacos", "Enchiladas", "Burritos", "Antojitos Mexicanos", "Lunch Birria Plates", "Vegetarian"]),
    ("Lunch & Kids", ["Lunch Time", "Egg Specials", "Kids", "A La Carte", "Side Orders"]),
    ("Sweet", ["Desserts"]),
    ("Cantina", ["Beer / Margaritas / Tequilas", "Mix Drinks", "Wine", "Soft Drinks"]),
]
GROUP_OF = {c: g for g, cats in COURSE_GROUPS for c in cats}
# any category not placed above -> appended to a Menu group so nothing is dropped
_placed = {c for _, cats in COURSE_GROUPS for c in cats}
_extra = [c["name"] for c in CATS_LIST if c["name"] not in _placed]
if _extra:
    COURSE_GROUPS.append(("More", _extra))
    for c in _extra: GROUP_OF[c] = "More"

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "x"

# ---------------- photos (base = menu-<slug>; files at assets/images/menu-<slug>-{400,800,1600}.webp)
CATEGORY_PHOTO = {
    "Seafood": "menu-camaron-culiacan", "Beer / Margaritas / Tequilas": "menu-margarita-tropical",
    "Combos From The Grill": "menu-asada-de-rancho", "Chicken": "menu-chicken-mushroom", "Appetizers": "menu-dinner-appetizer",
    "Nachos": "menu-sampler", "Dips": "menu-dinner-appetizer", "Salads": "menu-raspberry-chicken-salad",
    "Lunch Time": "menu-fajita", "Egg Specials": "menu-carne-asada", "Lunch Birria Plates": "menu-birria-ramen",
    "Combinations": "menu-sampler", "Rice Bowls": "menu-molcajete", "Vegetarian": "menu-taco-salad",
    "Kids": "menu-fajita", "A La Carte": "menu-dinner-appetizer", "Side Orders": "menu-camaron-guajillo",
    "Enchiladas": "menu-enchiladas-blancas", "Burritos": "menu-carne-asada", "Antojitos Mexicanos": "menu-sampler",
    "Fajitas": "menu-fajita", "Street Tacos": "menu-taco-salad", "Molcajete / Specialty Bowls": "menu-molcajete",
    "Wine": "menu-sangria-swirl",  # Wine list includes Homemade Sangria, so a sangria shot fits
    "Mix Drinks": "menu-cantarito", "Soft Drinks": "menu-jarrito-preparado", "Desserts": "menu-pina-colada",
}
def card_photo(cat):
    b = CATEGORY_PHOTO.get(cat)
    return b if (b and _has(b)) else None
# per-item featured photos where an item name matches a real dish shot
PHOTO_RULES = [
    ("Seafood", "culiac", "menu-camaron-culiacan"), ("Seafood", "guajillo", "menu-camaron-guajillo"),
    ("Combos From The Grill", "asada", "menu-asada-de-rancho"), ("Combos From The Grill", "parrillada", "menu-sampler"),
    ("Combos From The Grill", "sampler", "menu-sampler"), ("Combos From The Grill", "molcajete", "menu-molcajete"),
    ("Chicken", "mushroom", "menu-chicken-mushroom"),
    ("Salads", "taco salad", "menu-taco-salad"), ("Salads", "raspberry", "menu-raspberry-chicken-salad"),
    ("Lunch Birria Plates", "birria", "menu-birria-ramen"),
    ("Combinations", "sampler", "menu-sampler"), ("Combinations", "parrillada", "menu-sampler"),
    ("Enchiladas", "poblana", "menu-enchilada-poblana"), ("Enchiladas", "chipotle", "menu-enchilada-chipotle"),
    ("Enchiladas", "blanca", "menu-enchiladas-blancas"), ("Enchiladas", "enchilada", "menu-enchiladas-blancas"),
    ("Fajitas", "fajita", "menu-fajita"), ("Molcajete / Specialty Bowls", "molcajete", "menu-molcajete"),
    ("Beer / Margaritas / Tequilas", "passion", "menu-passion-fruit-margarita"),
    ("Beer / Margaritas / Tequilas", "coronarita", "menu-coronarita"),
    ("Beer / Margaritas / Tequilas", "colada", "menu-pina-colada"),
    ("Beer / Margaritas / Tequilas", "margarita", "menu-margarita-tropical"),
    ("Mix Drinks", "cantarito", "menu-cantarito"), ("Mix Drinks", "mojito", "menu-mojito"),
    ("Mix Drinks", "sangria", "menu-sangria-swirl"), ("Mix Drinks", "blue", "menu-blue-tuesday"),
    ("Mix Drinks", "marijuana", "menu-liquid-marijuana"), ("Mix Drinks", "bourbon", "menu-bourbon"),
    ("Wine", "sangria", "menu-sangria-swirl"),
    ("Soft Drinks", "jarrito", "menu-jarrito-preparado"),
    ("Appetizers", "sampler", "menu-dinner-appetizer"), ("Appetizers", "dinner", "menu-dinner-appetizer"),
]
def item_photo(cat, name):
    nl = name.lower()
    for c, sub, base in PHOTO_RULES:
        if c == cat and sub in nl and _has(base):
            return base
    return None

_MONEY = re.compile(r"\d+\.\d{1,2}")
def parse_price(raw):
    raw = (raw or "").strip().lstrip("$")
    variants = []
    if "/" in raw:
        for part in raw.split("/"):
            part = part.strip(); m = _MONEY.search(part)
            if m:
                price = "$" + m.group(); label = (part[:m.start()] + part[m.end():]).strip().strip("()").strip() or "Price"
            else: price, label = part, "Price"
            variants.append({"label": label, "price": price})
    else:
        m = _MONEY.search(raw)
        variants.append({"label": "Price", "price": ("$" + m.group()) if m else (raw or "—")})
    minp = min([float(x) for x in _MONEY.findall(raw)] or [None]) if _MONEY.findall(raw) else None
    return variants, minp
def price_str(variants):
    if len(variants) == 1 and variants[0]["label"] == "Price": return variants[0]["price"]
    return "   ".join(f'{v["label"]} {v["price"]}' for v in variants)

_SEAFOOD = ["shrimp","camaron","camarones","pulpo","octopus","fish","tilapia","mojarra","scallop","crab","ceviche","langostino","mariscos","seafood","del mar","salmon"]
_SPICY = ["diabla","jalape","chipotle","toreado","habanero","spicy","relleno"]
_VEG = ["veggie","vegetarian","vegetable","cheese quesadilla","bean burrito","spinach","vegan"]
def derive_tags(name, desc, cat):
    s = f"{name} {desc} {cat}".lower(); t = []
    if "new" in s: t.append("New")
    if any(k in s for k in _SEAFOOD): t.append("Seafood")
    if any(k in s for k in _SPICY): t.append("Spicy")
    if cat == "Vegetarian" or any(k in s for k in _VEG): t.append("Veggie")
    if "for two" in s or "(2)" in s or "pitcher" in s or "family" in s or "sharable" in s or "shareable" in s: t.append("For two")
    return t
def _present_filters():
    order = ["New", "Featured", "Spicy", "Seafood", "Veggie", "Under $10", "For two"]
    cnt = {k: 0 for k in order}
    for c in CATS_LIST:
        for it in c["items"]:
            for t in derive_tags(it["name"], it.get("description", ""), c["name"]):
                if t in cnt: cnt[t] += 1
            if item_photo(c["name"], it["name"]): cnt["Featured"] += 1
            _, minp = parse_price(it.get("price", ""))
            if minp is not None and minp < 10: cnt["Under $10"] += 1
    return [k for k in order if cnt[k] > 0]
FILTERS = _present_filters()

def pic(base, ratio, sizes, alt=""):
    return (f'<div class="slot" style="aspect-ratio:{ratio}"><img src="/assets/images/{base}-800.webp" '
            f'srcset="/assets/images/{base}-400.webp 400w,/assets/images/{base}-800.webp 800w,/assets/images/{base}-1600.webp 1600w" '
            f'sizes="{sizes}" width="800" height="500" alt="{e(alt)}" loading="lazy" decoding="async"></div>')

# ---------------- locations (per-location menus for SEO) + shared /menu/
LOCS = json.loads((ROOT / "menu_locations.json").read_text())
LOCMAP = {l["slug"]: l for l in LOCS}
def mbase(loc): return f"/{loc}/menu" if loc else "/menu"
def order_url(loc): return (LOCMAP[loc]["order"] or f"/{loc}/") if loc else "/locations/"
def write(route, doc):
    p = ROOT / route.strip("/")
    p.mkdir(parents=True, exist_ok=True)
    (p / "index.html").write_text(doc)

# ---------------- shared chrome
def header(active="", loc=None):
    def L(href, label, key):
        on = ' style="color:var(--corn)"' if key == active else ""
        return f'<a href="{href}"{on}>{label}</a>'
    home = f"/{loc}/" if loc else "/"
    vip = f"/{loc}/vip/" if loc else "/locations/"
    return ('<header class="hdr"><div class="hdr-in">'
            f'<a class="hdr-logo" href="{home}" aria-label="El Rancho Grande home"><img src="/assets/brand/logo-color.webp" alt="El Rancho Grande Mexican Grill &amp; Cantina" width="152" height="112"></a>'
            '<nav class="hdr-nav">' + L(mbase(loc) + "/", "Menu", "menu") + L("/locations/", "Locations", "") + L("/about/", "About", "") + L("/gallery/", "Gallery", "gallery") + L("/events/", "Events", "") + L(vip, "Become a VIP", "") + '</nav>'
            f'<a class="hdr-cta" href="{order_url(loc)}"' + (' target="_blank" rel="noopener"' if loc and LOCMAP[loc]["order"] else "") + '>Order Online</a></div></header>')
def footer():
    return ('<footer class="ft"><div class="ft-in">'
            '<a href="/" aria-label="El Rancho Grande home"><img src="/assets/brand/logo-gold.webp" alt="El Rancho Grande" width="118" height="88"></a>'
            '<div class="ft-links"><a href="/">Home</a><a href="/menu/">Menu</a><a href="/locations/">Locations</a><a href="/about/">About</a><a href="/events/">Events</a></div></div>'
            '<div class="ft-bar">&copy; 2026 El Rancho Grande Group &middot; Serving Cincinnati &amp; Dayton, OH &middot; Powered By <strong>Chowdown</strong></div></footer>')

def rail(active=None, loc=None):
    label = f"&#8592; {e(LOCMAP[loc]['name'])} menu" if loc else "&#8592; Full menu"
    out = [f'<aside class="mrail"><a class="mrail-brand" href="{mbase(loc)}/"><b>{label}</b></a>']
    for g, cats in COURSE_GROUPS:
        present = [c for c in cats if c in CAT_BY_NAME]
        if not present: continue
        out.append(f'<div class="mrg"><h4>{e(g)}</h4>')
        for c in present:
            n = len(CAT_BY_NAME[c]["items"]); on = " on" if c == active else ""
            out.append(f'<a class="{on.strip()}" href="{mbase(loc)}/{slug(c)}/">{e(c)}<span class="ct">{n}</span></a>')
        out.append("</div>")
    out.append("</aside>")
    return "".join(out)

def utility():
    chips = "".join(f'<button class="mchip" type="button" data-t="{e(f)}" aria-pressed="false">{e(f)}</button>' for f in FILTERS)
    return ('<div class="mutil"><label class="msearch"><span>&#9906;</span>'
            '<input id="msearch" type="search" placeholder="Search the menu" aria-label="Search the menu"></label>'
            '<button class="mfilter-toggle" type="button" aria-label="Filters" aria-expanded="false" '
            'onclick="var u=this.closest(&#39;.mutil&#39;);var o=u.classList.toggle(&#39;filters-open&#39;);this.setAttribute(&#39;aria-expanded&#39;,o)">Filters</button>'
            f'<div class="mfilters" id="mfilters"><div id="mchips" style="display:flex;flex-wrap:wrap;gap:8px">{chips}</div>'
            '</div></div><div id="mresults" hidden></div>')

def item_row(it, cat, loc=None):
    name = it["name"]; desc = it.get("description", "").strip()
    variants, _ = parse_price(it.get("price", "")); tags = derive_tags(name, desc, cat)
    base = item_photo(cat, name)
    data = {"n": name, "c": cat, "d": desc, "vars": variants, "tags": tags,
            "img": ("/assets/images/" + base) if base else "", "order": order_url(loc)}
    da = e(json.dumps(data, ensure_ascii=False))
    tag_html = ('<div class="mr-tags">' + "".join(f'<span class="mtag">{e(t)}</span>' for t in tags) + "</div>") if tags else ""
    desc_html = f'<p class="mr-desc">{e(desc)}</p>' if desc else ""
    return (f'<div class="mrow" id="{slug(name)}" data-item=\'{da}\' tabindex="0" role="button" aria-label="{e(name)}">'
            f'<div class="mr-top"><span class="mr-name">{e(name)}</span><span class="mr-lead"></span><span class="mr-price">{e(price_str(variants))}</span></div>'
            f'{tag_html}{desc_html}</div>')

def feat_card(it, cat, base, loc=None):
    variants, _ = parse_price(it.get("price", "")); desc = it.get("description", "").strip()
    desc_html = f'<p class="mc-d">{e(desc)}</p>' if desc else ""
    return (f'<a class="mcard" href="{mbase(loc)}/{slug(cat)}/#{slug(it["name"])}">'
            f'{pic(base, "4/3", "(max-width:860px) 90vw, 320px", alt=it["name"])}'
            f'<div class="mc-b"><div class="mc-h"><span class="mc-n">{e(it["name"])}</span><span class="mc-p">{e(price_str(variants))}</span></div>{desc_html}</div></a>')

def head(title, desc, canonical, ld):
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{e(title)}</title><meta name=\"description\" content=\"{e(desc)}\"><link rel=\"canonical\" href=\"{e(canonical)}\">"
            f"<meta property=\"og:title\" content=\"{e(title)}\"><meta property=\"og:description\" content=\"{e(desc)}\"><meta property=\"og:type\" content=\"restaurant\"><meta property=\"og:url\" content=\"{e(canonical)}\">"
            "<link rel=\"preload\" as=\"font\" type=\"font/woff2\" href=\"/assets/fonts/Tanker-Regular.woff2\" crossorigin><link rel=\"preload\" as=\"font\" type=\"font/woff2\" href=\"/assets/fonts/BespokeSerif-Regular.woff2\" crossorigin>"
            "<link rel=\"stylesheet\" href=\"/assets/css/menu.css?v=erg2\">"
            f"<script type=\"application/ld+json\">{json.dumps(ld, ensure_ascii=False)}</script></head><body>")

def section_ld(cat):
    c = CAT_BY_NAME[cat]
    items = []
    for it in c["items"]:
        variants, _ = parse_price(it.get("price", ""))
        node = {"@type": "MenuItem", "name": it["name"]}
        if it.get("description"): node["description"] = it["description"]
        m = _MONEY.search(variants[0]["price"] or "")
        if m: node["offers"] = {"@type": "Offer", "price": m.group(), "priceCurrency": "USD"}
        items.append(node)
    return {"@type": "MenuSection", "name": cat, "hasMenuItem": items}

def page_category(cat, prev_c, next_c, loc=None):
    c = CAT_BY_NAME[cat]; items = c["items"]; grp = GROUP_OF.get(cat, "Menu")
    lname = LOCMAP[loc]["name"] if loc else None
    feats = [(it, item_photo(cat, it["name"])) for it in items]
    feats = [(it, b) for it, b in feats if b][:3]
    feat_html = ('<div class="mfeat">' + "".join(feat_card(it, cat, b, loc) for it, b in feats) + "</div>") if feats else ""
    rows = '<div class="mgrid">' + "".join(item_row(it, cat, loc) for it in items) + "</div>"
    back = "Full menu" if not loc else f"{lname} menu"
    prevlink = f'<a href="{mbase(loc)}/{slug(prev_c)}/">&#8592; {e(prev_c)}</a>' if prev_c else "<span></span>"
    nextlink = f'<a href="{mbase(loc)}/{slug(next_c)}/">{e(next_c)} &#8594;</a>' if next_c else "<span></span>"
    spread = (f'<section id="mspread"><a class="mback" href="{mbase(loc)}/"><span aria-hidden="true">&#8592;</span> {e(back)}</a>'
              f'<div class="msec-ey">{e(grp)} &middot; {len(items)} items</div><h1 class="msec-h disp">{e(cat)}</h1>'
              f'{feat_html}{rows}<div class="mnav">{prevlink}{nextlink}</div></section>')
    body = header("menu", loc) + '<main class="mboard">' + rail(cat, loc) + '<div class="mcontent">' + utility() + spread + '</div></main>'
    body += '<button id="mscrim" hidden aria-label="Close menu item"></button><div id="msheet" role="dialog" aria-modal="true" aria-label="Menu item" hidden></div>'
    body += footer() + '<script defer src="/assets/js/menu-index.js?v=erg2"></script><script defer src="/assets/js/menu.js?v=erg2"></script>'
    ld = {"@context": "https://schema.org", "@graph": [section_ld(cat)]}
    title = f"{cat} | El Rancho Grande {lname} Menu" if loc else f"{cat} | El Rancho Grande Menu"
    desc = (f"{cat} at El Rancho Grande {lname}, OH. {len(items)} items. Order online for pickup." if loc
            else f"{cat} at El Rancho Grande. {len(items)} items. Order online for pickup across Cincinnati & Dayton.")
    doc = head(title, desc, f"{DOMAIN}{mbase(loc)}/{slug(cat)}/", ld) + body + "</body></html>"
    write(f"{mbase(loc)}/{slug(cat)}", doc)

def page_menu_landing(loc=None):
    lname = LOCMAP[loc]["name"] if loc else None
    lcity = LOCMAP[loc]["city"] if loc else None
    groups_html = ""
    for g, cats in COURSE_GROUPS:
        present = [c for c in cats if c in CAT_BY_NAME]
        if not present: continue
        cards = ""
        for c in present:
            n = len(CAT_BY_NAME[c]["items"]); b = card_photo(c)
            photo = pic(b, "16/10", "(max-width:860px) 90vw, 300px", alt=c) if b else ""
            cls = "mcard" if b else "mcard mcard-np"
            cards += (f'<a class="{cls}" href="{mbase(loc)}/{slug(c)}/">{photo}<div class="mc-b"><div class="mc-h">'
                      f'<span class="mc-n">{e(c)}</span><span class="mc-p">{n}</span></div></div></a>')
        groups_html += (f'<section style="margin-bottom:44px"><div class="msec-ey">{e(g)}</div>'
                        f'<div class="mfeat mfeat-cats" style="margin:14px 0 0">{cards}</div></section>')
    total = sum(len(c["items"]) for c in CATS_LIST)
    eyebrow = (f"El Rancho Grande {e(lname)} &middot; {e(lcity)}, OH &middot; {total} items" if loc
               else f"El Rancho Grande &middot; Cincinnati &amp; Dayton &middot; {total} items")
    sub = (f"Search it, filter it, or browse by course. Order online for pickup at El Rancho Grande {e(lname)}." if loc
           else "Search it, filter it, or browse by course. Order online for pickup at your neighborhood El Rancho Grande.")
    intro = (f'<section id="mspread"><div class="msec-ey">{eyebrow}</div>'
             '<h1 class="msec-h disp" style="font-size:clamp(58px,13vw,170px);line-height:.8">MENU</h1>'
             f'<p style="margin:14px 0 0;font-size:17px;line-height:1.7;color:var(--bone-muted);max-width:52ch">{sub}</p>'
             '<div style="display:flex;flex-wrap:wrap;gap:12px;margin:24px 0 40px">'
             f'<a href="{e(order_url(loc))}"' + (' target="_blank" rel="noopener"' if loc and LOCMAP[loc]["order"] else "") + ' style="padding:15px 26px;background:var(--red);color:#fff;font-family:\'Tanker\',sans-serif;letter-spacing:.16em;text-transform:uppercase;font-size:14px">Order online</a></div>'
             f'{groups_html}</section>')
    body = header("menu", loc) + '<main class="mboard">' + rail(None, loc) + '<div class="mcontent">' + utility() + intro + '</div></main>'
    body += '<button id="mscrim" hidden aria-label="Close menu item"></button><div id="msheet" role="dialog" aria-modal="true" aria-label="Menu item" hidden></div>'
    body += footer() + '<script defer src="/assets/js/menu-index.js?v=erg2"></script><script defer src="/assets/js/menu.js?v=erg2"></script>'
    ld = {"@context": "https://schema.org", "@type": "Menu", "@id": f"{DOMAIN}{mbase(loc)}/#menu", "name": (f"El Rancho Grande {lname} Menu" if loc else "El Rancho Grande Menu"), "hasMenuSection": [section_ld(c["name"]) for c in CATS_LIST]}
    title = f"Menu | El Rancho Grande {lname}" if loc else "Menu | El Rancho Grande"
    desc = (f"The full El Rancho Grande {lname}, OH menu: fajitas, birria, seafood, enchiladas, street tacos, margaritas and more. Order online for pickup." if loc
            else "The full El Rancho Grande menu: fajitas, birria, seafood, enchiladas, street tacos, margaritas and more. Search, filter, and order online for pickup.")
    doc = head(title, desc, f"{DOMAIN}{mbase(loc)}/", ld) + body + "</body></html>"
    write(f"{mbase(loc)}", doc)

GALLERY_SHOTS = ["menu-fajita","menu-birria-ramen","menu-molcajete","menu-carne-asada","menu-camaron-culiacan",
 "menu-enchiladas-blancas","menu-chicken-mushroom","menu-sampler","menu-asada-de-rancho","menu-raspberry-chicken-salad",
 "menu-taco-salad","menu-enchilada-poblana","menu-camaron-guajillo","menu-dinner-appetizer","menu-enchilada-chipotle",
 "menu-margarita-tropical","menu-cantarito","menu-sangria-swirl","menu-mojito","menu-pina-colada",
 "menu-passion-fruit-margarita","menu-jarrito-preparado","menu-coronarita","menu-blue-tuesday","menu-liquid-marijuana",
 "menu-mojito-flight","menu-bourbon"]
def page_gallery():
    grid = "".join(pic(b, "1/1", "(max-width:860px) 45vw, 22vw", alt="El Rancho Grande") for b in GALLERY_SHOTS if _has(b))
    body = header("gallery") + (
        '<main class="container" style="padding:60px 24px 100px"><div style="display:grid;gap:14px;margin-bottom:40px">'
        '<div class="msec-ey">Food, cantina &amp; good times</div>'
        '<h1 class="disp" style="margin:0;font-size:clamp(52px,12vw,168px);line-height:.8;letter-spacing:.01em;color:var(--bone)">GALLERY</h1></div>'
        f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule)">{grid}</div>'
        '</main>') + footer()
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ImageGallery", "url": f"{DOMAIN}/gallery/", "name": "El Rancho Grande Gallery", "about": {"@id": f"{DOMAIN}/#organization"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Gallery", "item": f"{DOMAIN}/gallery/"}]}]}
    doc = head("Gallery | El Rancho Grande", "Photos from El Rancho Grande: fajitas, birria, seafood, enchiladas, hand-shaken margaritas and the cantina across Cincinnati & Dayton, OH.", f"{DOMAIN}/gallery/", ld) + body + "</body></html>"
    write("/gallery", doc)

def build_search_index():
    idx = []
    for c in CATS_LIST:
        cat = c["name"]
        for it in c["items"]:
            variants, minp = parse_price(it.get("price", ""))
            idx.append({"n": it["name"], "c": cat, "u": f"{slug(cat)}/#{slug(it['name'])}", "p": minp,
                        "v": price_str(variants), "t": "|".join(derive_tags(it["name"], it.get("description", ""), cat)),
                        "f": 1 if item_photo(cat, it["name"]) else 0, "d": it.get("description", "")})
    (ROOT / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "js" / "menu-index.js").write_text("window.MENU_INDEX=" + json.dumps(idx, ensure_ascii=False, separators=(",", ":")) + ";")
    return len(idx)

if __name__ == "__main__":
    names = [c["name"] for c in CATS_LIST]
    def build_menu_for(loc):
        page_menu_landing(loc)
        for i, cat in enumerate(names):
            page_category(cat, names[i-1] if i > 0 else None, names[i+1] if i+1 < len(names) else None, loc)
    build_menu_for(None)                      # shared /menu/
    for l in LOCS:                            # per-location /{slug}/menu/
        build_menu_for(l["slug"])
    page_gallery()                            # /gallery/ in the menu design system
    n = build_search_index()
    print(f"built /menu/ + {len(LOCS)} location menus x {len(names)} categories; search index {n} items")
