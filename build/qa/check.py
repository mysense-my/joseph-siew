# QA for the built page: at each width, load, sweep with real wheel events (so reveals fire), then report
# console errors, failed requests, broken images, horizontal overflow, section geometry, and save a
# full-page screenshot.  usage: PORT=9611 python3 check.py URL [widths...]
import sys, os, time, json, base64
sys.path.insert(0, "/Users/mysense/Desktop/Website Works/Joseph Siew LP/Pactum/_teardown/tools"); import cdp
URL = sys.argv[1]; WS = [int(w) for w in sys.argv[2:]] or [1440, 834, 390]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots"); os.makedirs(OUT, exist_ok=True)
REPORT = r"""(()=>{const secs=[...document.querySelectorAll('main > section, footer')].map(s=>{const r=s.getBoundingClientRect();const cs=getComputedStyle(s);return [s.id||s.className.split(' ')[0],Math.round(r.top+scrollY),Math.round(r.height),cs.paddingTop]});
const imgs=[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.getAttribute('src'));
const wide=[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.right>innerWidth+1&&getComputedStyle(e).position!=='fixed'&&!e.closest('.ticker')&&!e.closest('.sprite')&&r.width>0}).slice(0,8).map(e=>(e.className&&e.className.baseVal===undefined?e.className:e.tagName)+' '+Math.round(e.getBoundingClientRect().right));
const hidden=[...document.querySelectorAll('[data-r]')].filter(e=>+getComputedStyle(e).opacity<0.99).map(e=>e.className.split(' ')[0]);
return {docH:document.documentElement.scrollHeight,scrollW:document.documentElement.scrollWidth,secs,broken:imgs,overflow:wide,stillHidden:hidden}})()"""
for W in WS:
    H = 900 if W >= 1280 else (1112 if W >= 810 else 844)
    c = cdp.Attach(int(os.environ.get("PORT", "9611"))); c.ws.s.settimeout(180); c.viewport(W, H, mobile=W < 810)
    c.cmd("Runtime.enable"); c.cmd("Log.enable")
    c.goto(URL + ("&" if "?" in URL else "?") + "cb=%d" % time.time(), 4)
    y = 0; Hd = c.js("document.documentElement.scrollHeight")
    while y < Hd + H:
        c.cmd("Input.dispatchMouseEvent", {"type": "mouseWheel", "x": W // 2, "y": H // 2, "deltaX": 0, "deltaY": int(H * .5)}); time.sleep(.25); y += int(H * .5)
        Hd = c.js("document.documentElement.scrollHeight")
    time.sleep(2.5)
    rep = c.js(REPORT)
    errs, bad = c.drain()
    print("=== %d  docH %s  scrollW %s  broken %s  errors %s  failed %s" % (W, rep["docH"], rep["scrollW"], rep["broken"], errs[:5], bad[:5]))
    print("    overflow:", rep["overflow"])
    print("    still hidden:", rep["stillHidden"])
    for s in rep["secs"]: print("    %-14s y%-6s h%-6s pad %s" % tuple(s))
    c.js("window.scrollTo(0,0)"); time.sleep(.5)
    d = c.cmd("Page.captureScreenshot", {"format": "jpeg", "quality": 70, "captureBeyondViewport": True,
              "clip": {"x": 0, "y": 0, "width": W, "height": min(rep["docH"], 16000), "scale": 1}})
    open(os.path.join(OUT, "page_%d.jpg" % W), "wb").write(base64.b64decode(d["data"]))
    c.close()
