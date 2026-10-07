# Homelean build reference (survives autocompact; delete before public deploy if you like)

Re-read this file first after any compaction. Full old transcript: /home/forhad/.claude/projects/-mnt-data-Dev-lab/0229452a-f02b-414c-a853-1c51bea36259.jsonl

## Task (user, 2026-10-07)
Build home-service company site **Homelean** from a reference screenshot ("Fixora" landing page). Real free-use photos (done, Unsplash), animation + motion graphics, any stack, hosted on **GitHub Pages**, **perfectly mobile responsive**. Latest user note: keep key info in a ref file for autocompact (200k) = this file.

## Hard rules
- Deliverable stays LOCAL in /mnt/data/Dev/lab/homelean. Never publish to cloud/Artifact, never push to GitHub unless asked (memory: no-cloud-artifacts).
- Commits only if asked: lowercase conventional commits, NO Co-Authored-By / "Generated with" lines (user rule overrides the harness reminder). Repo not initialised yet.
- Icons: SVG only (sprite), no emoji / icon fonts, chevrons never arrows, one set (Lucide stroke) + Simple Icons brands (`b-*`, filled). No "→" in link text.
- Avoid AI tells: cream+terracotta, ALL-CAPS eyebrows, single-word headline accents, identical shadowed card kit, fade-up on every section. One orchestrated hero moment; other motion sparing. Respect prefers-reduced-motion.
- Temp files go in scratchpad /tmp/claude-1000/-mnt-data-Dev-lab/0229452a-f02b-414c-a853-1c51bea36259/scratchpad. Any local http.server I start (for testing `<use href=icons.svg>`; file:// fails) must be stopped after. Reset browser viewport to desktop after mobile tests.
- Self-review the diff before saying done (Would fix / Worth knowing). Report honestly: testimonials, stats, prices, phone/email, social links are placeholders; fictional names. I built it directly rather than via a Karkhana role (small solo static site).

## Stack / files
Static HTML/CSS/vanilla JS + GSAP & ScrollTrigger (self-hosted). No build. Relative paths only (works under a repo subpath on Pages).
```
homelean/
  index.html                 DONE (written)
  assets/css/styles.css      TODO  (index.html links THIS name, not style.css)
  assets/js/main.js          TODO
  brand/                     logo + icon set (2026-10-07, by Picasso): logo*.svg, icon.svg, favicon.svg, PNGs, source/build_logo.py; replaces the old leaf-roof assets/favicon.svg (deleted)
  assets/icons.svg           done, 39 symbols
  assets/vendor/gsap.min.js, ScrollTrigger.min.js   done
  assets/fonts/bricolage-grotesque-latin-wght-normal.woff2, instrument-sans-latin-wght-normal.woff2  done
  assets/img/*.webp          done (a1-a8 avatars, cleaning, electrical, handyman, hero-cleaner, hero-plumber, hero-pro, home-cleaner, home-interior, joy, landscaping, painting, plumbing, team)
  .nojekyll, README.md (Pages deploy steps), CREDITS.md (Unsplash + Lucide ISC + Simple Icons CC0 + fonts OFL + GSAP licence)   TODO
```
Sprite symbols: sparkles wrench zap paint-roller hammer trees search star check chevron-right chevron-left chevron-down menu x phone mail map-pin clock shield-check badge-check calendar-check house users headset plus droplets leaf brush-cleaning message-circle wallet timer thumbs-up send circle-check b-facebook b-instagram b-x b-youtube b-whatsapp.
Sprite usage: host `svg.i` needs CSS `width/height:1.25em; stroke:currentColor; fill:none; stroke-width:2; stroke-linecap/linejoin:round`; `.i-fill` => `fill:currentColor` (star); `.i-brand` => `fill:currentColor; stroke:none`.

## Design tokens (planned)
Palette: ink green #0e2b22 (text, dark buttons), page bg cool off-white #f6faf7 (not cream), mint #d9f0e3, butter #fbefc4, blush #fbdcd6, sky #d8e8f7, lilac #e6def7, accent green #1f7a55, star amber #f5a524. Utility classes `tint-butter|blush|sky|lilac|mint`.
Type: Switzer everywhere, one variable woff2 (Bricolage+Instrument Sans -> Nohemi -> Switzer, all 2026-10-07; Forhad rejected Nohemi). File from ~/karkhana/library/fonts/switzer/web, must stay unmodified; FFL bars public-repo redistribution. Fluid clamp() type. Radii by hierarchy (pills for buttons/search/nav, 28-36px big panels, 20px tiles, 999px chips, arch = 999px 999px 24px 24px).
Mobile-first; breakpoints ~640 / 900 / 1200. `.wrap` container with 16-20px gutters. No horizontal scroll at 360px.

## index.html class/JS contract (what CSS and JS must implement)
- Header `.site-header .bar`: `.brand` (an `<img>` of brand/logo.svg; footer uses logo-reversed.svg), `nav#nav.nav` (links + `.nav-cta` button), `.head-cta` (shown on mobile bar), `#menuBtn.menu-btn` (aria-expanded; icons `.i-open`/`.i-close`). Mobile: nav is a drop panel toggled by JS (class on header/body, e.g. `.nav-open`), closes on link click/Esc; desktop (>=900) inline pill nav, hide menuBtn and `.head-cta`.
- Buttons: `.btn` + `.btn-dark | .btn-soft | .btn-light`, `.btn-block`. Any `[data-book]` opens `#book` dialog; value of data-book (HTML-escaped service name) preselects `#b-svc`.
- Hero `.hero`: `.hero-bg` (`.blob.b1-b3`, `.house-line` svg path to draw via stroke-dashoffset), `.hero-grid` > `.hero-copy` (h1 with `.ln > span` lines to rise from mask, `.lead`, `form#searchForm.search` with input#q + datalist, `#searchMsg`, `.rated` with `.faces` avatars) and `.hero-art` (`.spark.s1-s3`, `.arches` > `figure.arch.a-left|a-mid|a-right`, chips `.chip.chip-rate|chip-eta|chip-top` all `[data-float]`; `.eta-bar > i` animates width, `.pulse` dot). hero-plumber.webp is landscape 1000x667: needs object-fit:cover + object-position to crop into portrait arch.
- `.marquee > .track > ul x2` (duplicate list, translateX -50% loop, pause on reduced motion).
- Trust `.bento` tiles: `.tile.t-butter.t-wide | .t-blush | .t-mint | .t-sky.t-wide`, photo tiles `figure.tile.t-photo.t-photo-a|b`; counters `[data-count][data-suffix][data-decimals]` (text already holds final value as no-JS fallback). `.stars-row`, `.deco`.
- Services `#svcGrid.svc-grid` > `article.svc[data-svc][data-keys]` (`.ico.tint-*`, h3, p, `.from`, button). Search filters/highlights by data-keys and scrolls to #services; `#searchMsg` reports result ("Showing N matches" / "No match, try ...").
- How `.steps` (ol) `.step` `.step-ico`, decorative `.steps-line` svg (draw on scroll, desktop only).
- Reasons `.reasons-grid`: `#carousel.carousel` > `#carTrack.car-track` (scroll-snap, `figure.slide` w/ img + figcaption), `.car-btn.prev|next`, `#dots.dots` (JS builds dots); right `.why-card` with `.checks` list.
- Pricing `.plans` > `.plan` (`.plan-pop` highlighted dark card with `.badge`), `.price strong + span`, `.fine`.
- Testimonials `.voice-list` > `figure.voice` (middle `.voice-mid`), `.stars-row.sm`.
- FAQ `.faq-grid`, `.faq-list details[name=faq]` > summary (chevron-down rotates when open) + div. Native accordion.
- CTA `.cta-wrap > .cta`: `img.cta-img` bg + dark green overlay, `.cta-shine`, `.spark.c1-c3`, `.cta-body`.
- Contact `.contact-grid`: `.reach` list (`.ico`), `form#contactForm.card-form` with `.field`, `#contactNote` status. JS: validate, no backend => show friendly "message saved locally / demo" note (no fake send claims; say this is a static demo) — keep honest.
- Footer `.footer .foot` (`.foot-brand`, `.foot-nav`, `.social` w/ `.i-brand`), `.legal`, `#year` filled by JS.
- Dialog `dialog#book.book`: `form#bookForm.book-form` (`.book-head`, `.book-body`, `.book-foot`, `.row2`, `.field`, `.opt`, `#bookErr`), done state `#bookDone.book-done[hidden]` with `.done-mark` svg (circle + path stroke draw) and `#bookSummary`; `[data-close]` closes; set date min = today; backdrop click closes. No data is sent anywhere (static site) — say so in the confirmation copy.
- Utility: `.skip` skip link, `.sr` visually hidden, `.section`, `.sec-head` (h2 + p), `.lead`.

## Status log (final)
- [x] All files written: index.html, styles.css, main.js, favicon, .nojekyll, README.md, CREDITS.md
- [x] Tested 320/360/390/768/1024/1280/1440: no horizontal overflow, no console errors
- [x] Fixed in testing: `[hidden]` override, h1 overflow at 320, hero 2-col from 960, search stem match (plumber -> plumbing), body scroll lock after dialog close, carousel dots update on scroll without rAF
- [x] Interactions verified: search, carousel prev/next/wrap, FAQ exclusive accordion, contact + booking validation and success state, dialog close
- [ ] Not tested: prefers-reduced-motion (read in code only); real touch devices
- Test server stopped, browser viewport reset to desktop.
- Not pushed, no git repo. Commit only if Forhad asks (lowercase conventional, no attribution lines).
- 2026-10-07: (superseded by Switzer, see below) switched to Nohemi; added brand/ logo set (idea: lowercase h drawn as a lean-to, "home" ink + "lean" green); header/footer/favicon/apple-touch/og:image now use it. Library of fonts added at ~/karkhana/library/fonts. Logo awaits Forhad approval; no trademark search done.
- Preview server stopped (it had died on its own; restarted via the `homelean` entry in /mnt/data/Dev/lab/.claude/launch.json, then stopped).
- 2026-10-07 later: Forhad said "nope. use switzer": site font now Switzer; logo wordmark rebuilt in Switzer Semibold via brand/source/build_logo.py.
- 2026-10-07: footer realigned. <900 stacked and left-aligned; 900-1099 brand on top, links and social icons on one row (space-between, centred on each other); >=1100 brand | links | social on one row, all centred on one line, links never wrap. Checked at 320, 768, 900, 1000, 1100, 1280 with no overflow. Switzer confirmed loading in the browser.
- 2026-10-07: marquee under hero already existed; it was frozen for anyone with OS reduce-motion on (the reduced-motion block set animation:none). It now runs at 90s under reduced motion (38s otherwise) and pauses on hover. Local server on :8765 left running at Forhad's request (stop via the Browser pane preview_stop).
- 2026-10-07: reasons carousel autoplay (4.5s) now runs under reduced motion too (instant swap), pauses on hover/focus/touch/wheel/buttons for 10s (2.5s after the mouse leaves), then resumes; before, it stopped for good after the first touch and never ran with reduce-motion on. Tested with stubbed IntersectionObserver in the hidden pane.
- 2026-10-07: marquee light sweep: a .sheen span (JS-created in main.js) glides left to right, against the scroll, every 1.8-7.3s at random, 1.1-2.6s long, random brightness; runs under reduced motion too (faint fade, no content moves); only while the strip is on screen and the tab is visible.
- 2026-10-07: sweep retuned: glint 440px wide, 4.2-6.5s long (gentle ease), new one every 1.5-4s at random (a span per sweep, overlap allowed, removed on finish). Carousel wrap (last to first) now jumps instead of rewinding through every slide. Verified in real headless Chrome via playwright (uv run --with playwright, executable_path /usr/bin/google-chrome): advances every ~4.5s at 1280 and 390, reduced motion on and off, wraps 5 to 0, no script errors.

## Trust photo cards rotate (2026-10-07)
- `figure.t-photo[data-rotate]` holds 7 stacked imgs (`.on` = visible, opacity fade .35s). Card A: joy + work-01..06 (cleaners); card B: plumbing + work-07..12 (trades + cleaners). JS block "trust photo cards" in main.js (before the marquee sweep): each card swaps every 1000-1800ms (random, own timer), only while 25% on screen, tab visible, and mouse not over it. Runs under reduce-motion (fade becomes an instant swap).
- work-*.webp are 560x420, 8-20 KB each (172 KB total). Unsplash IDs are in CREDITS.md. Only free `photo-` IDs work; `premium_photo-` ones are Unsplash+ (paid), skip them.
- Sourcing: unsplash.com search pages work in the Browser pane after its automatic bot check (do not script around it); read img src/alt, then fetch `images.unsplash.com/photo-<id>?w=640&q=70&fm=jpg`.
- Test: scratchpad `rot.py` (playwright, real clock): gaps 1.0-1.8s, all 7 photos cycle, no console errors, 1280 + 390, reduce on/off.
- Photo-card transitions (2026-10-07): main.js `FX` list (8 reveals: wipe x4 sides, circle from centre/corner, slanted slice, curtains, rounded box, zoom-blur, push, rise). Random per swap, never the same twice in a row per card. New photo gets `.in` (z-index 2) and is animated with WAAPI (680-860ms, cubic-bezier(.77,0,.18,1)); `finish` moves `.on`. Reduce-motion uses only the `calm` ones (clip-path reveals, no sliding/scaling of the new photo). CSS: `.t-photo[data-rotate] img{opacity:0}`, `.on`, `.in`. Test: scratchpad `fx.py`.
- Bento ambient icons (2026-10-07): each stat tile has an inline `svg.deco` with its own loop: house bobs + sparkles twinkle (`.deco-house`), clock hands tick (`.deco-clock`), badge pulses + check redraws (`.deco-badge`, pathLength=1), thumbs-up tilts every ~4s (`.deco-thumb`), rating stars wave in sequence (`.t-sky .stars-row .i`). Hover brightens the deco.
- Services hover (2026-10-07): no border change. `.svc::before` = tint circle (per-card `--tint`) grows out of the icon (`--pad` + 28px), `.svc::after` = light streak, card lifts + shadow, icon chip goes white and tilts, button turns ink, icon plays its own loop via `--wiggle` (sparkle, drip, zap flicker, roller, hammer swing, tree sway). Also on `:focus-within`. Reduce-motion block excludes `.svc *`, `.deco *`, the rating stars from the global kill-switch (`*:not(...)` list), same policy as marquee/carousel. Test: scratchpad `hv.py`.

## Marching steps line, review rotator, marquee fix
- `.steps-line path` dashes march along the curve (`march .8s`, dashoffset -12 = one dash period). Exempt from the reduce rule.
- Removed the "Prices are examples..." `.fine` line under the plans.
- Reviews: 9 in 3 `[data-reviews]` cards, 3 each, all stacked in one grid cell (`.rv`) so card height is fixed. Each card swaps every 5-7.5s (offset per card), random effect from 8 (rise, slide, words, flip, zoom, wipe, curtains, fade); only wipe/curtains/fade under reduce. Avatar pops and stars tick on after each swap. Pauses off-screen, on hover/focus, in a hidden tab. Two reviews use initials badges (`.av`) because only 7 customer photos exist.
- Marquee bug: the reduce-motion `*:not(...)` rule had specificity (0,3,0) because of `.t-sky .stars-row .i`, beating `.marquee .track` (0,2,0), so the track froze with reduce on. Fix: `.marquee .track` is in the :not() list. If the list grows, check this override still wins.

## Icon redesign (2026-10-07)
Candidate C ("home in the h") chosen by Forhad, with the right leg cut short at the bottom (`NOTCH`, 8 units on the 100 grid, 2 on the favicon's 32 grid) so doorway + gap read as a hidden L. `brand/source/build_logo.py` now draws it as one pathops shape; the old two-colour lean-to build is gone (copy in git history only if one is made). The three drafts and their build script stay in `brand/candidates/` as a record (c/ is without the notch). Header logo `<img>` width is 154 (lock-up is 482x81.5). Logo QA: 0 fail; warns are the pale mint plate on white and the reversed home/lean pair under colour-blind simulation, both carried over from before.
- 2026-10-07 (later): Forhad dropped the hidden L: right leg is full again (`NOTCH` removed). The h is the icon AND the wordmark's first letter; o, e, m, l, a, n are drawn from the same parts in `build_logo.py` (`arch`, `bowl`, `letter`, `word_paths`), no font involved (Switzer no longer in the logo). Logo viewBox 582.5x89; header/footer `<img>` 144x22 (CSS height 22px, 19px under 380px wide). Old notch version backed up in the session scratchpad only.
- 2026-10-07 (final logo): Forhad rejected the hand-built block letters and chose Picasso's candidate A: Outfit Medium outlined, h counter recut as a gabled doorway, full leg (brand/candidates2/). `brand/source/build_logo.py` now only rolls candidate a out to brand/ and exports the PNGs (it imports candidates2/build_candidates.py). Logo viewBox 592.47x105.39; header/footer `<img>` 124x22. Outfit licence: the font folder holds OFL.txt (the library README wrongly says Fontshare FFL). b (Switzer) and c (Zodiak) are FFL: do not ship modified glyphs from them.
- 2026-10-07: logo weight raised one step on Forhad's request: Outfit Medium -> SemiBold (candidates2/build_candidates.py candidate a). viewBox 600.68x105.38, header/footer img 125x22. Bold/ExtraBold also available in the font folder if heavier is wanted.

## Meet the team strip (2026-10-07)
- `#team` section sits between "why us" and pricing: four department cards (Cleaning, Plumbing, Electrical, Handyman), each led by a team manager. One photo shape per department (arch, leaf, cut-corner, capsule) and the service icon and tint. Grid at 900px+, snap scroll below.
- PLACEHOLDER content: stock photos (`hero-cleaner`, `hero-plumber`, `hero-pro`, `handyman`) with invented manager names, team ratings and visit counts. Replace with real, consenting team members before launch (see the comment above the section in `index.html`).
- The cards are not clickable on purpose: customers book a service, not a named pro.

## Review cards: colour per review and swap blink (2026-10-07)
- Each `.rv` has `data-tint` (sky, mint, butter, blush, lilac); `.voice` takes the tint of the review on show and main.js fades the background with a Web Animation (so it also runs under reduced motion).
- Blink cause: the global reduced-motion rule puts a 0.01ms transition on everything, so the old review's `visibility` flipped a frame late and showed at full opacity. Fixed with `.rv{transition-property:none}`, and animations are now cancelled 120ms after the class change instead of in the same frame.
- Incoming text now starts 60-140ms in (was 260-380ms), so the card is no longer empty between old and new.

## Pre-launch lockdown, Open Graph, scrollbar (2026-10-07)
- Search engines off: `<meta name="robots" content="noindex, nofollow, …">` in the head plus `robots.txt` (Disallow all, link-preview bots allowed so shared links still show the card). robots.txt only counts at a domain root (custom domain or `<user>.github.io`), not at `<user>.github.io/<repo>/`, so the meta tag is the one that always works. **Remove both at launch.**
- Open Graph: site_name, locale, image type/size/alt and `twitter:card` are set. Still open: `og:image` is a relative path and `og:url` is missing; both need the real domain (see the LAUNCH comment in `index.html`).
- Scrollbar: ink pill on the page colour, green on hover (`::-webkit-scrollbar`; Firefox gets `scrollbar-color`). `scrollbar-gutter:stable` stops the page jumping 12px when the booking dialog locks scroll.
- `.pros` negative margin now uses `var(--gutter)` (it was a fixed 16px, which pushed the page 2px wide at 360px and under, where the gutter is 14px).
- `main.js` collisions to remember: reviews helper is `animate` (a `var go` there once overwrote the carousel's `go()`).

## Font swap (2026-10-07)
- Switzer replaced by Instrument Sans (Google Fonts, OFL), self-hosted as `assets/fonts/InstrumentSans-Variable.woff2` (Latin subset, wght 400-700, from Fontsource). Picked over Hanken Grotesk, Inter Tight, Figtree, Schibsted, Jakarta and Onest because it matched Switzer's widths and line breaks almost exactly. Reason: Switzer's FFL licence forbids a public repo.
- Mobile polish: stat-tile clock/badge icons hidden under 640px (they sat on the numbers), CTA overlay darker, topics fieldset margin reset (was 2px off), single-line form fields fixed at 50px so Date and Select match.
