# CLAUDE.md: jacksoncoldiron.github.io

Personal research website for **Jackson Coldiron**, environmental scientist (MESM '26, UCSB Bren).
Live at <https://jacksoncoldiron.github.io>. The aim is a site that is modern, calm, and professional, with
soft pastel colors (ploen palette plus blue-green water tones) and the "contour wave" look of
*The Carbon Wave* cover and the Dune covers.

---

## How the site works

| Thing | Where |
|---|---|
| Framework | **Quarto website** (`_quarto.yml`), rendered to `docs/` and served by GitHub Pages from `main:/docs` |
| Brand tokens (colors, fonts) | **`_brand.yml`**, which Quarto applies site-wide. Edit hex values here first |
| Component styles | `styles.scss` (CSS variables `--jc-*` mirror `_brand.yml`) |
| Brand guide (visual) | `brand.qmd` → `/brand.html` (linked in footer, hidden from search) |
| Wave artwork | `scripts/make_waves.py` → `assets/waves-{hero,banner,lines}.svg` |
| Photo map | `photography.qmd` + `assets/photo-map.{js,css}` reading `data/places.json` |
| Photo pipeline | `scripts/build_photos.py`: `photos-inbox/<place>/` → `media/photos/` + `data/places.json` |

### Common commands
```bash
quarto render                          # build the whole site into docs/
quarto preview                         # live-reload local preview
python3 scripts/make_waves.py --seed 11   # regenerate wave art (try other seeds)
python3 scripts/build_photos.py        # rebuild photo gallery from photos-inbox/
python3 scripts/build_photos.py --demo # restore sample placeholder gallery
```
Publishing means running `quarto render`, then committing **both** the sources and `docs/`, then pushing to `main`.

### Conventions
- Pages put their custom layout in raw `{=html}` blocks with brand classes: `.wrap`, `.section`, `.eyebrow`,
  `.section-title`, `.jc-card`, `.card-grid`, `.tag(.water|.land|.dune|.sand)`, `.entry`, `.timeline`, `.stat`, `.btn-pill(.dark|.ghost)`.
- Asset URLs inside `styles.scss` are root-relative (`/assets/...`) because the compiled CSS lives in `site_libs/`.
- Text colors: Ink/Slate for text, Eucalyptus for links. Pastels are only for surfaces and data, never text.
- Private repos get a lock label (`<span class="private">`) instead of a link, so visitors never hit a 404.
- `.claude/launch.json` serves `docs/` on port 4321 for in-app previewing.

---

## Changelog: Oct 16, 2026 redesign

**Brand**
- Created `_brand.yml` (ploen core + seafoam/eucalyptus/sage extensions + neutrals; Fraunces / Inter / IBM Plex Mono).
- Built a living brand guide page (`brand.qmd`): palette, gradients, type scale, wave art, mark, components, R/Python
  data-viz snippets, voice do/don'ts, photo style.
- Wrote a procedural wave-art generator inspired by the Carbon Wave cover, and made a three-wave favicon/monogram.

**Design**
- Replaced the flatly/darkly themes and `styles.css` with `theme: [cosmo, brand, styles.scss]`. The site is light-only for a consistent look.
- New navbar (serif wordmark, small-caps links), wave banners on page titles, glassy cards, a gradient timeline, and a footer with wave texture.
- Optimized the headshot from 4.3 MB PNG to a 164 KB JPG (`media/headshot.jpg`); the original PNG is kept.
- Added Open Graph tags, a site description, `site-url`, and a favicon.

**Content** (from the TNC, SWB, and June 2026 resumes plus the CV in `~/Documents/Bren/Resumes`)
- **Home:** hero, bio updated for post-graduation (EDF role), quick facts, four research themes, "by the numbers" stats, selected work, news.
- **Research:** reorganized into four themes (water policy, irrigation and remote sensing, multifunctional landscapes,
  conservation). Added EDF groundwater work, Merced River, coastal dunes, SGMA biodiversity, and an HPC pipeline. Added a publications / reports / talks section.
- **Projects:** featured apps and tools, plus smaller analyses. Descriptions were checked against the repo READMEs. Added the
  live **Accounting for Groundwater** portfolio site.
- **CV page (new):** color-coded timeline, skills, leadership, certifications, coursework.
- **Photography page (new):** replaces the old "Cool Places" listing. Leaflet map with a pastel-tinted CARTO basemap, circles sized
  by photo count and colored by category, hover previews, a side panel list, and a full-screen carousel (keyboard, swipe, thumbnails).
  It currently shows **sample placeholder images** (`"sample": true` in `data/places.json`).
- Fixed the LinkedIn URL (it was `/in/jacksoncoldiron/` and is now `/in/jackson-coldiron/`).
- Removed `cool-places*`, the empty `media/places`, `media/travel`, and `styles.css`.
- Added a `.gitignore` for `.Rproj.user/`, `.Rhistory`, `.quarto/`, and `photos-inbox/`.

---

## Needed from Jackson (open items)

**Facts to confirm**
- [ ] Current role and status as of Oct 2026. The bio says you're at EDF now (6/26 to present). Also, are you job-hunting (e.g. TNC)? If so, consider an "Open to opportunities" line.
- [ ] Email to publish. The site uses `jcoldiron@bren.ucsb.edu`. Will it keep working after graduation, or should it switch to `jcoldiron@ucsb.edu` or a personal address?
- [ ] Dune restoration talk: the conference name, date, and location (currently "Conference presentation (2025)").
- [ ] Manuscript details: working titles, co-authors, and status for the ERL (SPARCLE) and *Irrigation Science* papers. The titles on the research page are placeholders.
- [ ] Whether the Salinas plan PDF (28 MB) is OK to keep public. A compressed version under 5 MB would load faster.
- [ ] Anything in LinkedIn that isn't in the resumes (awards, volunteer work, featured posts). LinkedIn needs a sign-in, so Claude couldn't read it.

**Links and assets**
- [ ] **Zambia Shiny app URL** (shinyapps.io / Posit Connect). Its code is in the private `anna-boser/smallholder-irrigation-dataset` repo.
- [ ] **Intercropping Shiny app** live URL, if deployed.
- [ ] Decide on the **private repos**: make public, keep private, or publish a cleaned public copy:
      `multifunctional-landscapes`, `IPLC-Climate-Nexus/main-analysis`, `smallholder-irrigation-dataset(-archive)`, `dwr-landscape-analysis`.
- [ ] A **CV PDF without your phone number** → `media/Coldiron_CV.pdf`, then uncomment the button in `cv.qmd`.
- [ ] Google Scholar / ORCID IDs (add to navbar + research page once you have them).
- [ ] 1–3 figures or maps from your research (PNG/SVG) to turn the project cards into image cards. This is the biggest visual upgrade available.
- [ ] **Photos** (see below).

---

## Photos: sharing them and showing them

**Best way to get photos to Claude:** export them to a local folder rather than sharing links. Claude can't
log into Google Photos or iCloud, and shared albums usually strip location data.

1. Pick about 5–15 favorites per place.
2. **iCloud / Apple Photos (Mac):** select the photos → File → Export → *Export Unmodified Original* (keeps GPS + HEIC is fine)
   → save into `photos-inbox/<place-name>/`.
   **Google Photos:** make an album per place → ⋮ → *Download all* (zip keeps EXIF/GPS) → unzip into `photos-inbox/<place-name>/`.
   Or use Google Takeout for everything.
3. Optionally add `photos-inbox/<place>/place.yml`:
   ```yaml
   title: Lusaka & the Zambian countryside
   region: Zambia
   date: 2025-07
   category: field        # field | nature | travel  (sets marker color)
   blurb: A summer with the University of Zambia...
   cover: 3               # which photo (1-based, sorted by filename) leads the gallery
   # lat: -15.42          # override if photos lack GPS
   # lng: 28.28
   ```
   and `captions.yml` (`IMG_0412.HEIC: Center-pivot fields near Mkushi`).
4. Run `python3 scripts/build_photos.py && quarto render`.

Originals stay in the git-ignored `photos-inbox/`. Published copies are WebP (2000px long edge plus a 520px thumbnail),
**with all metadata stripped**, and each place is placed at ~100 m precision. Don't use photo locations that reveal your home.

**Why this display:** one circle per curated place (not per photo) keeps the map calm and readable. Circle size shows
how many photos there are, and color shows the kind of trip. Hovering previews the cover photo and clicking opens an
immersive carousel. Budget around 150 photos (~60 MB) before thinking about an external image host.

**Ideas to explore later**
- Globe view: swap Leaflet for MapLibre GL with `projection: globe` and a slow auto-rotate on load.
- A "Field sites" layer: show research sites (Zambia sample points, SSA suitability extent) as a toggle on the same map, linking photos to research.
- Story mode: scroll-driven "trip" pages (scrollama) that fly the map between photo stops.
- If the photo library grows past ~300 images, host images on Cloudinary or Cloudflare R2 and keep only JSON in git.

---

## Is GitHub Pages + Quarto still the right platform?

**Yes, keep it.** It's free, fast, version-controlled, and in the same R/Quarto toolkit you use for research, so
analyses, Shiny links, and figures drop in natively. A custom domain costs ~$12/yr and is the main upgrade worth making.
Squarespace or Wix would be easier to click-edit but cost $16–25/mo, lock in the design, and handle code and data poorly.
A move to Astro or Next.js only makes sense if you want a heavy, app-like site.

## Further suggestions for a world-class but simple site
1. **Custom domain** (e.g. `jacksoncoldiron.com`): add a `CNAME` file and set it in the repo's Pages settings.
2. **Project images:** a hero figure per research entry (map, chart, or field photo) is the single biggest polish step.
3. **Writing/notes page** (Quarto blog listing): short posts explaining a method or finding. Good for SEO and for showing communication skills.
4. **GitHub Action** to run `quarto render` on push, so `docs/` doesn't need committing by hand (switch Pages to "GitHub Actions" source).
5. **Untrack `.quarto/` and `.Rproj.user/`** (now git-ignored but still tracked): `git rm -r --cached .quarto .Rproj.user`.
6. **Analytics:** privacy-friendly GoatCounter or Plausible to see which projects recruiters open.
7. **Accessibility:** add alt text and captions to real photos. Colors already meet WCAG AA for text.
8. **Dark mode** (optional): add a `color.dark` block to `_brand.yml` with ink-navy backgrounds and lavender accents.
9. Consider pinning the best 6 repos on your GitHub profile and adding a profile README that links back here.
