from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import QWidget

import config
import font_util


class BarDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.text = "00:00:00"
        self.pixmap = None

    def set_text(self, text):
        if text != self.text:
            self.text = text
            self.update()

    def set_image(self, path):
        pixmap = QPixmap(path) if path else QPixmap()
        self.pixmap = pixmap if not pixmap.isNull() else None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        outline_width = max(1, config.scaled(config.CARD_OUTLINE_WIDTH))
        inset = outline_width / 2
        width = self.width() - outline_width
        shadow_offset = config.scaled(config.CARD_SHADOW_OFFSET)
        height = self.height() - outline_width - shadow_offset
        radius = min(config.scaled(config.BAR_RADIUS), height / 2)

        shadow = QPainterPath()
        shadow.addRoundedRect(inset, inset + shadow_offset, width, height, radius, radius)
        painter.fillPath(shadow, QColor(config.CARD_SHADOW))

        bar = QPainterPath()
        bar.addRoundedRect(inset, inset, width, height, radius, radius)

        if config.STYLE == "glass":
            fill = QLinearGradient(0, inset, 0, inset + height)
            fill.setColorAt(0, QColor(config.CARD_FILL_TOP))
            fill.setColorAt(1, QColor(config.CARD_FILL_BOTTOM))
            painter.fillPath(bar, QBrush(fill))
        else:
            painter.fillPath(bar, QColor(config.CARD_FILL_TOP))

        if self.pixmap is not None:
            painter.save()
            painter.setClipPath(bar)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawPixmap(
                int(inset),
                int(inset),
                int(width),
                int(height),
                self.pixmap.scaled(
                    int(width),
                    int(height),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ),
            )
            painter.restore()
        elif config.STYLE == "glass":
            painter.save()
            painter.setClipPath(bar)
            highlight = QLinearGradient(0, inset, 0, inset + height * 0.55)
            highlight.setColorAt(0, QColor(config.GLASS_HIGHLIGHT))
            highlight.setColorAt(1, QColor("#00FFFFFF"))
            painter.fillPath(bar, QBrush(highlight))
            painter.restore()

        if config.STYLE == "glass":
            border = QLinearGradient(0, inset, 0, inset + height)
            border.setColorAt(0, QColor(config.CARD_BORDER_TOP))
            border.setColorAt(1, QColor(config.CARD_BORDER_BOTTOM))
            painter.setPen(QPen(QBrush(border), outline_width))
        else:
            painter.setPen(QPen(QColor(config.CARD_BORDER_TOP), outline_width))
        painter.drawPath(bar)

        font = font_util.value_font(config.BAR_FONT_SIZE)
        metrics = QFontMetrics(font)
        text_width = metrics.horizontalAdvance(self.text)
        padding = config.scaled(config.BAR_PADDING)
        x = self.width() - padding - text_width
        y = (self.height() - shadow_offset) / 2 + metrics.ascent() / 2

        text_path = QPainterPath()
        text_path.addText(x, y, font, self.text)
        painter.setPen(
            QPen(
                QColor(config.DIGIT_OUTLINE),
                config.scaled(config.DIGIT_OUTLINE_WIDTH_SMALL),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.strokePath(text_path, painter.pen())
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(text_path, QColor(config.DIGIT_FILL))
