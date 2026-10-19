# Behaviour checks on the built page, mirroring the measurements taken on the template.
# usage: PORT=9611 python3 motion.py URL WIDTH
import sys, os, time, json
sys.path.insert(0, "/Users/mysense/Desktop/Website Works/Joseph Siew LP/Pactum/_teardown/tools"); import cdp
URL, W = sys.argv[1], int(sys.argv[2]); H = 900 if W >= 1280 else (1112 if W >= 810 else 844)
c = cdp.Attach(int(os.environ.get("PORT", "9611"))); c.ws.s.settimeout(120); c.viewport(W, H, mobile=W < 810)
# hero intro timeline from navigation start
c.cmd("Page.addScriptToEvaluateOnNewDocument", {"source": r"""window.__tl=[];(function(){const t0=performance.now();function s(){const z=document.querySelector('.hero__zoom'),b=document.querySelector('[data-hero-btns]');if(z&&b){__tl.push([Math.round(performance.now()-t0),getComputedStyle(z).transform,(+getComputedStyle(b).opacity).toFixed(3),getComputedStyle(b).transform])}if(performance.now()-t0<1800)setTimeout(s,100)}setTimeout(s,0)})();"""})
c.goto(URL + "?cb=%d" % time.time(), 3)
js = c.js
def wheel(dy, n=1, pause=0.05):
    for _ in range(n):
        c.cmd("Input.dispatchMouseEvent", {"type": "mouseWheel", "x": W // 2, "y": H // 2, "deltaX": 0, "deltaY": dy}); time.sleep(pause)
def wheel_to(y):
    for _ in range(600):
        d = y - js("scrollY")
        if abs(d) < 30: break
        wheel(max(-250, min(250, d)), 1, 0.03)
    time.sleep(0.5)
R = {}
R["hero_intro"] = [r for i, r in enumerate(json.loads(js("JSON.stringify(__tl)"))) if i % 3 == 0]
navs = "(()=>{const n=document.querySelector('.nav');return scrollY+' '+getComputedStyle(n).transform+' light='+n.classList.contains('is-light')})()"
R["nav_top"] = js(navs)
wheel(100, 3); time.sleep(1); R["nav_down300"] = js(navs); R["parallax_300"] = js("getComputedStyle(document.querySelector('.hero__bg')).transform")
wheel(-100, 1); time.sleep(1); R["nav_up"] = js(navs)
seq = []
wheel_to(0)
for k in range(12):
    wheel(100, 1); time.sleep(0.35); seq.append(js("scrollY+':'+document.querySelector('.nav').classList.contains('is-light')"))
R["nav_light_switch"] = seq
# hero card cycle
wheel_to(0); t0 = time.time(); cyc = []
for k in range(14):
    cyc.append("%.1f:%s" % (time.time() - t0, js("[...document.querySelectorAll('.hcard')].findIndex(e=>e.classList.contains('is-on'))")))
    time.sleep(0.7)
R["hero_cycle"] = " ".join(cyc)
if W >= 1280:
    top = js("Math.round(document.querySelector('.feats').getBoundingClientRect().top+scrollY)")
    wheel_to(top - 300); t0 = time.time(); tabs = []
    for k in range(18):
        tabs.append("%.1f:%s/%s" % (time.time() - t0, js("[...document.querySelectorAll('.tab')].findIndex(e=>e.classList.contains('is-on'))"),
                                    js("Math.round(document.querySelector('.tab.is-on .tab__bar span').getBoundingClientRect().width)")))
        time.sleep(0.5)
    R["tabs"] = " ".join(tabs)
    R["vticker_2s"] = []
    for k in range(2):
        R["vticker_2s"].append(js("getComputedStyle(document.querySelector('[data-vticker]')).transform")); time.sleep(2)
# heading colour progress: Top Features heading, share of characters fully dark at several positions
hp = "(()=>{const p=document.querySelector('#approach .ctext');const r=p.getBoundingClientRect();const cs=[...p.querySelectorAll('.ctw span')];const dark=cs.filter(s=>getComputedStyle(s).color==='rgb(11, 36, 39)').length;return [Math.round(r.top/innerHeight*100)/100,(dark/cs.length).toFixed(2)]})()"
top = js("Math.round(document.querySelector('#approach .ctext').getBoundingClientRect().top+scrollY)")
cp = []
for f in (0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1):
    wheel_to(top - int(H * f)); cp.append(js(hp))
R["ctext_progress[top/vh, darkShare]"] = cp
# ticker speed
top = js("Math.round(document.querySelector('.process .ticker').getBoundingClientRect().top+scrollY)")
wheel_to(top - 300); a = js("new DOMMatrix(getComputedStyle(document.querySelector('.process .ticker__ul')).transform).m41"); time.sleep(2)
b = js("new DOMMatrix(getComputedStyle(document.querySelector('.process .ticker__ul')).transform).m41"); R["ticker_px_per_s"] = round((a - b) / 2, 1)
# FAQ: click third question
top = js("Math.round(document.querySelector('.acc').getBoundingClientRect().top+scrollY)")
wheel_to(top - 200)
q = js("(()=>{const r=document.querySelectorAll('.acc__q')[2].getBoundingClientRect();return [Math.round(r.x+40),Math.round(r.y+r.height/2)]})()")
for t in ("mouseMoved", "mousePressed", "mouseReleased"):
    c.cmd("Input.dispatchMouseEvent", {"type": t, "x": q[0], "y": q[1], "button": "left", "clickCount": 1})
time.sleep(1.2)
R["faq_after_click3"] = js("[...document.querySelectorAll('.acc__item')].map(e=>(e.classList.contains('is-open')?'Open':'Close')+':'+Math.round(e.getBoundingClientRect().height)).join(' ')")
# Let's Talk scale
top = js("Math.round(document.querySelector('.talk').getBoundingClientRect().top+scrollY)")
ts = []
for off in (-800, -500, -200, 0):
    wheel_to(top + off); time.sleep(0.6); ts.append([js("Math.round(document.querySelector('.talk').getBoundingClientRect().top)"), js("getComputedStyle(document.querySelector('.talk__h')).transform")])
R["talk_scale[top, tf]"] = ts
# menu
if W < 1280:
    wheel_to(0); time.sleep(0.6)
    b = js("(()=>{const r=document.querySelector('.burger').getBoundingClientRect();return [Math.round(r.x+r.width/2),Math.round(r.y+r.height/2)]})()")
    for t in ("mouseMoved", "mousePressed", "mouseReleased"):
        c.cmd("Input.dispatchMouseEvent", {"type": t, "x": b[0], "y": b[1], "button": "left", "clickCount": 1})
    time.sleep(0.6)
    R["menu_open"] = js("(()=>{const m=document.querySelector('#mmenu');const n=document.querySelector('.nav');return {menuHidden:m.hidden,menuOp:getComputedStyle(m).opacity,tabOpen:n.classList.contains('is-open-tab'),linksVisible:getComputedStyle(document.querySelector('.nav__links')).display,overflow:getComputedStyle(document.documentElement).overflow}})()")
    import base64
    d = c.cmd("Page.captureScreenshot", {"format": "jpeg", "quality": 70}); open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots", "menu_%d.jpg" % W), "wb").write(base64.b64decode(d["data"]))
errs, bad = c.drain()
R["console"] = errs
print(json.dumps(R, indent=1))
c.close()
