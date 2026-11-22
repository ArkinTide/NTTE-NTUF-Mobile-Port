# NTTE + NTUF 2.1.5 · build 110

## 更新内容

1. 修复自定义模式的“解锁角色”选项未对甲虫、鹦鹉、泡泡生效的问题；保留内容开关和各槽位进度隔离。
2. 修复骷髅复活后同一帧继续执行熔化的技能输入、触发血赌而立即死亡的问题。复活恢复为 1／4 HP，并将原定五个逻辑帧保护接入真实伤害入口；保护结束后正常受伤。
3. **仍待定位：新增角色无法解锁物品的报告未复现，没有标为已修复。** 甲虫、鹦鹉、泡泡的金武器、皇冠、皮肤保存、启动重读和实际配装选择通过本轮测试。控制台、练习模式及自定义模式的原有解锁规则保留。

## Changes and known issue

- Custom mode's Unlock Characters override now includes Beetle, Parrot and Bubbles while retaining content/readiness gates and independent slot progress.
- Melting-to-Skeleton revival now atomically restores 1/4 HP, cancels the old ability input and ends that Player Step. The intended five logical ticks of protection also cover damage paths that bypass normal iframes. Healing stays available and ordinary damage/blood-gamble costs resume afterward.
- **Pending/unresolved: the report that additional characters cannot unlock items was not reproduced.** Their gold, crowns and skin award/save/startup-reload/loadout paths passed; this report is not claimed fixed.

## Validation and downloads

The final 2.1.5 Windows VM passed all ten selected muted background native cases, including 30/60 FPS logic checks. Five packaging boundary tests passed. No historical VM PASS is counted as new acceptance. Package bytes, source bindings, Android v1/v2 signature and 16KB ZIP/ELF layout, iOS VM/native compatibility and complete upload readback were separately checked.

No physical Android/iOS or exhaustive random-campaign test was performed. Android retains its original application/signing identity (versionCode 3000110). iOS build 110 requires re-signing and uses fresh game data with a retained native runner. GAME_BUILD/save protocol remains 3004.

GitHub distributes text source and notes. APK, IPA and SHA256 checksums use the existing download folder:

https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA

SHA256 (complete package bytes):

`ef22290b70a8f6b7f07ee16d430373629fb618e51f550e14e7bda16b93c87a1e`  NuclearThrone.NTTE-NTUF-Android-2.1.5.apk (305933539 bytes)

`2af31e93cbea5949d8b0494868dbcb691f6ca047aa9e44f3321a360b83c97e0e`  NuclearThrone.NTTE-NTUF-iOS-2.1.5.ipa (213156123 bytes)

Checksum file: `SHA256SUMS-NTTE-NTUF-2.1.5.txt`.

Authors and sources: [NTTE](https://github.com/Yokinman/NTTE), [Uncharted Frontier 1.0.3.3](https://wigglercola.itch.io/uncharted-frontier), [Undergrowth](https://attfooy.itch.io/undergrowth), [Details+](https://wigglercola.itch.io/detailsplus).
