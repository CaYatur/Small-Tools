BluetoothWatch - Wear OS Bluetooth scan & pairing demo

What this project does
- A minimal Android (Wear OS capable) app that scans for nearby Bluetooth devices (classic discovery), shows them in a list and provides Pair / Unpair buttons.

Notes & limitations
- System-level pairing (createBond) will normally trigger the platform pairing UI. Removing a bond uses reflection (removeBond) which is not part of the public API and may not work on all devices or Android versions.
- Pairing without user confirmation is not possible for third-party apps on standard Android builds (requires system privileges).

How to build
1. Make sure you have Java, Android SDK and Gradle installed. From this machine I checked Java and adb and Gradle.
2. From project root run:

   gradle :app:assembleDebug

3. The APK output will be in app/build/outputs/apk/debug/app-debug.apk

If you want me to run the build here, tell me and I'll run Gradle assemble (it may take several minutes the first time).
