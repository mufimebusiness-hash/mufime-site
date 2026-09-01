#!/usr/bin/env python3
"""
Mufime — page generator.
Rebuilds every secondary page on the shared identity so nav, footer,
head metadata and markup stay identical across the site.

Run from the site root:  python3 build.py
"""
import os, html

SITE = "https://mufime.com"
EMAIL = "mufime.business@gmail.com"

# ----------------------------------------------------------------- partials

def head(title, desc, path, extra=""):
    url = f"{SITE}/{path}".rstrip("/")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{title}</title>
<meta name="description" content="{desc}">

<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" href="/images/favicon.png">

<meta property="og:type" content="website">
<meta property="og:site_name" content="Mufime">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/images/og-cover.jpg">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/images/og-cover.jpg">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://img.youtube.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Hanken+Grotesk:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="/css/site.css">
<script defer data-domain="mufime.com" src="https://plausible.io/js/script.js"></script>
{extra}</head>
<body>
"""

NAV = f"""
<div class="nav-trigger-row">
  <button class="logo-btn" id="logoBtn" aria-expanded="false" aria-controls="navPanel" aria-label="Open menu">
    <img src="/images/logo.png" alt="">
    <span class="logo-word">Mufime</span>
    <span class="logo-bars" aria-hidden="true"><i></i><i></i><i></i></span>
  </button>
  <div class="nav-quick">
    <a class="btn btn-line btn-sm" href="/#contact">Start a project</a>
  </div>
</div>

<div class="nav-scrim" id="navScrim"></div>

<nav class="nav-panel" id="navPanel" aria-label="Main">
  <span class="tag">Menu</span>
  <div class="nav-links">
    <a href="/#home"><span>01</span> Home</a>
    <a href="/services.html"><span>02</span> Services</a>
    <a href="/#process"><span>03</span> Process</a>
    <a href="/#contact"><span>04</span> Contact</a>
  </div>
  <div class="nav-foot">
    <p>Tell us what you're building and we'll tell you what it takes.</p>
    <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a>
  </div>
</nav>
"""

FOOTER = f"""
<footer class="site">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        <img src="/images/logo.png" alt="Mufime" loading="lazy" width="62" height="62">
        <p>A post-production partner for creators and brands, not just an editor.</p>
      </div>
      <div class="foot-col">
        <h4>Navigate</h4>
        <a href="/#home">Home</a>
        <a href="/services.html">Services</a>
        <a href="/#process">Process</a>
        <a href="/#contact">Contact</a>
      </div>
      <div class="foot-col">
        <h4>Get in Touch</h4>
        <a href="https://www.instagram.com/mufi.me/" target="_blank" rel="noopener">Instagram</a>
        <a href="https://www.youtube.com/@mufime7411" target="_blank" rel="noopener">YouTube</a>
        <a href="https://www.upwork.com/agencies/1952708819031826853/" target="_blank" rel="noopener">Upwork</a>
        <a href="mailto:{EMAIL}">Email</a>
      </div>
    </div>

    <div class="editor-band">
      <div>
        <h4>Are You an Editor?</h4>
        <p>We're always looking for senior editors, motion designers and animators who want steady, well-paid client work.</p>
      </div>
      <a class="btn btn-key" href="/join-team.html" data-track="Join the Team Clicked">Join the Team</a>
    </div>

    <div class="foot-base">
      <span>&copy; <span id="year"></span> Mufime</span>
      <span>{EMAIL}</span>
    </div>
  </div>
</footer>

<a class="dock" id="dock" href="/#contact" data-track="Dock Contact Clicked">
  <svg viewBox="0 0 24 24"><path d="M4 5h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z"/><path d="M3 8l9 6 9-6"/></svg>
  Start a project
</a>

