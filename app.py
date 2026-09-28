from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QIcon
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

import config
import settings
import styles
from bar_display import BarDisplay
from keyboard_hook import GlobalKeys
from settings_dialog import SettingsDialog
from time_card import TimeCard
from timer_engine import TimerEngine


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowIcon(QIcon(config.ICON_FILE))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

        self.data = settings.load()
        config.SCALE = self.data["scale"] / 100
        styles.apply(self.data["style"])

        self.engine = TimerEngine()
        self.drag_offset = None
        self.cards = []
        self.bar = None

        self.root = QVBoxLayout(self)
        self.root.setSpacing(0)
        self.rebuild()

        self.hotkeys = GlobalKeys(self)
        self.hotkeys.pressed.connect(self.on_global_key)
        self.hotkeys.start()

        self.quitting = False
        self.build_tray()

        self.timer = self.startTimer(self.tick_interval())

    def tick_interval(self):
        return config.TICK_MS_FAST if self.data["show_ms"] else config.TICK_MS

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            child = item.layout()
            if child is not None:
                self.clear_layout(child)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def rebuild(self):
        self.clear_layout(self.root)
        self.cards = []
        self.bar = None

        if self.data["layout"] == "bar":
            self.root.setContentsMargins(0, 0, 0, 0)
            self.bar = BarDisplay(self)
            self.root.addWidget(self.bar)
            self.setFixedSize(
                config.scaled(config.BAR_WIDTH), config.scaled(config.BAR_HEIGHT)
            )
            return

        margin = config.scaled(config.MARGIN)
        self.root.setContentsMargins(margin, margin, margin, margin)
        row = QHBoxLayout()
        row.setSpacing(config.scaled(config.CARD_SPACING))

        self.cards = [
            TimeCard(config.UNITS["hour"]),
            TimeCard(config.UNITS["min"]),
            TimeCard(config.UNITS["sec"]),
        ]
        if self.data["show_ms"]:
            self.cards.append(TimeCard(config.UNITS["ms"], small=True))

        for card in self.cards:
            row.addWidget(card)
        self.root.addLayout(row)

        count = len(self.cards)
        width = (
            margin * 2
            + count * config.scaled(config.CARD_SIZE)
            + (count - 1) * config.scaled(config.CARD_SPACING)
        )
        height = margin * 2 + config.scaled(config.CARD_SIZE)
        self.setFixedSize(width, height)

    def refresh(self):
        elapsed = self.engine.current()
        h, m, s = self.engine.format(elapsed)

        if self.bar is not None:
            text = f"{h}:{m}:{s}"
            if self.data["show_ms"]:
                text += f".{int((elapsed - int(elapsed)) * 1000):03d}"
            self.bar.set_text(text)
            return

        for card, value in zip(self.cards, (h, m, s)):
            card.set_value(value)
        if self.data["show_ms"] and len(self.cards) > 3:
            self.cards[3].set_value(f"{int((elapsed - int(elapsed)) * 1000):03d}")

    def timerEvent(self, event):
        self.refresh()

    def build_tray(self):
        self.tray = QSystemTrayIcon(QIcon(config.ICON_FILE), self)
        self.tray.setToolTip(config.APP_NAME)
        self.tray.activated.connect(self.on_tray_activated)

        tray_menu = QMenu()
        tray_menu.addAction("显示 / 隐藏", self.toggle_visible)
        tray_menu.addAction("退出", self.quit_app)
        self.tray.setContextMenu(tray_menu)
        self.tray.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_visible()

    def toggle_visible(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()

    def show_menu(self, pos):
        menu = QMenu(self)
        menu.addAction("设置…", self.open_settings)
        menu.addSeparator()

        top_action = menu.addAction("窗口置顶")
        top_action.setCheckable(True)
        top_action.setChecked(bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))
        top_action.triggered.connect(self.set_always_top)

        menu.addSeparator()
        menu.addAction("隐藏到托盘", self.hide)
        menu.addAction("退出", self.quit_app)
        menu.exec(self.mapToGlobal(pos))

    def open_settings(self):
        dialog = SettingsDialog(self.data, self)
        if dialog.exec():
            self.data = dialog.result_data()
            settings.save(self.data)
            config.SCALE = self.data["scale"] / 100
            styles.apply(self.data["style"])
            self.killTimer(self.timer)
            self.rebuild()
            self.timer = self.startTimer(self.tick_interval())
            self.refresh()

    def set_always_top(self, checked):
        flags = self.windowFlags()
        if checked:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def request_reset(self):
        if self.engine.running:
            answer = QMessageBox.question(
                self,
                "确认清空",
                "计时正在进行中，确定要清空吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self.engine.reset()

    def on_global_key(self, vk):
        if vk == self.data["start"]:
            self.engine.start()
        elif vk == self.data["pause"]:
            self.engine.pause()
        elif vk == self.data["reset"]:
            self.request_reset()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
        event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
        event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.unsetCursor()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        event.accept()

    def quit_app(self):
        self.quitting = True
        self.close()

    def closeEvent(self, event):
        if not self.quitting:
            event.ignore()
            self.hide()
            self.tray.showMessage(config.APP_NAME, "已缩小到托盘，双击图标可重新打开")
            return
        self.hotkeys.stop()
        self.tray.hide()
        event.accept()
