# NTTE＋Uncharted Frontier 2.0.3 — READY

本说明已按最终统一 VM 的回归结果定稿，仅描述 NTTE＋NTUF 移植版的本轮修改，
不涉及 Hardmode 或 Steam 模组。安装包独立核验与发布回读另行记录；
本说明本身不是安装包、上传或发布完成的回执，也没有包哈希或新提交号。

## 修改内容

- 修正区域球生成期间的背景初始化顺序，避免区域 setup 读取尚未创建的背景。
  清理本次区域球新增且远离真实墙边的墙顶装饰，保留实体墙、边缘过渡与旧地图，
  并修正旧实体墙处理误删新过渡贴图的冲突。
- 修正 NTUF 新增近战与 NTTE 化石锤的重复翻转、挥动所有权、参数传递和副手重装。
  恢复重建武器表后的 NTUF 元数据与范围，处理泡泡两种皮肤及随机选角的起始武器。
- 将泡泡技能条接入正常与暂停的原生生命条绘制，修正低血等状态下的位置，
  保护颜色与透明度；增加独立的技能切换偏好。统计页兼容默认数字及旧数组字段，
  不改写存档中的统计数据。
- 极光天气使用原生实例遍历，减少每源 tick 的重复分配和全图过滤。
  已有桌面场景可比较性能，但不能据此承诺手机整体减速或所有天气卡顿已经消除。
- 修正 NTUF 弹药增强对普通、诅咒及 NTTE 弹药包的数量处理，保留原始倍率、
  每名玩家的弹药上限与拾取加成，以及原生基准表更新后的加成。
- HYPERION 无人机和震波按子弹当前阵营拦截敌弹，避免消除友方弹幕，
  包括原本属于敌方、反弹后已归属友方的弹幕。
- 宫殿移动方块与玩家接触时使用来源推挤逻辑，保留移动墙代理，
  避免原生静态墙碰撞抢先处理该接触。独立场景覆盖接触、推挤、墙面和陷阱条件；
  不把显式夹压恢复对照当作自然游玩已经发生夹压伤害的证明。
- 描边着色移除对桌面雾效果的依赖，保留透明度及调用方绘制状态，
  覆盖宠物、羽毛魅惑等实际绘制调用路径。手机图形后端的实际输出仍待硬件验证。
- 单独降低重海豹旋转瞬态音效的增益，保留原音高调用与强弱比例。
  这项修改与持续菜单杂音的报告分别记录。
- 水晶分身复制墙顶或原生抛掷中的来源时，建立独立的 Top／PalankingToss 控制器与保存状态，
  保持来源的当前运动、竖直阶段和副本放置偏移，避免分身遗留悬空碰撞状态。
  原生落地与 Cleanup 各自恢复控制对象，保留 Top 闹钟恢复和 Toss 原落地伤害。
  30／60 Hz 的独立 Top 和 Toss 专项已通过，包含原生 Cleanup、Toss 自然定时落地、
  真实 Bullet1 精确 3 点伤害及 Guardian 15 点伤害。
  同一最终 VM 的 24 次自然 City 地图诊断与完整 43 套所选测试均已通过。

## 验收状态与限制

最终 Python 检查 **153 项通过**；最终原生回归选取 **43 套，全部通过**，
运行包装器退出码为 0。全部原生结果来自同一最终 VM，不继承已停用旧 VM 的通过数。
原生回归目录为 `tests/20261107T182528229074Z`，VM SHA256 为
`4bc772621c054e3f4a66003bac75f900d75ae99d8aeb8847359b33f5bb8c0545`，
输入 SHA256 为 `6849309290b02d96c9c558e730f4e56fb2bd159ba86f7915e9bb6c0160911d13`。
Python 证据为 `review/post202-python-regression-final7.json`，对应日志 SHA256 为
`42adb09b8be9b3d620f1fcc10a18837ef677f6c1af3a74c16822e31af0dcea96`。

持续菜单低频轰鸣／爆音仍未定位。重海豹音效增益调整不能证明菜单杂音已修复；
后台静音测试也不能替代手机实际混音输出或听感验收。
原隐身录屏中的具体目标尚未确认，水晶分身 Top／Toss 的窄修复不等于所有隐形敌人已修复。
没有进行 Android／iOS 真机、完整随机战役或所有设备帧率验收。

版本目标为 **2.0.3**，内部构建 **99**；Android versionCode **3000099**。
Android 继续保留应用身份和签名，GAME_BUILD／存档协议维持 **3004**。
iOS build **99** 需要重新签名，使用新游戏数据与保留的原生 Runner；
未进行新的 Mac 原生编译。以上平台信息仍需最终安装包核验确认。

