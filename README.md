# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

NTTE 与 **Uncharted Frontier（NTUF）1.0.3.3** 的 Android／iOS 移植源码，
保留 Undergrowth、Details+ 和简体中文。当前版本 **2.0.5**，内部构建 **103**。

从 [MEGA 下载文件夹](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) 获取 APK／IPA，并核对同目录的
`SHA256SUMS-NTTE-NTUF-2.0.5.txt`。GitHub 仅分发文本源码及版本说明；
iOS 安装包需要重新签名。见 [2.0.5 说明](docs/RELEASE-2.0.5.md)。

## 2.0.5 build103 — 续局音效、轮廓设置、墙体及关卡出口修复

当前重新编译的最终 Windows VM／输入通过 82 项明确列出的原生专项，
另有 398 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](docs/validation/2.0.5-development-regression.json)。

- 处理续局持续激光声、泡泡 B 皮肤提示框和风暴王冠轮廓。
- 视频设置增加角色／宠物轮廓和颜色；本地血条随颜色更新。
- 泡泡偏好模式改由攻击操作发射技能泡泡。
- 处理墙体顶层／空隙、王冠密室清关出口、巢穴入口返程卡墙和海盗隐形无敌实体。
- 补齐食肉酶实际死亡计数，保留原技能十三杀恢复一点生命并防止重复计数。
- 同一 VM 的 82 项原生回归和 398 项 Python 检查通过；验证范围限于所列专项，Hardmode 未改动。

Android versionCode 3000103，保留应用标识和签名，并核验 16KB 布局；
iOS build 103 需要重新签名。iOS 使用新编译游戏数据及保留的原生 Runner，
没有新的 Mac 原生编译。GAME_BUILD／存档协议仍为 3004。

本轮只对明确列出的续局激光声及海盗实体生命周期场景作验收。
其他菜单混音和未知隐形敌人场景尚不能作整体保证。
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
