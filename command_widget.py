import sys
import typing
from typing import List

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from time import time
from math import *

from typing import Optional, Union
from data_manager import GroupData, Command, CommandArgument, ChannelArgumentType


class OptionGroup(QWidget):

    button_toggled = pyqtSignal(int, bool)

    def __init__(self, options: [str], parent: typing.Optional['QWidget'] = None) -> None:
        super().__init__(parent=parent)
        self.hlayout = QHBoxLayout(self)
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.hlayout.setSpacing(0)
        self.selected_idx = None
        for i, option in enumerate(options):
            button = QToolButton(parent=self)
            button.setText(option)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setProperty("idx", i)
            button.toggled.connect(self.handle_button_toggled)
            self.hlayout.addWidget(button)
            if i == 0:
                button.click()

    @pyqtSlot(bool)
    def handle_button_toggled(self, checked: bool):
        sender = self.sender()
        idx = sender.property("idx")
        if checked:
            self.selected_idx = idx
        self.button_toggled.emit(idx, checked)


class CommandWidget(QWidget):

    user_message = pyqtSignal(str)
    send_command = pyqtSignal(str)

    def __init__(self, command: Command, channel: Optional[str], parent: typing.Optional['QWidget'] = None) -> None:
        super().__init__(parent=parent)

        self.command = command
        self.channel = channel
        self.command.arg_values_updated.connect(self.update_arg_values)

        self.grid_layout = QGridLayout(self)

        self.label = QLabel(text=command.name, parent=self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid_layout.addWidget(self.label, 0, 0, 2, 1)

        self.set_button = QPushButton(text="Set", parent=self)
        self.set_button.clicked.connect(self.send_set_command)
        if command.has_optional_arg:
            self.get_button = QPushButton(text="Get", parent=self)
            self.set_button.clicked.connect(self.send_get_command)
            self.grid_layout.addWidget(self.set_button, 0, 1, 1, 1)
            self.grid_layout.addWidget(self.get_button, 1, 1, 1, 1)
        else:
            self.get_button = None
            self.grid_layout.addWidget(self.set_button, 0, 1, 2, 1)

        self.arg_labels: [QLabel] = []
        self.arg_edits: [Union[QLineEdit, QGroupBox]] = []
        for i, arg in enumerate(command.args):
            label = QLabel(text=(arg.name + ("*" if not arg.optional else "")), parent=self)
            label.setAlignment(QtCore.Qt.AlignCenter)
            if len(arg.options) == 0:
                edit = QLineEdit(parent=self)
                edit.setMaximumWidth(100)
            else:
                edit = OptionGroup(options=arg.options, parent=parent)

            self.grid_layout.addWidget(label, 0, 2 + i, 1, 1)
            self.grid_layout.addWidget(edit, 1, 2 + i, 1, 1)
            self.arg_labels.append(label)
            self.arg_edits.append(edit)

        spacer = QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.grid_layout.addItem(spacer, 0, 2 + len(command.args), 2, 1)

    @pyqtSlot()
    def send_set_command(self):
        p = [self.command.name]
        if self.channel is not None:
            p.append(self.channel)
        for edit in self.arg_edits:
            if type(edit) is QLineEdit:
                p.append(edit.text())
            elif type(edit) is OptionGroup:
                p.append(str(edit.selected_idx))
            else:
                raise RuntimeError("Invalid edit type")
        self.send_command.emit(' '.join(p))

    @pyqtSlot()
    def send_get_command(self):
        p = [self.command.name]
        if self.channel is not None:
            p.append(self.channel)
        for label, edit in zip(self.arg_labels, self.arg_edits):
            if label.text().endswith('*'):  # required
                if type(edit) is QLineEdit:
                    p.append(edit.text())
                elif type(edit) is OptionGroup:
                    p.append(str(edit.selected_idx))
                else:
                    raise RuntimeError("Invalid edit type")
        self.send_command.emit(' '.join(p))

    @pyqtSlot(list)
    def update_arg_values(self, vals: list):
        if len(vals) != len(self.arg_edits):
            self.user_message.emit(f"Unexpected arg value count for {self.command.name}")
            return
        for edit, val in zip(self.arg_edits, vals):
            edit.setPlainText(str(val))


class GroupControlPanel(QTabWidget):

    user_message = pyqtSignal(str)
    send_command = pyqtSignal(str)

    def add_tab(self, name: str) -> (QScrollArea, QWidget, QVBoxLayout):
        area = QScrollArea(self)
        widget = QWidget()
        area.setWidget(widget)
        area.setWidgetResizable(True)
        layout = QVBoxLayout(widget)
        self.addTab(area, name)
        return area, widget, layout

    def create_command_widget(self, command: Command, channel: Optional[str], parent: QWidget, layout: QVBoxLayout):
        w = CommandWidget(command=command, channel=channel, parent=parent)
        w.user_message.connect(self.user_message)
        w.send_command.connect(self.send_command)
        layout.addWidget(w)  # before the spacer

    def __init__(self, group: GroupData, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.none_area, self.none_widget, self.none_layout = self.add_tab("None")
        self.all_area, self.all_widget, self.all_layout = self.add_tab("All")

        self.channel_areas: [QScrollArea] = []
        self.channel_widgets: [QWidget] = []
        self.channel_layouts: [QVBoxLayout] = []
        for channel in group.channels:
            area, widget, layout = self.add_tab(channel.name)
            self.channel_areas.append(area)
            self.channel_widgets.append(widget)
            self.channel_layouts.append(layout)

        for command in group.commands.values():
            if command.channel == ChannelArgumentType.NONE:
                self.create_command_widget(command, None, self.none_widget, self.none_layout)
            if command.channel == ChannelArgumentType.ALL or command.channel == ChannelArgumentType.CHANNEL_ALL:
                self.create_command_widget(command, 'A', self.all_widget, self.all_layout)
            if command.channel == ChannelArgumentType.CHANNEL or command.channel == ChannelArgumentType.CHANNEL_ALL:
                for i, (widget, layout) in enumerate(zip(self.channel_widgets, self.channel_layouts)):
                    self.create_command_widget(command, str(i), widget, layout)

        self.none_layout.addItem(QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.all_layout.addItem(QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        for layout in self.channel_layouts:
            layout.addItem(QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))


if __name__ == '__main__':
    import sys
    import data_manager

    app = QApplication(sys.argv)

    m, groups = data_manager._test()
    w = GroupControlPanel(groups[0])
    w.show()

    sys.exit(app.exec_())
