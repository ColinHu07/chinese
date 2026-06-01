# Meta DAT Notes

The current bridge is a plain iOS audio + WebSocket prototype. The vendored Meta DAT sample remains under:

`../mobile/ios/vendor/meta-wearables-dat-ios/`

Use that sample for DAT registration, session lifecycle, camera/display examples, and device-specific development patterns. Keep DAT-specific code isolated from the local translator server so the laptop translation path stays usable without Meta-specific dependencies.
