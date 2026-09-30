DUSKBLOOM SONAR v15.2 — LIVE STATUS POLISH

The screenshot confirms the actual Sonar connection is now working:
- SONAR • LIVE
- Master/Game/Chat/Media/Aux/Mic show real current values.

The remaining UI bug was stale wording: the widget could say "auto-retrying..."
even after the connection was LIVE.

v15.2:
- Shows "synced with SteelSeries Sonar" after a successful mixer read.
- Shows "reconnecting to SteelSeries Sonar" only after a real connection failure.
- Removes stale auto-retrying wording from the connected state.
- Keeps the working v15.1 mixer/connection implementation unchanged.
