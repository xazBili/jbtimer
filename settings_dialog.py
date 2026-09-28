from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import settings as settings_module
import styles


class KeyButton(QPushButton):
    def __init__(self, key_code, parent=None):
        super().__init__(QKeySequence(key_code).toString(), parent)
        self.key_code = int(key_code)
        self.capturing = False
        self.setMinimumWidth(110)
        self.clicked.connect(self.begin_capture)

    def begin_capture(self):
        if self.capturing:
            return
        self.capturing = True
        self.setText("按下按键…")
        self.grabKeyboard()

    def finish_capture(self, key_code):
        self.key_code = int(key_code)
        self.capturing = False
        self.releaseKeyboard()
        self.setText(QKeySequence(self.key_code).toString())

    def keyPressEvent(self, event):
        if self.capturing:
            key = event.key()
            if key not in (Qt.Key.Key_unknown, Qt.Key.Key_Escape):
                self.finish_capture(key)
            else:
                self.finish_capture(self.key_code)
            event.accept()
            return
        super().keyPressEvent(event)


class SettingsDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.start_button = KeyButton(data["start"], self)
        self.pause_button = KeyButton(data["pause"], self)
        self.reset_button = KeyButton(data["reset"], self)

        form.addRow("开始计时", self.start_button)
        form.addRow("暂停计时", self.pause_button)
        form.addRow("清空计时", self.reset_button)

        self.scale_spin = QSpinBox(self)
        self.scale_spin.setRange(settings_module.MIN_SCALE, settings_module.MAX_SCALE)
        self.scale_spin.setSingleStep(10)
        self.scale_spin.setSuffix("%")
        self.scale_spin.setValue(int(data["scale"]))
        form.addRow("总体大小", self.scale_spin)

        self.style_combo = QComboBox(self)
        for key in styles.STYLES:
            self.style_combo.addItem(styles.NAMES.get(key, key), key)
        current = self.style_combo.findData(data["style"])
        if current >= 0:
            self.style_combo.setCurrentIndex(current)
        form.addRow("外观", self.style_combo)

        self.layout_combo = QComboBox(self)
        self.layout_combo.addItem("方块（时 / 分 / 秒）", "blocks")
        self.layout_combo.addItem("长条（时:分:秒，右对齐）", "bar")
        layout_index = self.layout_combo.findData(data["layout"])
        if layout_index >= 0:
            self.layout_combo.setCurrentIndex(layout_index)
        form.addRow("形状", self.layout_combo)

        self.image_edit = QLineEdit(data["image"], self)
        self.image_edit.setPlaceholderText("长条背景图片路径，可留空")
        pick_button = QPushButton("选择…", self)
        pick_button.clicked.connect(self.pick_image)
        clear_button = QPushButton("清除", self)
        clear_button.clicked.connect(lambda: self.image_edit.clear())
        image_row = QHBoxLayout()
        image_row.addWidget(self.image_edit, 1)
        image_row.addWidget(pick_button)
        image_row.addWidget(clear_button)
        image_widget = QWidget(self)
        image_widget.setLayout(image_row)
        self.image_widget = image_widget
        form.addRow("背景图片", image_widget)
        self.layout_combo.currentIndexChanged.connect(self.sync_image_row)
        self.sync_image_row()

        layout.addLayout(form)

        self.ms_check = QCheckBox("显示毫秒（额外增加一个方块）", self)
        self.ms_check.setChecked(bool(data["show_ms"]))
        layout.addWidget(self.ms_check)

        hint = QLabel("按键在任意界面都生效；点击按钮后按下新键即可更改", self)
        layout.addWidget(hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def sync_image_row(self):
        self.image_widget.setEnabled(self.layout_combo.currentData() != "bar")

    def pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择背景图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.webp *.gif);;所有文件 (*.*)",
        )
        if path:
            self.image_edit.setText(path)

    def result_data(self):
        return {
            "start": self.start_button.key_code,
            "pause": self.pause_button.key_code,
            "reset": self.reset_button.key_code,
            "show_ms": self.ms_check.isChecked(),
            "scale": self.scale_spin.value(),
            "style": self.style_combo.currentData(),
            "layout": self.layout_combo.currentData(),
            "image": self.image_edit.text().strip(),
        }
