#!/usr/bin/env python3
"""Stamp the three jetpacs.org sub-site docs sources from verified content.

For each slug: writes a sync config, runs scaffold.sh (theme + shared assets),
runs sync-docs.py (curated docs → content/), and writes hugo.toml, _index.md,
and build.sh. Run build.sh afterwards to compile + deploy.

Reads content-<slug>.json (the workflow's verified output) from this dir.
"""
import json
import os
import subprocess
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
SITES = os.path.dirname(KIT)
DOCROOT = os.path.join(os.path.dirname(KIT), "public")

CROSS_REPO = {
    "jetpacs": "https://github.com/calebc42/jetpacs/blob/main",
    "ebp": "https://github.com/calebc42/ebp/blob/main",
    "glasspane": "https://github.com/calebc42/glasspane/blob/main",
    "jetpacs-composer": "https://github.com/calebc42/jetpacs-composer/blob/main",
}

# slug -> (short title, repo checkout path, github repo url, git ref to sync)
# All sites track main. Docs for ebp/jetpacs-composer are mid-migration off
# slop-fork, so main may be sparse until the repo-split lands. sync reads the
# committed ref, so the checkouts' dirty working trees don't matter.
REPOS = {
    "ebp": ("EBP", "/home/calebc42/pkb/projects/jetpacs/ebp",
            "https://github.com/calebc42/ebp", "main"),
    "jetpacs-composer": ("Jetpacs Composer", "/home/calebc42/pkb/projects/jetpacs/jetpacs-composer",
                         "https://github.com/calebc42/jetpacs-composer", "main"),
    "glasspane": ("Glasspane", "/home/calebc42/pkb/projects/jetpacs/glasspane",
                  "https://github.com/calebc42/glasspane", "main"),
}

HUGO_TOML = """\
# {title} docs — hugo-book (theme + shared assets copied from _jetpacs-kit).
# Served under {baseurl} from {dest}.
# Content under content/ is synced from the {slug} repo by sync-docs.sh — do
# not edit content/*.md by hand; edit upstream and re-sync.

baseURL = '{baseurl}'
locale = 'en-us'
title = '{title}'
theme = 'hugo-book'

disableKinds = ['taxonomy', 'term']

[markup]
  [markup.goldmark.renderer]
    unsafe = true
  [markup.tableOfContents]
    startLevel = 2
    endLevel = 3
  [markup.highlight]
    noClasses = false

[params]
  description = '{desc}'
  BookTheme = 'auto'
  BookFavicon = 'jetpacs-icon.svg'
  BookLogo = 'jetpacs-icon.svg'
  BookSection = '/'
  BookRepo = '{github}'
  BookEditLink = '{{{{ .Site.Params.BookRepo }}}}/edit/main/{{{{ with .Page.Params.repo_path }}}}{{{{ . }}}}{{{{ end }}}}'
  BookSearch = true
  BookComments = false
  BookPortableLinks = 'warning'
  BookDateFormat = 'January 2, 2006'

# Ecosystem cross-nav — identical across every jetpacs.org site.
[menu]
  [[menu.after]]
    name = '← Jetpacs home'
    url = 'https://jetpacs.org/'
    weight = 10
  [[menu.after]]
    name = 'EBP (protocol)'
    url = 'https://jetpacs.org/ebp/'
    weight = 20
  [[menu.after]]
    name = 'Composer'
    url = 'https://jetpacs.org/jetpacs-composer/'
    weight = 30
  [[menu.after]]
    name = 'Glasspane'
    url = 'https://jetpacs.org/glasspane/'
    weight = 40
  [[menu.after]]
    name = 'GitHub'
    url = '{github}'
    weight = 50
"""

BUILD_SH = """\
#!/usr/bin/env bash
# Build the {slug} docs site and deploy into the jetpacs.org docroot.
# Usage: ./build.sh [destination]   (default: {dest})
set -euo pipefail
SITE="$(cd "$(dirname "$0")" && pwd)"
DEST="${{1:-{dest}}}"
cd "$SITE"
hugo --minify --gc
rm -rf "$DEST"
mkdir -p "$DEST"
cp -r public/. "$DEST"/
echo "deployed to $DEST"
"""

SYNC_SH = """\
#!/usr/bin/env bash
# Re-sync {slug} docs from the repo and rewrite links. Edit upstream, not here.
set -euo pipefail
SITE="$(cd "$(dirname "$0")" && pwd)"
python3 "$SITE/../_jetpacs-kit/sync-docs.py" "$SITE/sync.config.json"
"""


def index_md(content, title):
    name = content["name"]
    tagline = content.get("tagline", "")
    lede0 = content.get("lede_paragraphs", [""])[0]
    lines = [f"# {name}", ""]
    if tagline:
        lines += [f"> {tagline}", ""]
    lines += [lede0, "", "## In this section", ""]
    for d in sorted(content["docs_manifest"], key=lambda x: x["weight"]):
        pagename = os.path.splitext(os.path.basename(d["file"]))[0].lower()
        lines.append(f"- [{d['title']}]({pagename}/)")
    lines += [
        "",
        f"← Back to the [{title} overview](../) · "
        "[Jetpacs home](https://jetpacs.org/)",
        "",
    ]
    return "\n".join(lines) + "\n"


def main():
    for slug, (title, repo, github, ref) in REPOS.items():
        content = json.load(open(os.path.join(KIT, f"content-{slug}.json")))
        site = os.path.join(SITES, slug)
        dest = os.path.join(DOCROOT, slug, "docs")
        baseurl = f"https://jetpacs.org/{slug}/docs/"
        desc = content.get("tagline", title).replace("'", "’")

        # 1. scaffold from kit (theme + shared assets)
        subprocess.run(["bash", os.path.join(KIT, "scaffold.sh"), slug], check=True)

        # 2. sync config
        cfg = {
            "slug": slug, "site": site, "repo": repo, "ref": ref,
            "blob": f"{github}/blob/{ref}", "cross_repo": CROSS_REPO,
            "docs": [{"src": d["file"], "title": d["title"], "weight": d["weight"]}
                     for d in content["docs_manifest"]],
        }
        with open(os.path.join(site, "sync.config.json"), "w") as f:
            json.dump(cfg, f, indent=2)

        # 3. hugo.toml, _index.md, sync-docs.sh, build.sh
        with open(os.path.join(site, "hugo.toml"), "w") as f:
            f.write(HUGO_TOML.format(title=title, baseurl=baseurl, slug=slug,
                                     dest=dest, desc=desc, github=github))
        with open(os.path.join(site, "content", "_index.md"), "w") as f:
            f.write(index_md(content, title))
        for fn, tmpl in (("sync-docs.sh", SYNC_SH), ("build.sh", BUILD_SH)):
            p = os.path.join(site, fn)
            with open(p, "w") as f:
                f.write(tmpl.format(slug=slug, dest=dest))
            os.chmod(p, 0o755)

        # 4. sync docs now
        subprocess.run(["python3", os.path.join(KIT, "sync-docs.py"),
                        os.path.join(site, "sync.config.json")], check=True)
        print(f"== {slug}: scaffolded + synced -> {site}\n")


if __name__ == "__main__":
    main()
