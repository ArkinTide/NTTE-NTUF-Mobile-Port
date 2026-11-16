# NTTE + NTUF 2.1.3 · build108

- 修复墓地区域数据回调、追踪目标消失、无人机残留判定框及重置设置的已复现报错。
- 修复海滩区域球地块被新增墙体完全包围的问题；终极解密入口／钥匙地块在地面重建后保留原位置和交互。重新验证有序钥匙合成、清怪门禁、交付及奖励。
- 修复大苍蝇蛆虫重复生成、诅咒箱掉落任务骨头，以及泡泡手动瞄准回到摇杆中央再松手时不攻击的问题。
- 轮廓／血条颜色设置新增默认开启的“同时更换准心颜色”；关闭后恢复白色准心。修复60帧开始菜单旋涡背景闪烁。
- 自动降帧使用持续CPU余量决定恢复；首次恢复失败后本关保持30帧，避免反复切换。新关卡、菜单或关闭开关会重置，暂停保留保护，连续稳定5秒才接受恢复；减少Alarm计时扫描和类行星加农炮融合近战的射线碰撞扫描。共享优化适用于新增地图及游戏内困难模式。

The reproducible fixes cover data-scope and target-lifetime errors, sealed Coast orb areas, puzzle-floor survival, repeated fly-larva spawning, cursed-chest bones and Bubbles' manual release gesture. A default-on crosshair-color switch and stable 60 Hz menu spiral are included. A failed frame-cap recovery probe stays at 30 Hz for the scene instead of repeatedly switching. New generation, menu or opt-out resets it, while pause preserves it; five stable seconds accept a recovery. Common Alarm/Quasar collision work is optimized, including added maps and the embedded hard mode.

当前重新编译的Windows VM在独立、静音后台环境通过32项选定原生专项，并通过160项Python回归检查；未复用旧PASS收据。验证范围包括真实菜单／触摸输入、两种泡泡初始武器、新局及死亡后重试、30／60帧运动与计时、恢复失败保护、地图墙体和终极解密流程。

融合射线固定CPU测试中，250个列表目标筛为2个候选，测得查询耗时从8939μs降至330μs，6336次精确碰撞对照全部一致，另有3项Alarm检查。此数值仅是该桌面测试夹具的CPU查询结果，不能换算为手机帧率。

The final Windows VM passed 32 selected native cases and 160 Python regression checks; prior receipts are not inherited. A controlled fused-laser fixture reduced 250 listed targets to 2 candidates and measured 8939 μs versus 330 μs for CPU collision queries, with 6336 collision-parity checks and 3 Alarm checks. These measurements do not certify device frame rates.

未进行Android／iOS真机、完整随机战役或所有武器组合验收；新增地图的手机速度、困难模式负载和未知随机闪退仍需设备反馈。自动降帧改动保留视频设置中的原有开关。独立Hardmode移植版及Steam模组未修改。iOS安装包需要重新签名，未进行新的Mac原生编译。GAME_BUILD／存档协议保持3004。

No physical Android/iOS, exhaustive campaign, universal 60 FPS or absence of every unexplained crash is claimed. The separate Hardmode port and Steam mod are unchanged. iOS requires re-signing and uses a retained native Runner with newly compiled game data; no new Mac native build was performed.

GitHub仅分发文本源码和版本说明；安装包与校验文件使用原NTTE下载目录：

https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA

原作与模组来源：

- Nuclear Throne Together: https://yellowafterlife.itch.io/nuclear-throne-together
- NTTE: https://github.com/Yokinman/NTTE
- Uncharted Frontier: https://wigglercola.itch.io/uncharted-frontier
- Undergrowth: https://attfooy.itch.io/undergrowth
- Details+: https://wigglercola.itch.io/detailsplus

SHA256 (full package bytes):

`6f90956c1d11199fe5d32e84a359b4cd5fedf25d70494e70ac9bb2ff9e54802b`  NuclearThrone.NTTE-NTUF-Android-2.1.3.apk (305814634 bytes)

`4c05c0713ff05e50af97415ee6239a80e1e83c85aae7e5c9003b90116d4581d1`  NuclearThrone.NTTE-NTUF-iOS-2.1.3.ipa (213118882 bytes)

The same SHA256SUMS-NTTE-NTUF-2.1.3.txt is distributed in the MEGA folder.
