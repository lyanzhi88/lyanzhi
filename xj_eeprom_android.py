#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
西继迅达主板 EEPROM 工具 — Android 版
基于 Kivy 框架，支持编译为 APK

功能：
  1. 读取 BIN 文件提取密码
  2. 手动输入字节计算密码
  3. 生成出厂默认 EEPROM 镜像
  4. 全权主码计算器
"""

import struct
import os

# ─────────────────────────────────────────────────────────────────────────────
# 核心算法（与 PC 版完全相同）
# ─────────────────────────────────────────────────────────────────────────────

ROM_XOR_KEY = bytes([
    0x23, 0x45, 0x62, 0x49, 0x8a, 0x8f, 0x2a, 0x7f, 0xad, 0x6f, 0xdc, 0xe9, 0x34, 0xb9, 0x36, 0x2c,
    0x7a, 0xeb, 0x94, 0xa4, 0xbe, 0xc4, 0xe4, 0xa8, 0x28, 0xaa, 0x32, 0x58, 0xa8, 0x2e, 0x46, 0x84,
    0x1f, 0xf1, 0x7f, 0x41, 0x9d, 0xb1, 0x1d, 0xd2, 0xec, 0x32, 0xc1, 0x0f, 0x52, 0x92, 0x61, 0x38,
    0xf1, 0xd6, 0xfe, 0xa2, 0x74, 0x35, 0x77, 0x8f, 0x65, 0x18, 0x36, 0xe2, 0x46, 0x8a, 0x47, 0x82,
    0x1e, 0x13, 0x54, 0x5e, 0x51, 0x55, 0xfa, 0x11, 0x83, 0x2a, 0x55, 0x95, 0x68, 0x1b, 0x2c, 0x43,
    0xa4, 0xfe, 0x27, 0x46, 0xfe, 0x94, 0x24, 0x24, 0x24, 0x2f, 0xb4, 0x24, 0x26, 0x58, 0x8c, 0x64,
    0x36, 0x4f, 0x29, 0x29, 0xcf, 0x98, 0xe1, 0x23, 0x26, 0x29, 0x28, 0x2b, 0x27, 0x55, 0x8f, 0x4d,
    0xd4, 0xfe, 0x2e, 0x24, 0xfc, 0x84, 0x36, 0xf8, 0x68, 0x17, 0xa2, 0xc3, 0x49, 0x66, 0xfc, 0x69,
    0x19, 0xdd, 0x16, 0xfd, 0x21, 0x28, 0x4b, 0x7d, 0x69, 0x99, 0x3f, 0xf9, 0x49, 0x8f, 0x48, 0x78,
    0x48, 0xfc, 0x98, 0xe8, 0xf8, 0x04, 0xfe, 0xc8, 0xf8, 0x38, 0xf8, 0x58, 0xb8, 0xfe, 0x28, 0x18,
    0x76, 0x78, 0x4a, 0x51, 0x51, 0x6a, 0x57, 0x49, 0x49, 0x49, 0x69, 0x51, 0x41, 0x41, 0x42, 0x44,
    0x25, 0x24, 0xfe, 0x27, 0x44, 0xfe, 0xb4, 0x7c, 0x44, 0x7c, 0x42, 0x4b, 0x54, 0x48, 0x8f, 0x7e,
    0x16, 0x1a, 0x18, 0x25, 0x24, 0x63, 0xbd, 0x24, 0x25, 0x26, 0x24, 0x25, 0x26, 0x24, 0x25, 0x21,
    0x49, 0x4a, 0x48, 0xfc, 0x5c, 0x64, 0xfe, 0xaa, 0xfc, 0x64, 0x91, 0xf8, 0x8a, 0xa8, 0xf8, 0x38,
    0xf2, 0x11, 0xf8, 0x27, 0x21, 0x41, 0x42, 0x77, 0xd3, 0x51, 0x51, 0x52, 0x54, 0x77, 0x5a, 0xc4,
    0xc8, 0x98, 0xab, 0xfe, 0xd8, 0xe8, 0x52, 0xbc, 0x84, 0x28, 0x98, 0xa4,
])

FACTORY_BLOCK1 = bytes([
    0x01, 0x00, 0x0c, 0x0a, 0x01, 0x01, 0x01, 0x00, 0x00, 0x05, 0x0f, 0x2d, 0x08, 0x02, 0x3c, 0x0a,
    0x16, 0x19, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x0f, 0x05, 0x14, 0x05, 0x00, 0x32, 0x41,
    0x14, 0x00, 0x68, 0x01, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0x58, 0x02, 0xf0, 0x00, 0xc8, 0x00,
    0x9b, 0x05, 0x37, 0x00, 0x35, 0x00, 0x96, 0x00, 0x50, 0x00, 0x50, 0x00, 0x96, 0x00, 0xc8, 0x00,
    0x96, 0x00, 0x5a, 0x00, 0x00, 0x00, 0xa4, 0x01, 0xdc, 0x00, 0x6e, 0x00, 0x5a, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0xc8, 0x00, 0xfc, 0x04, 0x0e, 0x13, 0x00, 0x00,
    0x00, 0x00, 0xb4, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x11, 0x00, 0x12, 0x00, 0x13, 0x00, 0x14,
    0x00, 0x15, 0x00, 0x16, 0x00, 0x17, 0x00, 0x18, 0x00, 0x19, 0x11, 0x10, 0x11, 0x11, 0x11, 0x12,
    0x11, 0x13, 0x11, 0x14, 0x11, 0x15, 0x11, 0x16, 0x11, 0x17, 0x11, 0x18, 0x11, 0x19, 0x12, 0x10,
    0x12, 0x11, 0x12, 0x12, 0x12, 0x13, 0x12, 0x14, 0x12, 0x15, 0x12, 0x16, 0x12, 0x17, 0x12, 0x18,
    0x12, 0x19, 0x13, 0x10, 0x13, 0x11, 0x13, 0x12, 0x13, 0x13, 0x13, 0x14, 0x13, 0x15, 0x13, 0x16,
    0x13, 0x17, 0x13, 0x18, 0x13, 0x19, 0x14, 0x10, 0x14, 0x11, 0x14, 0x12, 0x14, 0x13, 0x14, 0x14,
    0x14, 0x15, 0x14, 0x16, 0x14, 0x17, 0x14, 0x18,
    0x00, 0x9d, 0x69, 0x3a,   # 密码: 980000000
    0xe6, 0xd7, 0x31, 0x00,   # 备用密码: 3266534
    0xfc, 0xeb,
    0xe0, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

FACTORY_BLOCK2 = bytes([
    0x08, 0x1e, 0x14, 0x19, 0x23, 0x03, 0x03, 0x03, 0x03, 0x01, 0x02, 0x02, 0x02, 0x02, 0x03, 0x02,
    0x20, 0x06, 0x20, 0x32, 0x74, 0x19, 0x1e, 0x05, 0x05, 0x38, 0x11, 0x1a, 0x4f, 0x26, 0x05, 0x05,
    0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
    0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
    0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
    0x05, 0x05, 0x0a, 0x19, 0x05, 0x0a, 0x32, 0x0a, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
    0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
    0x01, 0x00, 0x41, 0x00, 0x54, 0x01, 0x50, 0x05, 0x80, 0x07, 0x60, 0x00, 0xe8, 0x03, 0x00, 0x08,
    0x00, 0x00, 0x0f, 0x00, 0xe8, 0x03, 0xe8, 0x03, 0x01, 0x00, 0x01, 0x00, 0x0f, 0x0e, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2c, 0x01, 0x2c, 0x01, 0x00, 0x00,
    0x3c, 0x00, 0x1e, 0x00, 0xe8, 0x03, 0x3c, 0x00, 0x1e, 0x00, 0x2c, 0x01, 0x2d, 0x00, 0x28, 0x00,
    0x90, 0x01, 0x88, 0x13, 0x3c, 0x00, 0xdc, 0x05, 0x1e, 0x00, 0x64, 0x00, 0xfa, 0x00, 0x01, 0x00,
    0x5e, 0x01, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00,
    0x78, 0x00, 0x14, 0x00, 0x05, 0x00, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
    0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
    0x08, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b,
    0x1c, 0x10, 0x1f, 0x2b, 0x3a, 0x43, 0x4c, 0x54, 0x59, 0x5c, 0x5d, 0x5d, 0x5c, 0x58, 0x54, 0x4b,
    0x42, 0x39, 0x2b, 0x1d, 0x0d, 0x1c, 0x13, 0x0d,
])


def crc32(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xEDB88320 if (crc & 1) else (crc >> 1)
    return crc & 0xFFFFFFFF


def _firmware_crc(data: bytes, poly: int = 0xEDB88320) -> int:
    a3 = 0xFFFFFFFF
    for byte in data:
        v5 = byte & 0xFF
        for _ in range(8):
            if (a3 ^ v5) & 1:
                a3 = poly ^ (a3 >> 1)
            else:
                a3 >>= 1
                v5 >>= 1
    return (~a3) & 0xFFFFFFFF


def calc_master_password(sys_cd: int, param_114: int):
    key = struct.pack('<II', param_114, sys_cd)
    master_pw = _firmware_crc(key, poly=0xEDB88320) % 1_000_000_000
    delay_pw  = _firmware_crc(key, poly=0x82F63B78) % 1_000_000_000
    return master_pw, delay_pw


def block_checksum(data: bytes) -> int:
    return (0x5219 - sum(data)) & 0xFFFF


def xor_decrypt(cipher: bytes, eeprom_key: bytes, size: int) -> bytes:
    rom = ROM_XOR_KEY[:size]
    return bytes(c ^ k ^ r for c, k, r in zip(cipher, eeprom_key[:size], rom))


def xor_encrypt(plain: bytes, eeprom_key: bytes, size: int) -> bytes:
    return xor_decrypt(plain, eeprom_key, size)


def verify_block(plaintext: bytes, data_len: int):
    data_sum = sum(plaintext[:data_len]) & 0xFFFF
    stored   = struct.unpack_from('<H', plaintext, data_len)[0]
    total    = (data_sum + stored) & 0xFFFF
    return (total == 0x5219), total, stored


def _try_page(dump: bytes, page_base: int) -> dict:
    if page_base + 0x800 > len(dump):
        return {}
    try:
        stored_crc   = struct.unpack_from('<I', dump, page_base)[0]
        computed_crc = crc32(dump[page_base + 4 : page_base + 0x800])
        crc_ok       = (stored_crc == computed_crc)
    except Exception:
        stored_crc = computed_crc = 0
        crc_ok = False
    try:
        cipher1  = dump[page_base+0x400 : page_base+0x400+0xFC]
        key1     = dump[page_base+0x100 : page_base+0x100+0xFC]
        plain1   = xor_decrypt(cipher1, key1, 0xFC)
        blk1_ok, blk1_total, _ = verify_block(plain1, 0xFA)
        password     = struct.unpack_from('<I', plain1, 0xC8)[0]
        alt_password = struct.unpack_from('<I', plain1, 0xCC)[0]
        param_114    = struct.unpack_from('<I', plain1, 0xF6)[0]
    except Exception:
        return {}
    try:
        cipher2  = dump[page_base+0x700 : page_base+0x700+0xFA]
        key2     = dump[page_base+0x200 : page_base+0x200+0xFA]
        plain2   = xor_decrypt(cipher2, key2, 0xFA)
        blk2_ok, _, _ = verify_block(plain2, 0xF8)
    except Exception:
        blk2_ok = False
    return {
        'password': password, 'alt_password': alt_password,
        'param_114': param_114, 'crc_ok': crc_ok,
        'stored_crc': stored_crc, 'computed_crc': computed_crc,
        'block1_ok': blk1_ok, 'block2_ok': blk2_ok,
        'blk1_total': blk1_total, 'page_base': page_base,
    }


def extract_password(dump: bytes, eeprom_start: int = 0) -> dict:
    base = -eeprom_start
    candidates = [0x0800, 0x1000, 0x1800]
    results = []
    for phys in candidates:
        page_base = phys + base
        if page_base < 0:
            continue
        r = _try_page(dump, page_base)
        if r:
            r['source_phys'] = phys
            results.append(r)
    if not results:
        return {'error': '数据太短或格式不匹配'}
    for r in results:
        if r.get('block1_ok'):
            r['_candidates'] = results
            return r
    for r in results:
        if r.get('crc_ok'):
            r['_candidates'] = results
            return r
    results[0]['_candidates'] = results
    return results[0]


def calc_password_from_bytes(block_hex: str, key_hex: str) -> int:
    b = bytes(int(x, 16) for x in block_hex.split())
    k = bytes(int(x, 16) for x in key_hex.split())
    if len(b) != 4 or len(k) != 4:
        raise ValueError('需要恰好 4 个字节')
    rom_pw = ROM_XOR_KEY[0xC8:0xCC]
    plain  = bytes(bi ^ ki ^ ri for bi, ki, ri in zip(b, k, rom_pw))
    return struct.unpack('<I', plain)[0]


def build_eeprom_image(custom_password: int = None) -> bytes:
    blk1 = bytearray(FACTORY_BLOCK1)
    if custom_password is not None:
        struct.pack_into('<I', blk1, 0xC8, custom_password)
    cs1 = block_checksum(blk1)
    blk1_with_cs = bytes(blk1) + struct.pack('<H', cs1)
    cipher1 = xor_encrypt(blk1_with_cs, bytes(0xFC), 0xFC)

    blk2 = bytearray(FACTORY_BLOCK2)
    cs2  = block_checksum(blk2)
    blk2_with_cs = bytes(blk2) + struct.pack('<H', cs2)
    cipher2 = xor_encrypt(blk2_with_cs, bytes(0xFA), 0xFA)

    page = bytearray(0x1000)
    page[0x400 : 0x400 + 0xFC] = cipher1
    page[0x700 : 0x700 + 0xFA] = cipher2
    crc_val = crc32(bytes(page[4:0x800]))
    struct.pack_into('<I', page, 0, crc_val)

    image = bytearray(0x2800)
    image[0x0800 : 0x1800] = page
    image[0x1800 : 0x2800] = page
    return bytes(image)


# ─────────────────────────────────────────────────────────────────────────────
# Kivy GUI
# ─────────────────────────────────────────────────────────────────────────────

from kivy.config import Config
Config.set('graphics', 'resizable', True)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform

# 颜色主题
C_BG      = (0.08, 0.09, 0.11, 1)    # 深黑底色
C_CARD    = (0.13, 0.15, 0.18, 1)    # 卡片背景
C_ACCENT  = (0.18, 0.52, 0.90, 1)    # 蓝色强调
C_SUCCESS = (0.20, 0.78, 0.35, 1)    # 绿色成功
C_WARN    = (0.95, 0.62, 0.10, 1)    # 橙色警告
C_DANGER  = (0.90, 0.25, 0.25, 1)    # 红色错误
C_TEXT    = (0.92, 0.93, 0.95, 1)    # 主文字
C_HINT    = (0.55, 0.58, 0.63, 1)    # 提示文字
C_NAV_ACT = (0.18, 0.52, 0.90, 1)    # 导航激活
C_NAV_IN  = (0.35, 0.38, 0.43, 1)    # 导航未激活


def make_label(text, font_size=14, color=C_TEXT, bold=False,
               halign='left', valign='middle', size_hint_y=None, height=None):
    lbl = Label(
        text=text,
        font_size=dp(font_size),
        color=color,
        bold=bold,
        halign=halign,
        valign=valign,
        size_hint_y=size_hint_y,
        height=height,
        markup=True,
    )
    lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
    return lbl


def make_input(hint='', multiline=False, height=44, **kw):
    ti = TextInput(
        hint_text=hint,
        multiline=multiline,
        size_hint_y=None,
        height=dp(height),
        background_color=(0.17, 0.20, 0.25, 1),
        foreground_color=C_TEXT,
        hint_text_color=C_HINT,
        cursor_color=C_ACCENT,
        font_size=dp(14),
        padding=[dp(10), dp(10)],
        **kw
    )
    return ti


def make_btn(text, color=C_ACCENT, on_press=None, height=48):
    btn = Button(
        text=text,
        size_hint_y=None,
        height=dp(height),
        background_color=color,
        background_normal='',
        color=C_TEXT,
        font_size=dp(15),
        bold=True,
    )
    if on_press:
        btn.bind(on_press=on_press)
    return btn


def make_result_box(text, color=C_CARD):
    sv = ScrollView(size_hint_y=None, height=dp(180))
    lbl = Label(
        text=text,
        font_size=dp(13),
        color=C_TEXT,
        halign='left',
        valign='top',
        markup=True,
        size_hint_y=None,
        padding=[dp(10), dp(8)],
    )
    lbl.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1]))
    lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
    sv.add_widget(lbl)
    sv._lbl = lbl
    return sv


# ── 文件选择弹窗 ─────────────────────────────────────────────────────────────

class FileDialog(Popup):
    def __init__(self, callback, **kw):
        super().__init__(**kw)
        self.callback = callback
        self.title = '选择 BIN 文件'
        self.size_hint = (0.95, 0.85)
        self.background_color = C_BG

        layout = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(8))

        # 起始路径
        if platform == 'android':
            start = '/sdcard'
        else:
            start = os.path.expanduser('~')

        self.fc = FileChooserListView(
            path=start,
            filters=['*.bin', '*.BIN', '*.dat', '*.DAT', '*'],
            size_hint_y=1,
        )
        layout.add_widget(self.fc)

        btns = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        btns.add_widget(make_btn('取消', color=(0.3, 0.3, 0.35, 1),
                                  on_press=lambda _: self.dismiss()))
        btns.add_widget(make_btn('确认', color=C_ACCENT,
                                  on_press=self._confirm))
        layout.add_widget(btns)
        self.content = layout

    def _confirm(self, *_):
        sel = self.fc.selection
        if sel:
            self.dismiss()
            self.callback(sel[0])
        else:
            show_toast('请先选择文件')


def show_toast(msg):
    popup = Popup(
        title='', content=Label(text=msg, color=C_TEXT, font_size=dp(14)),
        size_hint=(0.7, 0.18),
        background_color=(0.15, 0.17, 0.22, 0.95),
    )
    popup.open()
    from kivy.clock import Clock
    Clock.schedule_once(lambda _: popup.dismiss(), 2.2)


# ── 屏幕1：BIN文件提取密码 ───────────────────────────────────────────────────

class ExtractScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._file_path = ''
        root = BoxLayout(orientation='vertical',
                         padding=dp(12), spacing=dp(10))
        root.canvas.before.clear()

        # 标题
        root.add_widget(make_label(
            '[b]读取BIN文件 — 提取密码[/b]',
            font_size=17, halign='center', size_hint_y=None, height=dp(40)))

        # 提示
        root.add_widget(make_label(
            '将EEPROM转储文件(.bin)通过文件管理器复制到手机，\n'
            '然后在此选择该文件进行解析。',
            font_size=12, color=C_HINT, size_hint_y=None, height=dp(48)))

        # 文件路径显示
        self.lbl_file = make_label(
            '未选择文件', font_size=13, color=C_HINT,
            size_hint_y=None, height=dp(36))
        root.add_widget(self.lbl_file)

        # 按钮行
        row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        row.add_widget(make_btn('选择BIN文件', color=C_ACCENT,
                                 on_press=self._pick_file))
        row.add_widget(make_btn('开始解析', color=C_SUCCESS,
                                 on_press=self._do_extract))
        root.add_widget(row)

        # 结果区
        root.add_widget(make_label(
            '解析结果：', font_size=13, color=C_HINT,
            size_hint_y=None, height=dp(28)))

        self.sv = ScrollView()
        self.result_lbl = Label(
            text='', font_size=dp(13), color=C_TEXT,
            halign='left', valign='top', markup=True,
            size_hint_y=None, padding=[dp(10), dp(8)],
        )
        self.result_lbl.bind(
            texture_size=lambda i, v: setattr(i, 'height', v[1]))
        self.result_lbl.bind(
            size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        self.sv.add_widget(self.result_lbl)
        root.add_widget(self.sv)

        self.add_widget(root)

    def _pick_file(self, *_):
        FileDialog(callback=self._on_file_chosen).open()

    def _on_file_chosen(self, path):
        self._file_path = path
        self.lbl_file.text = f'[color=aaaaaa]{os.path.basename(path)}[/color]'

    def _do_extract(self, *_):
        path = self._file_path
        if not path:
            self.result_lbl.text = '[color=ff6666]请先选择文件[/color]'
            return
        if not os.path.isfile(path):
            self.result_lbl.text = f'[color=ff6666]文件不存在:\n{path}[/color]'
            return
        try:
            with open(path, 'rb') as f:
                dump = f.read()
        except Exception as e:
            self.result_lbl.text = f'[color=ff6666]读取失败: {e}[/color]'
            return

        size = len(dump)
        eeprom_start = 0 if size > 0x1800 else 0x800
        result = extract_password(dump, eeprom_start)

        if 'error' in result:
            self.result_lbl.text = f'[color=ff6666]解析错误: {result["error"]}[/color]'
            return

        ok  = '[color=44cc66]✓ 通过[/color]'
        nok = '[color=ff5555]✗ 失败[/color]'

        crc_s  = ok if result['crc_ok']   else nok
        blk1_s = ok if result['block1_ok'] else nok
        blk2_s = ok if result['block2_ok'] else nok
        src    = result.get('source_phys', 0x800)

        pw     = result['password']
        alt_pw = result['alt_password']
        p114   = result.get('param_114', 0)

        pw_color  = '44cc66' if pw != 980000000 else 'aaaaaa'
        pw_note   = '' if pw != 980000000 else '  (出厂默认)'

        lines = [
            f'[b]文件:[/b] {os.path.basename(path)}  ({size} 字节)',
            f'[b]来源区:[/b] 物理 0x{src:04X}',
            '',
            f'[b]CRC32校验:[/b]  {crc_s}',
            f'[b]参数块1校验:[/b] {blk1_s}',
            f'[b]参数块2校验:[/b] {blk2_s}',
            '',
            '━━━━━━━━━━━━━━━━━━━━━━━━',
            f'[b][color={pw_color}]密  码（主）: {pw:>12d}[/color][/b]{pw_note}',
            f'[b]密  码（备）: {alt_pw:>12d}[/b]',
            '━━━━━━━━━━━━━━━━━━━━━━━━',
        ]

        if result.get('block1_ok') and p114:
            lines += [
                '',
                f'[b]全权主码参数:[/b]',
                f'param_114 = 0x{p114:08X}',
                f'(请在"主码计算"页输入SysCD计算主码)',
            ]

        candidates = result.get('_candidates', [result])
        if len(candidates) > 1:
            lines += ['', '[b]所有区域扫描：[/b]']
            for c in candidates:
                tag = '▶ ' if c is result else '   '
                lines.append(
                    f'{tag}0x{c["source_phys"]:04X}  '
                    f'CRC:{ok if c["crc_ok"] else nok}  '
                    f'块1:{ok if c["block1_ok"] else nok}  '
                    f'密码:{c["password"]}'
                )

        self.result_lbl.text = '\n'.join(lines)
        # 保存 param_114 供主码页使用
        App.get_running_app().last_param114 = p114


# ── 屏幕2：手动字节计算密码 ──────────────────────────────────────────────────

class CalcScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical',
                         padding=dp(12), spacing=dp(10))

        root.add_widget(make_label(
            '[b]手动输入字节 — 计算密码[/b]',
            font_size=17, halign='center', size_hint_y=None, height=dp(40)))

        root.add_widget(make_label(
            '从EEPROM芯片读取以下两处4字节（十六进制，空格分隔）：',
            font_size=12, color=C_HINT, size_hint_y=None, height=dp(36)))

        root.add_widget(make_label(
            '密文：物理地址 0x0CC8（主区）或 0x14C8（备份区）',
            font_size=12, color=C_HINT, size_hint_y=None, height=dp(28)))
        self.inp_block = make_input(
            hint='密文4字节，如: 06 CE 9D 21')
        root.add_widget(self.inp_block)

        root.add_widget(make_label(
            '密钥：物理地址 0x09C8（主区）或 0x11C8（备份区）',
            font_size=12, color=C_HINT, size_hint_y=None, height=dp(28)))
        self.inp_key = make_input(
            hint='密钥4字节，如: 00 00 00 00')
        root.add_widget(self.inp_key)

        root.add_widget(make_btn('计算密码', color=C_SUCCESS,
                                  on_press=self._calc))

        self.result_lbl = make_label(
            '', font_size=14, size_hint_y=None, height=dp(140))
        root.add_widget(self.result_lbl)

        root.add_widget(Label())  # 弹性空白
        self.add_widget(root)

    def _calc(self, *_):
        block = self.inp_block.text.strip()
        key   = self.inp_key.text.strip()
        if not block:
            self.result_lbl.text = '[color=ff6666]请输入密文字节[/color]'
            return
        if not key:
            key = '00 00 00 00'
        try:
            pw = calc_password_from_bytes(block, key)
        except Exception as e:
            self.result_lbl.text = f'[color=ff6666]错误: {e}[/color]'
            return

        rom_pw = ROM_XOR_KEY[0xC8:0xCC]
        b = bytes(int(x, 16) for x in block.split())
        k = bytes(int(x, 16) for x in key.split())
        plain = bytes(bi ^ ki ^ ri for bi, ki, ri in zip(b, k, rom_pw))

        note = '  [color=aaaaaa](出厂默认)[/color]' if pw == 980000000 else ''
        self.result_lbl.text = (
            f'明文字节: {plain.hex(" ").upper()}\n\n'
            f'━━━━━━━━━━━━━━━━━━━━━\n'
            f'[b][color=44cc66]密码: {pw:>12d}[/color][/b]{note}\n'
            f'[b][color=44cc66]     (0x{pw:08X})[/color][/b]\n'
            f'━━━━━━━━━━━━━━━━━━━━━'
        )


# ── 屏幕3：生成出厂EEPROM镜像 ────────────────────────────────────────────────

class GenerateScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical',
                         padding=dp(12), spacing=dp(10))

        root.add_widget(make_label(
            '[b]生成出厂默认 EEPROM 镜像[/b]',
            font_size=17, halign='center', size_hint_y=None, height=dp(40)))

        root.add_widget(make_label(
            '用于修复 EEPROM 全零/全FF损坏导致的主板死循环。\n'
            '生成后用编程器写入芯片物理地址 0x0000 处。',
            font_size=12, color=C_WARN, size_hint_y=None, height=dp(52)))

        root.add_widget(make_label(
            '自定义密码（留空=出厂默认 980000000）：',
            font_size=13, size_hint_y=None, height=dp(28)))
        self.inp_pw = make_input(
            hint='0 ~ 999999999，留空使用出厂默认',
            input_filter='int')
        root.add_widget(self.inp_pw)

        root.add_widget(make_label(
            '保存文件名（留空=eeprom_factory.bin，保存到下载目录）：',
            font_size=13, size_hint_y=None, height=dp(28)))
        self.inp_name = make_input(hint='eeprom_factory.bin')
        root.add_widget(self.inp_name)

        root.add_widget(make_btn('生成并保存', color=C_ACCENT,
                                  on_press=self._generate))

        self.result_lbl = make_label(
            '', font_size=13, size_hint_y=None, height=dp(160))
        root.add_widget(self.result_lbl)

        root.add_widget(Label())
        self.add_widget(root)

    def _generate(self, *_):
        pw_str = self.inp_pw.text.strip()
        pw = None
        if pw_str:
            try:
                pw = int(pw_str)
                if not (0 <= pw <= 999_999_999):
                    self.result_lbl.text = '[color=ff6666]密码范围: 0~999999999[/color]'
                    return
            except ValueError:
                self.result_lbl.text = '[color=ff6666]请输入纯数字密码[/color]'
                return

        fname = self.inp_name.text.strip() or 'eeprom_factory.bin'
        if not fname.endswith('.bin'):
            fname += '.bin'

        # 保存路径
        if platform == 'android':
            save_dir = '/sdcard/Download'
        else:
            save_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
        os.makedirs(save_dir, exist_ok=True)
        out_path = os.path.join(save_dir, fname)

        try:
            image = build_eeprom_image(custom_password=pw)
            with open(out_path, 'wb') as f:
                f.write(image)
        except Exception as e:
            self.result_lbl.text = f'[color=ff6666]生成失败: {e}[/color]'
            return

        # 自验证
        vr = extract_password(image, eeprom_start=0)
        eff_pw = pw if pw is not None else 980_000_000
        ok_s = '[color=44cc66]✓ 通过[/color]'
        nok_s = '[color=ff5555]✗ 失败[/color]'

        self.result_lbl.text = (
            f'[b][color=44cc66]文件已保存！[/color][/b]\n'
            f'路径: {out_path}\n'
            f'大小: {len(image)} 字节\n\n'
            f'密码: [b]{eff_pw:09d}[/b]\n\n'
            f'自验证:\n'
            f'  CRC32   {ok_s if vr.get("crc_ok") else nok_s}\n'
            f'  参数块1 {ok_s if vr.get("block1_ok") else nok_s}\n'
            f'  参数块2 {ok_s if vr.get("block2_ok") else nok_s}\n\n'
            f'[color=ffaa33]写入说明: 用编程器从物理地址0x0000开始烧写[/color]'
        )


# ── 屏幕4：全权主码计算器 ────────────────────────────────────────────────────

class MasterScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical',
                         padding=dp(12), spacing=dp(10))

        root.add_widget(make_label(
            '[b]全权主码计算器[/b]',
            font_size=17, halign='center', size_hint_y=None, height=dp(40)))

        root.add_widget(make_label(
            'Special Para 服务主码 → 全权主码\n'
            '注意：SysCD 约每24小时刷新，主码随之改变。',
            font_size=12, color=C_WARN, size_hint_y=None, height=dp(48)))

        root.add_widget(make_label(
            'SysCD（驱动器Special Para界面显示，8位十六进制）：',
            font_size=13, size_hint_y=None, height=dp(28)))
        self.inp_syscd = make_input(
            hint='如: 1A2B3C4D  （不需要0x前缀）')
        root.add_widget(self.inp_syscd)

        root.add_widget(make_label(
            'param_114（从"读取BIN"页提取，或手动输入十六进制）：',
            font_size=13, size_hint_y=None, height=dp(28)))
        self.inp_p114 = make_input(
            hint='如: 0xF75776D5  或  F75776D5')
        root.add_widget(self.inp_p114)

        # 自动填充按钮
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        row.add_widget(make_btn('从BIN页自动填入param_114',
                                 color=(0.25, 0.35, 0.55, 1),
                                 on_press=self._autofill))
        root.add_widget(row)

        root.add_widget(make_btn('计算全权主码', color=C_SUCCESS,
                                  on_press=self._calc))

        self.result_lbl = make_label(
            '', font_size=14, size_hint_y=None, height=dp(180))
        root.add_widget(self.result_lbl)

        root.add_widget(Label())
        self.add_widget(root)

    def _autofill(self, *_):
        app = App.get_running_app()
        p114 = getattr(app, 'last_param114', None)
        if p114:
            self.inp_p114.text = f'0x{p114:08X}'
            show_toast(f'已填入 0x{p114:08X}')
        else:
            show_toast('请先在"读取BIN"页解析文件')

    def _calc(self, *_):
        syscd_str = self.inp_syscd.text.strip().lstrip('0x').lstrip('0X')
        p114_str  = self.inp_p114.text.strip().lstrip('0x').lstrip('0X')

        if not syscd_str:
            self.result_lbl.text = '[color=ff6666]请输入 SysCD[/color]'
            return
        if not p114_str:
            self.result_lbl.text = '[color=ff6666]请输入 param_114[/color]'
            return

        try:
            sys_cd = int(syscd_str, 16)
        except ValueError:
            self.result_lbl.text = '[color=ff6666]SysCD 格式无效，请输入十六进制[/color]'
            return
        try:
            param_114 = int(p114_str, 16)
        except ValueError:
            self.result_lbl.text = '[color=ff6666]param_114 格式无效，请输入十六进制[/color]'
            return

        master_pw, delay_pw = calc_master_password(sys_cd, param_114)

        key8 = struct.pack('<II', param_114, sys_cd)
        self.result_lbl.text = (
            f'SysCD:     0x{sys_cd:08X}\n'
            f'param_114: 0x{param_114:08X}\n'
            f'密钥(8B):  {key8.hex(" ").upper()}\n\n'
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
            f'[b][color=33ddff]全权主码: {master_pw:09d}[/color][/b]\n'
            f'[b][color=88aaff]延时主码: {delay_pw:09d}[/color][/b]  (Delay OK)\n'
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n'
            f'[color=ffaa33]在驱动器Special Para密码框输入全权主码即可进入[/color]'
        )


# ── 底部导航栏 ───────────────────────────────────────────────────────────────

class NavBar(BoxLayout):
    TABS = [
        ('读取BIN', 'extract'),
        ('字节计算', 'calc'),
        ('生成镜像', 'generate'),
        ('主码计算', 'master'),
    ]

    def __init__(self, sm, **kw):
        super().__init__(size_hint_y=None, height=dp(56),
                         orientation='horizontal', **kw)
        self.sm = sm
        self._btns = {}
        for label, name in self.TABS:
            btn = Button(
                text=label,
                font_size=dp(12),
                background_normal='',
                background_color=C_NAV_IN,
                color=C_TEXT,
                bold=False,
            )
            btn.bind(on_press=lambda b, n=name: self._switch(n))
            self.add_widget(btn)
            self._btns[name] = btn
        self._highlight('extract')

    def _switch(self, name):
        self.sm.transition = SlideTransition(direction='left')
        self.sm.current = name
        self._highlight(name)

    def _highlight(self, name):
        for n, b in self._btns.items():
            if n == name:
                b.background_color = C_NAV_ACT
                b.bold = True
            else:
                b.background_color = C_NAV_IN
                b.bold = False


# ── 主 App ───────────────────────────────────────────────────────────────────

class XJEepromApp(App):
    last_param114 = None

    def build(self):
        Window.clearcolor = C_BG

        sm = ScreenManager()
        sm.add_widget(ExtractScreen(name='extract'))
        sm.add_widget(CalcScreen(name='calc'))
        sm.add_widget(GenerateScreen(name='generate'))
        sm.add_widget(MasterScreen(name='master'))

        nav = NavBar(sm)

        root = BoxLayout(orientation='vertical')
        root.add_widget(sm)
        root.add_widget(nav)

        return root

    def get_application_name(self):
        return '西继迅达EEPROM工具'


if __name__ == '__main__':
    XJEepromApp().run()
