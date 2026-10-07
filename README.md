# Homelean

Marketing site for a home-services company: cleaning, plumbing, electrical, painting, repairs and garden care.
Static HTML, CSS and vanilla JavaScript. GSAP and ScrollTrigger are bundled in `assets/vendor`. There is no build step.

## Run it locally

Serve the folder over HTTP. Opening `index.html` straight from disk breaks the SVG icon sprite, because browsers block `<use>` of an external file on `file://`.

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploy to GitHub Pages

All paths are relative, so the site works at `https://<user>.github.io/<repo>/` without changes.

1. Create a new GitHub repository and push this folder to it (`BUILD-REF.md` is a working note; delete it first if you don't want it public).
2. In the repository open **Settings > Pages**.
3. Under **Build and deployment**, set Source to **Deploy from a branch**, pick `main` and `/ (root)`, then save.
4. After a minute the site is live at the URL Pages shows. For a custom domain, add it in the same screen and add a `CNAME` file.

`.nojekyll` is included so Pages serves the folders as they are.

## Before you go live

- **Forms send nothing.** This is a demo: the booking dialog and the contact form validate input and show a confirmation, but there is no backend. Connect them to a form service or your own endpoint for real use.
- **Placeholder content.** Phone number, email, social links, prices, customer stats, testimonials and names are made up. Replace them.
- **Search engines are blocked.** `index.html` has a `noindex` robots tag and `robots.txt` disallows crawlers (link-preview bots are allowed). Remove both to let the site be indexed.
- Update the `<title>`, description and social metadata in `index.html` once you have the real domain.

## Structure

```
index.html
assets/css/styles.css   all styles, mobile first
assets/js/main.js       menu, booking dialog, search, carousel, motion
assets/icons.svg        icon sprite (Lucide + Simple Icons brand marks)
assets/img/             WebP photos
brand/                  logo and icon files (SVG, PNG); brand/README.md says which is for what
assets/fonts/           self-hosted Instrument Sans (variable woff2, SIL OFL)
assets/vendor/          gsap, ScrollTrigger
```

Motion is turned off for visitors who ask their system for reduced motion.

## Credits

See [CREDITS.md](CREDITS.md).
