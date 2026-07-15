# Tripiṭaka section for vidyaudapadi.org

A self-contained Pāli–Sinhala **Buddha Jayanti Tripiṭaka** reader. Drop this
folder into the site repo and it serves at `/tripitaka/` — no server, no R2,
no database. Just static files on Cloudflare Pages.

## What's here

| File | Role |
|------|------|
| `index.html` | The viewer. Loads `books.json` for the collapsible nav tree, then `static/text/<book>.json` on demand. Side-by-side Pāli/Sinhala, Pāli-only, or Sinhala-only; search; font-size control; About page; deep links (`/tripitaka/#dn-1-1`). |
| `sync-tipitaka.ps1` / `.sh` | Pull the text **and** `tree.json` from `pathnirvana/tipitaka.lk`, copy the text into `static/text/`, and rebuild `books.json`. Need `git` + `python`. Use the `.ps1` on Windows, `.sh` on Linux/macOS/WSL. |
| `build-manifest.py` | Reads upstream `tree.json` (the real bilingual table of contents) and writes a compact `books.json` (the full Piṭaka → Nikāya → Vagga → Sutta tree). Called by the sync script. |
| `static/text/*.json` | The 285 book files. **Created by the sync script — commit them.** |
| `books.json` | Navigation tree. Generated (~2 MB, ~240 KB gzipped). Commit it. |

`tree.json` is only needed at build time and stays in the git-ignored `.cache/`; it is **not** deployed.

## First-time setup

Windows (PowerShell):

```powershell
cd tripitaka
powershell -ExecutionPolicy Bypass -File .\sync-tipitaka.ps1   # static/text/ (~36 MB) + books.json
cd ..
python -m http.server 8000                                     # preview: http://localhost:8000/tripitaka/
```

Linux/macOS/WSL: `bash sync-tipitaka.sh` instead of the PowerShell line.

Then commit and push — Cloudflare Pages auto-deploys:

```bash
git add tripitaka && git commit -m "Add Tripiṭaka section" && git push
```

## Where it goes in the repo

Place `tripitaka/` wherever your published site output lives:

- **Plain static site** (files served as committed): repo root → `/tripitaka/`.
- **Static generator** (Hugo/Astro/Eleventy/etc.): the generator's static
  passthrough dir (`static/`, `public/`, `assets/`) so it's copied verbatim.

Add a link to it from your main nav, e.g. `<a href="/tripitaka/">ත්‍රිපිටකය</a>`.

## Keeping it current (the license obligation)

The BJT Pāli text is **CC BY-ND 4.0**: use and redistribute with attribution,
but **no modifications**. Two duties, both handled:

1. **Attribution** — shown in the viewer footer and this README.
2. **Stay synced** — re-run `sync-tipitaka.sh` periodically (e.g. monthly) so
   upstream corrections flow in. If you find an error, report it to
   `path.nirvana@gmail.com`; never edit the JSON locally.

## Notes

- Navigation is built from the physical book files, not path-nirvana's internal
  menu router, so it's a clean top-level browse (collection → book → pages),
  independent of upstream structural changes.
- `.cache/` (the upstream git mirror) is git-ignored; only `static/text/` and
  `manifest.json` are committed.
