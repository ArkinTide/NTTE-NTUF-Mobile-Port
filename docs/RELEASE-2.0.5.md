# NTTE + NTUF 2.0.5 — internal103

本轮十项修复已通过同一最终 VM 的全部 82 项原生回归，以及 398 项 Python 检查。以下仅说明所列修复和专项验证范围；移动设备实测不在本次证据范围内。

All 82 selected native regressions on the final VM and all 398 Python checks passed. The claims below are limited to the listed repairs and selected evidence; no physical mobile-device acceptance is claimed.

中文

1. 处理保存后重新进入游戏时持续播放的激光声。
2. 修正泡泡 B 皮肤解锁提示框过大，保留交易进度和图标。
3. 将未解锁风暴王冠显示为透明背景的皇冠黑色轮廓。
4. 在设置－视频加入角色和宠物轮廓开关、颜色选择，并使本地角色轮廓与血条颜色一致。
5. 泡泡开启偏好技能模式时，攻击操作发射技能泡泡。
6. 处理只有顶端贴图的墙体及墙体之间异常空隙。
7. 恢复正常击败王冠守护者后的出口，并保留终极解密尚未完成时的出口限制。
8. 处理从披萨下水道巢穴入口回走时卡入墙体的问题。
9. 处理海盗区域中不可见、无法受击并阻止清关的实体生命周期问题。
10. 补齐敌人实际死亡时的食肉酶计数，保留原技能每十三次击杀恢复一点生命的效果，并防止源脚本与死亡处理重复计数。

本轮仅修改 NTTE＋NTUF 移植版，Hardmode 和 Steam 模组未改动。版本为 2.0.5，内部构建 103；保留应用标识、签名和 GAME_BUILD 3004 存档协议。2.0.5 成为当前下载版本，历史源码、标签、发布和验证记录保留。

English

1. Address a sustained laser sound after resuming a saved run.
2. Bound Bubbles' B-skin unlock tooltip while retaining trade progress and icons.
3. Use a crown-shaped silhouette with transparent background for locked Storms.
4. Add Video settings for player/Pet outlines and color selection, sharing the local player outline color with the healthbar.
5. Make Bubbles' preferred ability mode fire ability bubbles through attack controls.
6. Address top-only wall artwork and unexpected gaps between wall sections.
7. Restore the normal Crown Guardian exit while retaining unfinished Ultimate Quest exit restrictions.
8. Address wall entrapment when returning through the opened Pizza Sewer Lair entrance.
9. Address Pirate entity lifecycle states that become invisible, invulnerable and block completion.
10. Count real enemy deaths for Carnivorous Enzymes, retaining the original one-health heal after thirteen kills and preventing duplicate source-poll/death-boundary counting.

Scope is NTTE＋NTUF Mobile only; Hardmode and Steam mods are unchanged. Public version is 2.0.5, internal build 103. Application/signing identities and GAME_BUILD/save protocol 3004 are retained. Historical source, tags, release pages and evidence remain available.

下载 / Downloads: https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA

验证范围 / Validation limits: Selected same-VM tests use a silent background desktop runner and independent saves. No physical Android/iOS device, complete random campaign, universal frame-rate or phone audio-mixing acceptance is claimed. The iOS package requires re-signing. Unknown audio/invisible-enemy scenarios are not generally certified.

原作者 / Upstream: NTTE https://github.com/Yokinman/NTTE ; Uncharted Frontier https://wigglercola.itch.io/uncharted-frontier ; Undergrowth https://attfooy.itch.io/undergrowth ; Details+ https://wigglercola.itch.io/detailsplus .

SHA256 (full package bytes):

`95eaaa26d5a1e89b145424a454d8dd69a3b0952d1d6b9079cd698ba05e381e50`  NuclearThrone.NTTE-NTUF-Android-2.0.5.apk (305447768 bytes)

`7fe9293d34325630c3f125d6062ea05969a947eb2f0957fd3c04daf39149cc0d`  NuclearThrone.NTTE-NTUF-iOS-2.0.5.ipa (213015744 bytes)

The same SHA256SUMS-NTTE-NTUF-2.0.5.txt is distributed in the MEGA folder.
