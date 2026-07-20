+++
title = "Jetpacs — Emacs–Android Bridge Protocol"
author = ["calebc42"]
description = "Don't approximate Emacs — connect to it. The phone is a thin pane of glass; Emacs is the source of truth behind it."
date = 2026-07-19T00:00:00-06:00
draft = false
tagline = "Don't approximate Emacs — connect to it."
badge = "An Android-focused implementation of the Emacs Bridge Protocol"
+++

## Foundation {#foundation}

At its soul, Jetpacs aspires to be nothing more than yet another implementation
of the ever elusive Lisp Machine. Specifically, Jetpacs sets its sights on being
optimized for mobile form factors and touchscreen interaction models. Instead of
rebuilding a Lisp Interpreter from scratch, Jetpacs positions itself to leverage
the existing Lisp Machine experience already ported for Android: Emacs.

For anyone who shares this aspiration, it is a path that has been trodden and had
its routes carved over decades: server.el/emacsclient in the 1980s,
`make-network-process` in Emacs 22, `elnode` and `simple-httpd` in the early-2010s.
This "Emacs-as-a-server" battle-testing carried the TCP foundation right over to
"smartphone-as-a-client". However, here Emacs promptly hits a wall: even after
constructing infrastructure for NAT traversal and weathering latency, it finds
that it needs a persistent connection or polling from the client on a wireless,
intermittent device whose Operating System is optimized for battery life by
aggressively killing background processes. Emacs shouts communications to a
remote listener who has been rendered unreliable by an outright hostile host.
Then, in 2009, the Org Mode Community recognized that the state must live on the
phone and that a local state would require a native parser which led to
implementing MobileOrg. This Emacs-approximation has been the only rational
implementation: eliminate the link entirely, sync the files, parse them, and
approximate the logic with lossy, destructive round-trips. This approach was
carried through Orgzly, organice, Orgro, beorg, each one shouldering the
Herculean task of reimplementing the file format per platform per question Emacs
had already answered.

Recently, with the advent of Po Lu's diligent Android port released in Emacs 30,
this duplicated org-parsing and application logic can be returned to its home in
Elisp where its introspection and configuration is restored. However, we
promptly find ourselves presented with a program built before the concept of a
mouse and demand it render interactive buttons, high-refresh animations, create
home screen widgets, interop with vCal, access a hardware camera. Even if the
user doesn't care for such niceties, it is only a matter of time before the Lisp
Machine in their hand emboldens them to ask questions like: "If the phone knows
my location, how do I get location based-reminders?", "Why can't I input using
the hardware camera as a barcode scanner?", or "What if I could execute elisp by
scanning an NFC Tag/QR Code?". We have successfully mobilized our Lisp Machine
experience into the modern world only to find that it requires lugging around an
external keyboard or installing a litany of third-party keyboards that lack
sufficient FST algorithms, workable auto-complete, or spell-check all just to use
an interaction model not built for the form-factor. To implement any such native
functionalities in Emacs is tantamount to open-heart surgery: rewrite the display
engine for animation, bind Android's camera APIs into the C core, write an elisp
software keyboard. In the end, each one of them is an inversion of the exact
approximation mistakes from the Org parsers of the past. Ultimately, Emacs finds
itself a foreign-citizen with no viable path to assimilation.

At its core, Jetpacs is an Android-focused implementation of the Emacs Bridge
Protocol, a JSON-RPC envelope inspired by Language Server Protocol that can be
transported to any companion (not just Jetpacs) that can hold a socket and draw
pixels to a canvas. Jetpacs stands atop the EBP to extend the mobile-native half
of the equation to Emacs without either side regressing to approximations. The
EBP wires a formally-specified structured-input that is interpreted by the
companion who holds no application logic; Emacs computes the declarations of what
to draw, the companion faithfully renders, caches snapshots and queues your
inputs. By design, Elisp remains the only whole programming language in the
system.

However, unlike in `emacs --daemon` where the durable, long-lived thing listens and
the ephemeral client dials, Jetpacs flips the traditional approach that you'd
expect and treats the "smartphone-as-the-server". For our environment, we need to
answer which side is durable where the only process guaranteed to be alive when
you're tapping on the screen is the app you're looking at. Since we have
determined that Emacs should not approximate a phone, the companion must be the
foreground service and this precludes Emacs being the reliable server per the
manual: "Application processes are treated as disposable entities by the system.
When all Emacs frames move to the background, Emacs might be terminated by the
system at any time.". Further, it's arguably not even the companion's process — it
is the companion's disk cache. For all intents and purposes, "reliable server"
means designing the companion process so that it can die freely and when revived,
it rebuilds from disk, fires the `wake` policy, makes a handshake, then flushes the
queue.

The Lisp Machine experience has been nicely folded into your pocket, but it
remains isolated from interaction in the real world. Emacs has been embodied with
no access to its senses and granted a face whose functions rely on a non-existent
appendages. These are the landmarks of Jetpacs' roadmap.