<script src="/js/site.js" defer></script>
</body>
</html>
"""

CTA_SEC = """
<section class="sec contact-sec">
  <div class="wrap wrap-narrow" style="text-align:center;">
    <span class="tag rv">Next Step</span>
    <h2 class="rv d1" style="margin:14px 0 16px;">%s</h2>
    <p class="lede rv d2" style="margin:0 auto 30px;">%s</p>
    <div class="btn-row center rv d3">
      <a class="btn btn-key" href="/#sample" data-track="Free Sample CTA Clicked">Get a Free Sample Edit</a>
      <a class="btn btn-line" href="/#quote" data-track="Get a Quote Clicked">Get a Quote</a>
    </div>
    <p class="alt-contact rv">Larger project? Email us at <a href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=%s" target="_blank" rel="noopener">%s</a></p>
  </div>
</section>
""" % ("%s", "%s", EMAIL, EMAIL)


PLAY_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
             '<path d="M8 5v14l11-7z"/></svg>')


def slot(prefix, n, cat, wide=True, video=None):
    """One portfolio card.

    Without `video` it renders the designed placeholder. With one it renders
    the real project: poster, play badge, title and client. `video` is a dict
    holding either "drive" (Google Drive file ID) or "yt" (YouTube ID), plus
    an optional "title" and "client".
    """
    ratio = "slot-16x9" if wide else "slot-9x16"
    d = f" d{n-1}" if 1 < n <= 5 else ""

    if not video:
        return f"""        <a class="slot {ratio} rv{d}" href="/services.html" data-video-id="REPLACE_WITH_{prefix}_{n:02d}">
          <div class="slot-centre"><svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M10 9l5 3-5 3z"/></svg><span>Slot {n:02d}</span></div>
          <div class="slot-body">
            <div class="slot-info"><h4>Project Title</h4><p>Client · Category</p></div>
          </div>
        </a>"""

    title = html.escape(video.get("title") or "Project")
    client = html.escape(video.get("client") or cat)

    if video.get("drive"):
        vid = video["drive"]
        attr = f'data-drive-id="{vid}"'
        href = f"https://drive.google.com/file/d/{vid}/view"
        poster = f"https://drive.google.com/thumbnail?id={vid}&amp;sz=w800"
    else:
        vid = video["yt"]
        attr = f'data-video-id="{vid}"'
        href = f"https://www.youtube.com/watch?v={vid}"
        poster = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"

    return f"""        <a class="slot {ratio} filled rv{d}" href="{href}" target="_blank" rel="noopener"
           {attr} data-title="{title}" data-track="Portfolio Project Opened">
          <img src="{poster}" alt="{title}" loading="lazy">
          <span class="slot-play">{PLAY_ICON}</span>
          <div class="slot-body">
            <div class="slot-info"><h4>{title}</h4><p>{client}</p></div>
          </div>
        </a>"""


# ----------------------------------------------------------------- data

SERVICES = [
    ("story-driven-youtube",     "Long-Form YouTube",        "Narrative structure, pacing and retention editing for videos that hold attention for minutes, not seconds.", "Long-Form"),
    ("youtube-shorts-ig-reels",  "Short-Form",               "Hooks, captions and rhythm engineered for the first second, built for Shorts, Reels and TikTok.", "Short-Form"),
    ("performance-ads",          "Performance Content",      "Ad creative built to be tested and iterated: variants, hooks and cutdowns that answer to real numbers.", "Performance"),
    ("saas-product-demos",       "SaaS &amp; B2B",           "Product demos, launch films and explainers that make complex software look clear and enterprise-ready.", "SaaS &amp; B2B"),
    ("motion-graphics",          "Motion Graphics",          "Titles, lower-thirds, kinetic type and animated callouts that make a deliverable feel finished.", "Motion"),
    ("2d-animation",             "2D Animation",             "Explainers, character work and illustrated sequences built frame by frame.", "2D"),
    ("3d-animation",             "3D Animation",             "Product renders and dimensional sequences with real depth, lighting and camera movement.", "3D"),
    ("documentary-editing",      "Documentary Editing",      "Long-form storytelling with the pacing, sound design and structure that keeps people watching.", "Documentary"),
    ("tech-explainers",          "Tech Explainers",          "Complex ideas and products broken down into clean, easy-to-follow videos.", "Explainer"),
    ("educational-content",      "Educational Content",      "Concepts taught clearly on screen: structured, paced and visualised so ideas actually land.", "Educational"),
    ("true-crime-storytelling",  "Investigative Storytelling", "Tension-building edits, pacing and sound design that keep viewers on edge.", "Investigative"),
    ("sales-videos-vsl",         "Sales Videos (VSLs)",      "Persuasion-first edits built to turn viewers into customers.", "VSL"),
    ("brand-ad-films",           "Brand &amp; Ad Films",     "Concept-to-cut brand films and paid ad creative built to drive action.", "Brand"),
    ("podcast-talking-head",     "Talking Head Video Editing", "Full episode edits and scroll-stopping clips cut from raw interview footage.", "Talking Head"),
]

PROCESS = [
    ("pre-production", "Pre-Production", "01",
     "Planning, creative direction, references and preparation, all agreed before a single cut is made.",
     [("Brief and objectives", "We start with what the video is for, who it's for, and what it has to achieve. Nothing gets cut until that's settled."),
      ("References and direction", "You send what you like the feel of. We translate that into a treatment the editor can actually work to."),
      ("Footage review", "We go through the material before starting, so problems surface early rather than at first-cut stage."),
      ("Structure and outline", "Longer pieces get a paper edit first: the shape of the story before the shape of the timeline.")]),
    ("post-production", "Post-Production", "02",
     "Editing, motion graphics, sound design, VFX, animation and finishing, with quality control before anything ships.",
     [("First cut", "A named editor builds the edit against the agreed brief and structure."),
      ("Motion, sound and effects", "Graphics, sound design, VFX and animation are layered in according to the production level."),
      ("Quality control", "A Senior Editor reviews the finished edit for pacing, audio, captions and export quality, then checks it again across two rounds of review before it reaches you."),
      ("Revision and delivery", "One consolidated round of feedback, then final files in the formats you need.")]),
    ("content-strategy", "Content Strategy", "03",
     "Planning content around your audience, objectives and distribution, so each video serves something bigger.",
     [("Audience and positioning", "Who the content is for and what it should make them think, feel or do."),
      ("Format and cadence", "What to make, how often, and at what length to suit the platform you're publishing to."),
      ("Hooks and retention", "Where attention gets lost and what to change structurally to hold it."),
      ("Measurement", "What to watch after publishing, so the next round of content is better informed.")]),
]


# ----------------------------------------------------------------- real videos
#
# Real project videos, keyed by service-page slug. Each list fills that page's
# slots in order; any slot without an entry keeps its designed placeholder.
# Give each entry EITHER "drive" (Google Drive file ID, shared as
# "Anyone with the link - Viewer") OR "yt" (YouTube video ID).

VIDEOS = {
    "podcast-talking-head": [
        {"drive": "1gAJJFt9pkL_HinPCj1TbX1nnX4YTwfdc",
         "title": "Talking Head Video Edit",
         "client": "Talking Head Video Editing"},
        {"yt": "rwvzM3mHqxw",
         "title": "Talking Head Video Edit",
         "client": "Talking Head Video Editing"},
        {"drive": "1fUTQYKTPxOvpZpvcVzTLgQRqi6CMNX7f",
         "title": "Talking Head Video Edit",
         "client": "Talking Head Video Editing"},
    ],
    "performance-ads": [
        {"drive": "1UuNggPY_suRlgu6iUXueW2_9SqfmMPn0",
         "title": "Performance Content Edit",
         "client": "Performance Content"},
        {"drive": "1-NQAwQ8AImoFQVq5jRWI5bvwH-avuIm9",
         "title": "Performance Content Edit",
         "client": "Performance Content"},
        {"drive": "1P3bVg1ZEvkGADVNJ2APRity1J6w6I7K7",
         "title": "Performance Content Edit",
         "client": "Performance Content"},
        {"drive": "1z8jBGaXCHeBs3LZQoOslvWCIFPz8ooPl",
         "title": "Performance Content Edit",
         "client": "Performance Content"},
        {"drive": "1qOiRvCd3tIyGP61_R2jXd-NqTpV-1xht",
         "title": "Performance Content Edit",
         "client": "Performance Content"},
    ],
    "2d-animation": [
        {"yt": "2awAZH6GCDs",
         "title": "2D Animation Edit",
         "client": "2D Animation"},
        {"yt": "Is8e7irQrWQ",
         "title": "2D Animation Edit",
         "client": "2D Animation"},
        {"yt": "NqPAdL4f188",
         "title": "2D Animation Edit",
         "client": "2D Animation"},
        {"yt": "-Zza4aA9z90",
         "title": "2D Animation Edit",
         "client": "2D Animation"},
        {"yt": "4SainMQhd-U",
         "title": "2D Animation Edit",
         "client": "2D Animation"},
        {"drive": "1BDkPCrLimCi-x7KQJeWhSYJAdZjotzoM",
         "title": "2D Animation Edit",
         "client": "2D Animation"},
    ],
    "3d-animation": [
        {"drive": "16CYtBOD_Rb9NmcA2YuFnv8LbmEL0eml9",
         "title": "3D Animation Edit",
         "client": "3D Animation"},
    ],
    "motion-graphics": [
        {"drive": "1TlDMxllf3Z6Pv-cFLuIoFTz4WIj-S8X2",
         "title": "Motion Graphics Edit",
         "client": "Motion Graphics"},
        {"drive": "1VUhWv8eCPZss5wu4LT2ouv8LiDCJlpit",
         "title": "Motion Graphics Edit",
         "client": "Motion Graphics"},
    ],
    "tech-explainers": [
        {"drive": "1Ep7Cbn2IKb1lg_SE260U-ZR23ZqNFbb7",
         "title": "Tech Explainer Edit",
         "client": "Tech Explainers"},
        {"drive": "1fUTQYKTPxOvpZpvcVzTLgQRqi6CMNX7f",
         "title": "Tech Explainer Edit",
         "client": "Tech Explainers"},
        {"drive": "1SuNnYaxPXnVGDI8SER4UeA6g6hYmIMD6",
         "title": "Tech Explainer Edit",
         "client": "Tech Explainers"},
    ],
    "educational-content": [
        {"yt": "OVsp_p7oRCI",
         "title": "Educational Explainer Edit",
         "client": "Educational Content"},
        {"yt": "kJVuZxYElec",
         "title": "Educational Explainer Edit",
         "client": "Educational Content"},
        {"yt": "EmQtPZLEtqE",
         "title": "Educational Explainer Edit",
         "client": "Educational Content"},
    ],
    "saas-product-demos": [
        {"drive": "1Ep7Cbn2IKb1lg_SE260U-ZR23ZqNFbb7",
         "title": "SaaS Product Demo Edit",
         "client": "SaaS & B2B"},
        {"drive": "1SuNnYaxPXnVGDI8SER4UeA6g6hYmIMD6",
         "title": "SaaS Product Demo Edit",
         "client": "SaaS & B2B"},
    ],
    "brand-ad-films": [
        {"drive": "1DN5G5oWo5I08mSVYWBtFEaGQ0SIYJdi9",
         "title": "Brand & Ad Film Edit",
         "client": "Brand & Ad Films"},
    ],
    "true-crime-storytelling": [
        {"drive": "16CYtBOD_Rb9NmcA2YuFnv8LbmEL0eml9",
         "title": "Investigative Storytelling Edit",
         "client": "Investigative Storytelling"},
        {"drive": "1KXtwZUP-IzLULcWECPM3Ca9y3D2a9QXy",
         "title": "Investigative Storytelling Edit",
         "client": "Investigative Storytelling"},
        {"drive": "1hh10_qzSeyBY0MdPPuMm0l0XM_fEnPK5",
         "title": "Investigative Storytelling Edit",
         "client": "Investigative Storytelling"},
    ],
    "sales-videos-vsl": [
        {"drive": "1x-_LMfA7QUh3dbspbyJFC7qyv7JQq4U5",
         "title": "Sales Video Edit",
         "client": "Sales Videos (VSLs)"},
        {"drive": "1gAJJFt9pkL_HinPCj1TbX1nnX4YTwfdc",
         "title": "Sales Video Edit",
         "client": "Sales Videos (VSLs)"},
        {"drive": "1qeKZgxrcdVOYI-4_hxflIMWsHrZfpMDB",
         "title": "Sales Video Edit",
         "client": "Sales Videos (VSLs)"},
    ],
    "youtube-shorts-ig-reels": [
        {"drive": "1nP97KM51Sk-eMnJaWbaTMu5g93pKyPcV",
         "title": "Short-Form Edit",
         "client": "Client"},
        {"drive": "1BAM5FxBfOUUH94zh_pQcwtvlZfySDqqV",
         "title": "Short-Form Edit",
         "client": "Client"},
        {"drive": "1c4KozPrXRPJ49eqaJHszxk4cLbil_wke",
         "title": "Short-Form Edit",
         "client": "Client"},
        {"drive": "16stcOSWzcXR8S-QplvToBRi5PL2Hkp-1",
         "title": "Lifestyle Reel Edit",
         "client": "Client"},
    ],
    "story-driven-youtube": [
        {"yt": "-Zza4aA9z90",
         "title": "How A Tea Cup Changed China's History",
         "client": "Junaid Akram Shorts"},
        {"yt": "w5oh1RCGUn4",
         "title": "Video Essay Edit",
         "client": "Paths Of Meaning"},
        {"yt": "XADZH4mpYmo",
         "title": "Business Documentary Edit",
         "client": "eTechvolution"},
        {"yt": "rwvzM3mHqxw",
         "title": "Tesla Safety Deep-Dive Edit",
         "client": "eTechvolution"},
        {"drive": "1DyXAnESiMpyn1Zfp-gJPzqLeyqkbxEi5",
         "title": "Project Edit",
         "client": "Client"},
        {"drive": "1mjDj9_Oomn1fljaLeWe0XazkpzMyql-V",
         "title": "Project Edit",
         "client": "Client"},
        {"yt": "xHgxB6Rpr6E",
         "title": "Retool vs Bubble Comparison Edit",
         "client": "Volo Humnytskyi"},
    ],
    "documentary-editing": [
        {"drive": "1anLTcuq8XAfr8viLLxP3bOYDmYHDwYeP",
         "title": "Documentary Edit",
         "client": "Documentary"},
        {"yt": "XADZH4mpYmo",
         "title": "Business Documentary Edit",
         "client": "eTechvolution"},
        {"yt": "zXWOWnfimZY",
         "title": "Documentary Series Edit",
         "client": "BE AMAZED · 13.5M Subscribers"},
        {"yt": "w5oh1RCGUn4",
         "title": "Video Essay Edit",
         "client": "Paths Of Meaning"},
        {"drive": "1mOGQEgJKxC3fmEqH45nh5ItFzUGPXiUC",
         "title": "Long-Form Documentary Edit",
         "client": "Eternal Passenger · 782K Subscribers"},
        {"drive": "16CYtBOD_Rb9NmcA2YuFnv8LbmEL0eml9",
         "title": "Documentary Edit",
         "client": "Documentary"},
    ],
}


# ----------------------------------------------------------------- writers

def write(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build_service(slug, name, desc, cat):
    plain = html.unescape(name)
    prefix = slug.upper().replace("-", "_")[:12]
    vids = VIDEOS.get(slug, [])
    wide = slug not in ("youtube-shorts-ig-reels", "performance-ads")
    slot_count = len(vids) if vids else 6
    slots = "\n".join(
        slot(prefix, i, cat, wide=wide, video=vids[i - 1] if i <= len(vids) else None)
        for i in range(1, slot_count + 1))
    body = f"""
