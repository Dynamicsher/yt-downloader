[app]
title = YT Downloader
package.name = ytdownloader
package.domain = org.ytdl

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

# --- Requirements ---
# yt-dlp is pure Python so it bundles fine.
# ffpyplayer gives us FFmpeg on Android without a separate binary.
requirements = python3==3.11.0,kivy==2.3.0,yt-dlp,certifi,requests,urllib3,charset-normalizer,idna

# --- Orientation ---
orientation = portrait

# --- Android permissions ---
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# --- Android API levels ---
android.minapi = 21
android.api = 33
android.ndk = 25b
android.sdk = 33

# --- Architecture (arm64 covers most modern phones; add armeabi-v7a for older ones) ---
android.archs = arm64-v8a

# --- Allow cleartext HTTP (yt-dlp needs it for some CDNs) ---
android.manifest.application_arguments = android:usesCleartextTraffic="true"

# --- NDK features ---
android.enable_androidx = True

# --- Fullscreen ---
fullscreen = 0

android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
