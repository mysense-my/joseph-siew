"""Exports every image the page uses to site/img/*.webp at about 2x its largest slot.

Big photo slots are the template's scenes with Joseph generated in (img-src/magnific/out, picks = _a);
everything about Joseph uses his public LinkedIn photos (../../assets/linkedin). Run: python3 assets.py
"""
import os
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "img-src", "template")
LI = os.path.join(os.path.dirname(os.path.dirname(HERE)), "assets", "linkedin")
OUT = os.path.join(os.path.dirname(HERE), "site", "img")


def li(name):
    for sub in ("1-joseph-photos", "2-his-posters-and-graphics"):
        p = os.path.join(LI, sub, name + ".jpg")
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


MAG = os.path.join(HERE, "img-src", "magnific", "out")


def mag(slot, pick="a"):
    """Joseph generated into the template scene with Magnific (Seedream 5 Pro, 19 Oct 2026)."""
    return os.path.join(MAG, "%s_%s.png" % (slot, pick))


def tpl(name):
    for f in os.listdir(TPL):
        if f.startswith(name):
            return os.path.join(TPL, f)
    raise FileNotFoundError(name)


# out name: (source, max width, crop box as fractions (l,t,r,b) or None, quality)
JOBS = {
    # Joseph in the template's scenes (Magnific); card-3, story-1 and contact stay template stock (no people)
    "hero": (mag("hero"), 2000, None, 78),
    "card-1": (mag("card-1"), 520, None, 80),
    "card-2": (mag("card-2"), 520, None, 80),
    "card-3": (tpl("eFj7l1sz77soh4nG7CiNCFRkDFI"), 520, None, 80),
    "feat-1": (mag("feat-1"), 1800, None, 78),
    "feat-2": (mag("feat-2"), 1800, None, 78),
    "feat-3": (mag("feat-3"), 1800, None, 78),
    "feat-2m": (mag("feat-2m"), 1540, None, 78),
    "feat-3m": (mag("feat-3m"), 1540, None, 78),
    "story-1": (tpl("973w4l4jziIiyIXFLjzJZWU8So"), 1000, None, 66),
    "story-3": (mag("story-3"), 1000, None, 78),
    "step-1": (mag("step-1"), 1220, None, 78),
    "step-2": (mag("step-2"), 1220, None, 78),
    "step-3": (mag("step-3"), 1220, None, 78),
    "step-4": (mag("step-4"), 1220, None, 78),
    "cta": (mag("cta"), 2000, None, 76),
    "contact": (tpl("jMOagMOfRNxQLQlCOQOAYFYjY"), 2000, None, 76),
    "talk": (mag("talk"), 2000, None, 76),
    # Joseph (LinkedIn, public posts)
    "about": (li("post-7488014818461892608-01"), 800, None, 82),
    "who-1": (li("post-7410952198022475777-02"), 960, (0, 0.13, 1, 1, "free"), 82),
    "who-2": (li("post-7400674589778817024-08"), 750, None, 82),
    "who-3": (li("post-7507678595025268736-01"), 960, None, 82),
    "who-4": (li("post-7386931262290116608-01"), 960, None, 82),
    "who-5": (li("post-7508005346951553024-02"), 960, None, 82),
    "who-6": (li("post-7400674589778817024-05"), 750, None, 82),
    "who-7": (li("post-7386931262290116608-04"), 960, None, 82),
    "talk-1": (li("post-7386931262290116608-02"), 800, None, 82),
    "talk-2": (li("post-7400674589778817024-09"), 1000, None, 82),
    "talk-3": (li("post-7508005346951553024-06"), 1080, None, 82),
    "post-1": (li("post-7341731025032548352-01"), 1080, None, 82),
    "post-2": (li("post-7491006866550861825-01"), 810, None, 82),
    "post-3": (li("post-7489858504917209088-01"), 800, None, 82),
    # avatar strip: Joseph at four different events, square face crops
    "av-1": (li("profile-photo-400_400"), 96, (0.22, 0.08, 0.78, 0.64), 82),
    "av-2": (li("post-7410952198022475777-02"), 96, (0.24, 0.20, 0.66, 0.48), 82),
    "av-3": (li("post-7488014818461892608-01"), 96, (0.555, 0.08, 0.755, 0.38), 82),
    "av-4": (li("post-7400674589778817024-08"), 96, (0.42, 0.395, 0.56, 0.50), 82),
}


VARIANTS = (640, 1080)  # extra widths for srcset (only when the master is wider)


def main():
    import json
    os.makedirs(OUT, exist_ok=True)
    widths = {}
    for name, (src, maxw, crop, q) in JOBS.items():
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        if crop:
            w, h = im.size
            l, t, r, b = crop[:4]
            im = im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))
            if len(crop) < 5:  # avatar crops are square
                side = min(im.size)
                im = im.crop((0, 0, side, side))
        if im.width > maxw:
            im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        p = os.path.join(OUT, name + ".webp")
        im.save(p, "WEBP", quality=q, method=6)
        widths[name] = [im.width]
        for vw in VARIANTS:
            if im.width > vw * 1.15 and not name.startswith("av-"):
                v = im.resize((vw, round(im.height * vw / im.width)), Image.LANCZOS)
                v.save(os.path.join(OUT, "%s-%d.webp" % (name, vw)), "WEBP", quality=q, method=6)
                widths[name].append(vw)
        print("%-9s %4dx%-4d %5.0f KB  variants %s" % (name, im.width, im.height, os.path.getsize(p) / 1024, widths[name][1:]))
    json.dump(widths, open(os.path.join(HERE, "img-widths.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
