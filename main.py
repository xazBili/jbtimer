import os
import sys
import traceback

from PyQt6.QtWidgets import QApplication, QMessageBox

from app import MainWindow


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def handle_exception(exc_type, exc_value, exc_tb):
    text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        with open(os.path.join(app_dir(), "error.log"), "a", encoding="utf-8") as handle:
            handle.write(text + "\n")
    except OSError:
        pass
    try:
        QMessageBox.critical(None, "程序出错", text[-1200:])
    except Exception:
        pass


def run():
    sys.excepthook = handle_exception
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
