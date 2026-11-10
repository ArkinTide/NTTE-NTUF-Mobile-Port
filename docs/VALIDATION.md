# 验证记录

[简体中文](VALIDATION.md) | [English](VALIDATION.en.md) | [返回首页](../README.md)

## 2.1.1 build106 — 禁用内容兼容与海水、机器人界面修复

当前重新编译的最终 Windows VM／输入通过 34 项明确列出的原生专项，
另有 403 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](validation/2.1.1-development-regression.json)。

修正关闭NTUF后的旧自定义武器及融合武器菜单崩溃，按角色默认武器回退并保存各槽位；隐藏禁用的泡泡选人和统计图标，补齐Undergrowth生成入口。海水中的实体保持原生像素清晰度；优化内容查询和菜单同步。控制台局禁止NTTE/NTUF解锁通知，修正通知文字偶发黑色。机器人蓝屏YES/NO跟随实际镜头和宽屏位置。 自定义初始变异列表补齐高度计算，使用设置菜单滚动条，并保持滚动后的点击位置准确。

Android versionCode 3000106，保留应用标识和签名，并核验 16KB 布局；
iOS build 106 需要重新签名。iOS 使用新编译游戏数据及保留的原生 Runner，
没有新的 Mac 原生编译。GAME_BUILD／存档协议仍为 3004。

本轮验证禁用内容与九槽存档迁移、选人与统计过滤、海水像素、通知绘制、机器人蓝屏，以及自定义变异滚动条拖动与末行选择等明确场景。
未知随机地图与所有武器组合尚不能作整体保证。
后台静音桌面测试不能证明手机混音或帧率；未进行 Android／iOS 真机、
完整随机战役或所有设备帧率验收。

## 2.1.0 build105 — 内容开关、墙体与无人机修复

当前重新编译的最终 Windows VM／输入通过 28 项明确列出的原生专项，
另有 403 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](validation/2.1.0-development-regression.json)。

修正侍从无人机对友军弹幕的碰撞并合并密集拦截特效；清理红水晶洞窟重复墙体、孤立顶端和道路边界；统一风暴王冠锁定轮廓颜色；甲虫解锁提示改为“打开秘密宝箱”。加入默认开启的 NTUF 与 Undergrowth 独立内容开关：NTUF 关闭时其余设置变灰，两项开关均仅允许在主菜单或选人界面操作，续局保留本局的内容状态。为 NTUF 蓄力武器加入蓄力条；控制台、练习及自定义局禁止解锁成就并在续局保留限制；天气音乐在触发当关接管区域音乐。 修正两个内容开关的实际点击响应；侍从无人机忽略玩家粉碎锤的飞行及落地火药；机器人完成网络空间后正常返回，并兼容修复前的续局。控制台局不再保存黄金武器或永久解锁，自定义模式的NTTE与NTUF进度按槽位独立保存。

Android versionCode 3000105，保留应用标识和签名，并核验 16KB 布局；
iOS build 105 需要重新签名。iOS 使用新编译游戏数据及保留的原生 Runner，
没有新的 Mac 原生编译。GAME_BUILD／存档协议仍为 3004。

本轮验证内容开关、蓄力条、成就排除、当关天气音乐、无人机碰撞及红水晶道路等明确场景。
未知随机地图与所有武器组合尚不能作整体保证。
后台静音桌面测试不能证明手机混音或帧率；未进行 Android／iOS 真机、
完整随机战役或所有设备帧率验收。

## 2.0.5 build103 — 续局音效、轮廓设置、墙体及关卡出口修复

当前重新编译的最终 Windows VM／输入通过 82 项明确列出的原生专项，
另有 398 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](validation/2.0.5-development-regression.json)。

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

## 2.0.4 build102 — NTTE＋NTUF 2.0.4：变异池、通路、立绘与终极解密修订

当前重新编译的最终 Windows VM／输入通过 72 项明确列出的原生专项，
另有 362 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](validation/2.0.4-build102-development-regression.json)。

修复普通升级混入警局专属变异和迷你变异；保留专属获取途径及明确开启的增强变异入池选项。修复红水晶洞窟隐藏小路与实体墙交界碰撞。恢复泡泡初始武器的专用立绘并保留普通武器绘制回退；补齐首领入场立绘资源与路径别名，避免入场时缺失立绘资源报错。 修复首领立绘在真实暂停和中断重开时的保留及恢复。阻止终极解密尚未完成时由清空敌人误生成普通出口，保留连续融合、奖励解锁和正常王冠出口。

