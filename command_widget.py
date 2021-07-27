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
from option_group import OptionGroup


class CommandWidget(QWidget):

    user_message = pyqtSignal(str)
    send_command = pyqtSignal(str)

    def __init__(self, command: Command, channel: Optional[str], parent: typing.Optional['QWidget'] = None) -> None:
        super().__init__(parent=parent)

        self.command = command
        self.channel = channel
        self.command.arg_values_updated.connect(self.update_arg_values)

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(text=command.pretty_name, parent=self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid_layout.addWidget(self.label, 0, 0, 2, 1)

        self.set_button = QPushButton(text="Set", parent=self)
        self.set_button.clicked.connect(self.send_set_command)
        if command.has_optional_arg:
            self.get_button = QPushButton(text="Get", parent=self)
            self.get_button.clicked.connect(self.send_get_command)
            self.grid_layout.addWidget(self.set_button, 0, 1, 1, 1)
            self.grid_layout.addWidget(self.get_button, 1, 1, 1, 1)
        else:
            self.get_button = None
            self.grid_layout.addWidget(self.set_button, 0, 1, 2, 1)

        col = 2

        self.arg_labels: [QLabel] = []
        self.arg_edits: [Union[QLineEdit, QGroupBox]] = []
        if self.channel is not None:
            label = QLabel(text="Channel*", parent=self)
            label.setAlignment(QtCore.Qt.AlignCenter)
            edit = QLabel(text=self.channel, parent=self)
            edit.setAlignment(QtCore.Qt.AlignCenter)
            self.arg_labels.append(label)
            self.arg_edits.append(edit)
            self.grid_layout.addWidget(label, 0, col, 1, 1)
            self.grid_layout.addWidget(edit, 1, col, 1, 1)
            col += 1

        for i, arg in enumerate(command.args):
            label = QLabel(text=(arg.name + ("*" if not arg.optional else "")), parent=self)
            label.setAlignment(QtCore.Qt.AlignCenter)
            if len(arg.options) == 0:
                edit = QLineEdit(parent=self)
                edit.setMaximumWidth(100)
            else:
                edit = OptionGroup(options=arg.options, parent=parent)

            self.grid_layout.addWidget(label, 0, col, 1, 1)
            self.grid_layout.addWidget(edit, 1, col, 1, 1)
            col += 1
            self.arg_labels.append(label)
            self.arg_edits.append(edit)

        spacer = QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.grid_layout.addItem(spacer, 0, col, 2, 1)

    def send_commend_from_input(self, all_required: bool):
        p = [self.command.name]
        for label, edit in zip(self.arg_labels, self.arg_edits):
            if all_required or label.text().endswith('*'):  # required
                if type(edit) is QLineEdit:
                    if edit.text() == "":
                        self.user_message.emit(f"Argument {label.text()} is missing")
                        return
                    p.append(edit.text())
                elif type(edit) is OptionGroup:
                    if edit.selected_idx is None:
                        self.user_message.emit(f"Argument {label.text()} is missing")
                        return
                    p.append(str(edit.selected_idx))
                elif type(edit) is QLabel:
                    p.append(edit.text())
                else:
                    raise RuntimeError("Invalid edit type")
        self.send_command.emit(' '.join(p))

    @pyqtSlot()
    def send_set_command(self):
        self.send_commend_from_input(all_required=True)

    @pyqtSlot()
    def send_get_command(self):
        self.send_commend_from_input(all_required=False)

    @pyqtSlot(list)
    def update_arg_values(self, vals: list):
        if len(vals) != len(self.arg_edits):
            self.user_message.emit(f"Unexpected arg value count for {self.command.name}")
            return
        for edit, val in zip(self.arg_edits, vals):
            edit.setPlainText(str(val))


class GroupControlPanel(QWidget):

    user_message = pyqtSignal(str)
    send_command = pyqtSignal(str)

    def add_tab(self, name: str) -> (QScrollArea, QWidget, QVBoxLayout):
        area = QScrollArea(self)
        area.setFrameShape(QFrame.NoFrame)
        widget = QWidget()
        area.setWidget(widget)
        area.setWidgetResizable(True)
        layout = QVBoxLayout(widget)
        self.stack_layout.addWidget(area)
        self.channel_switches.append_option(name)
        return area, widget, layout

    def create_command_widget(self, command: Command, channel: Optional[str], parent: QWidget, layout: QVBoxLayout):
        w = CommandWidget(command=command, channel=channel, parent=parent)
        w.user_message.connect(self.user_message)
        w.send_command.connect(self.send_command)
        layout.addWidget(w)  # before the spacer

    def __init__(self, group: GroupData, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.channel_switches = OptionGroup(parent=self)
        self.grid_layout.addWidget(self.channel_switches, 0, 0, 1, 1)
        self.grid_layout.addItem(QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum),
                                 0, 1, 1, 1)

        self.container = QWidget()
        self.grid_layout.addWidget(self.container, 1, 0, 1, 2)
        self.stack_layout = QStackedLayout(self.container)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)
        self.channel_switches.selected_idx_changed.connect(self.stack_layout.setCurrentIndex)

        self.none_area, self.none_widget, self.none_layout = self.add_tab("None")
        self.all_area, self.all_widget, self.all_layout = self.add_tab("All")

        self.channel_areas: [QScrollArea] = []
        self.channel_widgets: [QWidget] = []
        self.channel_layouts: [QVBoxLayout] = []
        for channel in group.channels:
            area, widget, layout = self.add_tab(channel.pretty_name)
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