<section class="page-hero">
  <div class="wrap">
    <a class="back" href="/services.html"><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg> All Services</a>
    <span class="tag" style="display:block;margin-top:18px;">Service</span>
    <h1>{name}</h1>
    <p class="lede">{desc}</p>
    <div class="btn-row">
      <a class="btn btn-key" href="/#sample" data-track="Free Sample CTA Clicked">Get a Free Sample Edit</a>
      <a class="btn btn-line" href="/#quote" data-track="Get a Quote Clicked">Get a Quote</a>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec-head sec-head-split rv">
      <div>
        <span class="tag">The Work</span>
        <h2>{plain} examples</h2>
      </div>
      <p class="lede">{"A selection of our " + plain.lower() + " work." if vids else "Selected " + plain.lower() + " projects. These slots fill in as work is cleared for publication."}</p>
    </div>
    <div class="grid-work grid-work-3">
{slots}
    </div>
  </div>
</section>

<section class="sec sec-raised">
  <div class="wrap">
    <div class="sec-head rv">
      <span class="tag">Related</span>
      <h2>Other things we do</h2>
    </div>
    <div class="spec-row rv" style="margin-top:0;padding-top:0;border-top:0;">
      <a class="spec" href="/services/story-driven-youtube.html">Long-Form YouTube</a>
      <a class="spec" href="/services/youtube-shorts-ig-reels.html">Short-Form</a>
      <a class="spec" href="/services/performance-ads.html">Performance Content</a>
      <a class="spec" href="/services/saas-product-demos.html">SaaS &amp; B2B</a>
      <a class="spec" href="/services/motion-graphics.html">Motion Graphics</a>
      <a class="spec" href="/services/2d-animation.html">2D Animation</a>
      <a class="spec" href="/services/3d-animation.html">3D Animation</a>
      <a class="spec" href="/services.html">All services →</a>
    </div>
  </div>
