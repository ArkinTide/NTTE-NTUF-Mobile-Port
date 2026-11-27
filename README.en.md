# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[Simplified Chinese](README.md) | [English](README.en.md)

Android/iOS source for NTTE with **Uncharted Frontier (NTUF) 1.0.3.3**, Undergrowth, Details+ and Simplified Chinese support. Current version **2.1.6**, internal build **111**.

Get APK/IPA packages from the [existing MEGA folder](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) and verify `SHA256SUMS-NTTE-NTUF-2.1.6.txt`. GitHub distributes text source and notes; iOS requires re-signing. See the [2.1.6 notes](docs/RELEASE-2.1.6.md).

## What changed

Fixes Custom mode character starts and touch movement.

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
