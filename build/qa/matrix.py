import sys, os, time, json
sys.path.insert(0, "/Users/mysense/Desktop/Website Works/Joseph Siew LP/Pactum/_teardown/tools"); import cdp
M = r"""(()=>{const f=s=>{const e=document.querySelector(s);if(!e)return null;const cs=getComputedStyle(e);return cs.fontSize+'/'+cs.lineHeight+'/'+cs.letterSpacing};const r=s=>{const e=document.querySelector(s);if(!e)return null;const b=e.getBoundingClientRect();return Math.round(b.width)+'x'+Math.round(b.height)};
return {nav:r('.nav__bar'),wrap:r('#about .wrap'),secPad:getComputedStyle(document.querySelector('#about')).paddingTop,hero:r('.hero'),h1:f('.t-h1'),h2:f('#approach .ctext'),h3:f('#about h2'),body:f('#about .about__tc p'),lead:f('.split__r .t-20'),btn:r('.hero .btn--light'),card:r('.hcard.is-on'),scard:r('.scard'),tcard:r('.tcard'),post:r('.post'),step:r('.step__in'),foot:r('.foot__frame'),ticker:f('.process .ticker p'),eyebrow:f('.eyebrow p'),tab:r('.tab'),fmedia:r('.fcard__media')}})()"""
T = r"""(()=>{const q=s=>document.querySelector(s);const f=e=>{if(!e)return null;const cs=getComputedStyle(e);return cs.fontSize+'/'+cs.lineHeight+'/'+cs.letterSpacing};const r=e=>{if(!e)return null;const b=e.getBoundingClientRect();return Math.round(b.width)+'x'+Math.round(b.height)};const N=n=>q('[data-framer-name="'+n+'"]');
return {nav:r(q('[data-framer-name^="Navigation"] nav')),wrap:r(q('[data-framer-name="About"] > [data-framer-name="Wrapper"]')),secPad:getComputedStyle(q('main [data-framer-name="About"]')).paddingTop,hero:r(N('Hero Header')),h1:f(q('h1')),h2:f(q('[data-framer-name="Top Features"] [data-framer-name="Title"] p')),h3:f(q('[data-framer-name="About"] h3')),body:f(q('[data-framer-name="About"] [data-framer-name="Text & CTA"] p')),lead:f(q('[data-framer-name="Top Features"] [data-framer-name="Text"] [data-framer-name="Text"] p')),btn:r(q('[data-framer-name="Hero Header"] a[data-framer-name*="Fill"]')),card:r(q('[data-framer-name="Hero Header"] [data-framer-name="Features"] [data-framer-name="Content"]')),scard:r(q('[data-framer-name="Service Card"]')),tcard:r(q('[data-framer-name="Desktop - Dark"],[data-framer-name="Mobile - Dark"]')),post:r(q('[data-framer-name="Posts"] a')),step:r(q('[data-framer-name="Process"] [data-framer-name="Process"] > div > div')),foot:r(N('Footer Content')),ticker:f(q('[data-framer-name="Ticker"] p')),eyebrow:f(q('[data-framer-name="Dark"] p')),tab:r(q('[data-framer-name="Desktop - Active"]')),fmedia:r(q('[data-framer-name="Image & Charts"] [data-framer-name="Content"]'))}})()"""
for W in (1440, 834, 390):
    H = 900 if W >= 1280 else (1112 if W >= 810 else 844)
    out = {}
    for name, url, expr in (("tpl", "https://pactum-tambe.framer.website/", T), ("mine", "http://127.0.0.1:8791/", M)):
        c = cdp.Attach(9611); c.viewport(W, H, mobile=W < 810); c.goto(url, 5 if name == "tpl" else 3)
        out[name] = c.js(expr); c.close()
    print("=====", W)
    for k in out["mine"]:
        a, b = out["tpl"].get(k), out["mine"].get(k)
        print("  %-8s %-26s %-26s %s" % (k, a, b, "" if a == b else "<-- diff"))
