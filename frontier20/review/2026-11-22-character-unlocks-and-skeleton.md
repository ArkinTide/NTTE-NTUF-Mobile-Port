# Character progress, custom character access and Skeleton revival

Baseline: NTTE + NTUF 2.1.4 / build 109, source commit
`1beaf3c6ba4cfd5324ad12205b9b586add16c78a`. Packaging and publication of 2.1.5 / build 110 were subsequently authorized by the user.

## Request status

1. **New characters cannot unlock gold, crowns or skins: not reproduced; context needed.**
   Beetle, Parrot and Bubbles passed real player identity changes, carried-gold
   Room Start, win/loop crown ownership, skin award providers, native and source
   save writes, startup `scrInit` reconstruction, and actual loadout drawing and
   pointer selection. These are Windows VM checks of the shared game code,
   at 30 and 60 FPS. They do not establish Android/iOS save-directory access or
   reproduce an unknown player's save. Natural skin-specific acquisition
   challenges are not newly claimed as completed by these provider tests.
   An optional question asks whether this occurred in a normal run without the
   console, in Custom mode, or in an unknown/mixed context. Do not mark fixed.
2. **Custom mode cannot use additional characters: fixed.** The existing
   Unlock Characters override now runs before the NTTE/NTUF availability early
   returns. It still requires the corresponding runtime/content to be enabled.
   This grants temporary selection, without awarding permanent character
   ownership or enabling gold/achievement storage in Custom mode.
3. **Skeleton dies immediately after revival: fixed.** A Melting death on a
   ReviveCircle previously continued the same Player Step into firing/powers,
   allowing the sampled Melting input to become a Skeleton blood gamble.
   The old `hurtframes` field was never read by the damage gate. Revival now
   restores the same body to 1/4 HP atomically, clears the sampled ability/toggle,
   and finishes that Player Step. The existing intended five logical ticks now
   protect against damage paths that bypass normal iframes. Healing remains
   allowed; damage and blood-gamble HP cost resume after the deadline.

Console, practice, normal save and independent Custom-slot progress rules remain
in force. Disabling these guards is not a fix for an unconfirmed normal-run issue.

## Verification

Fresh GameMaker 2026.0.0.23 Windows VM compilation succeeded, with all staged
resources bound to the build-input manifest. Ten selected background, muted
native cases passed: NewCharacterUnlockTests, CustomCharacterTests,
SkeletonRevivalTests, RaceNativeLifecycleTests, RaceProgressionNativeTests,
WeaponLoadoutNativeTests, CrownLoadoutNativeTests, PetSalamanderTests,
FrontierFollowup210Tests and FrontierUnlockTests. Their source and receipt
bindings are in `analysis/repair-verification-20261122.json`.

The Custom-role test failed on the unmodified availability predicate before its
fix. The normal unlock-provider test already passed that baseline; do not describe
it as a new normal-mode repair. The Skeleton test exercises the genuine Player
death event and ReviveCircle, remaining input, bullet/explosion/raw damage,
five-tick expiry and the actual level-Ultra Skeleton reward at both frame rates.

No mobile hardware test is recorded. The final 2.1.5 Windows VM has passed the same ten selected cases in `tests/20261122T091623243721Z`; packaging and publication receipts are recorded separately under `mobile-release215-build110-20261122`. Do not equate an unfinished packaging phase with a published release.

## Maintenance

Use this restored workspace for follow-up work. Every restored staged file was
verified against the 2.1.4 archive manifest before changes (73,899 files).
The old local encrypted backup and independent recovery keys were preserved.

Production changes are limited to `scrRaces`, `scrTurnIntoSkeleton`,
`scrPlayerProcTakeDamage` and `Player/Step_0.gml`. Existing script assets carry
the explicit desktop regressions; no YYP resource was added.
`native/character-revival-20261122.patch` retains the six-file source/test diff.
`tools/new_character215_hooks.py` reinstalls Custom-role access and its tests.
Keep the accepted staged Skeleton changes if maintaining or reimporting the game;
do not run the historical full-import builder over this repair workspace.
