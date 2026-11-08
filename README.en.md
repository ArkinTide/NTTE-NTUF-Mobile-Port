# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

Android/iOS source port of NTTE with **Uncharted Frontier (NTUF) 1.0.3.3**,
Undergrowth, Details+ and Simplified Chinese support. Current version **2.0.3**,
internal build **99**.

Get APK/IPA from the [MEGA download folder](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) and verify
`SHA256SUMS-NTTE-NTUF-2.0.3.txt`. GitHub distributes text source and release notes;
iOS requires re-signing. See the [2.0.3 notes](docs/RELEASE-2.0.3.md).

## 2.0.3 — Weapon, area and native interaction repairs

The newly compiled final Windows VM/input passed 43 explicitly selected native
cases. A hash-verified Python log records 153 passing checks. Earlier VM passes
are not inherited. See the [current validation summary](docs/validation/2.0.3-development-regression.json)
for exact cases and evidence.

Repair background initialization during area-orb generation, conflicts between wall-top decoration and solid-wall transitions, and swing ownership and offhand reloads for added melee weapons. Restore NTUF metadata after weapon-table reconstruction; correct Bubbles' starting weapon and skill HUD during ordinary play and pause; add a separate skill-toggle preference; and guard statistics display against legacy/default save fields. Aurora processing now uses native instance traversal to avoid repeated allocation and whole-map filtering. This desktop optimization does not establish that overall phone slowdown is resolved.

Correct NTUF ammo augments for ordinary, cursed and NTTE-configured bags while preserving authored multipliers and per-player ammo bonuses. HYPERION drone and shock interception now follows a projectile's current team, preserving allied shots, including reflected shots that have become friendly. Palace moving-block contact uses the authored player-push behavior while retaining the moving-wall proxy. Outline tinting no longer depends on desktop fog and preserves alpha and caller drawing state. Reduce only Heavy Seal's spin transient gain, retaining its source pitch and emphasis ratio.

Repair Crystal copies of sources suspended by wall-top or native PalankingToss controllers. Each copy owns an independent Top or Toss controller and restoration state, preserving its current motion and vertical phase. Native landing/Cleanup restores each body separately, retaining Top alarm restoration and authored Toss landing damage. This is a specific clone repair: the exact target in the original invisibility recording remains unidentified, so it does not establish a fix for all invisible enemies. Persistent low-frequency menu noise or clipping remains unlocated; the separate Heavy Seal gain change does not resolve that report.

All 153 final Python checks and all 43 selected native cases passed on the same final VM; the native run wrapper exited with code 0. Coverage includes 24 natural City maps and focused 30/60 Hz Top and Toss checks. No physical Android/iOS, complete random campaign or universal FPS acceptance is claimed.

Android versionCode is 3000099, retaining application/signing identities and checked
16KB layout. iOS build 99 requires re-signing; new game data uses a retained native
Runner without a fresh Mac native build. GAME_BUILD/save protocol remains 3004.

Persistent menu audio noise remains unresolved. Invisible enemies have no verified
repair. Silent background desktop tests do not establish phone mixing or frame
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
