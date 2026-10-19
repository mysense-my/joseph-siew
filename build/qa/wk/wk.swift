// Safari-engine (WebKit) check: loads URL in a WKWebView of WIDTHxHEIGHT, runs an async JS file (top-level await
// allowed, `return` a string), prints the result; optional 5th arg = PNG path for a viewport snapshot after the script.
// The web view sits inside a 1600x1200 borderless window so macOS keeps rAF running (a small window gets 0 frames).
// Width < 810 uses an iPhone user agent.  Usage: ./wk URL WIDTH HEIGHT script.js [shot.png]
// Build: swiftc -O wk.swift -o wk -vfsoverlay overlay.yaml   (overlay works around a CommandLineTools module-map bug)
import Cocoa
import WebKit
let a = CommandLine.arguments
let url = URL(string: a[1])!, W = Double(a[2])!, H = Double(a[3])!
let script = try! String(contentsOfFile: a[4], encoding: .utf8)
let shot: String? = a.count > 5 ? a[5] : nil
final class D: NSObject, WKNavigationDelegate {
  func webView(_ w: WKWebView, didFinish n: WKNavigation!) {
    w.callAsyncJavaScript(script, arguments: [:], in: nil, in: .page) { r in
      switch r {
      case .success(let v): print("\(Int(W)) \(String(describing: v ?? "nil"))")
      case .failure(let e): print("\(Int(W)) ERR \(e)")
      }
      if let p = shot {
        w.takeSnapshot(with: nil) { img, _ in
          if let img = img, let t = img.tiffRepresentation, let b = NSBitmapImageRep(data: t), let png = b.representation(using: .png, properties: [:]) {
            try? png.write(to: URL(fileURLWithPath: p))
          }
          exit(0)
        }
      } else { exit(0) }
    }
  }
}
let app = NSApplication.shared
app.setActivationPolicy(.prohibited)
let cfg = WKWebViewConfiguration()
cfg.userContentController.addUserScript(WKUserScript(source: "window.__errs=[];addEventListener('error',e=>window.__errs.push(String(e.message)));addEventListener('unhandledrejection',e=>window.__errs.push('rej '+String(e.reason)));", injectionTime: .atDocumentStart, forMainFrameOnly: true))
let win = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1600, height: 1200), styleMask: [.borderless], backing: .buffered, defer: false)
let host = NSView(frame: NSRect(x: 0, y: 0, width: 1600, height: 1200))
win.contentView = host
let wv = WKWebView(frame: NSRect(x: 0, y: 1200 - H, width: W, height: H), configuration: cfg)
if W < 810 {
  wv.customUserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
}
host.addSubview(wv)
win.setFrameOrigin(NSPoint(x: 0, y: 0)); win.orderFrontRegardless()
let d = D(); wv.navigationDelegate = d; wv.load(URLRequest(url: url))
DispatchQueue.main.asyncAfter(deadline: .now() + 120) { print("TIMEOUT"); exit(1) }
app.run()
