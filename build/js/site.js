/* Joseph Siew landing page: motion and behaviour, 1:1 with the Pactum Framer template (home).
   Timings are the template's own (Framer source + live measurements, see _teardown/TEARDOWN.md):
   - reveals: once, when half in view; y20 / y30 / y40 spring 1.2s bounce .1 (signature), hand-staggered delays
   - hero: image 1.2 -> 1 (1.2s [.44,0,.11,1]) and buttons y20 (1.2s [.12,.23,0,.99], .3s) on load; parallax 0.1
   - nav: hides on scroll down / returns on scroll up (spring .6s), turns light below the hero
   - headings: TextColorTransform, per-character colour over 'start 0.75' -> 'start 0.15'
   - hero card cycles every ~4.1s; feature tabs fill 3s each then switch (desktop)
   - tickers 90px/s, badge column 36px/s; "Let's Talk" scales 2 -> 1 as the section scrolls in
   SPRINGS = { name: [CSS linear() easing, duration ms] } is inlined by build.py. */
(function () {
  "use strict";
  var S = window.SPRINGS || {};
  var doc = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var mqDesk = window.matchMedia("(min-width: 1280px)");
  var mqPhone = window.matchMedia("(max-width: 809.98px)");
  var canAnimate = typeof Element.prototype.animate === "function";
  var hasLinear = !!(window.CSS && CSS.supports && CSS.supports("animation-timing-function", "linear(0, 1)"));
  function sp(name, fallback) {
    var s = S[name];
    if (!s) return { e: fallback || "ease-out", d: 1000 };
    return { e: hasLinear ? s[0] : (fallback || "cubic-bezier(0.22, 1, 0.36, 1)"), d: s[1] };
  }
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var vh = function () { return window.innerHeight; };

  /* ---------- reveals ---------- */
  var KIND = {
    up: ["s12b1"], up10: ["p500"], up24: ["tw06"], up30: ["s12b1"], up40: ["s12b1"], up120: ["p320"],
    "x-50": ["p250"], x50: ["p250"], s12: ["s07b0"]
  };
  var FROM = {
    up: "translateY(20px)", up10: "translateY(10px)", up24: "translateY(24px)", up30: "translateY(30px)",
    up40: "translateY(40px)", up120: "translateY(120px)", "x-50": "translateX(-50px)", x50: "translateX(50px)", s12: "scale(1.2)"
  };
  function showNow(el) { el.classList.add("is-shown"); el.style.opacity = ""; el.style.transform = ""; }
  function reveal(el) {
    if (el.classList.contains("is-shown")) return;
    var kind = el.getAttribute("data-r");
    var d = parseFloat(el.getAttribute("data-d") || "0") * 1000;
    if (!canAnimate || reduce) return showNow(el);
    var spec = kind === "up24" ? { e: "cubic-bezier(.12,.23,.27,1)", d: 600 } :
      (el.closest(".fcard__w") && kind === "up30") ? sp("s15b2") : sp(KIND[kind] ? KIND[kind][0] : "s12b1");
    var from = { transform: FROM[kind] || "none", opacity: kind === "s12" ? 1 : 0 };
    el.classList.add("is-shown");
    el.animate([from, { transform: "none", opacity: 1 }], { duration: spec.d, delay: d, easing: spec.e, fill: "backwards" });
  }
  function onHalfInView(els, fn, ratio) {
    if (!("IntersectionObserver" in window)) { els.forEach(fn); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        // Framer's threshold is a share of the element; very tall elements trigger once they fill the viewport
        var need = Math.min(ratio, (vh() * ratio) / Math.max(1, en.boundingClientRect.height));
        if (en.intersectionRatio + 0.001 >= need) { io.unobserve(en.target); fn(en.target); }
      });
    }, { threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5] });
    els.forEach(function (el) { io.observe(el); });
  }
  var revealEls = $$("[data-r]").filter(function (el) { return !el.hasAttribute("data-mount"); });
  onHalfInView(revealEls, reveal, 0.5);

  /* ---------- hero intro (on load) ---------- */
  var heroZoom = $("[data-mountzoom]");
  var heroBtns = $("[data-hero-btns]");
  function heroIntro() {
    if (heroZoom) {
      if (canAnimate && !reduce) heroZoom.animate([{ transform: "scale(1.2)" }, { transform: "scale(1)" }], { duration: 1200, easing: "cubic-bezier(.44,0,.11,1)", fill: "forwards" });
      else heroZoom.style.transform = "none";
    }
    if (heroBtns) {
      heroBtns.classList.add("is-shown");
      if (canAnimate && !reduce) heroBtns.animate([{ opacity: 0, transform: "translateY(20px)" }, { opacity: 1, transform: "none" }], { duration: 1200, delay: 300, easing: "cubic-bezier(.12,.23,0,.99)", fill: "backwards" });
    }
  }
  heroIntro();

  /* ---------- scroll-linked: hero parallax, nav, coloured headings, about image, let's talk ---------- */
  var nav = $("[data-nav]");
  var hero = $(".hero");
  var heroBg = $("[data-parallax]");
  var lastY = window.pageYOffset;
  var menuOpen = false;
  var ctexts = $$("[data-ctext]").map(function (p) {
    var dark = p.classList.contains("ctext--dark");
    var words = $$(".ctw", p);
    var chars = [];
    words.forEach(function (w, wi) {
      var cs = $$("span", w);
      var a = wi / words.length, b = (wi + 1) / words.length, step = (b - a) / Math.max(1, cs.length);
      cs.forEach(function (c, ci) { chars.push({ el: c, s: a + step * ci, e: a + step * (ci + 1), last: -1 }); });
    });
    return { el: p, chars: chars, from: dark ? [77, 96, 100] : [206, 211, 211], to: dark ? [255, 255, 255] : [11, 36, 39] };
  });
  var aboutPar = $("[data-iparallax]");
  var talk = $("[data-talk]"), talkH = $("[data-talkzoom]"), talkScale = 2, talkTarget = 2;
  function mix(a, b, t) { return "rgb(" + Math.round(a[0] + (b[0] - a[0]) * t) + "," + Math.round(a[1] + (b[1] - a[1]) * t) + "," + Math.round(a[2] + (b[2] - a[2]) * t) + ")"; }
  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function onScroll() {
    var y = window.pageYOffset, h = vh();
    // hero parallax (Framer speed 90 = 0.1 of the scroll)
    if (heroBg && hero && y < hero.offsetHeight + 50) heroBg.style.transform = "translate3d(0," + (y * 0.1).toFixed(1) + "px,0)";
    // nav: hide on scroll down, show on scroll up; light variant below the hero
    if (nav) {
      var dy = y - lastY;
      if (!menuOpen) {
        if (dy > 2 && y > 10) nav.classList.add("is-hidden");
        else if (dy < -2 || y <= 10) nav.classList.remove("is-hidden");
      }
      nav.classList.toggle("is-light", hero ? y > hero.offsetHeight - nav.offsetHeight - 2 : y > 10);
    }
    lastY = y;
    // TextColorTransform: offset ['start 0.75', 'start 0.15']
    ctexts.forEach(function (c) {
      var top = c.el.getBoundingClientRect().top;
      if (top > h * 1.05 || top < -c.el.offsetHeight - h) return;
      var p = clamp((h * 0.75 - top) / (h * 0.6));
      c.chars.forEach(function (ch) {
        var t = clamp((p - ch.s) / (ch.e - ch.s));
        var q = Math.round(t * 100) / 100;
        if (q !== ch.last) { ch.last = q; ch.el.style.color = mix(c.from, c.to, q); }
      });
    });
    // about image: slow parallax inside its frame (image is 105% tall)
    if (aboutPar) {
      var box = aboutPar.parentElement.getBoundingClientRect();
      if (box.bottom > 0 && box.top < h) {
        var pr = clamp((h - box.top) / (h + box.height));
        aboutPar.style.transform = "translate3d(0," + (-pr * box.height * 0.05).toFixed(1) + "px,0)";
      }
    }
    // "Let's Talk": scale 2 -> 1 while the section's top travels from the viewport bottom to its top
    if (talk && talkH) {
      var tt = talk.getBoundingClientRect().top;
      talkTarget = 2 - clamp(1 - tt / h);
      if (reduce) talkTarget = 1;
    }
  }
  var ticking = false;
  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; setTimeout(function () { ticking = false; onScroll(); }, 0); }
  }, { passive: true });
  window.addEventListener("resize", onScroll);
  onScroll();
  // spring-smoothed follow for the Let's Talk zoom (stiffness 500 / damping 60 feel)
  (function talkLoop() {
    if (talkH) {
      talkScale += (talkTarget - talkScale) * 0.22;
      if (Math.abs(talkTarget - talkScale) < 0.0005) talkScale = talkTarget;
      talkH.style.transform = "scale(" + talkScale.toFixed(4) + ")";
    }
    (window.requestAnimationFrame || function (f) { setTimeout(f, 16); })(talkLoop);
  })();

  /* ---------- moving lines ---------- */
  onHalfInView($$(".mline"), function (el) { el.classList.add("is-in"); }, 0.5);

  /* ---------- in-view zooms: CTA photo, avatars spreading out ---------- */
  var inzoom = $("[data-inzoom]");
  if (inzoom) {
    inzoom.style.transform = "scale(1.2)";
    onHalfInView([inzoom], function (el) {
      el.style.transform = "";
      if (canAnimate && !reduce) el.animate([{ transform: "scale(1.2)" }, { transform: "scale(1)" }], { duration: 1200, easing: "cubic-bezier(.44,0,.11,1)" });
    }, 0.25);
  }
  var avs = $("[data-avs]");
  if (avs) {
    var avEls = $$("[data-av]", avs);
    var offs = [0, -24, -48, -73];
    avEls.forEach(function (a, i) { a.style.transform = "translateX(" + offs[i] + "px)"; });
    onHalfInView([avs], function () {
      var s = sp("s12b0");
      avEls.forEach(function (a, i) {
        a.style.transform = "";
        if (canAnimate && !reduce) a.animate([{ transform: "translateX(" + offs[i] + "px)" }, { transform: "none" }], { duration: s.d, delay: 400, easing: s.e, fill: "backwards" });
      });
    }, 0.5);
  }

  /* ---------- tickers ---------- */
  function ticker(track, pxPerSec, vertical) {
    if (!track || reduce) return;
    var pos = 0, last = performance.now(), visible = true;
    var cycle = function () {
      var first = track.children[0], second = track.children[1];
      if (!first || !second) return 1;
      return vertical ? second.offsetTop - first.offsetTop : second.offsetLeft - first.offsetLeft;
    };
    if ("IntersectionObserver" in window) new IntersectionObserver(function (e) { visible = e[0].isIntersecting; }).observe(track);
    (function loop(now) {
      now = now || performance.now();
      var dt = Math.min(64, now - last); last = now;
      if (visible && !document.hidden) {
        var len = cycle();
        pos -= pxPerSec * dt / 1000;
        if (len > 0 && -pos >= len) pos += len;
        track.style.transform = vertical ? "translate3d(0," + pos.toFixed(2) + "px,0)" : "translate3d(" + pos.toFixed(2) + "px,0,0)";
      }
      (window.requestAnimationFrame || function (f) { setTimeout(function () { f(performance.now()); }, 16); })(loop);
    })();
  }
  $$("[data-ticker] .ticker__ul").forEach(function (t) { ticker(t, parseFloat(t.parentElement.getAttribute("data-ticker")) || 90, false); });
  var vt = $("[data-vticker]");
  if (vt) ticker(vt, 36, true);

  /* ---------- hero card cycle (~4.1s) ---------- */
  var cycleBox = $("[data-cycle]");
  if (cycleBox) {
    var slides = $$(".hcard", cycleBox), cur = 0, timer = null, heroVisible = true;
    var go = function (n) {
      cur = (n + slides.length) % slides.length;
      slides.forEach(function (s, i) {
        s.classList.toggle("is-on", i === cur);
        if (i === cur) s.removeAttribute("aria-hidden"); else s.setAttribute("aria-hidden", "true");
      });
      schedule();
    };
    var schedule = function () {
      clearTimeout(timer);
      if (!reduce && heroVisible && !document.hidden) timer = setTimeout(function () { go(cur + 1); }, 4100);
    };
    cycleBox.addEventListener("click", function (e) {
      var b = e.target.closest("[data-go]"); if (b) go(parseInt(b.getAttribute("data-go"), 10));
    });
    document.addEventListener("visibilitychange", schedule);
    if ("IntersectionObserver" in window) new IntersectionObserver(function (e) { heroVisible = e[0].isIntersecting; schedule(); }).observe(cycleBox);
    schedule();
  }

  /* ---------- feature tabs (desktop): 3s progress, then next tab + card crossfade ---------- */
  var feats = $("[data-feats]");
  if (feats) {
    var tabs = $$("[data-tab]", feats), cards = $$("[data-card]", feats), cti = 0, tt = null, inView = false;
    var setTab = function (n, run) {
      cti = n;
      tabs.forEach(function (t, i) { t.classList.toggle("is-on", i === n); t.classList.remove("is-run"); t.setAttribute("aria-selected", i === n ? "true" : "false"); });
      cards.forEach(function (c, i) { c.classList.toggle("is-on", i === n); });
      clearTimeout(tt);
      if (run && mqDesk.matches && !reduce) {
        void tabs[n].offsetWidth;
        tabs[n].classList.add("is-run");
        tt = setTimeout(function () { setTab((cti + 1) % tabs.length, inView); }, 3000 + 830);
      }
    };
    tabs.forEach(function (t, i) { t.addEventListener("click", function () { setTab(i, inView); }); });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (e) {
        var was = inView; inView = e[0].isIntersecting;
        if (inView && !was) setTab(cti, true);
        if (!inView) { clearTimeout(tt); tabs[cti].classList.remove("is-run"); }
      }, { threshold: 0.3 }).observe(feats);
    }
  }

  /* ---------- who list: hover / focus swaps the portrait ---------- */
  var rows = $$("[data-who]"), pics = $$("[data-pic]");
  rows.forEach(function (r, i) {
    var on = function () {
      rows.forEach(function (x, k) { x.classList.toggle("is-on", k === i); });
      pics.forEach(function (p, k) { p.classList.toggle("is-on", k === i); });
    };
    r.addEventListener("mouseenter", on);
    r.addEventListener("focus", on);
  });

  /* ---------- FAQ accordion (items toggle independently, like the template) ---------- */
  $$(".acc__q").forEach(function (q) {
    q.addEventListener("click", function () {
      var item = q.closest(".acc__item"), panel = $(".acc__panel", item);
      var open = !item.classList.contains("is-open");
      var from = panel.getBoundingClientRect().height;
      item.classList.toggle("is-open", open);
      q.setAttribute("aria-expanded", open ? "true" : "false");
      var to = open ? panel.scrollHeight : 0;
      if (canAnimate && !reduce) {
        var s = sp("p300");
        panel.animate([{ height: from + "px" }, { height: to + "px" }], { duration: s.d, easing: s.e });
        if (open) $(".acc__a", item).animate([{ opacity: 0, transform: "translateY(20px)" }, { opacity: 1, transform: "none" }], { duration: s.d, easing: s.e });
      }
    });
  });

  /* ---------- menu: phone overlay / tablet inline variant ---------- */
  var burger = $(".burger"), mmenu = $("#mmenu"), mclose = $(".mmenu__x");
  function setMenu(open) {
    if (mqPhone.matches) {
      menuOpen = open;
      burger.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        mmenu.hidden = false; void mmenu.offsetWidth; mmenu.classList.add("is-on");
        doc.style.overflow = "hidden"; document.body.style.overflow = "hidden";
        nav.classList.remove("is-hidden");
        mclose.focus({ preventScroll: true });
      } else {
        mmenu.classList.remove("is-on");
        doc.style.overflow = ""; document.body.style.overflow = "";
        setTimeout(function () { if (!menuOpen) mmenu.hidden = true; }, 300);
        burger.focus({ preventScroll: true });
      }
    } else if (!mqDesk.matches) {
      // tablet: the template's "Open" variant shows the links inline in the bar
      menuOpen = open;
      nav.classList.toggle("is-open-tab", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    }
  }
  if (burger) burger.addEventListener("click", function () { setMenu(!menuOpen); });
  if (mclose) mclose.addEventListener("click", function () { setMenu(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && menuOpen) setMenu(false); });
  mqDesk.addEventListener && mqDesk.addEventListener("change", function () { if (menuOpen) setMenu(false); nav.classList.remove("is-open-tab"); menuOpen = false; });

  /* ---------- in-page links ---------- */
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute("href").slice(1), el = id ? document.getElementById(id) : document.body;
    if (!el) return;
    e.preventDefault();
    if (menuOpen) setMenu(false);
    var top = id === "top" ? 0 : el.getBoundingClientRect().top + window.pageYOffset;
    window.scrollTo({ top: top, behavior: reduce ? "auto" : "smooth" });
    if (history.replaceState) history.replaceState(null, "", "#" + id);
  });

  /* ---------- enquiry form -> WhatsApp (no backend; user's choice) ---------- */
  var WA = "https://wa.me/60179198959?text=";
  var form = $("#enquiry");
  if (form) {
    var sel = form.querySelector("select");
    if (sel) sel.addEventListener("change", function () { sel.classList.toggle("is-set", !!sel.value); });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var err = $(".form__err", form);
      if (!form.checkValidity()) {
        var bad = form.querySelector(":invalid");
        err.textContent = bad && bad.type === "checkbox" ? "Please tick the box so Joseph can contact you." : "Please fill in the fields marked *.";
        err.hidden = false;
        if (bad) bad.focus();
        return;
      }
      err.hidden = true;
      var f = new FormData(form);
      var lines = ["Hi Joseph, I'd like to request a consultation.", "",
        "Name: " + f.get("name"), "Email: " + f.get("email"), "Phone: " + f.get("phone")];
      if (f.get("company")) lines.push("Company: " + f.get("company"));
      if (f.get("service")) lines.push("Interested in: " + f.get("service"));
      lines.push("", f.get("message"));
      window.open(WA + encodeURIComponent(lines.join("\n")), "_blank", "noopener");
    });
  }
  var news = $("#news");
  if (news) {
    news.addEventListener("submit", function (e) {
      e.preventDefault();
      var inp = news.querySelector("input");
      if (!inp.checkValidity() || !inp.value) { inp.focus(); return; }
      window.open(WA + encodeURIComponent("Hi Joseph, please keep me posted on your sessions and notes. My email: " + inp.value), "_blank", "noopener");
    });
  }
})();
