#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf release_macos build_macos
mkdir -p release_macos
python -m PyInstaller --noconfirm --clean --windowed --onedir --name DuskBloomCenterMac --distpath release_macos --workpath build_macos/center macOS/DuskBloomCenterMac.py
python -m PyInstaller --noconfirm --clean --windowed --onedir --name DuskBloomScreenMac --distpath release_macos --workpath build_macos/screen macOS/DuskBloomScreenMac.py
python -m PyInstaller --noconfirm --clean --windowed --onedir --name DuskBloomReaderMac --distpath release_macos --workpath build_macos/reader macOS/DuskBloomReaderMac.py
cp -R "Bundled/DuskBloom Web/Firefox-Zen" release_macos/DuskBloom-Web-Zen
ditto -c -k --sequesterRsrc --keepParent release_macos DuskBloom_macOS_v2.0.0.zip
echo "Built DuskBloom_macOS_v2.0.0.zip"