</section>
""" + (CTA_SEC % (f"Need {plain.lower()}?", "Send us a clip and a short brief. We'll cut a free sample so you can judge the work before spending anything."))

    write(f"services/{slug}.html",
          head(f"{plain}: Mufime", html.unescape(desc), f"services/{slug}.html") + NAV + body + FOOTER)


def build_process(slug, name, num, desc, steps):
    rows = "\n".join(f"""      <div class="pledge rv">
        <span class="n">{i+1:02d}</span>
        <h4>{t}</h4>
        <p>{p}</p>
      </div>""" for i, (t, p) in enumerate(steps))

    others = [f'<a class="spec" href="/process/{s}.html">{n}</a>'
              for s, n, _, _, _ in PROCESS if s != slug]

    body = f"""
<section class="page-hero">
  <div class="wrap">
    <a class="back" href="/#process"><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg> Process</a>
    <span class="tag" style="display:block;margin-top:18px;">Stage {num}</span>
    <h1>{name}</h1>
    <p class="lede">{desc}</p>
    <div class="btn-row">
      <a class="btn btn-key" href="/#sample" data-track="Free Sample CTA Clicked">Get a Free Sample Edit</a>
      <a class="btn btn-line" href="/#quote" data-track="Get a Quote Clicked">Get a Quote</a>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec-head rv">
      <span class="tag">Inside the stage</span>
      <h2>What actually happens</h2>
    </div>
    <div class="pledge-list">
{rows}
    </div>
  </div>
