# NTTE + NTUF 2.1.4 · build109

## 本轮八项

1. 复核本轮测试的17把 NTTE／NTUF 近战武器（10把 NTUF 和7把选定 NTTE 武器）及其融合前端的长臂加成，当前维护源与最终 Windows VM 未复现报告中的失效，不把原有加成公式描述为新增修复。普通骨镰刀经真实变异选择后，在目标间距为4像素的测试网格上，最远受伤目标的原始中心距离在30Hz为40→60像素、60Hz为44→60像素，重击均为56→80像素；这些数值描述所采样的靶心距离。切换形态、换武器及续局路径也通过本轮验证。

2. 修正豪宅黄金兑换站局部变量和转场螺旋预热问题；七张截图所涉的失效墙体引用、稀疏设置重置、已销毁追踪目标及自定义数据作用域创建实例的原有防护，也在当前最终 VM 中重新执行验证。

3. 手术变异的中文说明按实际字体高度换行并增加行距，标题与说明各自测量，避免中文文字叠在一起。

4. 机器人重启页面使用独立 GUI 相机绘制 YES／NO，并在原有选项出现时间之后恢复缺失按钮；确认选择后不重复创建或提交。

5. 优化高频弹幕家族的实体类型、数量与存在性查询，减少重复建立完整实体列表。差分测试检查旧实现的返回值、类型及非法输入行为；本轮不作手机帧率承诺。

6. 移除骨镰刀形态按钮右上角的额外白色箭头，保留武器图标、形态按钮及原有切换功能。

7. 对齐鹦鹉和泡泡角色偏好设置的图标、文字与开关列，给开关保留间距，并按可用宽度缩放长文本。

8. 触屏移动增加连续方向与小幅操作处理，检查原始触点输入、摇杆死区以及30／60Hz下相同时间的响应。

## Eight requests in this release

1. Reviewed Long Arms for the 17 tested NTTE/NTUF melee weapons (10 NTUF and 7 selected NTTE weapons), including front-melee fusion paths. The maintained source and final Windows VM did not reproduce the reported failure, so existing formulas are not presented as a new fix. After genuine mutation selection, a target grid spaced 4 pixels apart measured the distance to the original center of the farthest damaged target:40→60 pixels for light attacks at30Hz and44→60 at60Hz; heavy attacks measured56→80 at both rates. These values describe the sampled target centers. Form changes, weapon swaps and continuation also passed the current checks.

2. Corrected the mansion gold-station local index and transition-spiral warm-up. Existing guards for the seven screenshot paths involving stale walls, sparse settings reset, destroyed homing targets and instance creation from custom data scopes also ran again on the final current VM.

3. Measured Surgery text with the actual font and added line spacing, independently placing the title and description to prevent overlapping Chinese glyphs.

4. Drew Robot reboot YES/NO choices with an independent GUI camera and restored missing buttons after their authored appearance threshold, while preventing duplicate recreation or submission after a committed choice.

5. Optimized frequent projectile-family type, count and existence queries to avoid repeatedly assembling complete instance lists. Differential tests check legacy return values, types and invalid-input behavior; no phone frame-rate guarantee is made.

6. Removed the extra white arrow at the upper right of the Scythe form control, retaining its weapon icon, button and switching behavior.

7. Aligned the Parrot and Bubbles preference icon, label and switch columns, reserving space before each value and fitting long labels to the available width.

8. Refined continuous touch direction and fine movement, with checks for raw touch input, joystick deadzone and equal-time response at30/60Hz.

## Validation and downloads

The final Windows VM/input passed all 37 selected native cases in `tests/20261118T105514593253Z`. The current source-bound Python log records 190 passing tests. Earlier VM passes are not inherited. The final development review binds the exact VM and input hashes.

本轮最终 Windows VM／输入通过37项选定原生专项，当前源码绑定的 Python 日志记录190项检查通过；运行编号为 `20261118T105514593253Z`。长臂结论为本轮场景未复现失效，不把原有加成公式描述为新增修复。

These are silent background desktop checks. No physical Android/iOS, exhaustive campaign, phone save-migration or universal FPS acceptance is claimed. iOS requires re-signing and uses newly compiled game data with a retained native Runner; GAME_BUILD/save protocol remains3004. The separate Hardmode port and Steam mod are unchanged. Package, source and upload acceptance remain separate checks.

GitHub distributes text source and release notes. APK, IPA and SHA256 checksums use the existing NTTE destination:

https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA

Authors and sources: [NTTE](https://github.com/Yokinman/NTTE), [Uncharted Frontier1.0.3.3](https://wigglercola.itch.io/uncharted-frontier), [Undergrowth](https://attfooy.itch.io/undergrowth), [Details+](https://wigglercola.itch.io/detailsplus).

The full private project backup goes to the user-selected Quark folder. Local source retirement requires authenticated full download and restoration verification of that backup.

SHA256 (full package bytes):

`6872a214d6b516e7e7aa5a0b22881e7366b199171ed6a7b6cd0b2cea5b432fc9`  NuclearThrone.NTTE-NTUF-Android-2.1.4.apk (305916244 bytes)

`0fde5773761d2df019f4a700280f726c3873209b4f0c7d2337d2c73a4966613f`  NuclearThrone.NTTE-NTUF-iOS-2.1.4.ipa (213148460 bytes)

The same SHA256SUMS-NTTE-NTUF-2.1.4.txt is distributed in the MEGA folder.
