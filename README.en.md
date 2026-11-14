# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

Android/iOS source port of NTTE with **Uncharted Frontier (NTUF) 1.0.3.3**,
Undergrowth, Details+ and Simplified Chinese support. Current version **2.1.2**,
internal build **107**.

Get APK/IPA from the [MEGA download folder](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) and verify
`SHA256SUMS-NTTE-NTUF-2.1.2.txt`. GitHub distributes text source and release notes;
iOS requires re-signing. See the [2.1.2 notes](docs/RELEASE-2.1.2.md).

## 2.1.2 build107 — Red Crystal paths, Robot reboot and augmentation UI repairs

The newly compiled final Windows VM/input passed 21 explicitly selected native
cases. A hash-verified Python log records 157 passing checks. Earlier VM passes
are not inherited. See the [current validation summary](docs/validation/2.1.2-development-regression.json)
for exact cases and evidence.

Repair ordinary Red Crystal routes obstructed beside the hidden path; draw Robot reboot YES/NO in the final GUI layer with matching scaled hitboxes. Guard wall instances destroyed by melee collision callbacks and measure IDPD augmentation text layout. Add a default-on automatic frame-rate switch to Video settings while preserving motion and timer units across cap changes. Make the Bubbles ability preference fire weapon and skill bubbles together.

Android versionCode is 3000107, retaining application/signing identities and checked
16KB layout. iOS build 107 requires re-signing; new game data uses a retained native
Runner without a fresh Mac native build. GAME_BUILD/save protocol remains 3004.

This release validates Red Crystal paths, visible Robot reboot controls and touch input,
melee wall collisions, augmentation layout, automatic frame rate and combined Bubbles attacks. Unknown random
maps and every weapon combination are not generally certified. Silent background desktop tests do not establish phone mixing or frame
rates. No physical Android/iOS, complete random campaign or universal FPS acceptance
is claimed.

## Source and building

`project/` is the accepted common source, `platforms/android/` holds Android text
overlays, and `frontier20/` holds adapters, offline dependencies, localization and
upstream text references. Artwork, audio, fonts, icons, commercial Runners, compiled
extensions and installers are absent from Git and must be obtained separately.
See [building](docs/BUILDING.en.md), [source policy](docs/SOURCE_ONLY.md) and
[source restoration](frontier20/SOURCE_REPRODUCTION.md).

[License](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md) are retained.
This is an unofficial port. History: [2.0.2](docs/RELEASE-2.0.2.md),
[2.0.0](docs/RELEASE-2.0.0.md).
