# DuskBloom macOS 2.0

This branch is the macOS counterpart to DuskBloom Windows 2.0.

## Included
- DuskBloom Center for macOS
- DuskBloom Screen: low-memory static tint overlays; no screen capture/recording
- DuskBloom Reader
- DuskBloom Web for Firefox/Zen

## macOS design rules
- Never use continuous screen capture to implement the migraine filter.
- Keep overlays event-driven and static between setting/display changes.
- Avoid high-frequency polling and animation timers.
- Preserve the Windows 2.0 Web preset engine fixes: one active style, clean preset replacement, working custom colors, and true Off.
- Use macOS-native app packaging and login-item behavior.
- Keep Windows main independent; macOS work stays on this branch.

Sonar is intentionally excluded because SteelSeries Sonar is a Windows component.
