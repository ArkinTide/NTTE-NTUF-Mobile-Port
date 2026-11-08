# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

NTTE 与 **Uncharted Frontier（NTUF）1.0.3.3** 的 Android／iOS 移植源码，
保留 Undergrowth、Details+ 和简体中文。当前版本 **2.0.3**，内部构建 **99**。

从 [MEGA 下载文件夹](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) 获取 APK／IPA，并核对同目录的
`SHA256SUMS-NTTE-NTUF-2.0.3.txt`。GitHub 仅分发文本源码及版本说明；
iOS 安装包需要重新签名。见 [2.0.3 说明](docs/RELEASE-2.0.3.md)。

## 2.0.3 — 武器、区域与原生交互修复

当前重新编译的最终 Windows VM／输入通过 43 项明确列出的原生专项，
另有 153 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](docs/validation/2.0.3-development-regression.json)。

修复区域球生成时的背景初始化顺序、墙顶装饰与实体墙边缘过渡冲突，以及新增近战武器的挥动所有权和副手重装。恢复重建武器表后的 NTUF 元数据，修正泡泡起始武器、正常游玩与暂停时的技能条显示，增加独立的技能切换偏好，并保护新旧存档统计页的字段读取。极光天气改用原生实例遍历，减少重复分配与全图过滤；这项桌面优化不代表手机整体减速已经消除。

修正 NTUF 弹药增强对普通、诅咒及 NTTE 弹药包数量的处理，保留各自原始倍率及每名玩家的弹药加成。HYPERION 无人机与震波按子弹当前阵营拦截敌弹，保留友方和反弹后归属友方的子弹。宫殿移动方块的玩家接触沿用来源推挤逻辑，并保留移动墙代理；描边着色改为不依赖桌面雾效果的路径，同时保留透明度和调用方绘制状态。单独降低重海豹旋转瞬态音效的增益，保留原音高与强弱比例。

修复水晶分身复制墙顶或原生抛掷中的来源后遗留悬空状态的问题，使副本持有独立的 Top／PalankingToss 控制器与恢复状态，保持已有运动和竖直阶段，由原生落地／Cleanup 各自恢复碰撞、深度与影子，保留 Top 的闹钟恢复和 Toss 的原落地伤害。该修复针对已复现的分身生命周期；原隐身录屏的具体目标尚未确认，不能据此宣称全部隐形敌人问题已经修复。持续菜单低频杂音／爆音仍未定位，重海豹音效调整不构成该问题的修复。

最终 Python 检查 153 项通过；同一最终 VM 的 43 套所选原生回归全部通过，运行包装器退出码为 0，其中包含 24 次自然 City 地图及 30／60 Hz Top、Toss 专项。未进行 Android／iOS 真机、完整随机战役或所有设备帧率验收。

Android versionCode 3000099，保留应用标识和签名，并核验 16KB 布局；
iOS build 99 需要重新签名。iOS 使用新编译游戏数据及保留的原生 Runner，
没有新的 Mac 原生编译。GAME_BUILD／存档协议仍为 3004。

持续菜单低频／爆音仍未解决；隐形敌人问题未获证实修复。
后台静音桌面测试不能证明手机混音或帧率；未进行 Android／iOS 真机、
完整随机战役或所有设备帧率验收。

## 源码与构建

`project/` 是验收后的共用源码，`platforms/android/` 保存 Android 文本覆盖，
`frontier20/` 保存适配、离线依赖、汉化和原作者文本参考。图片、音频、字体、
图标、商业 Runner、预编译扩展和安装包不进入 Git，须另从作者或授权来源取得。
见[构建说明](docs/BUILDING.md)、[源码规则](docs/SOURCE_ONLY.md)和
[参考源码恢复](frontier20/SOURCE_REPRODUCTION.md)。

保留[许可证](LICENSE)和[第三方鸣谢](THIRD_PARTY_NOTICES.md)。本项目是非官方移植。
历史版本：[2.0.2](docs/RELEASE-2.0.2.md)、[2.0.0](docs/RELEASE-2.0.0.md)。
