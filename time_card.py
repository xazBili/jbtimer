from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import QWidget

import config
import font_util


class TimeCard(QWidget):
    def __init__(self, unit, small=False, parent=None):
        super().__init__(parent)
        self.size = config.scaled(config.CARD_SIZE)
        self.setFixedSize(self.size, self.size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.value_text = "00"
        self.unit = unit
        self.small = small

    def set_value(self, text):
        if text != self.value_text:
            self.value_text = text
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        outline_width = max(1, config.scaled(config.CARD_OUTLINE_WIDTH))
        inset = outline_width / 2
        side = self.width() - outline_width
        radius = min(config.scaled(config.CARD_RADIUS), side / 2)
        shadow_offset = config.scaled(config.CARD_SHADOW_OFFSET)

        shadow = QPainterPath()
        shadow.addRoundedRect(inset, inset + shadow_offset, side, side, radius, radius)
        painter.fillPath(shadow, QColor(config.CARD_SHADOW))

        card = QPainterPath()
        card.addRoundedRect(inset, inset, side, side, radius, radius)
        painter.fillPath(card, QColor(config.CARD_FILL_TOP))
        painter.setPen(QPen(QColor(config.CARD_BORDER_TOP), outline_width))
        painter.drawPath(card)

        if config.STYLE == "glass":
            painter.save()
            painter.setClipPath(card)
            fill = QLinearGradient(0, inset, 0, inset + side)
            fill.setColorAt(0, QColor(config.CARD_FILL_TOP))
            fill.setColorAt(1, QColor(config.CARD_FILL_BOTTOM))
            painter.fillPath(card, QBrush(fill))
            highlight = QLinearGradient(0, inset, 0, inset + side * 0.55)
            highlight.setColorAt(0, QColor(config.GLASS_HIGHLIGHT))
            highlight.setColorAt(1, QColor("#00FFFFFF"))
            painter.fillPath(card, QBrush(highlight))
            painter.restore()
            border = QLinearGradient(0, inset, 0, inset + side)
            border.setColorAt(0, QColor(config.CARD_BORDER_TOP))
            border.setColorAt(1, QColor(config.CARD_BORDER_BOTTOM))
            painter.setPen(QPen(QBrush(border), outline_width))
            painter.drawPath(card)

        value_font = font_util.value_font(config.FONT_SIZE_SMALL if self.small else config.FONT_SIZE)
        unit_font = font_util.unit_font(self.small)
        value_metrics = QFontMetrics(value_font)
        unit_metrics = QFontMetrics(unit_font)

        value_width = value_metrics.horizontalAdvance(self.value_text)
        unit_width = unit_metrics.horizontalAdvance(self.unit)
        gap = config.scaled(config.UNIT_GAP)
        total = value_width + gap + unit_width

        available = side - config.scaled(14)
        if total > available:
            factor = available / total
            value_shrink = QFont(value_font)
            value_shrink.setPixelSize(max(8, int(value_metrics.height() * factor)))
            unit_shrink = QFont(unit_font)
            unit_shrink.setPixelSize(max(6, int(unit_metrics.height() * factor)))
            value_font, unit_font = value_shrink, unit_shrink
            value_metrics = QFontMetrics(value_font)
            unit_metrics = QFontMetrics(unit_font)
            value_width = value_metrics.horizontalAdvance(self.value_text)
            unit_width = unit_metrics.horizontalAdvance(self.unit)
            gap = config.scaled(config.UNIT_GAP)
            total = value_width + gap + unit_width

        x = (self.width() - total) / 2
        y = (self.height() - shadow_offset) / 2 + value_metrics.ascent() / 2

        value_path = QPainterPath()
        value_path.addText(x, y, value_font, self.value_text)
        unit_path = QPainterPath()
        unit_path.addText(x + value_width + gap, y, unit_font, self.unit)

        painter.setPen(
            QPen(
                QColor(config.DIGIT_OUTLINE),
                config.scaled(
                    config.DIGIT_OUTLINE_WIDTH_SMALL if self.small else config.DIGIT_OUTLINE_WIDTH
                ),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.strokePath(value_path, painter.pen())
        painter.strokePath(unit_path, painter.pen())
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(value_path, QColor(config.DIGIT_FILL))
        painter.fillPath(unit_path, QColor(config.DIGIT_FILL))
