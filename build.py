#!/usr/bin/env python3
"""Build script for the Dhamma Library.

Scans content/ folders and generates:
  - manifest.json : machine-readable index the website (and any AI tool) reads
  - llms.txt      : plain-text index following the llms.txt convention, so AI
                    assistants can discover and read the whole library

Folder convention (all files share the same base name):
  content/audio/<name>.m4a       voice clip (.mp4 also accepted)
  content/thumbnail/<name>.txt   short summary, BOTH languages in one file,
                                 marked with [English] and [සිංහල] section
                                 headers (.md also accepted)
  content/transcript/<name>.md   full Sinhala transcript
  content/summary/<name>.md      detailed English summary

Usage: python build.py
Run it again whenever recordings are added or text is updated.
"""

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
AUDIO_DIR = CONTENT / "audio"

SITE_TITLE = "Dhamma Discussions Library"
SITE_DESCRIPTION = (
    "A library of recorded dhamma discussions with Sinhala transcripts, "
    "bilingual summaries, and detailed English summaries."
)


def title_from_name(name: str) -> str:
    return re.sub(r"[_\s]+", " ", name).strip()


def safe_id(name: str) -> str:
    """Stable id with no whitespace (valid in HTML ids and JS strings)."""
    return re.sub(r"\s+", "-", name.strip()).replace("'", "").replace('"', "")


def find_file(folder: str, name: str, exts: tuple[str, ...]) -> Path | None:
    for ext in exts:
        p = CONTENT / folder / f"{name}{ext}"
        if p.exists():
            return p
    return None


def parse_thumbnail(path: Path) -> dict[str, str | None]:
    """Split a combined thumbnail file into English and Sinhala parts.

    Sections are marked with lines like [English] and [සිංහල] (or [Sinhala]).
    A file without markers is treated as English-only.
    """
    text = path.read_text(encoding="utf-8").strip()
    parts = re.split(r"^\[(.+?)\]\s*$", text, flags=re.MULTILINE)
    if len(parts) < 3:
        return {"en": text or None, "si": None}
    result: dict[str, str | None] = {"en": None, "si": None}
    # parts = [preamble, label1, body1, label2, body2, ...]
    for label, body in zip(parts[1::2], parts[2::2]):
        body = body.strip()
        if not body:
            continue
        if re.search(r"english|ඉංග්", label, re.IGNORECASE):
            result["en"] = body
        elif re.search(r"sinhala|සිංහල", label, re.IGNORECASE):
            result["si"] = body
    return result


def audio_duration(path: Path) -> float | None:
    """Duration in seconds via ffprobe, if available."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        return round(float(out.stdout.strip()), 1)
    except Exception:
        return None


def build():
    recordings = []
    missing = []

    audio_files = [p for p in AUDIO_DIR.iterdir()
                   if p.suffix.lower() in (".m4a", ".mp4")]
    for audio in sorted(audio_files, key=lambda p: p.stem.lower()):
        name = audio.stem
        thumb_file = find_file("thumbnail", name, (".txt", ".md"))
        thumbs = parse_thumbnail(thumb_file) if thumb_file else {"en": None, "si": None}
        transcript = find_file("transcript", name, (".md", ".txt"))
        summary = find_file("summary", name, (".md", ".txt"))

        entry = {
            "id": safe_id(name),
            "title": title_from_name(name),
            "audio": f"content/audio/{audio.name}",
            "duration_seconds": audio_duration(audio),
            "thumb_en": thumbs["en"],
            "thumb_si": thumbs["si"],
            "transcript_si": f"content/transcript/{transcript.name}" if transcript else None,
            "summary_en": f"content/summary/{summary.name}" if summary else None,
        }

        for kind in ("thumb_en", "thumb_si", "transcript_si", "summary_en"):
            if not entry[kind]:
                missing.append(f"{name}: no {kind.replace('_', '-')}")

        recordings.append(entry)

    manifest = {
        "site": SITE_TITLE,
        "description": SITE_DESCRIPTION,
        "count": len(recordings),
        "recordings": recordings,
    }
    (ROOT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        f"# {SITE_TITLE}",
        "",
        f"> {SITE_DESCRIPTION}",
        "",
        "Machine-readable index: /manifest.json",
        "",
        "## Recordings",
        "",
    ]
    for r in recordings:
        lines.append(f"### {r['title']}")
        if r["thumb_en"]:
            lines.append(f"{r['thumb_en']}")
        lines.append(f"- Audio: /{r['audio']}")
        if r["transcript_si"]:
            lines.append(f"- Sinhala transcript: /{r['transcript_si']}")
        if r["summary_en"]:
            lines.append(f"- Detailed English summary: /{r['summary_en']}")
        lines.append("")
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")

    print(f"Built manifest.json and llms.txt with {len(recordings)} recording(s).")
    if missing:
        print("\nWarnings (site still works, the item is just hidden for that recording):")
        for m in missing:
            print(f"  - {m}")


if __name__ == "__main__":
    build()
