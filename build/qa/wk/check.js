// WebKit QA for the Joseph Siew page. Runs inside callAsyncJavaScript (top-level await, must return a string).
const wait = ms => new Promise(r => setTimeout(r, ms));
const R = {};
const H = innerHeight, W = innerWidth;
const q = s => document.querySelector(s), qa = s => [...document.querySelectorAll(s)];
await wait(1500);
// rAF health
let frames = 0; const f0 = performance.now();
await new Promise(res => { const tick = () => { frames++; if (performance.now() - f0 < 1000) requestAnimationFrame(tick); else res(); }; requestAnimationFrame(tick); });
R.fps = frames;
R.ua = navigator.userAgent.includes("iPhone") ? "iPhone" : "Mac";
R.linear = CSS.supports("animation-timing-function", "linear(0, 1)");
R.fontsOK = document.fonts.check("400 16px 'DM Sans'") && document.fonts.check("400 64px 'Rethink Sans'");
R.overflowAtLoad = document.documentElement.scrollWidth - W;
// mask icons render (mask-image resolved)
R.maskIcons = qa(".mi").slice(0, 3).map(e => { const cs = getComputedStyle(e); return (cs.webkitMaskImage || cs.maskImage || "").slice(0, 26); });
R.maskSize = (() => { const e = q(".scard__icon .mi"); const r = e.getBoundingClientRect(); return Math.round(r.width) + "x" + Math.round(r.height); })();
// hero card cycle
const idx = () => qa(".hcard").findIndex(e => e.classList.contains("is-on"));
const c0 = idx(); await wait(4400); R.heroCycle = c0 + "->" + idx();
// nav hide on scroll down / light below hero
const navTf = () => getComputedStyle(q(".nav")).transform;
for (let y = 0; y <= 400; y += 40) { scrollTo(0, y); await wait(40); }
await wait(800); R.navAfterDown = navTf();
for (let y = 400; y >= 300; y -= 20) { scrollTo(0, y); await wait(40); }
await wait(800); R.navAfterUp = navTf();
// sweep the page so every reveal fires; record heading colour progress on the way
const ct = q("#approach .ctext"); const ctTop = ct.getBoundingClientRect().top + scrollY;
const share = () => { const cs = [...ct.querySelectorAll(".ctw span")]; return (cs.filter(s => getComputedStyle(s).color === "rgb(11, 36, 39)").length / cs.length).toFixed(2); };
const doc = document.documentElement.scrollHeight;
R.ctext = [];
for (let y = 0; y < doc; y += Math.round(H * 0.25)) {
  scrollTo(0, y); await wait(70);
  const t = (ctTop - y) / H;
  if (Math.abs(t - 0.6) < 0.13 && R.ctext.length < 1) R.ctext.push(["0.6", share()]);
  if (Math.abs(t - 0.3) < 0.13 && R.ctext.length < 2) R.ctext.push(["0.3", share()]);
}
scrollTo(0, doc); await wait(2500);
R.overflowAfterSweep = document.documentElement.scrollWidth - W;
R.stillHidden = qa("[data-r]").filter(e => getComputedStyle(e).display !== "none" && e.offsetParent !== null && +getComputedStyle(e).opacity < 0.99).map(e => e.className.split(" ")[0]);
R.brokenImgs = qa("img").filter(i => i.offsetParent !== null && i.complete && i.naturalWidth === 0).map(i => i.getAttribute("src"));
// sticky: story panels and process steps
const story = q(".story"); const sTop = story.getBoundingClientRect().top + scrollY;
const tops = sel => qa(sel).map(p => Math.round(p.getBoundingClientRect().top)).join(",");
for (const f of [0.5, 1.0, 1.5]) { scrollTo(0, sTop + H * f); await wait(150); R["story+" + f + "vh"] = tops(".story__p"); }
const steps = q(".steps"); const pTop = steps.getBoundingClientRect().top + scrollY;
scrollTo(0, pTop + 900); await wait(150); R.stepTops = tops(".step");
// what's painted on top mid-story (WebKit paints in source order; check the dark panel covers panel 1's image half)
scrollTo(0, sTop + H * 0.6); await wait(200);
const hit = document.elementFromPoint(W * 0.75, H * 0.5); R.storyHitRight = hit ? (hit.closest(".story__p") || {}).className : null;
// tickers move
const tk = q(".process .ticker__ul"); const tkTop = tk.getBoundingClientRect().top + scrollY;
scrollTo(0, tkTop - H / 2); await wait(300);
const m1 = new DOMMatrix(getComputedStyle(tk).transform).m41; await wait(1000); const m2 = new DOMMatrix(getComputedStyle(tk).transform).m41;
R.tickerPxPerS = Math.round(m1 - m2);
// Let's Talk scale
const talk = q(".talk"); const tTop = talk.getBoundingClientRect().top + scrollY;
scrollTo(0, tTop - H * 0.5); await wait(900); R.talkScaleHalf = getComputedStyle(q(".talk__h")).transform;
// FAQ toggle
const qb = qa(".acc__q")[1]; scrollTo(0, qb.getBoundingClientRect().top + scrollY - H / 2); await wait(200);
qb.click(); await wait(1200); R.faqSecondOpen = qb.closest(".acc__item").classList.contains("is-open") + " h" + Math.round(qb.closest(".acc__item").getBoundingClientRect().height);
// phone menu
if (W < 810) {
  scrollTo(0, 0); await wait(400);
  q(".burger").click(); await wait(600);
  const m = q("#mmenu"); R.menu = { hidden: m.hidden, op: getComputedStyle(m).opacity, htmlOverflow: getComputedStyle(document.documentElement).overflow, linkY: Math.round(q(".mlink").getBoundingClientRect().top) };
  q(".mmenu__x").click(); await wait(500); R.menuClosed = q("#mmenu").hidden;
} else if (W < 1280) {
  scrollTo(0, 0); await wait(400); q(".burger").click(); await wait(400);
  R.tabletMenu = getComputedStyle(q(".nav__links")).display;
}
// spring easing actually animating (WAAPI with linear())
const probe = document.createElement("div"); document.body.appendChild(probe);
try { const an = probe.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 300, easing: (window.SPRINGS && SPRINGS.s12b1 && R.linear) ? SPRINGS.s12b1[0] : "ease" }); R.waapiOK = !!an; } catch (e) { R.waapiOK = "ERR " + e.message; }
probe.remove();
R.errors = window.__errs;
scrollTo(0, 0); await wait(300);
return JSON.stringify(R);
