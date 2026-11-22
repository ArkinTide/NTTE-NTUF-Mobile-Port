# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

NTTE 与 **Uncharted Frontier（NTUF）1.0.3.3** 的 Android／iOS 移植源码，保留 Undergrowth、Details+ 和简体中文。当前版本 **2.1.5**，内部构建 **110**。

从 [MEGA 下载文件夹](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) 获取 APK／IPA，并核对 `SHA256SUMS-NTTE-NTUF-2.1.5.txt`。GitHub 分发文本源码及版本说明；iOS 包需要自行重新签名。见 [2.1.5 说明](docs/RELEASE-2.1.5.md)。

## 本次修复与已知问题

- 自定义模式的“解锁角色”现在也适用于甲虫、鹦鹉和泡泡；仍遵守内容开关和当前槽位的进度隔离。
- 修复熔化变成骷髅后，旧技能输入在同一帧触发血赌而立即死亡的问题。恢复原定的五个逻辑帧保护，结束后正常受伤。
- **尚待定位：新增角色无法解锁物品的报告未复现。** 三个角色的金武器、皇冠、皮肤写入、实际启动重读和配装选择均通过测试。此项没有标为已修复。

本次最终 Windows VM 的 10 项后台静音原生专项通过，包含 30／60 帧逻辑检查；另有 5 项封装脚本边界检查通过。控制台／练习模式的限制和自定义槽位隔离保留。未进行 Android／iOS 手机实测或完整随机战役验收。

Android versionCode 为 3000110，保留应用标识和原签名并核验 16KB 布局；iOS build 110 使用新编译游戏数据与保留的原生 Runner，需要重新签名。GAME_BUILD／存档协议保持 3004。

## 源码与构建

`project/` 是验收后的共用源码，`platforms/android/` 保存 Android 文本覆盖，
`frontier20/` 保存适配、离线依赖、汉化和原作者文本参考。图片、音频、字体、
图标、商业 Runner、预编译扩展和安装包不进入 Git，须另从作者或授权来源取得。
见[构建说明](docs/BUILDING.md)、[源码规则](docs/SOURCE_ONLY.md)和
[参考源码恢复](frontier20/SOURCE_REPRODUCTION.md)。

保留[许可证](LICENSE)和[第三方鸣谢](THIRD_PARTY_NOTICES.md)。本项目是非官方移植。
历史版本：[2.0.2](docs/RELEASE-2.0.2.md)、[2.0.0](docs/RELEASE-2.0.0.md)。
