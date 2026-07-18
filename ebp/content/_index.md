# EBP — the Emacs Bridge Protocol

> The wire contract between a live Emacs and any companion that renders its UI — Emacs is the source of truth, the companion a thin pane of glass.

EBP is a wire protocol, not an application. It defines how a live Emacs drives server-driven UI on a *companion*: Emacs pushes native UI specs and handles the semantic events they generate, while the companion renders those specs, caches the last-known UI for offline display, and reports user interactions back by name. Frames are plain NDJSON — one JSON object per `\n`-terminated line — and Emacs dials in as the client, the same inversion `emacsclient` uses on the desktop.

## In this section

- [EBP — the Emacs Bridge Protocol](spec/)
- [Building your own companion](building-companion/)
- [SPEC amendment log](spec-changes/)

← Back to the [EBP overview](../) · [Jetpacs home](https://jetpacs.org/)

