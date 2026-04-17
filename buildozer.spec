[app]
title = 西继迅达EEPROM工具
package.name = xjeepromtool
package.domain = org.xjeeprom
source.main = xj_eeprom_android
version = 1.0
source.dir = .
source.include_exts = py

# 依赖：kivy 官方 Android 支持版本
requirements = python3,kivy==2.2.1

orientation = portrait
android.minapi = 21
android.api = 33
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.archs = arm64-v8a
fullscreen = 0
log_level = 2

[buildozer]
warn_on_root = 0
