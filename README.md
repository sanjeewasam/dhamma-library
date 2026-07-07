# Dhamma Discussions Library

A static, AI-ready website for a collection of recorded dhamma discussions with
Sinhala transcripts, bilingual thumbnail summaries, and detailed English summaries.

## How it works

There is no database and no backend. The site is just files:

```
dhamma-library/
├── content/
│   ├── audio/            <name>.m4a    — voice clips (.mp4 also accepted)
│   ├── thumbnail/        <name>.txt    — short summary, BOTH languages in ONE
│   │                                     file with [English] and [සිංහල]
│   │                                     section headers (.md also accepted)
│   ├── transcript/       <name>.md     — full Sinhala transcript
│   └── summary/          <name>.md     — detailed English summary
├── build.py              — scans content/, generates manifest.json + llms.txt
├── manifest.json         — generated machine-readable index (do not edit by hand)
├── llms.txt              — generated index for AI assistants (do not edit by hand)
└── index.html            — the whole website (one self-contained page)
```

All four files for a recording share the same base name (Sinhala characters
and spaces in file names are fine). The thumbnail file format is:

```
[English]
Short English summary…

[සිංහල]
Short Sinhala summary…
```

Titles are derived
from the file name (underscores become spaces), and recordings are listed
alphabetically.

## Adding a new recording

1. Drop the files into the four `content/` folders with the same base name.
   (Missing files are fine — that button/summary is simply hidden for that recording.)
2. Run `python build.py`
3. Refresh the page. That's it.

## Running locally / on OMV

Any static file server works. For a quick test:

```
python -m http.server 8420 --directory dhamma-library
```

On your OMV / Proxmox VM, serve the folder with nginx (recommended) or even
OMV's built-in web server. Example nginx config:

```nginx
server {
    listen 80;
    root /srv/dhamma-library;
    index index.html;
    # m4a/mp4 streaming works out of the box; nginx supports range requests
}
```

You could run `build.py` from a cron job or a systemd path unit so the
manifest regenerates automatically when files are added.

## Going public later (Cloudflare)

The same files deploy unchanged:

- **Cloudflare Pages** hosts `index.html`, `manifest.json`, `llms.txt`, and the
  markdown files (free tier is generous).
- **Cloudflare R2** holds the mp4 files (no egress fees). Change the `audio`
  paths in `build.py` to point at your R2 public bucket URL — one line.
- Your domain, TLS, and caching all come from Cloudflare automatically.

## Why this is "AI-ready"

- `manifest.json` — a complete structured index (titles, summaries, file paths)
  that any AI tool or script can consume directly.
- `llms.txt` — the emerging convention (llmstxt.org) that lets AI assistants
  discover and read a site's content as plain text/markdown.
- All content stays in markdown — the native format for LLMs. An AI assistant
  pointed at the site can list, summarise, search, and quote the discussions
  without scraping HTML.
- Future option: a small MCP server over `manifest.json` would let people
  "chat with the library" from Claude or other AI clients.