安装包沿用[原 NTTE MEGA 文件夹](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA)。
GitHub 保留文本源码与说明；图片、音频、字体、商业 Runner 和预编译扩展须另行取得。

## English

These notes are finalized against the common-VM regression results and cover the
NTTE＋NTUF mobile port only. Independent package review and publication readback
are recorded separately; this is not a build, upload or publication receipt. It
contains no package hash or new commit ID.

Repairs cover area-orb background initialization and wall transitions; native
melee swing ownership and offhand reloads; restored NTUF weapon metadata and
Bubbles' starting weapon; ordinary/pause skill HUD and a separate skill-toggle
preference; and legacy/default statistics fields. Aurora traversal avoids repeated
allocation and full-map filtering while retaining the authored processing.

Further focused repairs preserve authored ammo-bag multipliers and per-player
bonuses; classify HYPERION drone/shock interception using current projectile team;
use Palace blocks' authored player-push behavior with their wall proxy; tint
outlines without desktop fog while preserving alpha/draw state; and lower only
Heavy Seal's spin transient gain while preserving source pitch and emphasis.

Crystal copies of wall-top or native PalankingToss sources own independent
controllers and restoration state, retaining current motion, vertical phase and
placed offsets. Native landing/Cleanup restores each body separately, preserving
Top alarm restoration and authored Toss landing damage. Focused Top and Toss
checks passed at 30/60 Hz, including native Cleanup, naturally scheduled Toss
landing, actual Bullet1 damage of 3 HP and Guardian damage of 15 HP. The final
common-VM 24-map City diagnostic and all 43 selected native cases passed.
The original invisibility recording's exact target remains unidentified, so this
narrow repair does not establish that all invisible enemies are fixed.

All 153 final Python checks and all 43 selected native cases passed; the native
run wrapper exited with code 0. All native results belong to the final VM and
input hashes listed above; no old-VM pass is inherited. The Python evidence and
its bound log hash are also recorded above.
Persistent low-frequency menu noise or clipping remains unlocated; Heavy Seal's
separate gain change does not establish a repair. Silent desktop tests do not
prove phone mixing or frame rates. No physical Android/iOS, complete random
campaign or universal FPS acceptance is claimed.

Target version is 2.0.3/internal 99, Android versionCode 3000099, retaining the
Android application/signing identity and GAME_BUILD/save protocol 3004. iOS build
99 requires re-signing and uses new game data with a retained native Runner,
without a fresh Mac native build. Final package checks must confirm these fields.
Installers retain the original NTTE MEGA route linked above; GitHub remains
text-source-only.

## 原作者与第三方鸣谢 / Credits

保留现有游戏内鸣谢、原作者文本、许可证及 `THIRD_PARTY_NOTICES.md`；
本移植不扩大原游戏或第三方素材的授权。Retain all existing in-game credits,
upstream text notices and licenses; no new blanket asset license is asserted.

- Nuclear Throne：Vlambeer 及原美术／音频作者。
- NuclearThrone-Recreated-Epsilon：kcd-shichen；保留上游 GPL-3.0 文本。
- Nuclear Throne Mobile／recreated public project：toncho_／toarch7 及贡献者。
- [NTTE / Territorial Expansion](https://github.com/Yokinman/NTTE)：原作者与贡献者。
- [Uncharted Frontier 1.0.3.3](https://wigglercola.itch.io/uncharted-frontier)：wigglercola 与贡献者。
- [Undergrowth v1.0.3](https://attfooy.itch.io/undergrowth)：matt／attfooy 与贡献者。
- [Details+ 1.1](https://wigglercola.itch.io/detailsplus)：wigglercola。
- Input／SNAP、原生光标扩展、SDL／控制器数据：保留各自随附的许可证与声明。
- GameMaker、SDK 与官方 Runner：遵循其各自条款，商业运行时源码不在文本仓库内。
- 移植汉化、界面、平台适配与维护：ArkinTide 及项目贡献者。

SHA256 (full package bytes):

`b09d7404d451f81a1fa0155b694c17290a1b58ea41ccc03aafddc4a003aa575e`  NuclearThrone.NTTE-NTUF-Android-2.0.3.apk (304757587 bytes)

`500ae550763281f59bd9fd1bb8efa9a31be10db24ee9eb0536dbf0afc05e491c`  NuclearThrone.NTTE-NTUF-iOS-2.0.3.ipa (212790138 bytes)

The same SHA256SUMS-NTTE-NTUF-2.0.3.txt is distributed in the MEGA folder.
