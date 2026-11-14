# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

NTTE 与 **Uncharted Frontier（NTUF）1.0.3.3** 的 Android／iOS 移植源码，
保留 Undergrowth、Details+ 和简体中文。当前版本 **2.1.2**，内部构建 **107**。

从 [MEGA 下载文件夹](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) 获取 APK／IPA，并核对同目录的
`SHA256SUMS-NTTE-NTUF-2.1.2.txt`。GitHub 仅分发文本源码及版本说明；
iOS 安装包需要重新签名。见 [2.1.2 说明](docs/RELEASE-2.1.2.md)。

## 2.1.2 build107 — 红水晶通路、机器人与变异界面修复

当前重新编译的最终 Windows VM／输入通过 21 项明确列出的原生专项，
另有 157 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](docs/validation/2.1.2-development-regression.json)。

修正红水晶洞窟隐藏小路旁墙体堵住普通道路的问题；机器人重启YES/NO改在最终GUI层绘制并统一缩放后点击范围。修复近战碰墙时偶发崩溃，重新排版警局IDPD变异提示。视频设置新增默认开启的自动降帧开关，并保持切换帧率后的运动和计时单位一致。泡泡角色偏好改为按下技能后同时进行武器攻击和泡泡攻击。

Android versionCode 3000107，保留应用标识和签名，并核验 16KB 布局；
iOS build 107 需要重新签名。iOS 使用新编译游戏数据及保留的原生 Runner，
没有新的 Mac 原生编译。GAME_BUILD／存档协议仍为 3004。

本轮验证红水晶道路、机器人蓝屏可见按钮与触摸、近战碰墙、警局变异文字布局、自动帧率和泡泡双重攻击等明确场景。
未知随机地图与所有武器组合尚不能作整体保证。
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
