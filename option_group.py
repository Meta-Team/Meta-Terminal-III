from typing import Optional, List
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QToolButton, QHBoxLayout


class OptionGroup(QWidget):
    button_toggled = pyqtSignal(int, bool)
    selected_idx_changed = pyqtSignal(int)

    def __init__(self, options: Optional[List[str]] = None, parent: Optional['QWidget'] = None) -> None:
        super().__init__(parent=parent)
        self.hlayout = QHBoxLayout(self)
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.hlayout.setSpacing(0)
        self.selected_idx = None
        self.buttons: [QToolButton] = []
        if options is not None:
            for i, option in enumerate(options):
                self.append_option(option)

    def append_option(self, option: str):
        button = QToolButton(parent=self)
        button.setText(option)
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.setProperty("idx", len(self.buttons))
        button.toggled.connect(self.handle_button_toggled)
        self.hlayout.addWidget(button)
        self.buttons.append(button)
        if len(self.buttons) == 1:
            button.click()

    def clear(self):
        while len(self.buttons) > 0:
            button: QToolButton = self.buttons.pop()
            button.deleteLater()
        self.selected_idx = None

    @pyqtSlot(bool)
    def handle_button_toggled(self, checked: bool):
        sender = self.sender()
        idx = sender.property("idx")
        if checked:
            self.selected_idx = idx
            self.selected_idx_changed.emit(idx)
        self.button_toggled.emit(idx, checked)
