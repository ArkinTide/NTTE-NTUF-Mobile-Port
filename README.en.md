# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

Android/iOS source port of NTTE with **Uncharted Frontier (NTUF) 1.0.3.3**,
Undergrowth, Details+ and Simplified Chinese support. Current version **2.1.4**,
internal build **109**.

Get APK/IPA from the [MEGA download folder](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) and verify
`SHA256SUMS-NTTE-NTUF-2.1.4.txt`. GitHub distributes text source and release notes;
iOS requires re-signing. See the [2.1.4 notes](docs/RELEASE-2.1.4.md).

## 2.1.4 build109 — Melee, touch controls and compatibility maintenance

The newly compiled final Windows VM/input passed 37 explicitly selected native
cases. A hash-verified Python log records 190 passing checks. Earlier VM passes
are not inherited. See the [current validation summary](docs/validation/2.1.4-development-regression.json)
for exact cases and evidence.

1. Reviewed Long Arms for the 17 tested NTTE/NTUF melee weapons (10 NTUF and 7 selected NTTE weapons), including front-melee fusion paths. The maintained source and final Windows VM did not reproduce the reported failure, so existing formulas are not presented as a new fix. After genuine mutation selection, a target grid spaced 4 pixels apart measured the distance to the original center of the farthest damaged target:40→60 pixels for light attacks at30Hz and44→60 at60Hz; heavy attacks measured56→80 at both rates. These values describe the sampled target centers. Form changes, weapon swaps and continuation also passed the current checks.

2. Corrected the mansion gold-station local index and transition-spiral warm-up. Existing guards for the seven screenshot paths involving stale walls, sparse settings reset, destroyed homing targets and instance creation from custom data scopes also ran again on the final current VM.

3. Measured Surgery text with the actual font and added line spacing, independently placing the title and description to prevent overlapping Chinese glyphs.

4. Drew Robot reboot YES/NO choices with an independent GUI camera and restored missing buttons after their authored appearance threshold, while preventing duplicate recreation or submission after a committed choice.

5. Optimized frequent projectile-family type, count and existence queries to avoid repeatedly assembling complete instance lists. Differential tests check legacy return values, types and invalid-input behavior; no phone frame-rate guarantee is made.

6. Removed the extra white arrow at the upper right of the Scythe form control, retaining its weapon icon, button and switching behavior.

7. Aligned the Parrot and Bubbles preference icon, label and switch columns, reserving space before each value and fitting long labels to the available width.

8. Refined continuous touch direction and fine movement, with checks for raw touch input, joystick deadzone and equal-time response at30/60Hz.

Android versionCode is 3000109, retaining application/signing identities and checked
16KB layout. iOS build 109 requires re-signing; new game data uses a retained native
Runner without a fresh Mac native build. GAME_BUILD/save protocol remains 3004.

The eight conclusions above cover the Long Arms review, seven screenshot crash paths,
Surgery text, Robot reboot choices, instance-query performance, the Scythe button,
preference columns and touch movement. Existing map, save, character and content cases
also run again on this final VM. Unknown random
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
