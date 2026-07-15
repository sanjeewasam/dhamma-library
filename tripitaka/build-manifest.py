#!/usr/bin/env python3
"""
build-manifest.py — generate books.json (the navigation tree) for the viewer.

Reads the upstream tree.json (the Buddha Jayanti Tripiṭaka table of contents,
with proper Pāli + Sinhala names and full hierarchy) and emits a compact
books.json that index.html renders as a collapsible tree. The heavy text files
are never modified; this only reads tree.json and writes the nav index.

tree.json node format:  [ paliName, sinhName, level, [x,y], parentKey, fileKey ]

Called by the sync scripts, which pass --tree pointing at the cached upstream
copy. Output node format:  [ id, sinhName, paliName, file, [children] ]
where `file` is "" when it is the same as the parent's (inherited) to save size.
"""
import json, os, sys, argparse
from collections import defaultdict

def build(root, tree_path):
    if not os.path.exists(tree_path):
        sys.exit(f"tree.json not found at {tree_path}. Run the sync script (it fetches public/static/data).")
    with open(tree_path, encoding="utf-8") as fh:
        tree = json.load(fh)

    # parent -> [childId,...] preserving document order
    children = defaultdict(list)
    for nid, v in tree.items():
        parent = v[4]
        children[parent].append(nid)

    def make(nid, parent_file):
        v = tree[nid]
        pali, sinh, filekey = v[0], v[1], (v[5] or "")
        eff = filekey or parent_file
        kids = [make(c, eff) for c in children.get(nid, [])]
        file_out = "" if filekey == parent_file else filekey
        return [nid, sinh, pali, file_out, kids]

    roots = [make(r, "") for r in children.get("root", [])]
    if not roots:
        sys.exit("No root nodes found in tree.json (expected vp/sp/ap under parent 'root').")

    out = {
        "source": "Buddha Jayanti Tripiṭaka — tipitaka.lk",
        "license": "CC BY-ND 4.0",
        "sourceUrl": "https://github.com/pathnirvana/tipitaka.lk",
        "tree": roots,
    }
    dest = os.path.join(root, "books.json")  # not "manifest.json": repo .gitignore blocks that name everywhere
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))

    def count(n): return 1 + sum(count(c) for c in n[4])
    total = sum(count(r) for r in roots)
    size = os.path.getsize(dest)
    print(f"Wrote {dest}: {total} nav nodes, {size/1024:.0f} KB.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--root", default=here, help="tripitaka/ folder (output location)")
    ap.add_argument("--tree", default=os.path.join(here, "static", "data", "tree.json"),
                    help="path to upstream tree.json")
    a = ap.parse_args()
    build(a.root, a.tree)