</section>

<section class="sec sec-raised">
  <div class="wrap">
    <div class="sec-head rv">
      <span class="tag">The Rest of the Process</span>
      <h2>Where this sits</h2>
    </div>
    <div class="spec-row rv" style="margin-top:0;padding-top:0;border-top:0;">
      {' '.join(others)}
    </div>
  </div>
</section>
""" + (CTA_SEC % ("Ready to start?", "Send a clip and a short brief and we'll come back with a free sample edit."))

    write(f"process/{slug}.html",
          head(f"{name}: Mufime", desc, f"process/{slug}.html") + NAV + body + FOOTER)


HIDDEN_FROM_LISTING = set()


def build_services_hub():
    visible = [s for s in SERVICES if s[0] not in HIDDEN_FROM_LISTING]
    pillars = visible[:5]
    rest = visible[5:]

    pcards = "\n".join(f"""      <a class="pillar rv" href="/services/{s}.html">
        <span class="n">{i+1:02d}</span>
        <h3>{n}</h3>
        <p>{d}</p>
        <span class="go">See the work <svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>
      </a>""" for i, (s, n, d, _) in enumerate(pillars))

    rcards = "\n".join(f"""      <a class="pillar rv" href="/services/{s}.html">
        <span class="n">{i+6:02d}</span>
        <h3>{n}</h3>
        <p>{d}</p>
        <span class="go">See the work <svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>
      </a>""" for i, (s, n, d, _) in enumerate(rest))

    body = f"""