Android versionCode 3000102，保留应用标识和签名，并核验 16KB 布局；
iOS build 102 需要重新签名。iOS 使用新编译游戏数据及保留的原生 Runner，
没有新的 Mac 原生编译。GAME_BUILD／存档协议仍为 3004。

持续菜单低频／爆音仍未解决。已验证城市幽灵附身被魅惑宿主、丛林墙上伏击怪
苏醒后不能落地这两种具体卡关场景；尚不能保证覆盖所有未知的隐形敌人情况。
后台静音桌面测试不能证明手机混音或帧率；未进行 Android／iOS 真机、
完整随机战役或所有设备帧率验收。

## 2.0.4 — NTTE＋NTUF 2.0.4：天气、墙体与输入修复

当前重新编译的最终 Windows VM／输入通过 67 项明确列出的原生专项，
另有 256 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](validation/2.0.4-development-regression.json)。

修复暴风雪右侧竖线、电环汉化、区域回调报错及实验室／警局暗门侧墙贴图。修复城市17敌方幽灵附身友军后无法受击，以及丛林墙上伏击怪苏醒时丢失落地控制的问题。便携传送器支持连续摇杆角度并保留短点按，改进手柄输入、Android设备分配和断连恢复。减少模块查询和侍从无人机密集拦截的重复处理，合并重叠闪光与音效请求，保留逐颗敌弹销毁、原生回调和随机序列。修复机器人蓝屏复活前普通死亡界面抢先出现，以及60帧短点按被重复触摸采样清掉的问题，保留YES的真实网络空间传送和NO的普通死亡流程。选人导航和设置页核对当前本地输入所有权，修复触摸摇杆消失后残留方向输入导致的自动切换。

Android versionCode 3000100，保留应用标识和签名，并核验 16KB 布局；
iOS build 100 需要重新签名。iOS 使用新编译游戏数据及保留的原生 Runner，
没有新的 Mac 原生编译。GAME_BUILD／存档协议仍为 3004。

持续菜单低频／爆音仍未解决。已验证城市幽灵附身被魅惑宿主、丛林墙上伏击怪
苏醒后不能落地这两种具体卡关场景；尚不能保证覆盖所有未知的隐形敌人情况。
后台静音桌面测试不能证明手机混音或帧率；未进行 Android／iOS 真机、
完整随机战役或所有设备帧率验收。

## 2.0.3 — 武器、区域与原生交互修复

当前重新编译的最终 Windows VM／输入通过 43 项明确列出的原生专项，
另有 153 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](validation/2.0.3-development-regression.json)。

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

## 2.0.2 — 天气、移动陷阱和 NTUF 界面修复

当前重新编译的最终 Windows VM／输入通过 32 项明确列出的原生专项，
另有 118 项 Python 检查日志经哈希核验。旧 VM 的通过数不计入本次验收。
具体场景和结果见[本次验证摘要](validation/2.0.2-development-regression.json)。

本轮修复极光读取背景色报错、天气兼容开销、风暴王冠锁定图标、宫殿移动陷阱、
Bubbles 无效存档起始武器、墙上大苍蝇落地、统计／鸣谢布局、自定义 NTUF 武器分类和 goto 区域名称。

Android versionCode 3000098，保留应用标识和签名，并核验 16KB 布局；
iOS build 98 需要重新签名。iOS 使用新编译游戏数据及保留的原生 Runner，
没有新的 Mac 原生编译。GAME_BUILD／存档协议仍为 3004。

持续低频／爆音仍未归因。后台静音桌面测试不能证明手机混音或帧率；
未进行 Android／iOS 真机、完整随机战役或所有设备帧率验收。

## 2.0.1 — 生命周期、Bubbles 与武器存档修复

新编译的 2.0.1 最终 VM／输入通过 14 项明确列出的原生专项，另有 112 项
Python 检查日志经哈希核验。此前 VM 的 20 项测试保留为历史证据，不计入本次
最终 VM 的通过数。Python 收据保留日志和数量，没有历史源码快照绑定。

