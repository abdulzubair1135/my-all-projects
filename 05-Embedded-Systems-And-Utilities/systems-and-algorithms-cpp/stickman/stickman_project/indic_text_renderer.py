"""
indic_text_renderer.py
======================
High-precision Indic / Devanagari Hindi text rendering engine for Antigravity Video Production.
Uses Windows DirectWrite & Uniscribe via PyQt5 QPainter to achieve 100% proper OpenType
shaping, complex ligatures, rephs, matras, and conjuncts (e.g. क्या, क्यों, रिकॉर्डिंग).
Returns transparent RGBA PIL Images ready for instant alpha compositing onto frames.
"""

import sys
from PIL import Image

_app = None

def _get_qapp():
    global _app
    from PyQt5.QtWidgets import QApplication
    _app = QApplication.instance()
    if not _app:
        _app = QApplication(sys.argv)
    return _app

def render_indic_text_image(text, width, height, font_size=24, color=(24, 28, 36), bold=True, align="center"):
    """
    Renders complex Devanagari Hindi text into a transparent RGBA PIL Image.
    """
    _get_qapp()
    from PyQt5.QtGui import QImage, QPainter, QFont, QColor
    from PyQt5.QtCore import Qt

    qimg = QImage(width, height, QImage.Format_ARGB32)
    qimg.fill(QColor(0, 0, 0, 0))

    painter = QPainter(qimg)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    font = QFont("Nirmala UI", font_size)
    font.setBold(bold)
    painter.setFont(font)
    painter.setPen(QColor(color[0], color[1], color[2]))

    flags = Qt.TextWordWrap
    if align == "center":
        flags |= Qt.AlignCenter
    elif align == "left":
        flags |= (Qt.AlignLeft | Qt.AlignVCenter)
    elif align == "right":
        flags |= (Qt.AlignRight | Qt.AlignVCenter)

    painter.drawText(0, 0, width, height, flags, text)
    painter.end()

    # Fast memory copy from QImage buffer into PIL Image
    ptr = qimg.bits()
    ptr.setsize(qimg.byteCount())
    return Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "BGRA", 0, 1)
