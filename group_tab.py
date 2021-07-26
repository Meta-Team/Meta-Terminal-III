import typing
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QToolButton
from group_tab_ui import Ui_GroupTab
from graph_group import GraphGroup
from data_manager import GroupData


class GroupTab(QWidget, Ui_GroupTab):
    def __init__(self, group: GroupData, parent: typing.Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.graph_group = GraphGroup(group, self.splitter1)
        self.splitter1.insertWidget(0, self.graph_group)


if __name__ == '__main__':
    import sys
    import data_manager

    app = QApplication(sys.argv)

    m, groups = data_manager._test()
    w = GroupTab(groups[0])
    w.show()

    sys.exit(app.exec_())