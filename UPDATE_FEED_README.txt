DuskBloom Update Feed
=====================

Center v0.6 has a real remote-catalog/update engine.

Current built-in status:
- DuskBloom Screen 3.4.4: READY
- DuskBloom Web 1.1: READY
- Reader: WORKING ON...
- Pointer: WORKING ON...
- Sonar: WORKING ON...
- Atmosphere: WORKING ON...
- Assist: WORKING ON...

HOW FUTURE RELEASES WORK
------------------------
Center reads a JSON release catalog. When a future app is marked ready, Center can change its card from WORKING ON... to READY TO INSTALL. If an installed app has an older version, the card changes to UPDATE READY.

For automatic downloads, each released component entry in the hosted catalog should include:
  "version": "1.0.1",
  "ready": true,
  "url": "https://.../package.zip",
  "sha256": "..."

A stable HTTPS home for update_catalog.json still needs to be published once for friends/family installs to receive future releases over the internet. The updater engine is already in this Center build; the release feed is the only external piece still needed.
