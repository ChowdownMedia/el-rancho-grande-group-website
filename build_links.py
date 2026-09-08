#!/usr/bin/env python3
"""El Rancho Grande per-location linktree (/{loc}/links/) — ERG-branded
mobile link-in-bio, Roman-group pattern. Point QR codes / redirects here."""
import json, html, re, urllib.parse, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
def e(s): return html.escape(str(s), quote=True)
DOMAIN = "https://elranchogrande.info"
LOCS = json.loads((ROOT / "links_data.json").read_text())

FB='<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 9h3l.4-3H14V4.3c0-.9.3-1.5 1.6-1.5H17V.2C16.6.1 15.6 0 14.5 0 12 0 10.3 1.5 10.3 4v2H7.4v3h2.9v9H14V9z"/></svg>'
IG='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none"/></svg>'
GG='<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.35 11.1H12v2.98h5.35c-.23 1.4-1.64 4.1-5.35 4.1a5.9 5.9 0 0 1 0-11.8c1.68 0 2.8.72 3.45 1.33l2.35-2.27C16.4 4.02 14.42 3 12 3a9 9 0 1 0 0 18c5.2 0 8.64-3.65 8.64-8.8 0-.6-.07-1.06-.16-1.5z"/></svg>'
IC_VIP='<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 7l4.2 3.2L12 4l4.8 6.2L21 7l-1.6 11H4.6L3 7zm2 13h14v1.5H5V20z"/></svg>'
IC_MENU='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h16M4 12h16M4 18h10"/></svg>'
IC_ORDER='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 8h12l-1 12H7L6 8z"/><path d="M9 8a3 3 0 0 1 6 0"/></svg>'
IC_PIN='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s7-6 7-11a7 7 0 1 0-14 0c0 5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>'
IC_PHONE='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 5c0 8 7 15 15 15l2.5-3.5-4-2.5-2 2a12 12 0 0 1-5.5-5.5l2-2L9.5 4.5 6 3 4 5z"/></svg>'
ARW='<span class="arw" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M9 6l6 6-6 6"/></svg></span>'

CSS = """
@font-face{font-family:'Tanker';src:url('/assets/fonts/Tanker-Regular.woff2') format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:'Bespoke Serif';src:url('/assets/fonts/BespokeSerif-Regular.woff2') format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:'Bespoke Serif';src:url('/assets/fonts/BespokeSerif-Bold.woff2') format('woff2');font-weight:700;font-display:swap}
:root{--bg:#1F1E1F;--text:#E7DFD9;--primary:#E5312A;--on-primary:#fff;--primary-dk:#8f1a14;
--hi:#EB9911;--on-hi:#1F1E1F;--muted:#9a8f88;--card:#272322;--border:rgba(192,196,198,.18);
--f-display:'Tanker',Georgia,sans-serif;--f-body:'Bespoke Serif',Georgia,serif;--radius:12px;--pill:999px;
--shadow-sm:0 2px 9px rgba(0,0,0,.4);--shadow:0 12px 32px rgba(0,0,0,.55)}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:var(--f-body);color:var(--text);font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased;overflow-x:hidden;
  min-height:100dvh;display:flex;flex-direction:column;align-items:center;
  background:radial-gradient(1100px 460px at 50% -8%,rgba(235,153,17,.20) 0%,transparent 60%),
    radial-gradient(860px 400px at 50% 108%,rgba(229,49,42,.16) 0%,transparent 60%),var(--bg)}
img{max-width:100%;display:block}
a{color:var(--hi);text-decoration:none}
:focus-visible{outline:3px solid var(--hi);outline-offset:3px;border-radius:12px}
.wrap{width:100%;max-width:460px;padding:40px 20px 32px;text-align:center}
.logo{max-width:210px;height:auto;margin:0 auto 14px;filter:drop-shadow(var(--shadow))}
.loc{display:inline-flex;align-items:center;gap:9px;margin:6px 0 0;font-family:var(--f-display);
  font-size:.9rem;letter-spacing:.18em;text-transform:uppercase;color:var(--hi)}
.loc::before,.loc::after{content:"";width:18px;height:2px;border-radius:2px;background:var(--hi)}
.beads{height:14px;width:150px;margin:18px auto 24px;
  background-image:radial-gradient(circle,var(--primary) 42%,transparent 46%),radial-gradient(circle,var(--hi) 42%,transparent 46%);
  background-size:24px 14px,24px 14px;background-position:0 center,12px center;background-repeat:repeat-x;opacity:.95}
.socials{display:flex;justify-content:center;gap:14px;margin:0 0 24px}
.social{display:inline-flex;align-items:center;justify-content:center;width:50px;height:50px;border-radius:var(--pill);
  background:var(--card);color:var(--hi);box-shadow:var(--shadow-sm);border:1px solid var(--border);
  transition:transform .15s ease,background .15s ease,color .15s ease,border-color .15s ease}
.social:hover{transform:translateY(-3px);background:var(--hi);color:var(--on-hi);border-color:var(--hi)}
.social svg{width:23px;height:23px}
.links{display:flex;flex-direction:column;gap:13px}
.link{display:flex;align-items:center;gap:14px;width:100%;padding:16px 18px;border-radius:var(--radius);
  font-family:var(--f-display);font-size:1.06rem;letter-spacing:.02em;box-shadow:var(--shadow-sm);
  transition:transform .15s ease,box-shadow .15s ease,filter .15s ease}
.link:hover{transform:translateY(-2px);box-shadow:var(--shadow);filter:brightness(1.05)}
.link .ic{flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:var(--pill);
  background:color-mix(in srgb,currentColor 16%,transparent)}
.link .ic svg{width:20px;height:20px}
.link .lbl{flex:1 1 auto;text-align:left}
.link .arw{flex:0 0 auto;opacity:.6}
.link .arw svg{width:18px;height:18px}
.link--pri{background:var(--primary);color:var(--on-primary);box-shadow:0 6px 0 var(--primary-dk)}
.link--pri:hover{transform:translateY(2px);box-shadow:0 4px 0 var(--primary-dk);filter:none}
.link--hi{background:var(--hi);color:var(--on-hi)}
.link--gh{background:var(--card);color:var(--text);border:1px solid var(--border)}
.foot{margin:30px 0 4px;font-size:.82rem;color:var(--muted)}
.foot a{color:var(--hi);font-weight:700}
"""

