# -*- coding: utf-8 -*-
"""
tests/test_deliverables.py —— 交付物完整性门禁
=============================================

本仓的"电气图纸"交付物由脚本生成（文本字符画拓扑 → SVG 布局图），
本文件把它固化为断言，防止文件被误删或生成脚本失效后 CI 仍显示绿色：

  1. SVG 布局图存在、结构合法、含关键位号与柜体尺寸；
  2. 与 txt 字符画版共享同一套拓扑（位号一致，防口径漂移）；
  3. 生成脚本存在且带 UTF-8 输出保护。

说明：本文件只做存在性与内容断言（标准库即可），不实际重跑生成脚本，
      以免 CI 依赖字体/渲染环境。
"""

import re
from pathlib import Path

# 本文件位于 <repo>/Python上位机/tests/，故仓库根需上溯三层
ROOT = Path(__file__).resolve().parent.parent.parent

SVG_PATH = ROOT / "电气图纸" / "数据采集柜布局图.svg"
TXT_PATH = ROOT / "电气图纸" / "数据采集柜布局图.txt"
GEN_SCRIPT = ROOT / "scripts" / "gen_cabinet_layout.py"

# 三导轨分区上的关键位号（与 txt 版一致）
KEY_TAGS = ["QF1", "FU1", "PSU-24V", "PSU-5V", "STM32", "ESP8266", "KA1", "KA2", "K1", "PE"]


def test_svg_exists_and_valid():
    assert SVG_PATH.is_file(), "数据采集柜布局图.svg 缺失"
    svg = SVG_PATH.read_text(encoding="utf-8")
    assert svg.lstrip().startswith("<svg"), "不是合法 SVG（缺少 <svg 根元素）"
    assert svg.rstrip().endswith("</svg>"), "SVG 未闭合"
    assert SVG_PATH.stat().st_size > 4096, "SVG 体积过小，疑似生成失败"


def test_svg_contains_key_components():
    svg = SVG_PATH.read_text(encoding="utf-8")
    missing = [t for t in KEY_TAGS if t not in svg]
    assert not missing, f"布局图缺少关键位号：{missing}"


def test_svg_declares_cabinet_and_rail_zones():
    """柜体尺寸与三条导轨分区必须体现在图内。"""
    svg = SVG_PATH.read_text(encoding="utf-8")
    assert "400(W)×600(H)×200(D)" in svg, "未标注柜体尺寸"
    for zone in ("导轨 A", "导轨 B", "导轨 C"):
        assert zone in svg, f"缺少分区标注：{zone}"


def test_svg_and_txt_share_topology():
    """SVG 与 txt 字符画版必须描述同一套元件（防两者漂移）。"""
    assert TXT_PATH.is_file(), "txt 字符画版缺失"
    txt = TXT_PATH.read_text(encoding="utf-8")
    svg = SVG_PATH.read_text(encoding="utf-8")
    for tag in ("QF1", "FU1", "PSU-24V", "STM32", "ESP8266", "KA1", "KA2"):
        assert tag in txt, f"txt 版缺少 {tag}"
        assert tag in svg, f"SVG 缺少 {tag}"


def test_generator_script_exists_with_utf8_guard():
    assert GEN_SCRIPT.is_file(), "生成脚本缺失"
    src = GEN_SCRIPT.read_text(encoding="utf-8")
    assert re.search(r"reconfigure\(encoding", src), "生成脚本缺少 UTF-8 输出保护"
