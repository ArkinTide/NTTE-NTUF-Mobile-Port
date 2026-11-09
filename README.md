# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

NTTE 与 **Uncharted Frontier（NTUF）1.0.3.3** 的 Android／iOS 移植源码，
保留 Undergrowth、Details+ 和简体中文。当前版本 **2.0.4**，内部构建 **102**。

从 [MEGA 下载文件夹](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) 获取 APK／IPA，并核对同目录的
`SHA256SUMS-NTTE-NTUF-2.0.4-build102.txt`。GitHub 仅分发文本源码及版本说明；
iOS 安装包需要重新签名。见 [2.0.4 说明](docs/RELEASE-2.0.4.md)。

## 2.0.4 build102 — NTTE＋NTUF 2.0.4：变异池、通路、立绘与终极解密修订

当前重新编译的最终 Windows VM／输入通过 72 项明确列出的原生专项，
另有 362 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](docs/validation/2.0.4-build102-development-regression.json)。

修复普通升级混入警局专属变异和迷你变异；保留专属获取途径及明确开启的增强变异入池选项。修复红水晶洞窟隐藏小路与实体墙交界碰撞。恢复泡泡初始武器的专用立绘并保留普通武器绘制回退；补齐首领入场立绘资源与路径别名，避免入场时缺失立绘资源报错。 修复首领立绘在真实暂停和中断重开时的保留及恢复。阻止终极解密尚未完成时由清空敌人误生成普通出口，保留连续融合、奖励解锁和正常王冠出口。

Android versionCode 3000102，保留应用标识和签名，并核验 16KB 布局；
iOS build 102 需要重新签名。iOS 使用新编译游戏数据及保留的原生 Runner，
没有新的 Mac 原生编译。GAME_BUILD／存档协议仍为 3004。

持续菜单低频／爆音仍未解决。已验证城市幽灵附身被魅惑宿主、丛林墙上伏击怪
苏醒后不能落地这两种具体卡关场景；尚不能保证覆盖所有未知的隐形敌人情况。
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
