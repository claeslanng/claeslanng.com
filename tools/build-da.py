#!/usr/bin/env python3
"""Build the Danish page (da/index.html) from the English one (index.html).

Edit index.html, then run:  python3 tools/build-da.py

Every English text on the page has a Danish version below. If an English text
changes or a new one is added, this script stops and names the text, so the
Danish page never silently ends up with English on it: add or update its line
in TEXTS and run it again.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
OUT = ROOT / "da" / "index.html"

# (English exactly as in index.html, Danish). Each English text must appear in
# index.html exactly once, unless it is listed with a count as a third item.
TEXTS = [
    # Head: search and sharing
    ('<html lang="en">', '<html lang="da">'),
    ('<title>Claes Lanng: open-format DJ &amp; producer from Copenhagen</title>',
     '<title>Claes Lanng: open format-DJ og producer fra København</title>'),
    ('content="Claes Lanng is a Danish open-format DJ and producer based in Copenhagen. Listen to his remixes, mashups and originals, and book him for your club, festival or event."',
     'content="Claes Lanng er en dansk open format-DJ og producer fra København. Hør hans remixes, mashups og egne numre, og book ham til din klub, festival eller dit private arrangement."'),
    ('<meta property="og:title" content="Claes Lanng: DJ &amp; producer">',
     '<meta property="og:title" content="Claes Lanng: DJ og producer">'),
    ('content="Danish open-format DJ and producer based in Copenhagen. Listen, and book Claes for your event."',
     'content="Dansk open format-DJ og producer fra København. Lyt med, og book Claes til dit arrangement."'),
    ('<meta property="og:url" content="https://claeslanng.com/">',
     '<meta property="og:url" content="https://claeslanng.com/da/">'),
    ('<meta property="og:locale" content="en_US">\n<meta property="og:locale:alternate" content="da_DK">',
     '<meta property="og:locale" content="da_DK">\n<meta property="og:locale:alternate" content="en_US">'),
    ('<link rel="canonical" href="https://claeslanng.com/">',
     '<link rel="canonical" href="https://claeslanng.com/da/">'),
    ('"url": "https://claeslanng.com/",', '"url": "https://claeslanng.com/da/",'),
    ('"jobTitle": "Open-format DJ and producer",', '"jobTitle": "Open format-DJ og producer",'),
    ('"description": "Danish open-format DJ and producer based in Copenhagen.",',
     '"description": "Dansk open format-DJ og producer fra København.",'),
    ('"name": "Copenhagen, Denmark"', '"name": "København, Danmark"'),

    # Menu
    ('<a class="skip" href="#music">Skip to music</a>', '<a class="skip" href="#music">Spring til musik</a>'),
    ('aria-label="Back to top"', 'aria-label="Til toppen"'),
    ('<nav aria-label="Main">', '<nav aria-label="Hovedmenu">'),
    ('<a href="#music">Music</a>', '<a href="#music">Musik</a>'),
    ('<a href="#photos" class="hide-sm">Photos</a>', '<a href="#photos" class="hide-sm">Billeder</a>'),
    ('<a href="#about">About</a>', '<a href="#about">Om</a>'),
    ('<a href="/da/" class="lang hide-sm" hreflang="da" lang="da" aria-label="Dansk version">DA</a>',
     '<a href="/" class="lang hide-sm" hreflang="en" lang="en" aria-label="English version">EN</a>'),

    # Hero
    ('alt="Claes Lanng with his arms raised behind the decks, facing a festival crowd"',
     'alt="Claes Lanng med armene i vejret bag pulten, foran et festivalpublikum"'),
    ('<p class="tagline">Open-format DJ &amp; producer from Copenhagen. Remixes, mashups and originals made for the dance floor.</p>',
     '<p class="tagline">Open format-DJ og producer fra København. Remixes, mashups og egne numre lavet til dansegulvet.</p>'),
    ('<span class="tri" aria-hidden="true"></span>Listen</a>', '<span class="tri" aria-hidden="true"></span>Lyt</a>'),

    # Music
    ('<h2 id="music-title">Music</h2>', '<h2 id="music-title">Musik</h2>'),
    ('<p class="lead">Remixes, mashups, bootlegs and originals. New tracks land on SoundCloud first, and his second SoundCloud account has mashups and bootlegs, many free to download.</p>',
     '<p class="lead">Remixes, mashups, bootlegs og egne numre. Nye numre kommer først på SoundCloud, og på hans anden SoundCloud-konto ligger mashups og bootlegs, mange af dem til gratis download.</p>'),
    ('aria-label="Choose a SoundCloud account"', 'aria-label="Vælg en SoundCloud-konto"'),
    ('data-name="Claes Lanng">Main account</button>', 'data-name="Claes Lanng">Hovedkonto</button>'),
    ('data-name="Claes Lanng 2: mashups and bootlegs"', 'data-name="Claes Lanng 2: mashups og bootlegs"'),
    ('aria-label="Play Claes Lanng on SoundCloud"', 'aria-label="Afspil Claes Lanng på SoundCloud"'),
    ('<strong>Play on SoundCloud</strong>', '<strong>Afspil på SoundCloud</strong>'),
    ('<small>Loads the SoundCloud player here. Nothing from SoundCloud loads until you click.</small>',
     '<small>Åbner SoundCloud-afspilleren her. Intet fra SoundCloud indlæses, før du klikker.</small>'),
    ('<span class="meta">Original</span>', '<span class="meta">Eget nummer</span>'),
    ('aria-label="Listen on"', 'aria-label="Lyt på"'),

    # Photos
    ('<section id="photos" aria-label="Photos">', '<section id="photos" aria-label="Billeder">'),
    ('alt="Claes Lanng DJing at a street party in Copenhagen in front of a big crowd"',
     'alt="Claes Lanng spiller til en gadefest i København foran et stort publikum"'),
    ('alt="Claes Lanng smiling behind the decks in a club"', 'alt="Claes Lanng smiler bag pulten i en klub"'),
    ('alt="Black and white portrait of Claes Lanng with his eyes closed, tongue out"',
     'alt="Sort-hvidt portræt af Claes Lanng med lukkede øjne og tungen ude"'),
    ('alt="Black and white portrait of Claes Lanng laughing in a denim jacket"',
     'alt="Sort-hvidt portræt af Claes Lanng, der griner, i en denimjakke"'),

    # About
    ('alt="Portrait of Claes Lanng, seated, in a cap and vest"', 'alt="Portræt af Claes Lanng, siddende, med kasket og vest"'),
    ('<h2 id="about-title">About</h2>', '<h2 id="about-title">Om Claes</h2>'),
    ('<p>Claes Lanng is a Danish open-format DJ and producer based in Copenhagen. He DJs full-time, and for more than a decade he has played clubs, venues and festivals across Europe.</p>',
     '<p>Claes Lanng er en dansk open format-DJ og producer fra København. Han er DJ på fuld tid og har i mere end ti år spillet på klubber, spillesteder og festivaler rundt om i Europa.</p>'),
    ('<p>He plays everything: his sets move freely between genres and follow the crowd rather than one sound. His productions do the same, with mashups, bootlegs and remixes alongside his own tracks. Whatever the night, the goal is a full dance floor.</p>',
     '<p>Han spiller alt: hans sets bevæger sig frit mellem genrerne og følger publikum frem for én bestemt lyd. Hans produktioner gør det samme, med mashups, bootlegs og remixes side om side med hans egne numre. Uanset aftenen er målet et fyldt dansegulv.</p>'),
    ('<p class="small">Away from the decks he builds free tools for producers as <a href="https://claeslanng.shop">Claes Lanng Plugins</a>.</p>',
     '<p class="small">Når han ikke står bag pulten, laver han gratis værktøjer til producere under navnet <a href="https://claeslanng.shop">Claes Lanng Plugins</a>.</p>'),

    # Booking
    ('<p class="lead">For clubs, festivals, private events, collaborations and press, send an email with the date, venue and what you have in mind.</p>',
     '<p class="lead">Til klubber, festivaler, private arrangementer, samarbejder og presse: send en mail med dato, sted og hvad du har i tankerne.</p>'),
    ('?subject=Booking%20request">Write an email</a>', '?subject=Booking-foresp%C3%B8rgsel">Skriv en mail</a>'),
    ('id="copy-email">Copy email address</button>', 'id="copy-email">Kopiér mailadresse</button>'),
    ('download>Download press kit</a>', 'download>Hent pressekit</a>'),
    ('aria-label="Claes Lanng elsewhere"', 'aria-label="Claes Lanng andre steder"'),

    # Footer
    ('<a href="/da/" class="lang-foot" hreflang="da" lang="da">Dansk</a>',
     '<a href="/" class="lang-foot" hreflang="en" lang="en">English</a>'),

    # Script
    ('f.title = current.dataset.name + " on SoundCloud";', 'f.title = current.dataset.name + " på SoundCloud";'),
    ('btn?.setAttribute("aria-label", "Play " + tab.dataset.name + " on SoundCloud");',
     'btn?.setAttribute("aria-label", "Afspil " + tab.dataset.name + " på SoundCloud");'),
    ('copy.textContent = "Email address copied";', 'copy.textContent = "Mailadresse kopieret";'),
]


def main() -> int:
    html = SRC.read_text(encoding="utf-8")
    problems = []
    for item in TEXTS:
        en, da = item[0], item[1]
        want = item[2] if len(item) > 2 else 1
        found = html.count(en)
        if found != want:
            problems.append(f"found {found}x (expected {want}x): {en[:110]}")
            continue
        html = html.replace(en, da)
    if problems:
        print("The English page changed; update TEXTS in tools/build-da.py:", file=sys.stderr)
        for p in problems:
            print("  -", p, file=sys.stderr)
        return 1

    # The Danish page lives in /da/, so point relative links at the site root.
    html = re.sub(r'(?<=["\s,(])(assets/|press/)', r'/\1', html)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
