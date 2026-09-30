#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="$PWD/release_macos"
rm -rf "$OUT"
mkdir -p "$OUT"

make_app () {
  NAME="$1"
  SOURCE="$2"
  shift 2
  APP="$OUT/$NAME.app"
  mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
  swiftc -O "$SOURCE" -o "$APP/Contents/MacOS/$NAME" "$@"
  BUNDLE_ID=$(echo "$NAME" | tr -d ' ')
  cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>$NAME</string>
<key>CFBundleDisplayName</key><string>$NAME</string>
<key>CFBundleExecutable</key><string>$NAME</string>
<key>CFBundleIdentifier</key><string>com.duskbloom.$BUNDLE_ID</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>2.0.0</string>
<key>CFBundleVersion</key><string>200</string>
<key>LSMinimumSystemVersion</key><string>13.0</string>
<key>LSUIElement</key><true/>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
}
make_app "DuskBloom Screen" "macOS/DuskBloomScreen.swift" -framework Cocoa
make_app "DuskBloom Center" "macOS/DuskBloomCenter.swift" -framework Cocoa
make_app "DuskBloom Reader" "macOS/DuskBloomReader.swift" -framework Cocoa -framework PDFKit
cp -R "Bundled/DuskBloom Web/Firefox-Zen" "$OUT/DuskBloom Web for Zen"
cat > "$OUT/START HERE.txt" <<'TXT'
DUSKBLOOM FOR MAC
Drag the three DuskBloom apps to Applications.
DuskBloom Screen lives in the top menu bar as a flower and uses no screen capture.
Center and Reader close completely when their windows close.
If macOS blocks first launch: System Settings > Privacy & Security > Open Anyway.
TXT
ditto -c -k --sequesterRsrc --keepParent "$OUT" DuskBloom_macOS_v2.0.0.zip
echo "Built DuskBloom_macOS_v2.0.0.zip"
