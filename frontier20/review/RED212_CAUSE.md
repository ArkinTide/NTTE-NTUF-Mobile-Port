# Red ordinary-road blockage, 2.1.2

The real native scheduler reproduced the failure in 9 of 96 generated worlds:
seeds 15, 22, 33, 48, 74, 81, 82, 94 and 96. This is not a manual Alarm reproduction.
The exact user screenshot seed remains unknown.

The negative run is `tests/20261113T172205902876Z/FrontierRed212ProbeTests`.
Its compiled VM/input, receipt and raw geometry hashes are pinned in
`review/red212-native-seed15-evidence.json`.

For seed 15, Loop 3, the generator first performed five native safe-spawn
translations while there were no walls. Alarm0 then created population and
the appended Red rooms. That raised the nearby Floor count enough to trigger
another GenCont.Step safe-spawn translation while 362 Wall instances and 56
Fake/Helper pairs already existed. Step translated Floor by 32 pixels but did
not translate Wall/Fake/Helper. Afterwards 102 previously open road cells had
lost their Floor and 182 previously open Player-mask edges were blocked; the
remaining cells split into 19 components. Compact exterior walls filled the
lost road cells. The assertion correctly failed.

The repair sets `safespawn=false` only on the current Red GenCont at the start
of `scrNTTEFullRedPopulateNative`, before `scrPopulate` appends rooms. Initial
safe-spawn translations still run before the Alarm0 population boundary.
`scrNTTEFullAreaGeneratorPopulate` binds the callback with `method(id, ...)`;
the synchronous in-room generator binds it to its own `_generation` instance.
The `object_index==GenCont` guard prevents changing another caller instance.
No wall, rock, Floor or Fake/Helper is deleted by this repair.

`tools/fr_red212_hooks.py` installs only this exact audited callback change.
Its three boundary tests cover exact replacement, idempotence and rejection
of a drifted callback before any write.

Final acceptance is the scheduled case, not this diagnosis document. It must
pass the preserved ordinary-road nodes and actual 8x10 Player-mask pixel
edges, zero translations after population, legitimate rock preservation and
Warp/Twins round trips at 30 and 60 Hz in direct and in-room worlds. The
round-trip movement is explicit pixel integration with real collision and
helper EndStep callbacks, not a hardware input or phone test.

## Scheduled rock fixture boundary

A strict rock-ID assertion initially failed in the in-room seed 22, Loop 0,
30 Hz world. The six lost props at (9488, 10912), (9760, 10432), (9616, 10784), (9696, 10848), (9712, 10768), (9792, 10752)
all intersected an actual, still-active native PortalClear mask at sampling;
none overlapped another Wall. They disappeared during the native 12-logical-tick settle,
before the manual round trip. The only sampled rock outside PortalClear
(at 9952, 10096) survived both settle and walking. The native
PortalClear.Collision_Wall calls scrWallDestroy(other.id) unless lockstep is
stopped, so these are intentional entrance-clearance removals rather than this
repair deleting legitimate props. No native clearance behavior is changed.

The corrected fixture records every candidate and its actual PortalClear-mask
result, excludes just the intersecting candidates, and strictly preserves all
remaining rock IDs through native settle and Warp/Twins round trips. It also
requires a nonempty protected-rock population over the eight worlds. Ordinary
road-node and pixel-edge assertions remain unchanged.

Diagnostic only (not acceptance):

- Run: 20261113T174556542952Z/FrontierRed212ScheduledTests
- VM SHA-256: 857a2a952c615a7b9eb58823bc0b04aa345ef56af3ecce1a4ced0060fca8dddd
- Input SHA-256: 5f0e5385145fabdca4e92ff2eddf154859061f49d549127f353461cf3ed22429
- Receipt SHA-256: a4ff7d9a7147159d5e9773a3647407b101d91424805306cdee9ac2ba56066aca
- Raw smoke SHA-256: c317668075b4f296ef0586bd568d9bd490edb35945d9ba4b3913fdbfb6e2816f

## Scheduled path-fixture corrections

The genuine Twins instance is captured before broad hitme parking, then the
same ID is reactivated after the native settle. The final contract requires
both Warp and Twins round trips and a Fake-collision/reveal witness on the
Twins walk itself. The generator and every scheduled callback also assert the
actual engine rate, rather than relying on a requested option value. The
settle is 12 logical ticks (12 engine frames at 30 Hz, 24 at 60 Hz).

A diagnostic run at `tests/20261113T181705465464Z` reached the secret path
without any blocked contact, returned successfully, and recorded two Fake
collisions and full reveal. Its exact Twins target was the fractional position
(9982.744140625, 9823.6640625). The pixel walker incorrectly used a fractional
loop bound, so its integer counter stopped just before the target and failed
the strict 0.01-pixel arrival test. Taking the ceiling of the step count keeps
each axis increment at most one pixel and samples the exact original target.
The target and arrival assertion are unchanged.

