# DuskBloom release feed

The app is ready for a permanent remote update catalog.

Host one JSON file over HTTPS and place its URL in Center Settings > Updates:

`update_catalog.json`

The existing updater expects this shape:

```json
{
  "schema": 1,
  "center": {
    "version": "0.9.0",
    "url": "https://YOUR-HOST/DuskBloomCenter_v0.9.1.zip",
    "sha256": "..."
  },
  "components": {
    "screen": {
      "version": "3.4.4",
      "url": "https://YOUR-HOST/DuskBloomScreen_v3.4.4.zip",
      "sha256": "..."
    }
  }
}
```

Do not invent a repository or URL. Once the permanent host is selected, populate the URLs and SHA-256 hashes.
