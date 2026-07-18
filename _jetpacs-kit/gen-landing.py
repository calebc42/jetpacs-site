#!/usr/bin/env python3
"""Render a jetpacs.org sub-site landing page from a structured content JSON.

Usage: gen-landing.py <content.json> <output.html>

The JSON shape matches the ecosystem-content workflow's verified output
(slug, name, tagline, lede_paragraphs, what_bullets, status,
getting_started, primary_links, docs_manifest). The page reuses the
foundation landing's styling so the whole ecosystem reads as one system.
"""
import html
import json
import re
import sys

# All ecosystem sections, for the cross-nav + cards (self is filtered out).
ECOSYSTEM = [
    ("", "Jetpacs", "The foundation — Emacs–Android bridge. The pane of glass."),
    ("ebp", "EBP", "The wire protocol: spec, vocabulary, conformance corpus."),
    ("jetpacs-composer", "Composer", "Build Tier-1 apps as declarative org — no elisp."),
    ("glasspane", "Glasspane", "The reference Tier-1 org app, in pure elisp."),
]

STYLE = """\
  :root {
    --bg: #f0ebde; --fg: #3f3b3b; --muted: #6f695e;
    --accent: #624195; --accent-2: #7f5ab6;
    --surface: #f2efe4; --border: #d4cbb6;
    --modeline-bg: #d4cbb6; --modeline-fg: #3f3b3b;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #1e1c24; --fg: #e6e2d8; --muted: #9a9590;
      --accent: #b8a3e0; --accent-2: #8a6bc4;
      --surface: #2a2832; --border: #353240;
      --modeline-bg: #2a2832; --modeline-fg: #9a9590;
    }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--fg);
    font: 17px/1.65 system-ui, -apple-system, "Segoe UI", sans-serif; }
  code, pre, .mono { font-family: ui-monospace, "Cascadia Code", "JetBrains Mono", Consolas, monospace; }
  main { max-width: 44rem; margin: 0 auto; padding: 3.5rem 1.25rem 2rem; }
  a { color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }
  a:hover { color: var(--accent-2); }
  .brand { display: flex; align-items: center; gap: 1.1rem; }
  .brand img { width: 74px; height: 74px; flex: none; }
  .wordmark { font-family: ui-monospace, Consolas, monospace; font-size: 2.4rem;
    font-weight: 700; letter-spacing: -0.02em; margin: 0; }
  .wordmark .paren { color: var(--muted); font-weight: 400; }
  .tagline { font-size: 1.3rem; margin: 0.5rem 0 1.25rem; color: var(--accent); font-weight: 600; }
  .lede { font-size: 1.05rem; }
  .poc { display: inline-block; font-size: 0.75rem; font-family: ui-monospace, Consolas, monospace;
    color: var(--muted); border: 1px solid var(--border); border-radius: 2px;
    padding: 0.1rem 0.5rem; margin-bottom: 1rem; }
  .cta { margin: 1.5rem 0 0; display: flex; flex-wrap: wrap; gap: 0.6rem; }
  .cta a { display: inline-block; font-family: ui-monospace, Consolas, monospace; font-size: 0.9rem;
    text-decoration: none; padding: 0.45rem 0.9rem; border: 1px solid var(--border);
    border-radius: 2px; color: var(--fg); background-color: var(--surface);
    background-image: linear-gradient(var(--accent), var(--accent)); background-repeat: no-repeat;
    background-size: 0% 100%; transition: background-size 0.22s ease, color 0.22s ease, border-color 0.22s ease; }
  .cta a.primary { background-color: var(--accent); border-color: var(--accent); color: var(--bg); }
  .cta a:hover { border-color: var(--accent); background-size: 100% 100%; color: var(--bg); }
  .cta a.primary:hover { opacity: 0.9; }
  h2 { font-family: ui-monospace, Consolas, monospace; font-size: 1.25rem; margin: 3rem 0 0.75rem; }
  h2::before { content: "* "; color: var(--accent-2); }
  pre.code { background: var(--surface); border: 1px solid var(--border); border-radius: 2px;
    padding: 0.75rem 1rem; overflow-x: auto; font-size: 0.85rem; }
  code.inline { background: var(--surface); border: 1px solid var(--border); border-radius: 2px;
    padding: 0.05rem 0.35rem; font-size: 0.85em; }
  ul { padding-left: 1.4rem; }
  li { margin: 0.35rem 0; }
  li::marker { color: var(--accent-2); }
  .repos { display: grid; gap: 0.75rem; margin-top: 1rem; }
  .repo { border: 1px solid var(--border); border-radius: 2px; background: var(--surface);
    padding: 0.9rem 1.1rem; position: relative; }
  .repo::before, .repo::after { content: ''; position: absolute; width: 10px; height: 10px;
    border: 0 solid var(--accent-2); pointer-events: none; }
  .repo::before { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
  .repo::after { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }
  .repo .name { font-family: ui-monospace, Consolas, monospace; font-weight: 700; }
  .repo p { margin: 0.3rem 0 0; font-size: 0.92rem; color: var(--muted); }
  .note { border-left: 3px solid var(--accent-2); padding: 0.1rem 0 0.1rem 1rem;
    color: var(--muted); font-size: 0.95rem; }
  .banner { margin: 2rem 0 0; padding: 0.9rem 1.1rem; border: 1px dashed var(--accent-2);
    border-radius: 2px; background: var(--surface); font-size: 0.95rem; }
  .banner-label { font-family: ui-monospace, Consolas, monospace; font-size: 0.7rem;
    font-weight: 700; letter-spacing: 0.1em; color: var(--bg); background: var(--accent-2);
    padding: 0.1rem 0.45rem; border-radius: 2px; margin-right: 0.5rem; }
  footer { max-width: 44rem; margin: 4rem auto 2.5rem; padding: 0 1.25rem; }
  .modeline { font-family: ui-monospace, Consolas, monospace; font-size: 0.78rem;
    background: var(--modeline-bg); color: var(--modeline-fg); border-radius: 2px;
    padding: 0.35rem 0.75rem; display: flex; justify-content: space-between; gap: 1rem;
    white-space: nowrap; overflow-x: auto; }
"""


