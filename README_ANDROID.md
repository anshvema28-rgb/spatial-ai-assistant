# Spatial AI Assistant - Android Build Guide

## Overview
This project uses **Kivy + python-for-android (p4a)** via **Buildozer** to create an Android APK.

**Original files preserved:**
- `main.py` - Original CLI assistant (unchanged)
- `spatial_ui.py` - Original CustomTkinter desktop UI (unchanged)
- `.env` - Your GROQ_API_KEY (never exposed in APK)

---

## Prerequisites

### Option 1: GitHub Actions (Recommended for Windows)
No local setup needed. Push to GitHub and use the workflow.

### Option 2: WSL2 + Ubuntu (Local Build)
```bash
# In WSL2 Ubuntu 22.04+
sudo apt update && sudo apt install -y \
    git zip unzip openjdk-17-jdk python3-pip \
    autoconf libtool pkg-config zlib1g-dev \
    libncurses5-dev libncursesw5-dev libtinfo5 \
    cmake libffi-dev libssl-dev automake

# Install buildozer
pip3 install --user buildozer

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Project Structure
```
Ai assistant/
├── main.py                      # Original CLI (preserved)
├── spatial_ui.py                # Original Desktop UI (preserved)
├── .env                         # GROQ_API_KEY (preserved, NOT in APK)
├── requirements.txt             # Updated with Android deps
├── buildozer.spec               # Build configuration
├── android/
│   ├── main.py                  # Kivy App entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── holographic_ui.py    # Kivy canvas orb + glass panels
│   │   ├── main_layout.py       # Main layout combining panels
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py        # Groq AI integration
│   │   ├── system_service.py    # Time, date, weather, commands
│   │   ├── android_actions.py   # Android Intents (Settings, Camera, etc.)
│   │   ├── voice_service.py     # Android TTS/STT via plyer
│   │   ├── permissions.py       # Runtime permission handling
```

---

## Build Commands

### First Build (takes 15-30 mins)
```bash
cd "Ai assistant"
buildozer -v android debug
```

### Subsequent Builds
```bash
buildozer android debug
```

### Release Build (signed)
```bash
buildozer android release
```

### Clean Build
```bash
buildozer android clean
buildozer android debug
```

---

## GitHub Actions CI/CD

Create `.github/workflows/build.yml`:

```yaml
name: Build Android APK

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install system dependencies
        run: |
          sudo apt update
          sudo apt install -y git zip unzip openjdk-17-jdk python3-pip \
            autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
            libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev automake

      - name: Install buildozer
        run: pip install buildozer

      - name: Build APK
        run: buildozer -v android debug
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: spatial-ai-assistant-apk
          path: bin/*.apk
```

**Add `GROQ_API_KEY` as a GitHub Secret** (Settings → Secrets → Actions → New repository secret).

---

## Key Implementation Details

### Android Permissions (Runtime)
- `RECORD_AUDIO` - Voice input
- `CAMERA` - Camera app launch
- `MODIFY_AUDIO_SETTINGS` - Volume control
- `BLUETOOTH` / `BLUETOOTH_ADMIN` - Bluetooth settings
- `INTERNET` / `ACCESS_NETWORK_STATE` - Groq API, Weather API
- `ACCESS_FINE_LOCATION` - Optional, for weather geo

Permissions requested on first launch via `android/services/permissions.py`.

### Voice Implementation
- **TTS**: Uses Android `TextToSpeech` via `jnius` (primary) with `plyer.tts` fallback
- **STT**: Uses `plyer.stt` which wraps Android `SpeechRecognizer`
- Language: `en-IN` for Hinglish recognition

### Android Commands (via Intents)
| Command | Intent Action | Permission |
|---------|---------------|------------|
| Open Settings | `ACTION_SETTINGS` | None |
| Open Calculator | `CATEGORY_APP_CALCULATOR` | None |
| Open Camera | `ACTION_IMAGE_CAPTURE` | `CAMERA` |
| Wi-Fi Settings | `ACTION_WIFI_SETTINGS` | None |
| Bluetooth Settings | `ACTION_BLUETOOTH_SETTINGS` | None |
| Volume Up/Down | `AudioManager.adjustStreamVolume` | `MODIFY_AUDIO_SETTINGS` |

**Note:** Volume control shows system UI overlay. Camera requires runtime permission.

### AI & Weather
- Groq API calls work over HTTPS (same as desktop)
- Weather uses Open-Meteo (no API key needed)
- API key loaded from `.env` at build time (embedded in APK)

**Security:** Never commit `.env` to git. Use GitHub Secrets for CI.

---

## Testing on Desktop (Before APK Build)

```bash
# Install Kivy desktop deps
pip install kivy==2.3.0 plyer requests python-dotenv groq psutil

# Run from android/ directory
cd android
python main.py
```

**Limitations on Desktop:**
- Android intents return "Android only" messages
- TTS falls back to print statements
- STT not available
- Permissions always return "granted"

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `jnius` import error | Ensure `jnius` in requirements; rebuild |
| Permission denied | Check `android.permissions` in buildozer.spec |
| App crashes on launch | Check logcat: `adb logcat -s python` |
| TTS not speaking | Verify `MODIFY_AUDIO_SETTINGS` permission |
| STT not working | Needs Google app installed on device |
| Build fails on `psutil` | Remove `psutil` from requirements (optional) |

---

## APK Output Location
```
bin/spatialaiassistant-1.0.0-arm64-v8a-debug.apk
bin/spatialaiassistant-1.0.0-armeabi-v7a-debug.apk
```

Install via:
```bash
adb install bin/spatialaiassistant-1.0.0-arm64-v8a-debug.apk
```

---

## Next Steps After Build

1. Test on physical Android device (emulator lacks mic/camera)
2. Verify all voice commands work
3. Check Groq API responses over mobile data/WiFi
4. Test camera, settings, calculator intents
5. Adjust UI scaling for different screen sizes if needed
6. Add app icon and presplash images
7. Sign release build for Play Store