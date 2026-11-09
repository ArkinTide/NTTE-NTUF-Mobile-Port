# NTTE + NTUF 2.0.4

修复暴风雪右侧竖线、区域回调报错、实验室与警局暗门侧墙贴图，并将 Lightring 翻译为“电环”。修复城市17敌方幽灵附身友军后无法受击，以及丛林墙上伏击怪苏醒时丢失落地控制的两类已复现卡关问题。

便携传送器支持连续摇杆角度，保留短点按；改进手柄输入、Android设备分配和断连恢复。优化模块名查询和侍从无人机密集拦截：减少重复处理，合并重叠闪光和音效请求，同时保留敌弹销毁、原生回调及随机序列。友方弹幕仍可穿过侍从无人机。

Fix the blizzard edge seam, area callback errors, laboratory/HQ secret-room wall sides and the Chinese Lightring label. Repair two reproduced clearance blockers: hostile City 17 ghosts possessing allied hosts and Jungle wall-ambush landing handoffs. Improve Pocket Teleporter analogue input, short taps and controller routing. Reduce module lookup and dense drone-interception overhead while preserving hostile projectile destruction, native callbacks, random sequences and friendly projectile pass-through.

机器人死亡后的蓝屏YES／NO：修复普通死亡界面抢先于源复活流程出现的竞争，以及60帧短点按被同帧重复采样清掉的问题。YES保留连接动画、真实传送门和网络空间地图生成，NO保留原死亡原因与普通死亡结算。

Fix premature native GameOver during Robot blue-screen revival and lost short 60 Hz menu taps. YES retains its connection animation and genuine Portal/Cyberspace generation; NO retains the original death cause and ordinary death screen.

选人导航和设置页分别核对当前本地输入所有权，修复触摸摇杆消失后残留方向输入导致的选人自动切换与设置项变化。保留游戏内方向输入及菜单待处理触摸事件。

Check current local input ownership in native character navigation and settings. Direction presses left behind when a touch joystick disappears can no longer keep changing menu choices; gameplay direction input and pending menu touch events are preserved.

未知的其他隐形怪场景未被普遍认证修复；持续菜单低频杂音仍未解决。未做手机真机、实体手柄、完整随机战役或通用60帧验收。The persistent low menu hum remains unresolved; other unknown invisible-enemy cases are not certified. No physical phone/controller, complete random-campaign or universal FPS acceptance is claimed. The IPA requires re-signing.

Installers / 安装包：[原 NTTE MEGA 文件夹](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA)。GitHub contains text source and notes; installers are distributed through MEGA.

Version 2.0.4 · internal 100 · Android versionCode 3000100 · save protocol 3004. Existing application identities and the Android signing certificate are retained.

Validation: 67 selected native regressions passed on the same final VM; 256 Python checks passed. 验证：最终同一VM的67项选定原生回归、256项Python检查全部通过。

Upstream projects and credits:

- [NTTE](https://github.com/Yokinman/NTTE)
- [Uncharted Frontier](https://wigglercola.itch.io/uncharted-frontier)
- [Undergrowth](https://attfooy.itch.io/undergrowth)
- [Details+](https://wigglercola.itch.io/detailsplus)

SHA256 (full package bytes):

`900745f4af346c585862d74a844573227386f1092087ef717e523e89f1df4ece`  NuclearThrone.NTTE-NTUF-Android-2.0.4.apk (304998240 bytes)

`778a32cc4ee2aca2f06b3697a53966b8c1f5134b3f9876d891ba7f58d4fbbb32`  NuclearThrone.NTTE-NTUF-iOS-2.0.4.ipa (212860387 bytes)

The same SHA256SUMS-NTTE-NTUF-2.0.4.txt is distributed in the MEGA folder.
