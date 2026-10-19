"""Builds Joseph Siew's landing page (site/index.html) on a 1:1 static rebuild of the Pactum Framer template
(https://pactum-tambe.framer.website/, home page only).

Layout, components, motion, breakpoints and colours: the template's, measured from its source (see
../_teardown/TEARDOWN.md). Content: Joseph's, from ../../CLIENT-BRIEF.md and his public LinkedIn posts.
Skipped until Joseph confirms the facts (user's call, 19 Oct 2026): Stats section, Testimonials + client logo
grid, the 4.9-star rating, licence disclaimer.   Run: python3 build.py   (python3 assets.py if images changed)
"""
import html
import json
import os
import re
import shutil
import urllib.parse

import springs

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
E = html.escape

# ------------------------------------------------------------------ facts (CLIENT-BRIEF.md)
NAME = "Joseph Siew"
BRAND = "Joseph Siew Financial Advisory"
WA_NUMBER = "60179198959"            # from his LinkedIn headline ("Ask me - 60179198959")
PHONE_DISPLAY = "+60 17-919 8959"
LINKEDIN = "https://www.linkedin.com/in/joseph-siew-financial-advisory-489814360/"
INSTAGRAM = "https://www.instagram.com/josephsiew/"
FACEBOOK = "https://www.facebook.com/joseph.siew.56"
LOCATION = "Selangor, Malaysia"


def wa(text):
    return "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote(text)


WA_HELLO = wa("Hi Joseph, I'd like to talk about protecting and planning for my business.")

# ------------------------------------------------------------------ icons (the template's own SVGs, see icons/)
ICON_DIR = os.path.join(HERE, "icons")
SPRITE_IDS = ["arrow-ne", "x", "instagram", "linkedin", "mail", "phone", "pin", "arrow-left", "tab-1", "tab-2",
              "tab-3", "feat-1", "feat-2", "feat-3", "arrow-right", "chev-down", "star"]


def sprite():
    out = []
    for name in SPRITE_IDS:
        s = open(os.path.join(ICON_DIR, name + ".svgfrag")).read()
        vb = re.search(r'viewBox="([^"]+)"', s).group(1)
        inner = re.sub(r"^<svg[^>]*>|</svg>$", "", s.strip())
        inner = re.sub(r'stroke="var\(--[a-z0-9]+, [^)]+\)"', 'stroke="currentColor"', inner)
        inner = re.sub(r'stroke="var\(--token-[^)]+\)\)"', 'stroke="currentColor"', inner)
        inner = re.sub(r'fill="var\(--[a-z0-9]+, [^)]+\)"', 'fill="currentColor"', inner)
        inner = re.sub(r'fill="var\(--token-[^)]+\)\)"', 'fill="currentColor"', inner)
        inner = re.sub(r'stroke-width="var\(--[a-z0-9]+, ([0-9.]+)\)"', r'stroke-width="\1"', inner)
        inner = re.sub(r' id="[^"]*"', "", inner)
        out.append(f'<symbol id="i-{name}" viewBox="{vb}">{inner}</symbol>')
    # Facebook: the template's footer uses a stroked "f" in the same 24px grid
    out.append('<symbol id="i-facebook" viewBox="0 0 24 24"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v7h4v-7h3l1-4h-4V8z" '
               'fill="transparent" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>')
    return '<svg class="sprite" aria-hidden="true" focusable="false">' + "".join(out) + "</svg>"


