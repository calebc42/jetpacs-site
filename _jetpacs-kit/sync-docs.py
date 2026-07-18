#!/usr/bin/env python3
"""Sync a curated doc set from a project repo into a Hugo site's content/.

Config-driven so every jetpacs.org sub-site uses the same, correct link
rewriting. Reads each doc via `git show <ref>:<path>` (so the checkout's
current branch doesn't matter), prepends Hugo front matter, and rewrites
markdown links:

  - http(s):// and #anchors            → left as-is
  - a sibling repo (jetpacs, ebp, …)   → that repo's GitHub blob
  - another PUBLISHED doc in this set   → on-site relative link (../name/)
  - anything else repo-relative         → this repo's GitHub blob

Usage: sync-docs.py <site-config.json>
"""
import json
import os
import posixpath
import re
import subprocess
import sys

LINK_RE = re.compile(r"(!?\[[^\]]*\])\(([^)]+)\)")


def git_show(repo, ref, path):
    return subprocess.run(
        ["git", "-C", repo, "show", f"{ref}:{path}"],
        check=True, capture_output=True, text=True,
    ).stdout


def build_rewriter(cfg, doc_dir, published):
    blob = cfg["blob"]                 # this repo's blob base, e.g. .../ebp/blob/main
    cross = cfg["cross_repo"]          # {reponame: blobbase}

    def rewrite(m):
        label, target = m.group(1), m.group(2).strip()
        # Markdown allows `](url "title")` — preserve the title suffix.
        parts = target.split(None, 1)
        url = parts[0]
        title = f" {parts[1]}" if len(parts) > 1 else ""
        low = url.lower()
        if low.startswith(("http://", "https://", "//", "mailto:", "#")):
            return m.group(0)
        path, sep, anchor = url.partition("#")
        if not path:  # pure in-page anchor
            return m.group(0)
        anchor = (sep + anchor) if sep else ""
        joined = posixpath.normpath(posixpath.join(doc_dir, path))
        first = joined.split("/", 1)[0]
        if first in cross:                       # sibling-repo reference
            rest = joined[len(first) + 1:]
            new = f"{cross[first]}/{rest}{anchor}"
        elif joined in published:                # another published doc → on-site
            new = f"../{published[joined]}/{anchor}"
        else:                                    # this repo, some other file
            new = f"{blob}/{joined}{anchor}"
        return f"{label}({new}{title})"

    return rewrite


def main():
    cfg = json.load(open(sys.argv[1]))
    site = cfg["site"]
    content = os.path.join(site, "content")
    os.makedirs(content, exist_ok=True)

    # Map each published doc's normalized repo path -> its on-site page name.
    published = {}
    for d in cfg["docs"]:
        norm = posixpath.normpath(d["src"])
        name = os.path.splitext(os.path.basename(d["src"]))[0].lower()
        published[norm] = name

    for d in cfg["docs"]:
        body = git_show(cfg["repo"], cfg["ref"], d["src"])
        doc_dir = posixpath.dirname(posixpath.normpath(d["src"]))
        body = LINK_RE.sub(build_rewriter(cfg, doc_dir, published), body)
        title = d["title"].replace('"', '\\"')
        name = os.path.splitext(os.path.basename(d["src"]))[0].lower()
        # repo_path drives the per-page "Edit this page" link (see hugo.toml).
        front = (
            f'---\ntitle: "{title}"\nweight: {d["weight"]}\n'
            f'repo_path: "{d["src"]}"\n---\n\n'
        )
        with open(os.path.join(content, f"{name}.md"), "w") as f:
            f.write(front + body)
        print(f"  synced {name}.md  (weight {d['weight']})  ← {d['src']}")


if __name__ == "__main__":
    main()
