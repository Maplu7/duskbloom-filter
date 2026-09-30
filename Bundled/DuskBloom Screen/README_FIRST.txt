DUSKBLOOM SCREEN v3.4.4 — PAGE SWITCH FIX

The confirmed-good v3.4.3 filter engine is preserved exactly.

FIX:
• hide all content pages before showing the selected one
• recalculate that page's scrolling/layout immediately
• repaint the page, host and sidebar
• perform one deferred repaint after Windows finishes processing the switch

This targets the exact symptom where the first visit to a page looked glitched
but switching away and back made it correct.

No filter, color, intensity, overlay, or transition-engine code was changed.