<section class="page-hero">
  <div class="wrap">
    <a class="back" href="/"><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg> Home</a>
    <span class="tag" style="display:block;margin-top:18px;">Services</span>
    <h1>Everything we make</h1>
    <p class="lede">Five core pillars, plus the specialist craft that sits underneath them. Every one has its own page with examples.</p>
    <div class="btn-row">
      <a class="btn btn-key" href="/#sample" data-track="Free Sample CTA Clicked">Get a Free Sample Edit</a>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="cat-label rv">Core Pillars</p>
    <div class="pillar-grid">
{pcards}
    </div>
  </div>
</section>

<section class="sec sec-raised">
  <div class="wrap">
    <p class="cat-label rv">Specialisms &amp; Niches</p>
    <div class="pillar-grid" style="grid-template-columns:repeat(auto-fit,minmax(260px,1fr));">
{rcards}
    </div>
  </div>
</section>
""" + (CTA_SEC % ("Don't see your niche?", "Tell us what you're making. If it's post-production, there's a good chance we handle it."))

    write("services.html",
          head("Services: Mufime", "Every post-production service Mufime offers, including long-form, short-form, performance content, SaaS and B2B, motion graphics, animation, VFX and sound design.", "services.html")
          + NAV + body + FOOTER)



def build_redirect():
    # plans.html was the old pricing URL — kept alive as a redirect to home
    # now that pricing has been pulled from the site.
    write("plans.html", """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Mufime</title>
<link rel="canonical" href="https://mufime.com/">
<meta http-equiv="refresh" content="0; url=/">
<script>location.replace('/');</script>
</head>
<body><p>Redirecting to <a href="/">mufime.com</a>.</p></body>
</html>
""")


def build_seo():
    pages = ["", "services.html", "book.html", "join-team.html"]
    pages += [f"services/{s}.html" for s, *_ in SERVICES]
    pages += [f"process/{s}.html" for s, *_ in PROCESS]
    urls = "\n".join(
        f"  <url><loc>{SITE}/{p}</loc><changefreq>monthly</changefreq>"
        f"<priority>{'1.0' if p == '' else '0.8' if p == 'services.html' else '0.6'}</priority></url>"
        for p in pages)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + urls + "\n</urlset>\n")

    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


# ----------------------------------------------------------------- run

if __name__ == "__main__":
    for slug, name, desc, cat in SERVICES:
        build_service(slug, name, desc, cat)
    for args in PROCESS:
        build_process(*args)
    build_services_hub()
    build_redirect()
    build_seo()
    print(f"Built {len(SERVICES)} service pages, {len(PROCESS)} process pages,")
    print("plus services.html, plans.html redirect, sitemap.xml, robots.txt")
