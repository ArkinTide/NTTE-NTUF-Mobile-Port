# NTTE + NTUF 2.1.6 · build 111

- 修复自定义模式选泡泡开局后变成鱼的问题。泡泡会保留自己的初始武器和技能。
- 自定义模式开启「解锁角色」后，可以选择骷髅和青蛙。已解锁角色仍可按原规则使用。
- 调整触屏移动摇杆。小幅拖动能保持低速，转向响应更直接，另一根手指触屏时不会重新定位正在使用的移动摇杆。

- Bubbles now starts Custom games with the selected character, weapon, and ability.
- Custom mode's Unlock Characters option now includes Skeleton and Frog.
- Touch movement holds a steady low speed for small drags, responds sooner to turns, and keeps the movement stick anchored while another finger touches the screen.

The seven selected Windows VM tests include 30 and 60 FPS logic. A separate legacy Cyberspace prompt fixture failed on both 2.1.5 and 2.1.6 because it taps the button's position before layout. No physical Android or iOS device was tested. The 2.1.5 report about additional characters failing to unlock items was not reproduced and remains unresolved.

Android retains the original application identity and certificate, uses versionCode 3000111, and passed the 16KB alignment check. iOS build 111 requires re-signing. The save protocol remains 3004.

The APK, IPA, and checksum file passed complete MEGA readback verification. [Download from MEGA](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA)

- Android APK, 305941977 bytes. SHA256 `147d8761f90a8e5a81da84887db592ee9b64b94244a6573bf112d9b81d46846d`
- iOS IPA, 213158710 bytes. SHA256 `47972e64598d849429927b4870cf2a73058c01cb93de343a640cdc2d5e7a18e2`

Checksum file `SHA256SUMS-NTTE-NTUF-2.1.6.txt`.
