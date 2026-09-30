DuskBloom Web v1.1 — v54 engine rebuild

This build is intentionally based on the uploaded Migraine Filter v54 behavior,
rather than the simplified DuskBloom Web v1.0 engine.

Preserved from v54:
- Obsidian default
- Pink Blackout, Pink, Dark Pink, Rose Dim, Lavender, Amber, Forest Green,
  Warm White, Deep Red, Blue Light, Dark Dimmer, Midnight, and Obsidian presets
- Six custom theme colors
- Per-site settings
- Full OFF restoration behavior
- Canvas-specific fixes through the v54 top-bar / breadcrumb / Immersive Reader fixes
- Canvas artwork protection
- Bright-container catcher
- Google Docs dark document treatment
- Dynamic-page and shadow-DOM coverage
- Real images/video/course artwork protected from generic filtering
- Context-menu controls and keyboard toggle

The internal mf44/mf50/etc. identifiers are deliberately retained because they
are part of the proven compatibility chain in the v54 engine.

Install:
Firefox / Zen:
  about:debugging -> This Firefox -> Load Temporary Add-on -> manifest.json

Chrome / Edge / Brave / Opera / Vivaldi:
  Extensions -> Developer mode -> Load unpacked -> choose the Chromium folder

Browser internal pages and extension-store pages cannot be modified by a normal
content extension.
