# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[Simplified Chinese](README.md) | [English](README.en.md)

Android/iOS source for NTTE with **Uncharted Frontier (NTUF) 1.0.3.3**, Undergrowth, Details+ and Simplified Chinese support. Current version **2.1.5**, internal build **110**.

Get APK/IPA packages from the [existing MEGA folder](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) and verify `SHA256SUMS-NTTE-NTUF-2.1.5.txt`. GitHub distributes text source and notes; iOS requires re-signing. See the [2.1.5 notes](docs/RELEASE-2.1.5.md).

## Changes and known issue

- Custom mode's Unlock Characters option now includes Beetle, Parrot and Bubbles while retaining content switches and isolated slot progress.
- Fixed Melting-to-Skeleton revival continuing the old ability input into a same-frame blood gamble. Restored the intended five logical ticks of revival protection; normal damage resumes afterward.
- **Unresolved report: additional characters failing to unlock items was not reproduced.** Gold, crowns and skins passed actual writes, startup file reload and loadout selection for all three characters. This is not described as a fix.

The final Windows VM passed ten selected silent background native cases, including 30/60 FPS logic checks, plus five packaging-boundary checks. Console/practice restrictions and custom-slot isolation remain. No physical Android/iOS or complete random-campaign acceptance is claimed.

Android versionCode 3000110 retains application/signing identity and checked 16KB layout. iOS build 110 uses newly compiled data with a retained native runner and requires re-signing. GAME_BUILD/save protocol remains 3004.

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