Bubbles A／B 在 30／60 帧下分别完成真实新游戏及实际死亡后的 Retry，共 8 轮，
每轮桌面攻击、触摸轻点、按住松开均经真实 Slash 造成伤害，共 24 次；60 帧覆盖
两个逻辑帧相位。Retry 创建新的玩家并保留同一个内容注册表。还检查原初箱子实际
存盘／新局取出／开火、损坏引用链、控制台、重试和菜单清理、天气、局长椅子、
同队弹幕、续关及凶恶面容。完整 Event 天气流程的更早结果属于历史 VM。

Android／iOS 包的版本、应用标识、输入和结构经过核验。Android versionCode
3000097，保留签名并核验 16KB 对齐；iOS build 97，需要重新签名。iOS 使用新编译
游戏数据及保留的原生 Runner，没有新的 Mac 原生编译。GAME_BUILD 3004 保持。

持续低频／爆音问题仍未归因；静音桌面声音所有权检查没有证明手机实际混音正常。
未进行 Android／iOS 真机、完整随机战役或所有设备帧率验收。桌面性能诊断不能
证明手机帧率。见[本次验证摘要](validation/2.0.1-development-regression.json)和
[源码基线](SOURCE_BASELINE.json)。

## 2.0.0 — NTTE + Uncharted Frontier

同一最终 Windows VM／输入通过 88 项回归和 94 项 Python 检查，覆盖 30／60 帧、
四次 Bubbles 真实新游戏、12 次实际换枪／拾回、天气和交互、墙体与隐藏房间、
Wormhole 的 NTTE 弹丸伤害归属、存档续关与绘制。来源、VM、输入和最终移动安装包
的摘要见 [验证摘要](validation/2.0.0-development-regression.json) 和
[源码基线](SOURCE_BASELINE.json)。

2.0.0 是平台版本元数据正规化，游戏内角落保留简写 2.0。上述 88 项选定回归
与 94 项 Python 检查来自完全相同的已验证 VM；逐成员同源证明确认素材、VM 和
原生库未改变。没有宣称新 VM 重跑或所有保留的历史测试均通过。

修复了墙边武器被推远的已确认路径；未复现通用的武器删除。Bubbles 截图只包含
世界画面，GUI 证据来自实际绘制回调。未进行 Android／iOS 真机、完整随机战役或
所有设备 60 帧验收。性能记录是桌面诊断，不能据此承诺手机帧率。

APK／IPA 的版本、标识、结构及编译输入经过核验。Android 保留签名与 16KB 对齐，
versionCode 3000096；iOS build 96，需重签。iOS 使用新编译的游戏数据和保留的
原生 Runner，没有进行新的 Mac 原生编译。GAME_BUILD 3004 保持。

## 1.2.7

62 项最终 Windows VM 回归在 30／60 帧模式通过，156 个真实 Draw 画面对照和 31 项 Android 更新器 Java 本地检查通过。覆盖 Lab/HQ 延迟暗室规划、门与清场流程、实体墙交互、静态对象更新、海滩涉水区域合成与回退，以及此前融合武器、红水晶通道和藤蔓回归。一个涉水实体的诊断用例中复制像素减少约 92%，该数字不是总耗时或手机帧率提升。

测试使用隔离存档、未切换显示的私有桌面和进程静音。安装包版本、标识、结构、更新器和编译修复代码保留已核验；Android 保留原证书与 16KB 对齐。Android versionCode 3000095、iOS build 95，GAME_BUILD 3004 保持。未进行手机真机或完整随机战役验收，不能据此承诺具体手机帧率；iOS 使用新编译 VM 和保留的 runner，需重签，并非新 Mac 原生编译。

## 1.2.6

45项选定的最终Windows VM回归在30／60帧通过，31项Android更新器Java本地检查通过。覆盖真实PlayerFiring、18类继承效果、终极弩和弹射武器的原生碰撞、黏附跟随／脱离、枪枪双向融合、复制和延迟发射、红水晶通道遮罩、22类地形检查、局部破墙／脚本开路、远距离房间补墙及藤蔓交互。全部77个原版专用融合回调和44项效果更新入口有源码清单；并未穷举所有武器组合。

测试使用隔离存档、未切换显示的私有桌面和进程静音。安装包核验版本、标识、结构及编译修复代码保留；Android保持原证书和16KB对齐。Android versionCode3000094、iOS build94，GAME_BUILD3004保持。未进行手机真机或完整战役验收；iOS使用新编译VM与保留runner，需重签，并非新Mac原生编译。

## 1.2.5