The path graph was also aligned with the existing production Player wall
query: every non-Fake Wall blocks regardless of its solid flag. InvisiWall
and optional Helper retain their solid filtering. These are test-fixture
corrections; no production collision, wall or pet is altered. The original
negative-run pins and geometry remain unchanged. Final post-fix acceptance
must use one newly compiled VM and its exact staged-input manifest.

## Intended hidden-entrance route

The direct BFS-tree route can legally take an alternate entrance to the same
real Twins. In diagnostic run `tests/20261113T185920304304Z`, the in-room
seed 48, Loop 3, 60 Hz walk reached the genuine target (9728, 9728), returned
to the exact spawn and had no blocked contact, but crossed no Fake wall and
therefore correctly failed the required Twins reveal witness. A preceding
Warp reveal is not accepted as a Twins witness.

The fixture retains that original direct round trip inside each unique
Twins row as `direct_route`, with its unchanged target identity and all
arrival/return/cleanup assertions. Its main walk additionally goes through
a real Player-mask-intersecting graph node in the same room's genuine Fake
corridor, reaches the exact same Twins, and reverses the route to spawn.
The chosen Fake ID must be present in the before-geometry snapshot and in
that main walk's actual Wall-collision contact IDs. Its actual Helper ID
and creator must also match the before snapshot. No wall, pet, collision
mask, solid flag or reveal state is preset for this route.

Native Twins are a pair: the first real Pet Step creates a second member.
The fixture visits every captured member rather than treating the companion
as a second secret room. It derives the room's original member from the
actual partner link and creation IDs, then binds the Fake interval before
that room member. Normal generation has two captured members per world;
the synchronous in-room generation parks its one original member before
its first Pet Step. The independent validator requires the main Twins
walk IDs to equal the complete original Twins snapshot.

## Native Twins identity

Diagnostic run `tests/20261113T193120200380Z` recorded genuine IDs
110656 and 121279 with a numeric reciprocal link. The original target was
a native `ref`, while the companion's back-reference was a native instance
scope (`struct`): raw reference equality was false even though both values
identified live instance 110656. Numeric identity was true. This matches
the existing `scrNTTEFullTwinsHistorySame` rule and its earlier native
6797 evidence. The route fixture now reuses that existing live `.id`
comparison and records partner IDs through the live instance's `.id`.
No production pet link, constructor or AI behavior is changed.

## Final same-VM evidence

The completed candidate uses VM SHA-256
`ed80aa6ece093f09c937e1462f62a526e2bd322e653f523aa23c144bf4373fff`
and staged-input SHA-256
`9c5e9cd11bb7c2fafc113603ce7aa2bcf69cf1f8c67deb08c975779169c8b352`.
Full compilation finished successfully before either run; its complete
staged-resource manifest is
`analysis/build-inputs/9c5e9cd11bb7c2fafc113603ce7aa2bcf69cf1f8c67deb08c975779169c8b352.json`.

- `tests/20261113T193515988381Z`: all 21 selected cases PASS in the original
  selection order. Scheduled ran first; the remaining 20 were resumed in
  that exact run without changing the VM/input or replacing a passing case.
  Continue Write precedes Continue Read. No historical passing result is
  reused for this candidate.
- `tests/20261113T193515988381Z/FrontierRed212ScheduledTests`: PASS,
  39.64 seconds. Eight direct/in-room worlds cover seeds 15, 22 and 48,
  Loops 0/3 and actual 30/60 Hz. All expected road nodes and pixel-swept
  edges remain unchanged, all 61 protected non-clearance rocks retain
  their original IDs, and each real Warp and all 12 real Twins members
  are reached and returned from. The main Twins routes record 4–18
  actual Fake collisions and a peak reveal of 1, without blocked contacts
  or residual open/orphan Helpers. Every original direct route remains
  independently checked. The strict Scheduled validator accepts the
  real Fake/Helper/room identity bindings and both routes.
- `tests/20261113T193515988381Z/FrontierCollision212Tests`: PASS,
  7.33 seconds.
- `tests/20261113T194427097402Z/FrontierRed212ProbeTests`: PASS,
  189.39 seconds. All 96 native-generation worlds (seeds 1–96; 32 each
  at Loops 0, 1 and 3) preserve every expected ordinary-road node and
  pixel-swept edge. There are zero road failures and zero post-population
  translations, including the nine originally failing seeds.

The earlier `f84ad179...` candidate remains diagnostic history under
`review/diagnostic-history212/final1`; it is not current acceptance.
These are isolated, muted Windows VM checks using the native generator
and actual Player mask/collision callbacks. They do not establish phone
hardware performance, hardware touch-input behavior, or the unknown
screenshot seed itself.
