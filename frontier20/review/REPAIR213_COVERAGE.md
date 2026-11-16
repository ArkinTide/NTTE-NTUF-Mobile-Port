# NTTE＋NTUF 2.1.3 build108 修复覆盖

需求以 `release213-user-requirements.json` 为准。用户重复的第16项中，类行星融合近战记为17。本表区分确定性修复、流程复验和性能改进；并不把“32项通过”解释为所有随机情况都已测试。

最终运行：`tests/20261115T181411213666Z`。32个选定用例已在独立且未激活的静音Windows桌面全部PASS，退出码均为0且无提前终止；160项Python回归检查也通过（`review/post213-python-regression-final2.json`）。当前VM SHA256：`aca6686f040d0d1901e1c2bbaef194513e1d3e146dbe7d03c829beb1d52f24fa`；输入SHA256：`c7ca98ef98a02a4c599752185d55cac6282494653a337cfa8f22d1fdc87fd40a`，来自当前`build-windows/last-success.json`。历史测试名称表示复用源码实现并重新运行，不代表复用旧通过记录。

| 项目 | 实施与当前结果 | 直接证据／实际限制 |
| --- | --- | --- |
| 1 墓地区域struct.id报错 | 实例专属id读取前先区分数据struct与真实实例，保留真实交互提示代理分支。 | `FrontierCrash213Tests`：真实数据作用域分别创建普通对象、IceFlower和带伤害身份的弹体；真实提示实例仍创建代理。PASS。 |
| 2 海滩区域球封闭敌人 | 区域生成后对新增地块分量检查向海连通性，仅在本次新增墙／顶盖上开48px岸边入口，不移动旧房间。 | `FrontierWorld213Tests`：封闭海岛和敌人到岸边的碰撞射线、已有开口、旧墙保护及重复调用。PASS；不是所有随机种子的穷举。 |
| 3 自动降帧周期性卡顿 | 移除低负载确认前每5秒强制升回60的轮换；保持至少5秒并连续3秒CPU余量达标才首次恢复。恢复探测失败则本场景锁30，5秒连续稳定才接受恢复；真实新GenCont ID、菜单与关闭开关重置，暂停保留保护。 | `FrontierClock212Tests`、`FrontierClock212LiveTests`：持续负载不恢复、持续余量恢复，真实60→30→60与计时／运动一致；CPU轻／实际帧慢1800帧只恢复一次，真实GenCont身份、停用Player的暂停／quit_pause、菜单和关闭边界。PASS；未测手机调度抖动。 |
| 4 追踪弹目标失效报错 | 四个已审计追踪回调验证实际选中的实例，目标丢失后继续原飞行，保留有效目标转向。 | `FrontierCrash213Tests`：IDPD微型导弹真实factory和Step，零目标、有目标、最后目标销毁、发射者销毁。PASS；其余三个回调有补丁边界Python检查。 |
| 5 无预警闪退 | 修复可确认的data scope、失效追踪目标、失主无人机判定框销毁及稀疏设置分类路径。 | `FrontierCrash213Tests`、`FrontierCollision212Tests`、`FrontierLifecycleTests`。PASS；没有可支持“所有随机闪退已消除”的证据，也未做设备崩溃转储归因。 |
| 6 整体性能回退 | 减少原生Alarm无效槽位扫描和融合射线的全敌人扫描，稳定自动降帧恢复。没有用每帧全地图修复扫描替代事件逻辑。 | `FrontierPerformance213Tests`、两项Clock和`FrontierWeatherPerformanceTests`。PASS；CPU夹具结果并非全游戏设备帧率验收。 |
| 7 蛆虫被打后三倍分裂 | 飞行蛆虫落地操作单次消费，碰撞后销毁原弹体；已死亡蛆虫不再创建新的活蛆虫。 | `FrontierWorld213Tests`：真实Player／Wall碰撞、先死亡后碰撞、同队负对照及普通单次落地。PASS。 |
| 8 困难模式掉帧／慢动作 | 共享自动帧率、Alarm及碰撞改进也作用于NTTE＋NTUF内置困难模式，30／60运动与计时单位保持。 | 两项Clock、Performance及Lifecycle。PASS；没有独立高Loop困难模式整局或真机FPS验收，独立Hardmode产品未修改。 |
| 9 泡泡无法攻击 | 有效手动瞄准回到死区时保留最后方向，到真实松手才发出一次攻击；外拖取消与中央空点维持原规则。 | `FrontierBubbles213Tests`：技能开／关×两把初始武器×四类手势；`FrontierBubblesAttack212Tests`与Startup A／B：真实菜单开局、死亡重试、桌面／触摸及30／60。PASS。录像约2.8秒和7.0秒可见挥砍；本次确认修复死区松手路径，不能断言这是所有攻击间歇的唯一成因。 |
| 10 诅咒箱任务骨头 | 诅咒状态排除任务骨头候选，真实诅咒大箱自身状态优先；普通箱原有条件获取保留。 | `FrontierWorld213Tests`：单骨头候选负对照、普通合法候选、32次物理诅咒大箱选择。PASS。 |
| 11 重置设置报错 | 将稀疏分类数组、缺失／旧分类及无key行分层验证，只删除真实设置key，保留教程和进度。 | `FrontierCrash213Tests`：数组空洞、无效行、重复设置、重复重置、缺失集合与存档字段保护。PASS。 |
| 12 准心跟随颜色开关 | 颜色页面新增默认开启的开关，关闭统一白色；原生桌面cursor颜色变化会重建，软件／世界／触屏准心消费同一配置。 | `FrontierReticle213Tests`：默认开启、黑／白／RGB、关闭不改变血条颜色、真实菜单确认及GUI图。PASS；保存key已在正常及受限存档路径，测试不等同于手机重启实测。 |
| 13 终极解密钥匙合成 | 复验现有合成顺序、120tick合成等待、敌人／HeartBullet门禁、四部件交付、奖励与损坏骨头处理，未为复验虚构额外机制改动。 | `QuestLockedNativeTests`、`QuestFloorNativeTests`、`QuestTeleporterNativeTests`、`QuestHubNativeTests`，均在30／60真实对象流程PASS。 |
| 14 王冠密室解密地块消失 | 地块控制器绑定原坐标、外观／层级；FloorSet替换或地面消失后重绑定／恢复物理地块，保留传送配对和交互。 | `FrontierWorld213Tests`：真实配对传送地板和钥匙控制器被FloorSet替换／移除后的事件；四项Quest流程。PASS。 |
| 15 安卓新增地图变慢 | 已优化新增地图同样经过的共享Alarm、融合射线和帧率恢复CPU路径；原天气原生过滤与地图绘制专项重新运行。 | Performance、Clock、WeatherPerformance、VisualOptionsDraw和IOSRenderSurface。PASS；没有Android真机前后对比，不能确认所有新增地图的手机速度问题已根除。 |
| 16 60帧菜单闪烁 | 固定普通sprSpiral互补遮罩的源帧取样，IDPD等其他传送门仍按原帧动画。 | `FrontierPerformance213Tests`：实际GPU像素对照证明普通帧0／1输出一致、原遮罩确有差异、IDPD帧1保持原样。PASS。 |
| 17 类行星融合近战开火卡顿 | 每发射线先按保守扫掠框筛选候选，仍用原生精确mask碰撞、原步长与射程；小数坐标留1px余量，失效实例独立过滤。 | `FrontierPerformance213Tests`：正／负1和3倍缩放、24方向、小数原点／终点、stale ID，6336次精确碰撞对照及3项Alarm检查PASS。当前Performance213收据及JSON已完成：固定CPU夹具250项→2候选，8939μs→330μs；完整32项已在同一当前VM上通过；不是手机FPS。 |

性能计时从Begin Step至控制器GUI End，仅表示CPU处理余量，不覆盖GPU present。没有Android／iOS真机、全随机战役、所有武器组合、所有Loop或所有设备60帧保证。iOS绘制专项使用Windows上的兼容绘制路径，不是iOS硬件测试。未知闪退与手机慢动作问题仍需设备日志和实际游玩反馈进一步确认。

本文件只记录代码与当前原生专项覆盖，不证明安装包已经完成核验、上传或发布。交付还需当轮delivery、独立安装包审核及GitHub／MEGA完整回读证据。
