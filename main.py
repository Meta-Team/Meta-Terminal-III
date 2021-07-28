import sys
import os
import typing

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from pyhocon import ConfigFactory

from connection import ConnectionBase, SerialConnection, SocketConnection
# from graph_widget import Coordinatograph
# from chart_widget import ChartList
# from command_widget import CommandPanel

from typing import Optional, List
from option_group import OptionGroup
from graph_group import GraphGroup
from command_widget import GroupControlPanel
from main_window_ui import Ui_MainWindow
from data_manager import *


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowTitle('Meta Terminal III')
        self.setWindowIcon(QtGui.QIcon('res/meta_logo.jpeg'))

        self.control_panels: List[GroupControlPanel] = []
        self.control_panel_stack = QStackedLayout(self.control_panel_container)
        self.control_panel_stack.setContentsMargins(0, 0, 0, 0)

        self.graph_groups: List[GraphGroup] = []
        self.graph_group_stack = QStackedLayout(self.graph_group_container)
        self.graph_group_stack.setContentsMargins(0, 0, 0, 0)

        self.group_switch = OptionGroup(parent=self)
        self.group_switch.selected_idx_changed.connect(self.control_panel_stack.setCurrentIndex)
        self.group_switch.selected_idx_changed.connect(self.graph_group_stack.setCurrentIndex)
        self.general_control_container_layout.addWidget(self.group_switch)

        self.general_control_container_layout.addItem(
            QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.clear_graph_button = QtWidgets.QPushButton(self.general_control_container)
        self.clear_graph_button.setText("Clear Graphs")
        self.general_control_container_layout.addWidget(self.clear_graph_button)

        self.graph_layout_switch = OptionGroup([str(v + 1) for v in range(len(GraphGroup.LAYOUT_PLAN))], parent=self)
        self.general_control_container_layout.addWidget(self.graph_layout_switch)

        self.normal_commands_group_layout.addStretch()

        self.m = DataManager()
        self.m.group_added.connect(self.setup_ui_for_group)
        self.m.normal_commands_added.connect(self.add_normal_commands)
        self.m.user_message.connect(self.handle_user_message)
        self.m.send_command.connect(self.handle_send_command)
        self.clear_graph_button.clicked.connect(self.m.clear_data)

        self.conn: Optional[ConnectionBase] = None
        self.received_data: str = ""

        self.reload_button.clicked.connect(self.reload_ui)
        self.connect_button.clicked.connect(self.handle_connect_button_click)
        self.clear_terminal_button.clicked.connect(lambda: self.terminal_edit.clear())
        self.send_command_button.clicked.connect(lambda: self.handle_send_command(self.command_edit.text()))

        self.v_splitter.setSizes([QWIDGETSIZE_MAX, 0])
        self.h_splitter.setSizes([QWIDGETSIZE_MAX, 0])

    @pyqtSlot(GroupData)
    def setup_ui_for_group(self, group: GroupData):

        control_panel = GroupControlPanel(group, self)
        control_panel.user_message.connect(self.handle_user_message)
        control_panel.send_command.connect(self.handle_send_command)
        self.control_panels.append(control_panel)
        self.control_panel_stack.addWidget(control_panel)

        graph_group = GraphGroup(group, self)
        self.graph_groups.append(graph_group)
        self.graph_group_stack.addWidget(graph_group)
        self.graph_layout_switch.selected_idx_changed.connect(graph_group.update_layout)
        graph_group.update_layout(self.graph_layout_switch.get_current_index())

        self.group_switch.append_option(group.name)  # do it at last since it may emit click signal

        self.v_splitter.setSizes([QWIDGETSIZE_MAX, QWIDGETSIZE_MAX])
        self.h_splitter.setSizes([self.left_container.sizeHint().width(), QWIDGETSIZE_MAX])

    @pyqtSlot()
    def reload_ui(self):
        while len(self.control_panels) > 0:
            control_panel = self.control_panels.pop()
            control_panel.deleteLater()
        while len(self.graph_groups) > 0:
            graph_group = self.graph_groups.pop()
            graph_group.deleteLater()
        self.group_switch.clear()
        for child in self.normal_commands_group.children():
            if type(child) is QPushButton:
                child.deleteLater()
        self.m.reload()  # send help command inside

    @pyqtSlot(str)
    def handle_user_message(self, message: str):
        self.statusbar.showMessage(message, 5000)

    @pyqtSlot(str)
    def handle_send_command(self, command: str):
        try:
            self.terminal_edit.append(f"<b>{command}</b>")
            self.conn.send_data(bytes(command + '\r', encoding='utf-8'))

        except Exception as err:
            self.handle_user_message(f"Fail to send command: {str(err)}")

    @pyqtSlot(list)
    def add_normal_commands(self, commands: list):
        for command in commands:
            button = QPushButton(text=command, parent=self.normal_commands_group)
            button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            self.normal_commands_group_layout.insertWidget(self.normal_commands_group_layout.count() - 1,
                                                           button)  # skip the stretch
            button.clicked.connect(self.handle_normal_command_button_click)

    @pyqtSlot()
    def handle_normal_command_button_click(self):
        sender: QPushButton = self.sender()
        self.handle_send_command(sender.text())

    @pyqtSlot(bytes)
    def process_data(self, data: bytes):
        self.received_data += data.decode(encoding='ascii', errors='replace')
        while (i := self.received_data.find('\r\n')) != -1:
            line = self.received_data[:i]

            if self.show_raw_check.isChecked():
                # Handle individually before process_line since process_line may emit commands before return
                self.terminal_edit.append(line)

            # In the following if, process_line must be the first to always run
            if self.m.process_line(line) is True and not self.show_raw_check.isChecked():
                # If fallback to this case, normal message didn't emit commands, so no need to worry about print order
                self.terminal_edit.append(line)

            self.received_data = self.received_data[i + 2:]

    @pyqtSlot()
    def handle_connect_button_click(self):
        if self.connect_button.text() == "Connect":
            method = self.connection_type_combo.currentText()
            device = self.connection_addr_combo.currentText()
            from connection import _TestConnection
            self.conn = _TestConnection("test")
            # if method == "Serial":
            #     self.conn = SerialConnection(device)
            # elif method == "TCP":
            #     self.conn = SocketConnection(device)
            self.received_data = ""
            self.conn.data_received.connect(self.process_data)
            self.conn.connection_changed.connect(self.handle_connection_change)
            self.conn.user_message.connect(self.handle_user_message)
            self.conn.start()
        else:
            if self.conn is not None:
                self.conn.stop()

    @pyqtSlot(bool)
    def handle_connection_change(self, connected: bool):
        if connected:
            self.connect_button.setText('Disconnect')
            self.reload_ui()
        else:
            self.connect_button.setText('Connect')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.showMaximized()
    sys.exit(app.exec_())
