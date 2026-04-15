[app]
# 应用名称（显示在桌面）
title = 西继迅达EEPROM工具

# 包名（唯一标识符，只允许字母数字点）
package.name = xjeepromtool
package.domain = org.xjeeprom

# 主入口文件（不含.py）
source.main = xj_eeprom_android

# 版本
version = 1.0

# 源码目录
source.dir = .
source.include_exts = py

# 依赖的 Python 包
requirements = python3,kivy==2.3.0,plyer

# 屏幕方向（portrait=竖屏，landscape=横屏，all=两者均可）
orientation = portrait

# 支持的最低 Android 版本（API 21 = Android 5.0）
android.minapi = 21

# 目标 API（建议 33 = Android 13）
android.api = 33

# Android 权限
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# 架构（arm64-v8a 覆盖绝大多数现代手机；加 armeabi-v7a 兼容旧机型）
android.archs = arm64-v8a, armeabi-v7a

# 图标（可替换为你自己的图标文件，96x96 png）
# icon.filename = %(source.dir)s/icon.png

# 启动画面（可选）
# presplash.filename = %(source.dir)s/presplash.png

# 全屏模式（0=不全屏，1=全屏）
fullscreen = 0

# 日志级别（debug 模式下打印详细信息）
log_level = 2

[buildozer]
# Buildozer 工作目录
warn_on_root = 1
