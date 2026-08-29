#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
button_daemon.py
-----------------
タクトスイッチ3個を、以下のキーボード入力に変換して送り続けるデーモン。

  ボタン1: Tab      … 次のボタン/入力欄へフォーカス移動 (ブラウザ標準)
  ボタン2: Enter     … フォーカス中の要素を決定/クリック (ブラウザ標準)
  ボタン3: PageDown  … 画面を下にスクロール (ブラウザ標準)

Tab/Enter/PageDownはすべてブラウザ側の標準キー動作なので、
index_kiosk.html 側にはほぼ何も手を入れる必要がない。
このスクリプトは物理ボタンの押下をそのままキー入力として
OSに送り込むだけの役割。

配線 (GPIO BCMナンバー):
  ボタン1 (Tab)      : GPIO17 (物理11番ピン)
  ボタン2 (Enter)    : GPIO27 (物理13番ピン)
  ボタン3 (PageDown) : GPIO22 (物理15番ピン)
  各ボタンのもう片方の足は GND へ(内部プルアップ使用、GND直結でOK)

必要パッケージ:
  sudo apt install python3-gpiozero
  sudo pip3 install python-uinput --break-system-packages
  echo uinput | sudo tee -a /etc/modules-load.d/uinput.conf   # 起動時にuinputを自動ロード

このスクリプトは /dev/uinput への書き込み権限が必要なので、
基本は root(またはsystemdサービス)で動かす。
"""
import time
import os
from gpiozero import Button
import uinput

# ---- ピン設定 (必要ならここだけ書き換えればOK) ----
PIN_TAB      = 17  # 次のボタン/入力欄へ
PIN_ENTER    = 27  # 決定
PIN_PAGEDOWN = 22  # スクロール
BOUNCE_SEC = 0.05
LONG_PRESS_SEC = 5  # この秒数以上PageDownを押し続けたらシャットダウン

# ---- 仮想キーボードデバイスを作成 ----
device = uinput.Device([
    uinput.KEY_TAB,
    uinput.KEY_ENTER,
    uinput.KEY_PAGEDOWN,
])
# uinput デバイスがOSに認識されるまで少し待つ
time.sleep(0.3)

btn_tab      = Button(PIN_TAB,      pull_up=True, bounce_time=BOUNCE_SEC)
btn_enter    = Button(PIN_ENTER,    pull_up=True, bounce_time=BOUNCE_SEC)
btn_pagedown = Button(PIN_PAGEDOWN, pull_up=True, bounce_time=BOUNCE_SEC, hold_time=LONG_PRESS_SEC, hold_repeat=False)


def send(key):
    try:
        device.emit_click(key)
    except Exception as e:
        print("key send failed:", e)
def shutdown_pi():
    print("PageDown %d秒長押しを検出 -> シャットダウンします" % LONG_PRESS_SEC)
    os.system("shutdown -h now")


btn_tab.when_pressed = lambda: send(uinput.KEY_TAB)
btn_enter.when_pressed = lambda: send(uinput.KEY_ENTER)
btn_pagedown.when_pressed = lambda: send(uinput.KEY_PAGEDOWN)
btn_pagedown.when_held = shutdown_pi

print("button_daemon: started. GPIO%d=Tab GPIO%d=Enter GPIO%d=PageDown (%d秒長押しでshutdown) (Ctrl+Cで終了)"
      % (PIN_TAB, PIN_ENTER, PIN_PAGEDOWN, LONG_PRESS_SEC))

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