def inline(text):
    """Escape HTML, then turn `code` spans into <code> elements."""
    out = html.escape(text, quote=False)
    return re.sub(r"`([^`]+)`", r'<code class="inline">\1</code>', out)


def render_getting_started(text):
    """The three repos format getting_started differently — a plain shell
    script, prose + an indented command, or markdown with ``` fences. Render
    fenced markdown as prose paragraphs + code blocks; render anything without
    fences as a single code block (stripping stray backticks)."""
    text = text.strip()
    if "```" not in text:
        body = html.escape(text.replace("`", ""))
        return f'  <pre class="code">{body}</pre>'
    out = []
    # Split on fenced blocks; odd segments are code, even segments are prose.
    parts = re.split(r"```[^\n]*\n?", text)
    for i, seg in enumerate(parts):
        seg = seg.strip("\n")
        if not seg.strip():
            continue
        if i % 2 == 1:  # inside a fence
            out.append(f'  <pre class="code">{html.escape(seg)}</pre>')
        else:  # prose between fences → paragraphs
            for para in re.split(r"\n\s*\n", seg):
                if para.strip():
                    out.append(f'  <p>{inline(para.strip())}</p>')
    return "\n".join(out)


def render(data):
    slug = data["slug"]
    name = data.get("name", slug)
    wordmark = slug  # e.g. "ebp", "glasspane"

    lede = "\n".join(
        f'    <p class="lede">{inline(p)}</p>' for p in data.get("lede_paragraphs", [])
    )
    bullets = "\n".join(
        f"      <li>{inline(b)}</li>" for b in data.get("what_bullets", [])
    )

    # Top CTA: this site's docs (if any) + sibling ecosystem links + GitHub.
    cta = []
    if data.get("docs_manifest"):
        cta.append('      <a class="primary" href="docs/">Docs</a>')
    cta.append('      <a href="https://jetpacs.org/">Jetpacs home</a>')
    for s, label, _ in ECOSYSTEM:
        if s and s != slug:
            cta.append(f'      <a href="https://jetpacs.org/{s}/">{label}</a>')
    for link in data.get("primary_links", []):
        if "github.com" in link["url"]:
            cta.append(f'      <a href="{html.escape(link["url"])}">GitHub ↗</a>')
            break
    cta_html = "\n".join(cta)

    # Ecosystem cards (siblings, self excluded).
    cards = []
    for s, label, desc in ECOSYSTEM:
        if s == slug:
            continue
        href = f"https://jetpacs.org/{s}/" if s else "https://jetpacs.org/"
        cards.append(
            f'    <div class="repo">\n'
            f'      <a class="name" href="{href}">{label} →</a>\n'
            f"      <p>{inline(desc)}</p>\n"
            f"    </div>"
        )
    cards_html = "\n".join(cards)

    heading = data.get("what_heading", "What it does")
    sections = []
    if bullets:
        sections.append(f"  <h2>{html.escape(heading)}</h2>\n    <ul>\n{bullets}\n    </ul>")
    gs = data.get("getting_started", "").strip()
    if gs:
        sections.append(f"  <h2>Get started</h2>\n{render_getting_started(gs)}")
    if data.get("open_questions"):
        oq = "\n".join(f"      <li>{inline(q)}</li>" for q in data["open_questions"])
        sections.append(f"  <h2>Open questions</h2>\n    <ul>\n{oq}\n    </ul>")
    if data.get("status", "").strip():
        sections.append(f'  <h2>Status</h2>\n  <p class="note">{inline(data["status"])}</p>')
    sections.append(f"  <h2>The ecosystem</h2>\n  <div class=\"repos\">\n{cards_html}\n  </div>")
    body_sections = "\n\n".join(sections)

    # Optional prominent banner (e.g. a "PLANNED — not built yet" notice).
    banner = ""
    if data.get("banner", "").strip():
        label = html.escape(data.get("banner_label", "PLANNED"))
        banner = (
            f'\n  <div class="banner">'
            f'<span class="banner-label">{label}</span> {inline(data["banner"])}</div>\n'
        )

    badge = html.escape(
        data.get("badge", "Part of the Jetpacs ecosystem · LLM-generated proof of concept")
    )
    tagline = inline(data.get("tagline", ""))
    desc_meta = html.escape(data.get("tagline", name), quote=True)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(name)} — Jetpacs ecosystem</title>
<meta name="description" content="{desc_meta}">
<link rel="icon" type="image/svg+xml" href="jetpacs-icon.svg">
<style>
{STYLE}</style>
</head>
<body>
<main>
  <header>
    <div class="brand">
      <img src="jetpacs-icon.svg" alt="Jetpacs logo">
      <h1 class="wordmark"><span class="paren">(</span>{html.escape(wordmark)}<span class="paren">)</span></h1>
    </div>
    <p class="tagline">{tagline}</p>
    <span class="poc">{badge}</span>
{lede}
    <nav class="cta">
{cta_html}
    </nav>
  </header>
{banner}
{body_sections}
</main>

<footer>
  <div class="modeline">
    <span>-UUU:----F1&nbsp;&nbsp;{html.escape(slug)}</span>
    <span>© 2026 calebc42 · GPL-3.0-or-later&nbsp;&nbsp;(Org)</span>
  </div>
</footer>
</body>
</html>
"""


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: gen-landing.py <content.json> <output.html>")
    with open(sys.argv[1]) as f:
        data = json.load(f)
    with open(sys.argv[2], "w") as f:
        f.write(render(data))
    print(f"wrote {sys.argv[2]} for '{data['slug']}'")


if __name__ == "__main__":
    main()
