---
title: Jetpacs Documentation
---

# Jetpacs Documentation

**Don't approximate Emacs — connect to it.** Jetpacs renders live Emacs
state as native Android UI over an NDJSON bridge: the phone is a thin pane
of glass, Emacs is the source of truth behind it.

These pages are the foundation docs, synced from
[`docs/` in the jetpacs repo](https://github.com/calebc42/jetpacs/tree/main/docs).
The wire protocol itself lives in the
[ebp repo](https://github.com/calebc42/ebp/blob/main/SPEC.md), and the
reference Tier-1 org app in
[glasspane](https://github.com/calebc42/glasspane).

## Where to start

- **New here?** The [Tutorial](TUTORIAL.md) walks a hello-world Tier-1 app
  from an empty buffer to the phone screen.
- **Want the map?** [Architecture](ARCHITECTURE.md) covers the tier model,
  the module layout, and every extension seam.
- **Building your own app?** [Building a Tier 1](BUILDING-TIER1.md), then
  the [widget-DSL reference](WIDGETS.md) and the
  [binding layer](BINDING.md).
- **Tracking stability?** [API stability](API-STABILITY.md) and the
  [Roadmap](ROADMAP.md).

← Back to the [project page](https://calebc42.com/jetpacs/).
