[app]
title = 西继迅达EEPROM工具
package.name = xjeepromtool
package.domain = org.xjeeprom
source.main = main
version = 1.0
source.dir = .
source.include_exts = py,ttc

# 依赖：kivy + plyer（原生文件选择器）
requirements = python3,kivy==2.2.1,plyer

orientation = portrait
android.minapi = 21
android.api = 33
# 存储权限：MANAGE_EXTERNAL_STORAGE 允许 Android 11+ 访问所有文件
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.archs = arm64-v8a
fullscreen = 0
log_level = 2

[buildozer]
warn_on_root = 0