```text
┌─────────────────────────────────┐
│  Jetpacs (Android Companion)    │
│  • Foreground service           │
│  • Renders whatever Emacs sends │
│  • Caches last-known UI state   │
│  • Queues offline actions       │
└──────────────┬──────────────────┘
               │  Emacs Bridge Protocol: JSON-RPC bridge
               │  (loopback socket → signed Unix socket)
┌──────────────┴──────────────────┐
│  Emacs (the source of truth)    │
│  • Pushes native UI specs       │
│  • Handles user action events   │
│  • Runs all the actual logic    │
└─────────────────────────────────┘
```


## The Envelope {#the-envelope}

_Section stub — the EBP envelope overview goes here._


## The tiers in one breath {#the-tiers-in-one-breath}

-   **Tier 0** — any Emacs buffer renders on the phone by walking its text
    properties; minibuffer prompts become native dialogs; any keymap is a
    searchable command palette; `M-x` works. Zero per-package code.
-   **Tier 0.5** — one renderer per declarative Emacs UI framework:
    `tabulated-list-mode` (every package menu, process list, bookmark table) and
    `transient` (all of magit's menus) render as native touch UI.
-   **Tier 1** — curated apps and skins on top. Glasspane is mine. Yours is the
    point.


## What this makes possible {#what-this-makes-possible}

Things a file parser can't do, no matter how good it is:

-   Run the user's actual capture templates (`:function` entries, hooks,
    `%(elisp)`).
-   Run `org-ql-select` across the whole org-roam graph.
-   Reflect the real `org-todo-keywords` sequence.
-   `org-clock-in` with correct hooks and modeline behavior.
-   Trigger any interactive command — M-x on the phone.


## Working today {#working-today}

Proof of concept, but a broad one — everything in the [protocol spec](/ebp/) is
implemented on both sides:

-   **Rendering** — any buffer, the tabulated-list / transient / comint renderers,
    the full widget vocabulary through tables, charts, canvas, and the agenda month
    grid.
-   **The app shell** — multi-app launcher home with per-app tabs, chrome, and
    settings; package browser, customize browser, tools hub, and automations screen
    as stock chrome.
-   **Interaction** — semantic-action allowlist, offline queue with replay and
    dedupe, the full minibuffer-prompt bridge, dialogs, bottom sheets, radial pie
    menus.
-   **Editing** — live editor sync with completion, flymake diagnostics, eldoc, and
    fontification; the with-editor bridge (`git commit` from the phone). The bridge
    names no providers, only interfaces — so anything that speaks capf/flymake/eldoc,
    from dabbrev to eglot, is in-scope by construction.
-   **The device** — effectors callable from elisp (intents, TTS, torch, volume,
    clipboard…), device triggers, home-screen widgets, QS tiles, notifications,
    persistent reminders, Emacs-theme mirroring.
-   **Transport** — mutual HMAC pairing, reconnect backoff, monotonic surface
    revisions with offline rendering from cache.

> **Known limits:** v0 is local-only (loopback socket — Emacs and the companion on
> the same device), the companion is Android-only, and bridge latency / battery
> cost are unprofiled.


## The ecosystem {#the-ecosystem}

Jetpacs is the foundation. Sibling projects build on it — each has its own
section on this site:

{{< repos >}}
  {{< repo name="EBP — the wire protocol" href="/ebp/" github="https://github.com/calebc42/ebp" >}}
  The Emacs Bridge Protocol: the written spec, the machine-readable vocabulary, and the golden conformance corpus. An interface anyone may implement — pin this to build your own companion or renderer.
  {{< /repo >}}
  {{< repo name="Jetpacs Composer" href="/jetpacs-composer/" github="https://github.com/calebc42/jetpacs-composer" >}}
  Build Tier-1 apps as declarative org documents — no elisp. The no-code path onto the foundation.
  {{< /repo >}}
  {{< repo name="Glasspane" href="/glasspane/" github="https://github.com/calebc42/glasspane" >}}
  The reference Tier-1 org app, in pure elisp. It exists to prove the foundation and to be copied from — not to be the one true mobile Emacs.
  {{< /repo >}}
  {{< repo name="JELPA" href="/jelpa/" note="planned" dashed="true" >}}
  A MELPA-style archive for sharing and pulling Jetpacs apps. A captured idea, not built yet — the concept, written down so it isn't lost.
  {{< /repo >}}
{{< /repos >}}


## Get it running {#get-it-running}

Two halves: the Emacs client and the Android companion. The companion listens;
Emacs dials in. Requires Emacs 28+ — on-device via Termux, or via the native
Emacs 30+ Android port.

```emacs-lisp
;; 1. Load the client (single-file bundle from the repo root)
(add-to-list 'load-path "~/.emacs.d/elisp")
(require 'jetpacs-core)

;; 2. Build + install the companion:  ./gradlew installDebug

;; 3. Copy the pairing token from the companion screen, then
M-x jetpacs-connect
```

Full instructions, including `package-vc-install` straight from git, are in the
[README](https://github.com/calebc42/jetpacs#getting-started), or start with the
step-by-step [tutorial](/docs/tutorial/).


## License {#license}

Jetpacs and Glasspane are free software under the
[GNU GPL, version 3 or later](https://www.gnu.org/licenses/gpl-3.0.html). The
license covers the code; the wire protocol itself is an interface anyone may
implement — a clean-room companion written against the spec carries no obligation
from the repo's license.
