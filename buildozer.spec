[app]

# Application name
title = Spatial AI Assistant

# Package name (unique identifier for Google Play)
package.name = spatialaiassistant
package.domain = com.spatialai

# Source directory
source.dir = .

# Include patterns
source.include_exts = py,png,jpg,kv,atlas,json,txt
source.include_patterns = android/**,*.py

# Version
version = 1.0.0

# Requirements for python-for-android
requirements = python3,kivy==2.3.0,plyer,jnius,requests,python-dotenv,groq,openssl

# Android specific
android.permissions = RECORD_AUDIO,INTERNET,ACCESS_NETWORK_STATE,CAMERA,MODIFY_AUDIO_SETTINGS,BLUETOOTH,BLUETOOTH_ADMIN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.api = 33
android.minapi = 24
android.ndk = 25c
android.sdk = 33

# Architecture
android.archs = arm64-v8a, armeabi-v7a

# p4a branch
p4a.branch = master

# Build options
android.gradle_dependencies = 
android.enable_androidx = True
android.gradle_wrapper = True

# App orientation
android.orientation = portrait

# Icon and presplash (add your own)
# android.icon = assets/icon.png
# android.presplash = assets/presplash.png

# Intent filters for voice assistant
android.intent_filters = 

# Meta data
android.meta_data = 

# Services (for background operation)
# android.services = 

# Python optimization
android.python_optimize = 2

# Private storage
android.private_storage = 

# Wakelock
android.wakelock = True

# Log level
android.log_level = info

[buildozer]

# Log level
log_level = 2

# Warn on root
warn_on_root = 1

# Artifacts directory
# artifacts_dir = 

[presplash]
# presplash settings
presplash.filename = 
presplash.color = #0a0a12
presplash.always_show = False

[icon]
# icon settings
icon.filename = 
icon.adaptive_background = #0a0a12
icon.adaptive_foreground =