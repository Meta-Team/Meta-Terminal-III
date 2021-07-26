import typing
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QSplitter, QHBoxLayout
from graph_group import GraphGroup
from command_widget import GroupControlPanel
from data_manager import GroupData, PlotChannelData


class GroupTab(QWidget):
    user_message = pyqtSignal(str)
    send_command = pyqtSignal(str)

    def __init__(self, group: GroupData, parent: typing.Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self.hlayout = QHBoxLayout(self)
        self.splitter = QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.graph_group = GraphGroup(group, self.splitter)
        self.control_panel = GroupControlPanel(group, self.splitter)
        self.control_panel.user_message.connect(self.user_message)
        self.control_panel.send_command.connect(self.send_command)
        self.hlayout.addWidget(self.splitter)

if __name__ == '__main__':
    import sys
    import data_manager

    app = QApplication(sys.argv)

    m, groups = data_manager._test()
    w = GroupTab(groups[0])
    w.show()

    sys.exit(app.exec_())