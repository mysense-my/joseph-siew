# Joseph Siew landing page (on the Pactum template)

A single landing page for Joseph Siew (Joseph Siew Financial Advisory), built 19 Oct 2026 as a 1:1 static rebuild of the home page of the Pactum Framer template (https://pactum-tambe.framer.website/).

- **Template's:** colours, layout, components, motion, breakpoints and behaviour, all measured from its source (`_teardown/TEARDOWN.md`, `_teardown/spec/`, `_teardown/motion/`). Palette C, the template's own teal and lime, is kept unchanged.
- **Joseph's:** content, written from `../CLIENT-BRIEF.md` and his public LinkedIn posts.

## Folders

| Path | What |
|---|---|
| `site/` | The finished page: `index.html` and `img/`. Upload as-is. |
| `build/` | Generator. `python3 build.py` rebuilds `site/index.html`. The copy is in `build.py`, styles in `css/site.css`, behaviour in `js/site.js`. `python3 assets.py` re-exports images from `img-src/template` (template stock) and `../assets/linkedin` (Joseph). `qa/` holds `check.py`, `motion.py`, `matrix.py` and screenshots. |
| `_teardown/` | Template study and tools (CDP driver, spec / choreography / hover probes). |

**Preview locally:**

```bash
cd site && python3 -m http.server 8791
```

Then open http://localhost:8791.

## Section mapping (template → Joseph)

| # | Template section | Joseph's page |
|---|---|---|
| 1 | Hero Header | "Protect What You Built And What Comes Next." Lead line, WhatsApp + How It Works. The cycling card's 3 slides are Funding Ready / Business Protection / Continuity Planned. |
| 2 | Top Features (3 autoplay tabs) | His question "If you couldn't walk into your office tomorrow…". Tabs: buy-sell / keyman / funding. Card widgets: badge column, 18 yrs + 5 trigger events, director A/B chart. |
| 3 | Services (6 cards + CTA strip) | Business Funding, Buy-Sell Agreements, Business Continuity, Keyman & Directors' Cover, Estate & Succession, Business Structuring. |
| 4 | Stats | **Skipped** until Joseph confirms real numbers. |
| 5 | About | Bank background, 3 checks, 3 feature cells. |
| 6 | Scroll Section (pinned panels) | "A will says who inherits…", 3 tools / 5 trigger events, "Tomorrow isn't promised…". |
| 7 | Team list (hover swaps the portrait) | "Who Joseph works with": 7 audiences from his seminar list, each with a photo of Joseph. |
| 8 | Case Studies (3 cards) | Talks: E3 Clubhouse finance talk, SME outlook panel, PIKOM Business After Hours. Each links to its LinkedIn post. |
| 9 | Process (4 pinned steps) + ticker + FAQs | Continuity check → Structure → Fund → Review. Ticker: "PLAN TODAY. PROTECT TOMORROW. PRESERVE YOUR LEGACY." 6 FAQs from his posts. |
| 10 | CTA (photo + lime card) | "One conversation today can prevent years of uncertainty tomorrow." |
| 11 | Testimonials + client logo grid | **Skipped** until testimonials and logo permissions are confirmed. |
| 12 | Free Consultation (form) | The form opens WhatsApp (+60 17-919 8959) with every field typed into the message. |
| 13 | Blog | 3 of his LinkedIn posts. |
| 14 | Footer CTA ("Let's Talk") | Same, with a WhatsApp button. |
| 15 | Footer | Updates form (opens WhatsApp), 3 link columns, socials, "JOSEPH SIEW FINANCIAL ADVISORY" ticker. |

## Verified (headless Chrome 155 at 1440 / 834 / 390)

- **Measured against the template, identical:** nav height (98 / 98 / 80), container, section padding (132 / 96 / 64), hero (100vh), H1 / H2 / H3 / body / ticker / eyebrow type, and hero card, service card, case card, blog card, footer and feature-media boxes.
- **No errors:** no horizontal overflow before or after scrolling, no console errors, no failed requests.
- **Motion, matching the template's numbers:**
  - nav hides by 100px on scroll down and turns light exactly below the hero
  - hero parallax 0.1×, hero intro (scale 1.2 → 1 over 1.2s, buttons after 0.3s)
  - card cycle about 4.1s
  - tabs fill over 3s then switch
  - tickers 90px/s, badge column 36px/s
  - heading colour progress within a few percent at every scroll position
  - Let's Talk scale 2 → 1, linked to scroll
  - pinned scroll panels, steps pinned at 97px (76px on tablet and phone)
  - FAQ items toggle independently
  - phone menu overlay (scroll locked)
- **Hovers, matching the template:** buttons (fill + 45° arrow), service card lift (88 → 161px), case card (chip drops in, image 1.05×, panel lightens), blog zoom, team row fade, about icon tile, footer-link dot.

## Deviations and flags

1. **Tablet menu:** built to match the template's own "Open" variant (links inline in the bar, no close button). It looks like a template bug. I recommend using the phone overlay on tablet too.
2. **Skipped content:** Stats, Testimonials + logo grid, the "4.9 ★ Trusted by brands worldwide" rating in the services strip, and the licence/insurance disclaimer. All are waiting on facts from Joseph.
3. **Team list:** each row has one ↗ link (opens WhatsApp) instead of the template's three social icons, because the rows are audiences, not people.
4. **Service-card button:** "Read More" became "Ask Joseph" and opens WhatsApp with that service named.
5. **Avatar strip** (CTA card and phone menu): four face crops of Joseph from different events, not client photos.
6. **Logo:** a text wordmark "Joseph Siew" in Rethink Sans. He has no logo file yet. The favicon is a lime "JS" on dark teal.
7. **AI photos of Joseph:** all 15 big photo slots with a person in them now show Joseph. Each one was made in Magnific (Seedream 5 Pro, 2K High) from the template's own scene plus 3 of his LinkedIn photos. Magnific made 2 versions of each; both are kept in `build/img-src/magnific/out/<slot>_a.png` / `_b.png`, and the page uses `_a`. To use the other version, change `mag("<slot>")` to `mag("<slot>", "b")` in `assets.py`. The template's stock photos are still used in 3 slots: card-3, story-1 and contact (buildings and an empty office, no people).
   The hero crop on tablet and phone moved from `100% 0%` to `85% 0%` (`--hero-pos` in `site.css`), so Joseph stays in frame.
8. **Joseph's photos** are LinkedIn-compressed (750–1080px). They look soft on large retina screens. Ask him for originals.
9. **Hero headline:** rewritten to fit the template's 3-line measure. One sentence, no dash.

## Not verified

- Real iPhone Safari. The WebKit harness passed at 1440 / 834 / 390, both before and after the photo swap.
- Real touch devices.
- The WhatsApp links actually opening the app.
