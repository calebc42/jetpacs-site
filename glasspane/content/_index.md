# Glasspane

> A pane of glass over your org files — the reference Tier-1 Jetpacs app, built so a notes-app convert never has to see Emacs or raw org syntax unless they ask.

Glasspane is the reference Tier-1 application for the Jetpacs ecosystem: a pure-elisp Emacs client that vendors the Jetpacs core as a git submodule and drives an Android companion over the Jetpacs wire protocol. All Kotlin lives in the `jetpacs` repo; this repo is elisp only. The shipped client is a single generated bundle, `glasspane.el`, built from the app sources under `emacs/apps/glasspane/` and opened with `(require 'jetpacs-core)`.

## In this section

- [Roadmap — the Glasspane app](roadmap/)
- [Plan: PKM conversion (Obsidian / Logseq / Notion) & the KMP horizon](plan-pkm-conversion/)

← Back to the [Glasspane overview](../) · [Jetpacs home](https://jetpacs.org/)