def ic(name, cls="ic"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


def mask_icon(name):
    """CSS mask icons (the template's alpha-mask components) live in css as .mi--name."""
    return f'<span class="mi mi--{name}" aria-hidden="true"></span>'


# ------------------------------------------------------------------ small builders


def btn(label, href, kind="dark", arrow=True, extra="", cls=""):
    """Template button. kind: dark | light | line-dark | line-light. Desktop 50px, phone 44px."""
    ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
    return (f'<a class="btn btn--{kind} {cls}" href="{E(href)}"{ext}{extra}><span class="btn__t">{E(label)}</span>'
            + (ic("arrow-ne", "btn__ic") if arrow else "") + "</a>")


def eyebrow(text, tone="dark"):
    return f'<div class="eyebrow eyebrow--{tone}"><span class="eyebrow__dot"></span><p class="t-14s">{E(text)}</p></div>'


def colour_text(text, tag="p", cls="", tone="light"):
    """TextColorTransform: every character runs from the grey 'from' colour to the ink 'to' colour as the
    paragraph scrolls from 'start 0.75' to 'start 0.15'. Words are kept intact; chars carry the index."""
    words = text.split(" ")
    parts = []
    for w in words:
        chars = "".join(f"<span>{E(ch)}</span>" for ch in w)
        parts.append(f'<span class="ctw">{chars}&nbsp;</span>')
    return f'<{tag} class="ctext ctext--{tone} {cls}" data-ctext aria-label="{E(text)}"><span aria-hidden="true">{"".join(parts)}</span></{tag}>'


def r(d=None, kind="up", mount=False):
    """Reveal attributes. kind: up (y20 spring 1.2 / .1), up30, up40, up120, x-50, x50, fade, s12 (scale 1.2 in view)."""
    a = f' data-r="{kind}"'
    if d is not None:
        a += f' data-d="{d}"'
    if mount:
        a += " data-mount"
    return a


def mline(extra=""):
    """Template 'Moving Line': a 1px line that draws in (width 1% -> 100%) when half in view."""
    return f'<div class="mline {extra}" aria-hidden="true"><div class="mline__wrap"><div class="mline__line"></div></div></div>'


WIDTHS = json.load(open(os.path.join(HERE, "img-widths.json")))


def srcset(name):
    ws = WIDTHS.get(name, [])
    if len(ws) < 2:
        return ""
    full = ws[0]
    return ", ".join([f"img/{name}-{w}.webp {w}w" for w in sorted(ws[1:])] + [f"img/{name}.webp {full}w"])


def img(name, alt, cls="", sizes="100vw", lazy=True, pos=None):
    st = f' style="object-position:{pos}"' if pos else ""
    ss = srcset(name)
    return (f'<img class="{cls}" src="img/{name}.webp"' + (f' srcset="{ss}"' if ss else "") + f' alt="{E(alt)}"'
            + (' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"') + f' sizes="{sizes}"{st}>')


def minify(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};:,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


# ------------------------------------------------------------------ content

NAV = [("Home", "#top"), ("About", "#about"), ("Services", "#services"), ("How It Works", "#process"),
       ("Talks", "#talks"), ("FAQs", "#faq")]

HERO = dict(
    h1="Protect What You Built And What Comes Next.",
    lead=("A former senior banker with 18 years in SME financing, helping Malaysian business owners fund growth, "
          "protect what they built and plan what happens next."),
    cards=[
        ("Funding Ready", "Get your business ready for the financing that fuels its next stage of growth.", "card-1",
         "Joseph Siew pointing out the city view with a client"),
        ("Business Protection", "Buy-sell agreements and keyman cover, so one event never decides your company's future.",
         "card-2", "Joseph Siew in a meeting with two business owners"),
        ("Continuity Planned", "A clear plan, so your family, partners and team know exactly what happens next.", "card-3",
         "A glass office building"),
    ],
)

APPROACH = dict(
    heading="If you couldn't walk into your office tomorrow, what would happen to your business?",
    eyebrow="Where business continuity begins",
    lead=("For many owners, the business revolves around them. They make the key decisions, approve payments and hold "
          "the relationships. Without a plan, that dependence becomes the biggest risk in the company."),
    body=("Joseph has sat across the table from thousands of SME owners. Building a successful business is an achievement. "
          "Building one that can continue without you is a legacy."),
    tabs=[
        ("tab-1", "Partners buy your shares at a pre-agreed price, and your family gets a fair payout."),
        ("tab-2", "Keyman and directors' cover keeps the business funded if a key decision-maker is gone."),
        ("tab-3", "Structured funding gives the business capital to grow without giving away control."),
    ],
    badges=["Smooth ownership transition", "The business keeps running", "A fair payout to the family",
            "No disputes or deadlocks", "Partners stay in control"],
    counters=[("18", "yrs", "In senior banking leadership, focused on SME financing"),
              ("5", "", "Trigger events a buy-sell agreement can cover")],
    chart=("Two directors, two families. One agreement protects them both.", [("A", 96), ("B", 75)]),
)

SERVICES = dict(
    eyebrow="Funding, protection and continuity",
    heading="Everything a business owner needs to fund it, protect it and pass it on.",
    items=[
        ("pay", "Business Funding", "Access the right bank financing and structured funding to support daily operations and growth."),
        ("agreement", "Buy-Sell Agreements", "Pre-agreed share transfers funded by insurance, so ownership changes hands smoothly."),
        ("continuity", "Business Continuity", "A practical plan for what happens if an owner or key person can no longer lead."),
        ("keyman", "Keyman & Directors' Cover", "Protect the business against losing the people its decisions depend on."),
        ("estate", "Estate & Succession", "Wills, trusts and succession planning that keep family and business aligned."),
        ("strategy", "Business Structuring", "Get fund-ready and future-proof with a structure built for the next stage."),
    ],
    cta="From first-time founders to family businesses, Joseph helps owners plan funding, protection and continuity in one conversation.",
)

ABOUT = dict(
    h3="From the bank's side of the table to yours.",
    text=("Joseph spent 18 years in leadership roles at the head office of one of Malaysia's largest financial "
          "institutions, working on commercial banking, B2B funding and SME financing. Today he brings that "
          "experience straight to business owners."),
    checks=["Former senior banker, 18 years in SME financing", "E3 Finance & Investment PowerTeam Director",
            "Estate planning franchise and insurance agency licences"],
    feats=[("feat-1", "Funding solutions", "Bank financing and capital pathways matched to your stage of growth."),
           ("feat-2", "Risk management", "Keyman, directors' and business cover so one event can't undo years of work."),
           ("feat-3", "Continuity planning", "Buy-sell agreements, wills and trusts that keep the business running.")],
)

STORY = dict(
    eyebrow="Beyond a will",
    h3="A will says who inherits. It doesn't keep your business running.",
    counters=[("3", "Tools to compare: will, trust and buy-sell agreement"),
              ("5", "Trigger events to plan for: death, disability, exit, divorce, bankruptcy")],
    quote="Tomorrow isn't promised, but continuity can be planned.",
)

WHO = dict(
    eyebrow="Who Joseph works with",
    heading="Built for the people who carry a business on their shoulders.",
    rows=[("SME Owners", "The business still runs through you", "who-1"),
          ("Founders & Entrepreneurs", "Scaling fast and planning ahead", "who-2"),
          ("Business Partners", "Shares held in more than one name", "who-3"),
          ("Company Directors", "Decisions that can't wait", "who-4"),
          ("Family Business Owners", "Keeping family and business aligned", "who-5"),
          ("Professionals With Shares", "Your stake and your family's security", "who-6"),
          ("Legacy Builders", "A business built to outlast its founder", "who-7")],
    cta="Whichever seat you sit in, the first step is the same: one honest conversation about what happens next.",
)

TALKS = dict(
    eyebrow="Talks, panels and seminars",
    heading="Sharing what most business owners only learn when it's too late.",
    cards=[
        ("E3 Clubhouse", "Growing, scaling and protecting your business",
         "The first E3 finance talk series: how to grow a business, scale it, protect it and keep it as your legacy.",
         "talk-1", "Joseph presenting at the E3 Clubhouse finance talk",
         "https://www.linkedin.com/posts/joseph-siew-489814360_thank-you-everyone-for-dropping-by-e3-clubhouse-activity-7386931262290116608-ez1p"),
        ("Panel", "Malaysia's 2025/26 financial outlook for SMEs",
         "A panel on what the year ahead means for entrepreneurs and corporates, and how to stay financially resilient.",
         "talk-2", "Joseph on a panel at the Empowering SME Growth event",
         "https://www.linkedin.com/posts/joseph-siew-489814360_entrepreneurs-open-day-kl-this-thursday-was-activity-7400674589778817024-B3e8"),
        ("Networking", "Business After Hours with PIKOM",
         "An evening of founders, investors and industry leaders, and the conversations that start real partnerships.",
         "talk-3", "A crowd at the Business After Hours networking evening",
         "https://www.linkedin.com/posts/joseph-siew-financial-advisory-489814360_last-saturday-evening-join-abang-pikom-activity-7508005346951553024-NCEd"),
    ],
    cta="Joseph runs regular sessions on continuity, funding and succession. Ask about the next one.",
)

PROCESS = dict(
    eyebrow="How it works",
    heading="Four steps from first conversation to a plan that protects everyone.",
    steps=[
        ("Continuity check", "A conversation about how your business runs today, who it depends on and what would happen if you couldn't be there tomorrow.",
         ["Map key people and shareholders", "Spot the gaps in your current plan"], "step-1"),
        ("Structure the agreement", "Agree how shares transfer, and at what value, if a trigger event happens: death, disability, exit, divorce or bankruptcy.",
         ["Set the trigger events", "Agree a fair valuation method"], "step-2"),
        ("Fund the plan", "Choose how the payout is funded, through cross-purchase cover, company-owned policies or instalment payments.",
         ["Cross-purchase or entity purchase", "Match the cover to the share value"], "step-3"),
        ("Review and keep current", "Revisit the plan as the business grows, partners change and valuations move, so it still works when it's needed.",
         ["Regular plan reviews", "Updates as the business changes"], "step-4"),
    ],
    ticker="PLAN TODAY. PROTECT TOMORROW. PRESERVE YOUR LEGACY.",
)

FAQ = dict(
    intro="Find answers to the questions owners ask most about buy-sell agreements, continuity planning and funding.",
    items=[
        ("What is a buy-sell agreement?", "A legally binding contract between shareholders or directors that sets out what happens to shares when a trigger event occurs, such as death, disability or exit. It means a smooth ownership transition and a fair payout to the family."),
        ("I already have a will. Isn't that enough?", "A will says who inherits your assets. It doesn't make sure your business keeps operating, that your partners can buy over your shares, or that your family gets immediate financial support."),
        ("How is a buy-sell agreement funded?", "Usually with life insurance. Each shareholder can hold a policy on the other (cross-purchase), the company can own the policies (entity purchase), or the payout can be made in instalments."),
        ("Who needs one?", "Any Sdn Bhd with two or more shareholders or directors, family businesses, partners who built the company together, and professionals who hold company shares."),
        ("Can you help us get bank financing?", "Yes. Joseph spent 18 years in SME financing and helps owners understand which funding options fit their stage, structure and plans."),
        ("How do we get started?", "Send Joseph a WhatsApp message or fill in the form on this page. He'll reply to arrange a time to talk."),
    ],
)

CTA = dict(
    h6="One conversation today can prevent years of uncertainty tomorrow.",
    p="From the first check to a funded plan, Joseph walks you through every step in plain language.",
)

CONTACT = dict(
    eyebrow="Talk to Joseph",
    h3="Start planning what happens next.",
    p="Tell Joseph about your business and what you'd like to protect. He'll reply on WhatsApp to arrange a time.",
)

POSTS = [
    ("Jun 20, 2025", "Buy-Sell", "Buy-sell agreement: a must-have for business continuity",
     "What happens to your shares if a director passes away, and how Malaysian owners fund a fair buyout.",
     "post-1", "Diagram of a buy-sell agreement between two directors",
     "https://www.linkedin.com/posts/joseph-siew-financial-advisory-489814360_estateplanning-businesscontinuity-buysellagreement-activity-7341731025032548352-HqAR"),
    ("Aug 6, 2026", "Continuity", "“I have a will. Isn't that enough?”",
     "Why a will is only one piece of the puzzle, and what a full business continuity plan adds.",
     "post-2", "Joseph with a business owner at an event",
     "https://www.linkedin.com/posts/joseph-siew-financial-advisory-489814360_businesscontinuity-buysellagreement-estateplanning-activity-7491006866550861825-jic_"),
    ("Aug 3, 2026", "SME Owners", "The question nobody wants to answer",
     "If you couldn't walk into your office tomorrow, would your business continue with confidence?",
     "post-3", "Joseph speaking on strategic financing",
     "https://www.linkedin.com/posts/joseph-siew-financial-advisory-489814360_businesscontinuity-smeowners-leadership-activity-7489858504917209088-VqdM"),
]

FOOTER_COLS = [
    ("Explore", [("About Joseph", "#about"), ("How It Works", "#process"), ("Talks & Events", "#talks"),
                 ("FAQs", "#faq"), ("Insights", "#insights"), ("Contact", "#contact")]),
    ("Services", [(s[1], "#services") for s in SERVICES["items"]]),
    ("Connect", [("WhatsApp", WA_HELLO), ("LinkedIn", LINKEDIN), ("Instagram", INSTAGRAM), ("Facebook", FACEBOOK)]),
]

# ------------------------------------------------------------------ sections


def logo(tone):
    return f'<a class="logo logo--{tone}" href="#top" aria-label="{E(NAME)}, home"><span class="logo__t">{E(NAME)}</span></a>'


def nav():
    links = "".join(
        f'<li><a class="nlink{" is-active" if i == 0 else ""}" href="{h}"><span class="nlink__dot"></span><span>{E(t)}</span></a></li>'
        for i, (t, h) in enumerate(NAV))
    mlinks = "".join(f'<li><a class="mlink{" is-active" if i == 0 else ""}" href="{h}">{E(t)}</a></li>' for i, (t, h) in enumerate(NAV))
    avatars = "".join(f'<span class="av av--{i}">{img("av-" + str(i), "", sizes="40px")}</span>' for i in range(1, 5))
    return f"""
<header class="nav" data-nav>
  <div class="nav__bar">
    <div class="nav__in">
      <div class="nav__logo">{logo("light")}{logo("dark")}</div>
      <ul class="nav__links">{links}</ul>
      <div class="nav__cta">{btn("Book A Chat", WA_HELLO, "light", cls="nav__btn")}</div>
      <button class="burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mmenu"><span></span><span></span><span></span></button>
    </div>
  </div>
  <div class="mmenu" id="mmenu" hidden>
    <div class="mmenu__top">{logo("light")}<button class="mmenu__x" type="button" aria-label="Close menu"><span></span><span></span></button></div>
    <ul class="mmenu__links">{mlinks}</ul>
    <div class="mmenu__card"><div class="mmenu__in">
      <div class="avs">{avatars}</div>
      <p class="t-20">Funding, protection and continuity for Malaysian SME owners.</p>
      {btn("WhatsApp Joseph", WA_HELLO, "light", cls="btn--sm")}
    </div></div>
  </div>
</header>"""


def hero():
    cards = []
    for i, (t, p, im, alt) in enumerate(HERO["cards"]):
        bullets = "".join(f'<button class="hcard__dot{" is-on" if j == i else ""}" type="button" aria-label="Show slide {j + 1}" data-go="{j}"></button>'
                          for j in range(3))
        cards.append(f"""<div class="hcard{" is-on" if i == 0 else ""}" data-slide="{i}"{"" if i == 0 else ' aria-hidden="true"'}>
          <div class="hcard__text"><div class="hcard__copy"><p class="t-22">{E(t)}</p><p class="t-16 c-muted">{E(p)}</p></div>
            <div class="hcard__dots">{bullets}</div></div>
          <div class="hcard__img">{img(im, alt, sizes="(max-width: 809px) 144px, 236px")}</div>
        </div>""")
    return f"""
<section class="hero" id="top">
  <div class="hero__bg" data-parallax="0.1"><div class="hero__zoom" data-mountzoom>{img("hero", "Joseph Siew with a tablet by a tall office window", lazy=False, pos="var(--hero-pos)")}</div>
    <div class="ov ov--15"></div><div class="ov ov--grad"></div></div>
  <div class="hero__in">
    <div class="hero__content">
      <h1 class="t-h1">{E(HERO["h1"])}</h1>
      <div class="hero__text">
        {mline("mline--light mline--hero")}
        <div class="hero__row">
          <div class="hero__cta">
            <a class="hero__scroll" href="#approach"><span class="t-14 c-white">SCROLL DOWN</span><span class="hero__chev">{ic("chev-down", "ic-chev")}</span></a>
            <span class="hero__div" aria-hidden="true"></span>
            <div class="hero__tc">
              <p class="t-18 c-soft">{E(HERO["lead"])}</p>
              <div class="btns"{r(0.3, "up", mount=True)} data-hero-btns>{btn("WhatsApp Joseph", WA_HELLO, "light")}{btn("How It Works", "#process", "line-light", arrow=False)}</div>
            </div>
          </div>
          <div class="hero__cards" data-cycle>{"".join(cards)}</div>
        </div>
      </div>
    </div>
  </div>
</section>"""


def approach():
    tabs = []
    for i, (icn, text) in enumerate(APPROACH["tabs"]):
        tabs.append(f"""<button class="tab{" is-on" if i == 0 else ""}" type="button" data-tab="{i}"{r(round(0.2 + 0.1 * i, 1))}>
          <span class="tab__bar" aria-hidden="true"><span></span></span>
          <span class="tab__c">{ic(icn, "ic-40")}<span class="t-18 c-muted tab__t">{E(text)}</span></span></button>""")
    badges = "".join(f'<li class="badge"><span class="badge__ck">{mask_icon("check")}</span><span class="t-14 c-ink2">{E(b)}</span></li>' for b in APPROACH["badges"])
    (n1, u1, l1), (n2, u2, l2) = APPROACH["counters"]
    chart_t, bars = APPROACH["chart"]
    bar_html = "".join(f'<div class="chart__bar chart__bar--{k}" style="height:{h}%"{r(round(0.1 * k, 1), "up30")}><span class="t-22 chart__v">{E(lbl)}</span></div>'
                       for k, (lbl, h) in enumerate(bars))
    widgets = [
        f'<div class="ticker-v"><div class="ticker-v__ul" data-vticker><ul class="vset">{badges}</ul><ul class="vset" aria-hidden="true">{badges}</ul></div></div>',
        f"""<div class="fcounters"><div class="fcount fcount--white"{r(0, "up30")}><p class="t-72">{E(n1)}<span class="unit">{E(u1)}</span></p><p class="t-16 c-muted">{E(l1)}</p></div>
            <div class="fcount fcount--lime"{r(0.2, "up30")}><p class="t-72">{E(n2)}<span class="unit">{E(u2)}</span></p><p class="t-16 c-muted">{E(l2)}</p></div></div>""",
        f"""<div class="chart"{r(0, "up30")}><div class="chart__text"><p class="t-20 chart__t">{E(chart_t)}</p>{mask_icon("agreement")}</div><div class="chart__bars">{bar_html}</div></div>""",
    ]
    imgs = ["feat-1", "feat-2", "feat-3"]
    imgs_m = ["feat-1", "feat-2m", "feat-3m"]
    alts = ["Joseph Siew in a client meeting", "Joseph Siew talking a business owner through a plan", "Joseph Siew reviewing a plan with a client on a laptop"]
    cards = []
    for i in range(3):
        icn, text = APPROACH["tabs"][i]
        cards.append(f"""<div class="fcard{" is-on" if i == 0 else ""}" data-card="{i}">
          <div class="fcard__desc">{ic(icn, "ic-40")}<p class="t-18 c-muted">{E(text)}</p></div>
          <div class="fcard__media"><picture><source media="(max-width: 1279.98px)" srcset="{srcset(imgs_m[i]) or "img/" + imgs_m[i] + ".webp"}" sizes="100vw">{img(imgs[i], alts[i], pos="50% 100%" if i != 1 else None)}</picture>
            <div class="ov {"ov--deep15" if i == 0 else "ov--black30"}"></div>
            <div class="fcard__w fcard__w--{i}">{widgets[i]}</div></div>
        </div>""")
    return f"""
<section class="sec approach" id="approach">
  <div class="wrap">
    <div class="approach__text">
      <div class="title-64">{colour_text(APPROACH["heading"], "h2", "t-64")}</div>
      <div class="split">
        {eyebrow(APPROACH["eyebrow"])}
        <div class="split__r">
          <p class="t-20 c-ink2">{E(APPROACH["lead"])}</p>
          <p class="t-18 c-muted">{E(APPROACH["body"])}</p>
          <div class="btns">{btn("Book A Chat", WA_HELLO, "dark")}{btn("Joseph's Story", "#about", "line-dark", arrow=False)}</div>
        </div>
      </div>
    </div>
    <div class="feats" data-feats{r(0.4, "up120")}>
      <div class="feats__tabs">{"".join(tabs)}</div>
      <div class="feats__cards">{"".join(cards)}</div>
    </div>
  </div>
</section>"""


def services():
    cards = []
    for i, (icn, t, p) in enumerate(SERVICES["items"]):
        d = round(0.2 + 0.1 * (i % 3), 1)
        cards.append(f"""<div class="scard"{r(d)}>
          <div class="scard__icon">{mask_icon(icn)}</div>
          <div class="scard__c"><div class="scard__t"><h3 class="t-24 c-ink">{E(t)}</h3><p class="t-18 c-muted">{E(p)}</p></div>
            <div class="scard__more"><div class="scard__mi">{btn("Ask Joseph", wa("Hi Joseph, I'd like to know more about " + t.lower() + "."), "line-dark", arrow=False)}</div></div></div>
        </div>""")
    return f"""
<section class="sec services" id="services">
  <div class="wrap services__wrap">
    <div class="title">{eyebrow(SERVICES["eyebrow"])}{colour_text(SERVICES["heading"], "h2", "t-64")}</div>
    <div class="frame frame--light services__frame">
      <div class="services__grid">{"".join(cards)}</div>
      <div class="services__cta"{r(0.2)}><p class="t-18 c-muted">{E(SERVICES["cta"])}</p><div class="services__ctab">{btn("Get Advice", WA_HELLO, "dark")}</div></div>
    </div>
  </div>
</section>"""


def about():
    checks = []
    for i, c in enumerate(ABOUT["checks"]):
        if i:
            checks.append(mline("mline--grey"))
        checks.append(f'<div class="check">{mask_icon("check-s")}<p class="t-16 c-muted">{E(c)}</p></div>')
    feats = "".join(
        f'<div class="afeat afeat--{i}"><div class="afeat__ic">{ic(icn, "ic-24")}</div><div class="afeat__t"><p class="t-22 c-ink2">{E(t)}</p><p class="t-16 c-muted">{E(p)}</p></div></div>'
        for i, (icn, t, p) in enumerate(ABOUT["feats"]))
    return f"""
<section class="sec about" id="about">
  <div class="wrap">
    <div class="about__top">
      <div class="about__img"><div class="about__zoom"{r(0, "s12")}><div class="about__par" data-iparallax>{img("about", "Joseph Siew speaking with a microphone at a business event", sizes="(max-width: 809px) 350px, 664px")}</div></div></div>
      <div class="about__sp" aria-hidden="true"></div>
      <div class="about__c">
        <div class="about__t">
          <h2 class="t-44 c-ink2">{E(ABOUT["h3"])}</h2>
          <div class="about__tc"><p class="t-18 c-muted">{E(ABOUT["text"])}</p>
            <div class="btns">{btn("Our Services", "#services", "dark")}{btn("Learn More", "#story", "line-dark", arrow=False)}</div></div>
        </div>
        <div class="checks">{"".join(checks)}</div>
      </div>
    </div>
    <div class="afeats">{feats}</div>
  </div>
</section>"""


def story():
    ctr = "".join(f'<div class="scount"{r(0.2 * i, "up30")}><p class="t-72 c-ink2">{E(n)}</p><p class="t-16 c-muted">{E(l)}</p></div>'
                  for i, (n, l) in enumerate(STORY["counters"]))
    return f"""
<section class="story" id="story">
  <div class="story__p story__p--1">
    <div class="story__half story__copy">
      <div class="story__c">
        <div class="story__title">{eyebrow(STORY["eyebrow"])}<h2 class="t-44 c-ink2">{E(STORY["h3"])}</h2></div>
        <div class="frame frame--deep scounts">{ctr}</div>
      </div>
    </div>
    <div class="story__half story__img">{img("story-1", "A modern glass office tower", sizes="(max-width: 809px) 100vw, 50vw")}</div>
  </div>
  <div class="story__p story__p--2">
    <div class="story__half story__empty" aria-hidden="true"></div>
    <div class="story__half story__dark">
      <div class="story__q">{mask_icon("papers")}
        <div class="story__qt"><p class="t-36 c-lime">{E(STORY["quote"])}</p>{btn("Book A Chat", WA_HELLO, "light")}</div></div>
    </div>
  </div>
  <div class="story__p story__p--3">
    <div class="story__half story__img">{img("story-3", "Joseph Siew relaxing by an office window", sizes="(max-width: 809px) 100vw, 50vw")}</div>
    <div class="story__half story__clear" aria-hidden="true"></div>
  </div>
</section>"""


def who():
    rows = []
    for i, (t, j, im) in enumerate(WHO["rows"]):
        rows.append(f"""<a class="wrow{" is-on" if i == 0 else ""}" href="{E(wa("Hi Joseph, I'm one of the " + t.lower() + " you work with. I'd like to talk."))}" target="_blank" rel="noopener" data-who="{i}">
          <span class="wrow__t t-22 c-ink">{E(t)}</span>
          <span class="wrow__j"><span class="t-16 c-muted">{E(j)}</span><span class="wrow__ic">{ic("arrow-ne", "ic-20")}</span></span></a>""")
    pics = "".join(f'<div class="wpic{" is-on" if i == 0 else ""}" data-pic="{i}">{img(im, "Joseph Siew at a business event", sizes="472px")}</div>'
                   for i, (_, _, im) in enumerate(WHO["rows"]))
    return f"""
<section class="sec who" id="who">
  <div class="wrap">
    <div class="title title--split">{eyebrow(WHO["eyebrow"])}<div class="title__sp" aria-hidden="true"></div>{colour_text(WHO["heading"], "h2", "t-64")}</div>
    <div class="who__body">
      <div class="who__img"{r(0, "up40")}>{pics}</div>
      <div class="who__sp" aria-hidden="true"></div>
      <div class="who__right"{r(0.1, "up40")}>
        {mline("mline--grey mline--who")}
        <div class="who__rows">{"".join(rows)}</div>
        <div class="who__cta"><p class="t-18 c-muted">{E(WHO["cta"])}</p>
          <div class="btns">{btn("Book A Chat", WA_HELLO, "dark")}{btn("Connect On LinkedIn", LINKEDIN, "line-dark", arrow=False)}</div></div>
      </div>
    </div>
  </div>
</section>"""


def talks():
    cards = []
    for i, (chip, t, p, im, alt, href) in enumerate(TALKS["cards"]):
        cards.append(f"""<article class="tcard"{r(round(0.2 + 0.1 * i, 1))}>
          <div class="tcard__media"><span class="chip chip--dark t-12">{E(chip)}</span><div class="tcard__zoom">{img(im, alt, sizes="(max-width: 809px) 346px, 451px")}</div></div>
          <div class="tcard__c"><h3 class="t-24 c-white">{E(t)}</h3><div class="tcard__d"><p class="t-16 c-soft">{E(p)}</p>{btn("Read On LinkedIn", href, "line-light", arrow=False)}</div></div>
        </article>""")
    return f"""
<section class="sec sec--dark talks" id="talks">
  <div class="wrap talks__wrap">
    <div class="title">{eyebrow(TALKS["eyebrow"], "lime")}{colour_text(TALKS["heading"], "h2", "t-64", tone="dark")}</div>
    <div class="talks__body">
      <div class="frame frame--dark talks__grid">{"".join(cards)}</div>
      <div class="talks__cta"><p class="t-18 c-soft">{E(TALKS["cta"])}</p>
        <div class="btns btns--c">{btn("Join The Next Session", wa("Hi Joseph, please let me know about your next session."), "light")}{btn("See On LinkedIn", LINKEDIN, "line-light", arrow=False)}</div></div>
    </div>
  </div>
</section>"""


def process():
    steps = []
    for i, (t, p, checks, im) in enumerate(PROCESS["steps"]):
        ck = []
        for k, c in enumerate(checks):
            if k:
                ck.append(mline("mline--grey"))
            ck.append(f'<div class="check">{mask_icon("check-s")}<p class="t-16 c-muted">{E(c)}</p></div>')
        steps.append(f"""<div class="step"><div class="step__in">
          <p class="step__n t-104" aria-hidden="true">{i + 1}</p>
          <div class="step__ti">
            <div class="step__text"><div class="step__title"><h3 class="t-24 c-ink2">{E(t)}</h3><p class="t-16 c-muted">{E(p)}</p></div><div class="checks">{"".join(ck)}</div></div>
            <div class="step__img"><div class="step__zoom"{r(0, "s12")}>{img(im, "", sizes="(max-width: 809px) 278px, 508px")}</div></div>
          </div></div></div>""")
    faqs = []
    for i, (q, a) in enumerate(FAQ["items"]):
        faqs.append(f"""<div class="acc__item{" is-open" if i == 0 else ""}"{r(round(0.5 + 0.05 * i, 2), "up10")}>
          <button class="acc__q" type="button" aria-expanded="{"true" if i == 0 else "false"}" aria-controls="faq-{i}" id="faq-q-{i}">
            <span class="t-20 c-ink">{E(q)}</span><span class="acc__ic" aria-hidden="true"><i></i><i></i></span></button>
          <div class="acc__panel" id="faq-{i}" role="region" aria-labelledby="faq-q-{i}"><div class="acc__a"><p class="t-16 c-muted">{E(a)}</p></div></div>
          {mline("mline--grey mline--acc")}
        </div>""")
    tick = f'<p class="t-144 c-line">{E(PROCESS["ticker"])}&nbsp;</p>'
    return f"""
<section class="sec process" id="process">
  <div class="wrap process__wrap">
    <div class="process__top">
      <div class="title title--split">{eyebrow(PROCESS["eyebrow"])}<div class="title__sp" aria-hidden="true"></div>{colour_text(PROCESS["heading"], "h2", "t-64")}</div>
      <div class="steps">{"".join(steps)}</div>
    </div>
    <div class="ticker" data-ticker="90" aria-hidden="true"><div class="ticker__ul">{tick}{tick}</div></div>
    <div class="faqs" id="faq">
      <div class="faqs__head">{mline("mline--grey")}<div class="faqs__ht"><h2 class="t-24 c-ink2"{r(0, "up24")}>Help &amp; FAQs</h2>
        <div class="faqs__sub"{r(0.1, "up24")}><p class="t-14 c-muted">Questions? Here are the answers owners ask most</p><span class="eyebrow__dot"></span></div></div></div>
      <div class="faqs__body">
        <div class="faqs__cta"{r(0.2, "up30")}><p class="t-18 c-muted">{E(FAQ["intro"])}</p>
          <div class="faqs__btn"><p class="t-16 c-ink2">Still have questions?</p>{btn("Ask Joseph", WA_HELLO, "dark")}</div></div>
        <div class="faqs__sp" aria-hidden="true"></div>
        <div class="acc"{r(0.5, "up30")}>{"".join(faqs)}</div>
      </div>
    </div>
  </div>
</section>"""


def cta():
    avatars = "".join(f'<span class="av av--{i}" data-av="{i}">{img("av-" + str(i), "", sizes="40px")}</span>' for i in range(1, 5))
    return f"""
<section class="ctas" id="talk-cta">
  <div class="ctas__bg"><div class="ctas__zoom" data-inzoom>{img("cta", "Joseph Siew walking through a bright office lobby", sizes="100vw")}</div><div class="ov ov--cta"></div></div>
  <div class="ctas__wrap">
    <div class="ctas__card">
      <div class="ctas__text"><div class="avs" data-avs>{avatars}</div><h2 class="t-24 c-ink2">{E(CTA["h6"])}</h2><p class="t-16 c-ink2">{E(CTA["p"])}</p></div>
      <a class="ctas__btn" href="{E(WA_HELLO)}" target="_blank" rel="noopener"><span class="t-ui c-white">Book A Chat</span>{ic("arrow-ne", "btn__ic")}</a>
    </div>
  </div>
</section>"""


def contact():
    opts = "".join(f'<option>{E(s[1])}</option>' for s in SERVICES["items"])
    return f"""
<section class="contact" id="contact">
  <div class="contact__bg">{img("contact", "A quiet modern office", sizes="100vw")}<div class="ov ov--c55"></div><div class="ov ov--cgrad"></div></div>
  <div class="contact__wrap">
    <div class="contact__in">
      <div class="contact__l"{r(0, "x-50")}>
        <div class="contact__t">
          <div class="contact__title">{eyebrow(CONTACT["eyebrow"], "lime")}<h2 class="t-44 c-white">{E(CONTACT["h3"])}</h2></div>
          <div class="contact__tx"><p class="t-18 c-soft">{E(CONTACT["p"])}</p>
            <div class="btns">{btn("WhatsApp Joseph", WA_HELLO, "light")}{btn("LinkedIn", LINKEDIN, "line-light", arrow=False)}</div></div>
        </div>
        <div class="contact__info">
          <div class="cinfo__row">
            <a class="cinfo" href="{E(WA_HELLO)}" target="_blank" rel="noopener">{ic("phone", "ic-24")}<span class="t-ui c-white">{E(PHONE_DISPLAY)}</span></a>
            <span class="cinfo__div" aria-hidden="true"></span>
            <a class="cinfo" href="{E(LINKEDIN)}" target="_blank" rel="noopener">{ic("linkedin", "ic-24")}<span class="t-ui c-white">LinkedIn</span></a>
          </div>
          {mline("mline--light")}
          <div class="cinfo__row cinfo__row--2"><span class="cinfo">{ic("pin", "ic-24")}<span class="t-ui c-white">{E(LOCATION)}</span></span></div>
        </div>
      </div>
      <div class="contact__sp" aria-hidden="true"></div>
      <div class="cform"{r(0.4, "x50")}>
        <div class="cform__in">
          <h2 class="t-24 c-ink2">Request a consultation</h2>
          <form class="form" id="enquiry" novalidate>
            <div class="form__row">
              <label class="field"><span class="field__l t-14">Full Name*</span><span class="field__w"><input name="name" type="text" autocomplete="name" placeholder="ex. Tan Wei Ming" required></span></label>
              <label class="field"><span class="field__l t-14">Email Address*</span><span class="field__w"><input name="email" type="email" autocomplete="email" placeholder="name@company.com" required></span></label>
            </div>
            <div class="form__row">
              <label class="field"><span class="field__l t-14">Company Name</span><span class="field__w"><input name="company" type="text" autocomplete="organization" placeholder="ex. Tan Holdings Sdn Bhd"></span></label>
              <label class="field"><span class="field__l t-14">Phone Number*</span><span class="field__w"><input name="phone" type="tel" autocomplete="tel" placeholder="+60 12 345 6789" required></span></label>
            </div>
            <label class="field field--sel"><span class="sr">Service interested in</span><span class="field__w"><select name="service"><option value="">Service Interested In</option>{opts}</select></span></label>
            <label class="field field--ta"><span class="field__l t-14">Message*</span><span class="field__w"><textarea name="message" placeholder="Tell Joseph a little about your business..." required></textarea></span></label>
            <div class="form__end">
              <label class="tick"><input type="checkbox" name="agree" required><span class="t-14 c-muted">I agree to be contacted about my enquiry</span></label>
              <button class="fbtn" type="submit"><span class="t-ui">Send On WhatsApp</span><span class="fbtn__ic">{ic("arrow-right", "ic-18")}</span></button>
              <p class="form__err t-14" role="alert" hidden></p>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</section>"""


def insights():
    cards = []
    for i, (date, cat, t, p, im, alt, href) in enumerate(POSTS):
        cards.append(f"""<a class="post" href="{E(href)}" target="_blank" rel="noopener"{r(round(0.2 + 0.1 * i, 1))}>
          <div class="post__media"><div class="post__zoom">{img(im, alt, sizes="(max-width: 809px) 350px, 432px")}</div>
            <div class="post__meta"><span class="chip chip--light t-12">{E(date)}</span><span class="chip chip--dark t-12">{E(cat)}</span></div></div>
          <div class="post__c"><h3 class="t-24 c-ink">{E(t)}</h3><p class="t-16 c-muted">{E(p)}</p></div></a>""")
    return f"""
<section class="sec insights" id="insights">
  <div class="wrap">
    <div class="insights__title"><h2 class="t-64h c-ink2">Ideas every business owner should hear.</h2>
      <div class="insights__btn">{btn("More On LinkedIn", LINKEDIN, "dark")}</div></div>
    <div class="posts">{"".join(cards)}</div>
  </div>
</section>"""


def talk():
    return f"""
<section class="talk" id="lets-talk" data-talk>
  <div class="talk__bg">{img("talk", "Joseph Siew smiling as he looks out of an office window", sizes="100vw")}<div class="ov ov--t1"></div><div class="ov ov--t2"></div></div>
  <div class="talk__block"><div class="talk__h" data-talkzoom><p class="t-144 c-white">Let's Talk</p></div>{btn("Book A Chat", WA_HELLO, "light")}</div>
</section>"""


def footer():
    cols = []
    for title, links in FOOTER_COLS:
        items = "".join(
            f'<a class="flink" href="{E(h)}"' + (' target="_blank" rel="noopener"' if h.startswith("http") else "")
            + f'><span class="flink__dot"></span><span class="t-ui c-white">{E(t)}</span></a>'
            for t, h in links)
        cols.append(f'<div class="fcol"><p class="t-18 c-lime">{E(title)}</p><div class="fcol__l">{items}</div></div>')
    socials = "".join(f'<a class="soc" href="{h}" target="_blank" rel="noopener" aria-label="{n}">{ic(i, "ic-20")}</a>'
                      for n, h, i in (("LinkedIn", LINKEDIN, "linkedin"), ("Instagram", INSTAGRAM, "instagram"), ("Facebook", FACEBOOK, "facebook")))
    tick = f'<p class="t-144 c-line-d">{E(BRAND.upper())}&nbsp;</p>'
    return f"""
<footer class="foot">
  <div class="foot__wrap">
    <div class="frame frame--dark foot__frame">
      <div class="foot__top">
        <div class="foot__news">
          <div class="foot__nt"><p class="t-18 c-lime">Get Joseph's notes on continuity and funding</p>
            <form class="news" id="news" novalidate><label class="news__w"><span class="sr">Email address</span><input name="email" type="email" placeholder="Email address" autocomplete="email" required></label>
              <button class="news__b" type="submit" aria-label="Send">{ic("arrow-right", "ic-16")}</button></form>
            <p class="t-14 c-soft">Your details stay with Joseph. Opens WhatsApp to send.</p></div>
          <div class="socs">{socials}</div>
        </div>
        <div class="foot__cols">{"".join(cols)}</div>
      </div>
      <div class="foot__logo"><div class="ticker" data-ticker="90" aria-hidden="true"><div class="ticker__ul">{tick}{tick}</div></div></div>
      <div class="foot__copy"><p class="t-16 c-white">&copy; 2026 {E(BRAND)}. All rights reserved.</p><p class="t-16 c-soft foot__r">{E(LOCATION)}</p></div>
    </div>
  </div>
</footer>"""


# ------------------------------------------------------------------ page

SPRINGS = {
    # name: (duration, bounce) for Framer duration springs
    "s12b1": (1.2, 0.1),   # signature reveal (y20 / y30 / y40), tabs, cards
    "s15b2": (1.5, 0.2),   # counters, chart bars (y30)
    "s12b0": (1.2, 0.0),   # CTA avatars spreading out
    "s07b0": (0.7, 0.0),   # in-view zoom (about image)
    "s06b0": (0.6, 0.0),   # nav hide / show on scroll direction
    "s04b2": (0.4, 0.2),   # buttons, arrow rotate, hovers
    "s04b4": (0.4, 0.4),   # stars pop (unused while testimonials are skipped)
}
PHYS = {
    # name: (stiffness, damping) physics springs
    "p320": (320, 50),     # feature tabs block y120
    "p250": (250, 40),     # contact text / form slide
    "p300": (300, 40),     # FAQ answer
    "p500": (500, 60),     # FAQ list items, footer CTA zoom smoothing
}


def springs_js():
    out = {}
    for k, (d, b) in SPRINGS.items():
        e, dur = springs.duration_spring(d, b)
        out[k] = [e, int(dur * 1000)]
    for k, (st, dm) in PHYS.items():
        e, dur = springs.physics_spring(st, dm, 1, 34)
        out[k] = [e, int(dur * 1000)]
    import json
    return "window.SPRINGS=" + json.dumps(out, separators=(",", ":")) + ";"


MASKS = ["pay", "agreement", "continuity", "keyman", "estate", "strategy", "papers", "check", "check-s"]


def mask_css():
    out = []
    for m in MASKS:
        svg = open(os.path.join(ICON_DIR, "m-" + m + ".svg")).read().strip()
        svg = svg.replace('display="block" role="presentation" ', "")
        svg = re.sub(r'fill="[^"]*var\([^"]*"', 'fill="#000"', svg)
        svg = re.sub(r' id="[^"]*"', "", svg)
        out.append('.mi--%s{--m:url("data:image/svg+xml,%s")}' % (m, urllib.parse.quote(svg, safe=" =:/,.-_'")))
    return "".join(out)


def easing_vars():
    out = []
    for k, (d, b) in SPRINGS.items():
        e, dur = springs.duration_spring(d, b)
        out.append("--e-%s:%s" % (k, e))
    return ":root{" + ";".join(out) + "}"


def page():
    title = f"{NAME} | Business Continuity, Funding and Protection for SME Owners"
    desc = ("Former senior banker Joseph Siew helps Malaysian SME owners fund growth, protect their business with "
            "buy-sell agreements and keyman cover, and plan what happens next.")
    css = open(os.path.join(HERE, "css", "site.css")).read()
    fonts = open(os.path.join(HERE, "css", "fonts.css")).read()
    js = open(os.path.join(HERE, "js", "site.js")).read()
    body = "".join([nav(), '<main id="main">', hero(), approach(), services(), about(), story(), who(), talks(), process(),
                    cta(), contact(), insights(), talk(), "</main>", footer()])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="img/hero.webp">
<link rel="icon" href="img/favicon.svg" type="image/svg+xml">
<link rel="preload" as="font" type="font/woff2" href="fonts/RethinkSans.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="fonts/DMSans.woff2" crossorigin>
<link rel="preload" as="image" href="img/hero.webp" imagesrcset="{srcset("hero")}" imagesizes="100vw" fetchpriority="high">
<style>{minify(fonts + easing_vars() + css + mask_css())}</style>
</head>
<body>
<script>document.documentElement.classList.add("js")</script>
{sprite()}
<a class="skip" href="#main">Skip to content</a>
{body}
<script>{springs_js()}</script>
<script>{js}</script>
</body>
</html>"""


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#001c21"/><text x="32" y="44" text-anchor="middle" font-family="Rethink Sans, Arial, sans-serif" font-size="34" font-weight="500" fill="#cef79e" letter-spacing="-2">JS</text></svg>"""


def main():
    os.makedirs(os.path.join(SITE, "img"), exist_ok=True)
    open(os.path.join(SITE, "img", "favicon.svg"), "w").write(FAVICON)
    out = page()
    open(os.path.join(SITE, "index.html"), "w").write(out)
    print("index.html", len(out) // 1024, "KB")


if __name__ == "__main__":
    main()