19 项选定 Windows VM 回归在最终 1.2.5 / 内部 93 冻结构建的 30/60 帧下通过，另有 31 项 Android 更新器 Java 本地检查。覆盖未激活及已激活的警车预备对象、最后敌人准确一分钟和 Boss 保护、真实尸体传送门、大蝙蝠变形与可选特效、玩家及敌人六种下沉状态的原/新绘制像素对照、完整海面合成和原涉水运动/RNG 对照。绘制最大通道差为 1；24 个涉水实体的桌面耗时单独记录，不代表 Android 真机帧率。

音效触发、随机数和无效句柄保护经过静音检查；未进行手机扬声器实听。两端安装包检查版本、标识、结构及编译修复代码保留；Android 保持原签名和 16 KB 对齐。Android versionCode 3000093、iOS build93，GAME_BUILD 3004 保持。没有手机真机、完整战役或新 Mac 原生编译验收；iOS 使用新 VM 数据和保留 runner，需重签安装。

## 1.2.4

24 项选定 Windows VM 回归在最终 1.2.4 / 内部 92 冻结构建的 30/60 帧下通过。覆盖实际 HUD 与触屏提示像素对照、连续破墙和墙顶重排中断、入口生命值与旧续关、普通洞窟巢穴释放和收养、实际传送进入诅咒洞窟自动转化、JSON 续关及再次传送后保留形态，以及隐藏区域地形、墙上物件、宠物跨关、最后敌人传送门与语言和更新设置。

Android 更新器通过 31 项 Java 本地检查。两端安装包通过版本、包标识、结构及本轮编译代码保留检查；Android 保留原签名并通过 16 KB 对齐检查。Android versionCode 3000092，iOS build92，GAME_BUILD 3004 保持。未进行手机真机、完整战役或新 Mac 原生编译验收；iOS 使用新 VM 数据和保留 runner，需重签安装。

## 1.2.3

21 项选定 Windows VM 回归在最终 1.2.3 / 内部 91 冻结构建的 30/60 帧下通过。覆盖新区域真实生成、化石加农炮和宠物战斗、三个地图种子的循环前后组合、清场出口与最后敌对死亡坐标、水晶蜘蛛真实破墙释放和两次跨关、Lair 小猫移动与阴影像素，以及丛林、原超时规则、传送门界面防护、语言保存和版本更新。

Android 更新器通过 31 项 Java 本地检查。两端安装包通过版本、包标识、结构和本轮修复编译代码保留检查；Android 保留原签名并通过 16 KB 对齐检查。Android versionCode 3000091，iOS build91，GAME_BUILD 3004 保持。未进行手机真机、完整战役或新 Mac 原生编译验收；iOS 使用新 VM 数据和保留 runner，需重签安装。

## 1.2.2

32 项选定 Windows VM 回归在最终 1.2.2 / 内部 90 冻结构建的 30/60 帧下通过。覆盖藤蔓武器箱、3-3 入口清场守卫、马陆自然退场、丛林刺客、尸体倒计时、真实 Undergrowth 连续路线，以及水晶蜘蛛真实墙体生成、破墙出现、拾取、JSON 续关和两次真实传送门跨关。还复查了更新器、语言持久化、Details+、黄金武器保存、治疗/爆炸及披萨生成路径。

Android 更新器通过 31 项 Java 检查；APK/IPA 通过版本、包标识、编译函数和结构校验，Android 保留原签名并通过 16 KB 对齐检查。GAME_BUILD 3004 保持。未进行手机真机、完整战役或新 Mac 原生编译验收；iOS 使用新 VM 数据和保留 runner，需自行重签。

## 1.2.1

15 项选定 Windows VM 回归在实际 30/60 帧通过。覆盖猪笼草真实治疗/爆炸与特效生命周期，三种 NTTE 黄金武器的真实写盘重载，Details+ 批次和独立回退相对于原生精灵绘制的严格像素一致性，以及真实核弹和独立原版破墙实现的几何/RNG对照。披萨测试覆盖晚生成墙、不可见墙、中立老鼠转换和16组真实生成；猫井盖测试覆盖地图外/晚生成墙和真实披萨至巢穴入口生成（两档各19个井盖）。

最终构建另覆盖固定 MEGA 下载页解析、提示及确认/取消流程。更早的内部构建87另有37项30/60回归记录，不能混作最终构建结果。