def link(cls, href, icon, label, ext=True):
    t = ' target="_blank" rel="noopener"' if ext else ""
    return (f'<a class="link {cls}" href="{e(href)}"{t}><span class="ic" aria-hidden="true">{icon}</span>'
            f'<span class="lbl">{label}</span>{ARW}</a>')

def build(l):
    slug=l["slug"]; name=l["name"]; city=l["city"]; region=l.get("region","OH")
    maps=("https://www.google.com/maps/search/?api=1&query="
          + urllib.parse.quote(f'El Rancho Grande {l.get("street","")} {city} {region} {l.get("zip","")}'.strip()))
    buttons=[link("link--hi", f"/{slug}/vip/", IC_VIP, "Become a VIP", ext=False),
             link("link--pri", f"/{slug}/menu/", IC_MENU, "View Our Menu", ext=False)]
    if l.get("order"):
        buttons.append(link("link--pri", l["order"], IC_ORDER, "Order Online"))
    buttons.append(link("link--pri", maps, IC_PIN, "Get Directions"))
    if l.get("tel"):
        buttons.append(link("link--gh", f'tel:{l["tel"]}', IC_PHONE, "Call Us", ext=False))
    socials=[]
    if l.get("facebook"): socials.append(f'<a class="social" href="{e(l["facebook"])}" target="_blank" rel="noopener" aria-label="Facebook">{FB}</a>')
    if l.get("instagram"): socials.append(f'<a class="social" href="{e(l["instagram"])}" target="_blank" rel="noopener" aria-label="Instagram">{IG}</a>')
    socials.append(f'<a class="social" href="{maps}" target="_blank" rel="noopener" aria-label="Google">{GG}</a>')
    ld={"@context":"https://schema.org","@type":"WebPage","url":f"{DOMAIN}/{slug}/links/",
        "name":f"Links | El Rancho Grande {name}","about":{"@id":f"{DOMAIN}/#organization"}}
    doc=(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
         f'<title>Links | El Rancho Grande {e(name)}, {e(region)}</title>'
         f'<meta name="description" content="El Rancho Grande {e(name)}. Join our VIP club, see the menu, order online, get directions and follow us.">'
         f'<link rel="canonical" href="{DOMAIN}/{slug}/links/">'
         f'<meta property="og:title" content="Links | El Rancho Grande {e(name)}"><meta property="og:description" content="Join our VIP club, see the menu, order online and get directions."><meta property="og:type" content="website"><meta property="og:url" content="{DOMAIN}/{slug}/links/"><meta property="og:image" content="{DOMAIN}/assets/images/3415f02bc11c1557-800.webp">'
         f'<link rel="icon" href="/assets/brand/logo-color.webp">'
         f'<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/Tanker-Regular.woff2" crossorigin>'
         f'<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>'
         f'<style>{CSS}</style></head><body><main class="wrap">'
         f'<a href="/{slug}/"><img class="logo" src="/assets/brand/logo-color.webp" alt="El Rancho Grande Mexican Grill &amp; Cantina" width="210" height="150"></a>'
         f'<p class="loc">{e(name)}, {e(region)}</p>'
         f'<div class="beads" aria-hidden="true"></div>'
         f'<nav class="socials" aria-label="Social media">{"".join(socials)}</nav>'
         f'<div class="links">{"".join(buttons)}</div>'
         f'<p class="foot"><a href="/">elranchogrande.info</a></p>'
         f'</main></body></html>')
    p=ROOT/slug/"links"; p.mkdir(parents=True,exist_ok=True)
    (p/"index.html").write_text(doc)

if __name__=="__main__":
    for l in LOCS: build(l)
    print(f"built {len(LOCS)} location linktrees at /{{loc}}/links/")
