# -*- coding: utf-8 -*-
"""
gen_cabinet_layout.py —— 生成数据采集柜柜内布局图（SVG）
=======================================================

用途：`电气图纸/数据采集柜布局图.txt` 原为纯文本字符画。本脚本按该文本的
柜体尺寸与 DIN 导轨分区（电源区 / 控制区）、元件位号与间距渲染为标准图框的
SVG 布局图，供仓库展示与打印。

拓扑来源（与文本图逐项对应）：
  柜体 400(W)×600(H)×200(D) mm 墙挂式 IP54；柜顶走线区；DIN 导轨 A（电源区）、
  导轨 B（控制区）、导轨 C（端子区）；强弱电分侧走线。

用法：python scripts/gen_cabinet_layout.py
输出：电气图纸/数据采集柜布局图.svg
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "电气图纸" / "数据采集柜布局图.svg"

W, H = 1100, 900
FONT = "Microsoft YaHei, SimHei, sans-serif"
C_BG = "#ffffff"
C_FRAME = "#204e8c"
C_CAB = "#f7f9fc"
C_RAIL = "#b8bfc8"
C_DEV = "#e8eef7"
C_DEV_EDGE = "#4a5a70"
C_AC = "#c62828"
C_SIG = "#1565c0"
C_GRN = "#2e7d32"
C_LINE = "#1a1a1a"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=12, fill=C_LINE, anchor="start", weight="normal"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')


def rect(x, y, w, h, fill=C_DEV, stroke=C_DEV_EDGE, width=1.5, rx=3, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{width}"{d}/>')


def line(x1, y1, x2, y2, color=C_LINE, width=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="{width}"{d}/>')


def device(x, y, w, h, tag, name, spec=""):
    """元件：位号加粗 + 名称 + 规格。"""
    out = [rect(x, y, w, h)]
    out.append(text(x + w / 2, y + 21, tag, 13, "#12305c", "middle", "bold"))
    out.append(text(x + w / 2, y + 38, name, 11, "#333", "middle"))
    if spec:
        out.append(text(x + w / 2, y + 53, spec, 10, "#666", "middle"))
    return "".join(out)


def build() -> str:
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    s.append(f'<rect width="{W}" height="{H}" fill="{C_BG}"/>')

    # 图框
    s.append(rect(16, 16, W - 32, H - 32, fill="none", stroke=C_FRAME, width=3, rx=0))
    s.append(rect(28, 28, W - 56, H - 56, fill="none", stroke=C_FRAME, width=1, rx=0))
    s.append(text(44, 60, "数据采集柜 柜内布局图", 20, C_FRAME, weight="bold"))
    s.append(text(44, 82, "柜体 400(W)×600(H)×200(D) mm  墙挂式 IP54  比例：非等比示意", 12, "#555"))

    # 柜体（放大绘制，占主体）
    cx, cy, cw, ch = 90, 110, 520, 640
    s.append(rect(cx, cy, cw, ch, fill=C_CAB, stroke=C_LINE, width=2.5, rx=4))
    s.append(text(cx + cw / 2, cy - 8, "柜门（含观察窗）", 12, "#666", "middle"))

    # 柜顶走线区
    top_h = 70
    s.append(rect(cx + 8, cy + 8, cw - 16, top_h, fill="#f0f4f9", stroke=C_FRAME, width=1.2, dash="5 3"))
    s.append(text(cx + 18, cy + 28, "柜顶走线区", 12, C_FRAME, weight="bold"))
    entries = [("AC 进线", C_AC), ("信号", C_SIG), ("通信", C_GRN), ("接地", "#7cb342")]
    for i, (name, col) in enumerate(entries):
        ex = cx + 24 + i * 118
        s.append(rect(ex, cy + 38, 96, 30, fill="#fff", stroke=col, width=1.4))
        s.append(text(ex + 48, cy + 58, name, 11, col, "middle"))
    s.append(text(cx + cw - 12, cy + 28, "[PG7 防水接头]", 10, "#777", "end"))

    # DIN 导轨 A — 电源区
    railA_y = cy + 110
    s.append(rect(cx + 8, railA_y, cw - 16, 26, fill=C_RAIL, stroke="#8f979f", width=1, rx=2))
    s.append(text(cx + 16, railA_y + 18, "DIN 导轨 A —— 电源区（强电）", 11.5, "#2b333c"))
    pw, ph = 104, 68
    for i, (tag, name, spec) in enumerate([
        ("QF1", "2P 空开", "220VAC"),
        ("FU1", "熔断器", "2A"),
        ("PSU-24V", "开关电源", "24V / 1A"),
        ("PSU-5V", "开关电源", "5V / 2A"),
    ]):
        s.append(device(cx + 22 + i * 122, railA_y + 36, pw, ph, tag, name, spec))
    # 走线槽
    ductA_y = railA_y + 116
    s.append(rect(cx + 8, ductA_y, cw - 16, 20, fill="#eef2f6", stroke="#aeb6bf", width=1, rx=2, dash="4 3"))
    s.append(text(cx + cw / 2, ductA_y + 14, "走线槽 A（强弱电分侧）", 10, "#6b7480", "middle"))

    # DIN 导轨 B — 控制区
    railB_y = ductA_y + 34
    s.append(rect(cx + 8, railB_y, cw - 16, 26, fill=C_RAIL, stroke="#8f979f", width=1, rx=2))
    s.append(text(cx + 16, railB_y + 18, "DIN 导轨 B —— 控制区（弱电）", 11.5, "#2b333c"))
    cw2 = 88
    for i, (tag, name, spec) in enumerate([
        ("STM32", "采集主板", "F103C8T6"),
        ("ESP8266", "通信模块", "ESP-01S"),
        ("KA1", "继电器 1", "报警声"),
        ("KA2", "继电器 2", "联锁切"),
        ("K1", "安全继电器", "急停"),
    ]):
        s.append(device(cx + 18 + i * 100, railB_y + 36, cw2, 66, tag, name, spec))

    # DIN 导轨 C — 端子区
    railC_y = railB_y + 128
    s.append(rect(cx + 8, railC_y, cw - 16, 26, fill=C_RAIL, stroke="#8f979f", width=1, rx=2))
    s.append(text(cx + 16, railC_y + 18, "DIN 导轨 C —— 端子区", 11.5, "#2b333c"))
    for i, (tag, name) in enumerate([("X1", "AC 端子"), ("X2", "信号端子"), ("X3", "通信端子"), ("PE", "接地排")]):
        s.append(device(cx + 22 + i * 122, railC_y + 34, pw, 52, tag, name, ""))

    # 接地母排标识
    s.append(line(cx + 22, railC_y + 104, cx + cw - 22, railC_y + 104, "#7cb342", 3))
    s.append(text(cx + 26, railC_y + 122, "PE 接地母排（黄绿 4mm²，接地电阻 ≤4Ω）", 11, "#33691e"))

    # 右侧说明栏
    rx0, ry0, rw0 = 650, 110, 400
    s.append(rect(rx0, ry0, rw0, 300, fill="#fbfcfe", stroke=C_FRAME, width=1.4))
    s.append(text(rx0 + 14, ry0 + 26, "布局要点", 14, C_FRAME, weight="bold"))
    pts = [
        "强弱电分侧走线：AC 进线与信号线分左右两侧进柜，",
        "   交叉处垂直交叉，降低共模干扰。",
        "开关电源分压：24V 供继电器/报警，5V/3.3V 供 MCU 与传感器，",
        "   模拟量与数字量各自回到端子区。",
        "继电器隔离：KA1 报警声、KA2 联锁切换、K1 安全急停，",
        "   强电负载经继电器触点，不直接由 MCU 驱动。",
        "接地：柜体 PE 母排单点接地，屏蔽层单端接地。",
        "散热：柜顶留通风间隙，柜内温升不影响 DHT11 测温。",
    ]
    for i, p in enumerate(pts):
        s.append(text(rx0 + 14, ry0 + 54 + i * 30, p, 11.5, "#444"))

    # 端口/接线表
    s.append(rect(rx0, ry0 + 320, rw0, 320, fill="#fbfcfe", stroke=C_FRAME, width=1.4))
    s.append(text(rx0 + 14, ry0 + 346, "主要元件与接口", 14, C_FRAME, weight="bold"))
    rows = [
        ("位号", "元件", "规格/接口"),
        ("STM32", "主控", "F103C8T6 / ADC×3 / I2C"),
        ("ESP8266", "WiFi 模块", "ESP-01S / AT 固件 / MQTT"),
        ("DHT11", "温湿度", "单总线 3.3V"),
        ("ACS712", "电流互感", "20A / 模拟输出→ADC"),
        ("分压网络", "电压采集", "0~30V DC → ADC"),
        ("OLED", "显示", "SSD1306 / I2C"),
        ("KA1/KA2/K1", "继电器", "报警/联锁/急停"),
        ("PSU", "开关电源", "220VAC → 24V & 5V"),
    ]
    for i, (a, b, c) in enumerate(rows):
        yy = ry0 + 368 + i * 27
        if i == 0:
            s.append(rect(rx0 + 10, yy - 17, rw0 - 20, 24, fill="#eef3fa", stroke="none", width=0, rx=0))
            s.append(text(rx0 + 20, yy, a, 11.5, C_FRAME, weight="bold"))
            s.append(text(rx0 + 110, yy, b, 11.5, C_FRAME, weight="bold"))
            s.append(text(rx0 + 210, yy, c, 11.5, C_FRAME, weight="bold"))
        else:
            s.append(text(rx0 + 20, yy, a, 11.5))
            s.append(text(rx0 + 110, yy, b, 11.5))
            s.append(text(rx0 + 210, yy, c, 11.5, "#555"))

    # 标题栏
    tw, th = 400, 96
    tx, ty = W - 40 - tw, H - 40 - th
    s.append(rect(tx, ty, tw, th, fill="#eef3fa", stroke=C_FRAME, width=2, rx=0))
    s.append(line(tx, ty + 32, tx + tw, ty + 32, C_FRAME, 1))
    s.append(line(tx, ty + 64, tx + tw, ty + 64, C_FRAME, 1))
    s.append(text(tx + 12, ty + 22, "数据采集柜布局图", 14, C_FRAME, weight="bold"))
    s.append(text(tx + 12, ty + 54, "版本 V1.2", 12))
    s.append(text(tx + 150, ty + 54, "2026-08-22", 12))
    s.append(text(tx + 12, ty + 86, "制图：李安", 12))
    s.append(text(tx + 150, ty + 86, "比例：非等比示意", 12, "#555"))

    # 底部备注
    s.append(text(44, H - 54,
                  "说明：本图为按文本字符画拓扑渲染的 SVG 布局图（非 AutoCAD 出图）；"
                  "柜体尺寸、导轨分区、元件位号与 txt 版一致。", 10.5, "#666"))

    s.append("</svg>")
    return "\n".join(s)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"已生成 {OUT.relative_to(ROOT)}  ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