Android 更新器通过 31 项 Java 检查。两平台安装包通过版本、签名、结构及编译函数保留审核；内部构建序号89。电脑计时显示相关 CPU 开销下降，不代表手机实测帧数。未进行手机真机验收、完整战役或新 Mac 原生重建。iOS 使用新VM数据和保留runner，需重新签名。

## 1.2.0

26 项选定 Windows VM 测试在 30/60 帧通过。Details+ 覆盖原生视频开关、普通及练习/控制台模式的真实写盘重载、开关后的贴图恢复、重复应用的数量上限、地板/焦痕对应、六区域雕像销毁/尸体生命周期、几何数量与游戏随机种子保留，以及开启/关闭的离屏绘制截图。40 张精灵的 76 帧逐像素核对了源图、分帧、尺寸和原点。

回归还包括实际关卡地形、自然王冠雕像入口、Undergrowth 新内容与路线、披萨阴影、菜单、融合武器、更新器和最后敌人规则。Android 更新器通过 31 项 Java 检查。安装包通过冻结源码绑定、版本、签名、结构及 Details+/Undergrowth 编译函数保留审核。Android versionCode 3000085，iOS CFBundleVersion 85。

未进行手机真机验收、新 Mac 原生构建或完整战役验收。iOS 使用新编译 VM 数据与保留 runner，安装前需重新签名。[下载](https://github.com/ArkinTide/NTTE-Mobile-Port/releases/tag/1.2.0)。


## 1.1.0

21 项选定 Windows VM 测试在 30/60 帧通过，包括新增实体/武器/地形、双向融合、原生碰撞及销毁回调、1.0.x 续关编号迁移、自然 3-3 入口→新区域→丛林路线、10 秒战斗观察、先开箱关闭入口和 Last Wish 返还。保留披萨阴影像素回归、菜单汉化、掉落池、更新器与相关续关验证。

Android 下载器通过 31 项 Java 检查。两端安装包经过源码冻结绑定、版本/签名/结构及编译函数保留审核。Android versionCode 3000083，iOS CFBundleVersion 83。

未完成手机真机验收或新 Mac 原生构建；测试不代表完整战役验收。iOS 使用新编译 VM 数据及保留的原生 runner，安装前需重新签名。[下载](https://github.com/ArkinTide/NTTE-Mobile-Port/releases/tag/1.1.0)。


## 1.0.4

9 项选定 Windows VM 测试在 30/60 帧通过：`PizzaShadow104Tests`, `PizzaShadow104NaturalTests`, `PizzaShadow78Tests`, `OptionalShadowNativeTests`, `IOSShadowPresentTests`, `TopShadowNativeDrawTests`, `SewerPizzaNaturalEntryTests`, `UpdateCheckTests`, `UpdateStartupMenuTests`。

新增像素回归覆盖六种完整地板、炸开地面、墙角和无地板情况。使用未裁剪的原始阴影作为负对照，逐像素确认墙外无阴影、地板上的阴影保留，并比较角色阴影完全一致。三个真实披萨关卡种子在两档帧率下检查完整阴影表面，并调用原生墙侧面、墙顶绘制链路检查无报错。另验证 iOS 阴影兼容路径、正常可选阴影、墙顶阴影，以及真实下水道进入披萨关卡和更新提示。

共享修复已同步 Android。Android 原生下载策略通过 31 项 Java 检查；两平台包经编译函数保留、版本、结构和签名审核。Android versionCode 3000081，iOS CFBundleVersion 81；游戏版本为 1.0.4。

未进行手机真机验收或新的 Mac 原生编译。iOS 使用新编译的 VM 数据和保留运行库，安装前需要重新签名。[下载](https://github.com/ArkinTide/NTTE-Mobile-Port/releases/tag/1.0.4)。


## 1.0.3

19项选定Windows VM回归在30/60帧通过：`CatWarning78Tests`, `GatorStatueNativeTests`, `SecretWeapon78Tests`, `PizzaSpawn78Tests`, `PizzaShadow78Tests`, `MergedChinese78Tests`, `PizzaPropHurt78Tests`, `QuestDrop78Tests`, `RoadmapLoop78Tests`, `RoadmapNativeTests`, `RoadmapPlayerIconsTests`, `ChestDropNativeTests`, `InitialChestsNativeTests`, `BeetleMenuTests`, `Followup69PresentationNativeTests`, `OptionalShadowNativeTests`, `UpdateCheckTests`, `UpdateStartupMenuTests`, `SewerPizzaNaturalEntryTests`。

测试覆盖真实预警线/阴影/融合名称绘制像素、字形范围、雕像赐福回调、原生箱子与拾取碰撞顺序、箱子预览回滚、16个真实披萨关卡生成、家具受击动画、秘密组件掉落排除和循环1/2路线图。实际Sewer→Pizza流程通过原生开火、爆炸、传送门碰撞、房间重启及目标关卡绘制。原测试只沿一条直线寻找发射位置，在修复前后均会于60帧拒绝同一种子；本次仅扩大测试的自然发射角度搜索，未改变游戏地形或放宽进入目标的断言，原失败记录保留。

正式版本比较及启动提示经实际VM流程检查；原生Android下载策略重新通过31项Java检查，涵盖版本/地址校验及流式哈希、截断、损坏、取消。Android共享源码已同步。最终安装包通过编译函数保留、版本、签名和结构审核；Android签名身份保留并验证16KB ZIP对齐。iOS使用新编译VM数据和已验证保留运行库，需重新签名。

安装包：[1.0.3发布页](https://github.com/ArkinTide/NTTE-Mobile-Port/releases/tag/1.0.3)。未进行Android/iPhone真机验收、全新Mac原生编译或完整MOD全流程验收。


## 1.0.2（candidate77）

14 项选定 Windows VM 测试在 30/60 帧通过：`UpdateStartupMenuTests`, `UpdateCheckTests`, `SealKingMusicTests`, `PitSquidMusicPhaseTests`, `MusicBossRoutingTests`, `GoldenLoadoutDisplayTests`, `WeaponLoadoutNativeTests`, `LanguagePreferencePersistenceTests`, `PortalSelectionTransitionTests`, `RoadmapPlayerIconsTests`, `ParrotPerchShadowTests`, `DummyAmbushMusicTests`, `WorldEventsDummyWorldTests`, `BossClassificationNativeTests`。

更新提示、两项 Boss 音乐及黄金武器预览均在修复前复现失败。音乐测试启用真实音频，运行海豹王的 phase5 回调、幽灵蛸的清场 Step、首次浮出决策、完成浮出 Step 及 MusCont.Alarm2，检查实际播放句柄和重复请求不重启；黄金武器测试逐像素对照真实收起菜单的绘制，覆盖三个 NTTE 黄金模块和黄金融合武器。另复查语言持久化、变异选择及存储武器的原有回归。新增路线图真实绘制与默认图标像素对照、鹦鹉停靠大海螺的双皮肤像素对照、稻草人偏移及缺少生成墙的失败重试音频测试，并运行实际生成关卡中的完整稻草人召唤与死亡流程和 Boss 分类回归。用户已澄清没有大匪实际死亡，仅误播音乐；观察测试早期发现的 5 点扣血来自未隔离的宠物攻击，未作为 bug 复现。

两平台最终编译函数、元数据和安装包检查通过。Android 保留签名身份并验证 16 KB ZIP 对齐；未改动的原生更新策略沿用同源码哈希下 20 项通过记录。iOS 使用新 VM 导出及已验证的保留运行库封装，需要重新签名。

安装包见 [1.0.2 发布页](https://github.com/ArkinTide/NTTE-Mobile-Port/releases/tag/candidate77)。未进行 Android/iPhone 真机验收、全新 Mac 原生编译或完整 MOD 全流程验收。

## 1.0.1（candidate76）

8 项选定的 Windows VM 测试均在 30/60 帧通过：`PortalSelectionTransitionTests`, `LanguagePreferencePersistenceTests`, `LastEnemyHiddenTimeoutTests`, `LastEnemyTimeoutNativeTests`, `WorldCompletionNativeTests`, `UpdateCheckTests`, `MenuReminderPersistenceNativeTests`, `MenuNativeTests`。

新增回归在修复前均复现失败。传送门测试运行真实变异选择控制器、连续两次原生选择及下一关生成，并检查已排队的尸体回调、暂停/结束/生成阶段和正常空场传送门。语言测试点击真实语言菜单，在普通和练习模式保存分支检查即时磁盘写入、独立存档重新读取及语言表重建；无关进度值保持不变。

完整菜单图像回归首次超过 120 秒时限；同一构建单独复查，在 360 秒时限内完成两档并通过。首次超时记录保留。

两平台最终安装包逐函数核对通过。Android APK 签名、16 KB ZIP 对齐、版本与更新安装入口检查通过；更新策略 Java 源码未变，沿用同一源码哈希下的 20 项通过记录。iOS VM 导出、保留运行库兼容性及 Payload/版本检查通过。

安装包见 [1.0.1 发布页](https://github.com/ArkinTide/NTTE-Mobile-Port/releases/tag/candidate76)。本轮未进行 Android/iPhone 真机验收、全新 Mac 原生编译或完整 MOD 全流程验收。

## 1.0.0（candidate75）

9 项选定的 Windows VM 测试均在 30/60 帧通过：`CrystalWaterLightningTests`、`RavenLiftTargetTests`、`BubbleMergeColdStartTests`、`LastEnemyHiddenTimeoutTests`、`LastEnemyTimeoutNativeTests`、`UpdateCheckTests`、`MergedLightningUnitTests`、`BubbleWeaponTests`、`MenuNativeTests`。

沙漠/丛林测试覆盖实际飞行乌鸦、潜伏刺客、零血量残留、完整一分钟阈值、暂停、正常死亡/掉落/尸体回调，以及无友军、无尸体空场的原生传送门重试。Boss 和通用生成过渡不清除；没有基于墙体位置的清除机制。闪电测试覆盖绿洲/海沟水晶待机与攻击闪电的原生事件及子段，同时检查普通武器导电保留。

Android 原生更新策略 20 项检查通过；最终 APK 签名、16 KB ZIP 对齐、更新安装入口、版本与包名均已核对。iOS VM 导出、保留运行库注册兼容性、Payload 及版本检查通过。本轮改动的编译代码与两平台最终安装包逐函数比对通过。

安装包见 [1.0.0 发布页](https://github.com/ArkinTide/NTTE-Mobile-Port/releases/tag/candidate75)。这些是针对性自动回归，尚无本轮 Android/iPhone 真机验收，也未进行全新 Mac 原生编译或完整 MOD 全流程验收。

## candidate74：更新功能

- `UpdateCheckTests`、`MenuNativeTests`、`MenuReminderPersistenceNativeTests` 在 Windows VM 30/60 帧下通过。
- Android 原生更新模块编译通过；20 项 Java 策略测试覆盖流式下载、长度与 SHA-256 校验、文件损坏、取消及 URL/重定向规则。
- 更新模块 84 个汉字均在现有正文字体中。iOS VM 导出和保留运行库的函数注册兼容性检查通过。
- 本轮没有 Android/iPhone 真机下载或覆盖安装实测，也未进行全新 Mac 原生构建；系统安装授权和侧载签名仍需设备端操作。

candidate74 APK、IPA 和 SHA-256 校验文件见 [发布页](https://github.com/ArkinTide/NTTE-Mobile-Port/releases/tag/candidate74)。最终包中的更新逻辑与编译输出已逐函数核对；Android 安装权限、受限 FileProvider 路径、签名和 16 KB ZIP 对齐检查通过。

## candidate73：之前的修复基线

candidate73 的下列 10 项 Windows VM 回归均在 30/60 帧通过：

- `CrystalWaveAccuracyNativeTests`
- `LastEnemyTimeoutNativeTests`
- `ActorFireTests`
- `ActorMountTests`
- `CrystalCloneNativeTests`
- `ActorBirthCaptureNativeTests`
- `BossClassificationNativeTests`
- `GroundEnemyNoKillNativeTests`
- `WorldKillEnemiesTests`
- `TrenchCompletionPreventNativeTests`

修复了水晶友军延迟弹幕缺少 accuracy 属性的报错；同一只非 Boss 连续作为最后一只敌人超过 60 秒后设为零血量并走正常死亡流程。暂停不计时，出现其他敌人、目标变化/变友方及换关会重置。

Android 共用源码和 iOS VM 导出已核对。两种安装包已通过资源/结构和对应签名兼容性检查。本轮尚未进行手机实测、全新 Mac 原生构建或完整 MOD 全流程验收。

历史 candidate73 APK、IPA 及 SHA-256 校验文件通过 [GitHub Releases](https://github.com/ArkinTide/NTTE-Mobile-Port/releases/tag/candidate73) 提供。上传前已核对它们与 candidate73 交付记录的哈希一致。Git 源码目录不包含个人日志和构建产物。
