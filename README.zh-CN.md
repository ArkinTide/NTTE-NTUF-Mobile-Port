# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

NTTE 与 **Uncharted Frontier（NTUF）1.0.3.3** 的 Android／iOS 移植源码，
保留 Undergrowth、Details+ 和简体中文。当前版本 **2.1.0**，内部构建 **105**。

从 [MEGA 下载文件夹](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) 获取 APK／IPA，并核对同目录的
`SHA256SUMS-NTTE-NTUF-2.1.0.txt`。GitHub 仅分发文本源码及版本说明；
iOS 安装包需要重新签名。见 [2.1.0 说明](docs/RELEASE-2.1.0.md)。

## 2.1.0 build105 — 内容开关、墙体与无人机修复

当前重新编译的最终 Windows VM／输入通过 28 项明确列出的原生专项，
另有 403 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](docs/validation/2.1.0-development-regression.json)。

修正侍从无人机对友军弹幕的碰撞并合并密集拦截特效；清理红水晶洞窟重复墙体、孤立顶端和道路边界；统一风暴王冠锁定轮廓颜色；甲虫解锁提示改为“打开秘密宝箱”。加入默认开启的 NTUF 与 Undergrowth 独立内容开关：NTUF 关闭时其余设置变灰，两项开关均仅允许在主菜单或选人界面操作，续局保留本局的内容状态。为 NTUF 蓄力武器加入蓄力条；控制台、练习及自定义局禁止解锁成就并在续局保留限制；天气音乐在触发当关接管区域音乐。 修正两个内容开关的实际点击响应；侍从无人机忽略玩家粉碎锤的飞行及落地火药；机器人完成网络空间后正常返回，并兼容修复前的续局。控制台局不再保存黄金武器或永久解锁，自定义模式的NTTE与NTUF进度按槽位独立保存。

Android versionCode 3000105，保留应用标识和签名，并核验 16KB 布局；
iOS build 105 需要重新签名。iOS 使用新编译游戏数据及保留的原生 Runner，
没有新的 Mac 原生编译。GAME_BUILD／存档协议仍为 3004。

本轮验证内容开关、蓄力条、成就排除、当关天气音乐、无人机碰撞及红水晶道路等明确场景。
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
