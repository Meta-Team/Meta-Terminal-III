import typing
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QToolButton
from graph_group_ui import Ui_GraphGroup
from graph_widget import GraphWidget
from data_manager import GroupData


class GraphGroup(QWidget, Ui_GraphGroup):

    LAYOUT_PLAN = [
        # One
        [[0, 0, 1, 1]],
        # Two
        [[0, 0, 1, 1], [0, 1, 1, 1]],
        # Three
        [[0, 0, 2, 1], [0, 1, 1, 1], [1, 1, 1, 1]],
        # Four
        [[0, 0, 1, 1], [0, 1, 1, 1], [1, 0, 1, 1], [1, 1, 1, 1]]
    ]

    def __init__(self, group: GroupData, parent: typing.Optional['QWidget'] = None) -> None:
        super(QWidget, self).__init__(parent)
        self.setupUi(self)
        self.buttons: [QToolButton] = []
        self.graphs: [GraphWidget] = []
        for i in range(len(self.LAYOUT_PLAN)):
            button = QToolButton(parent=self)
            button.setText(str(i + 1))
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.toggled.connect(self.update_layout)
            self.buttons.append(button)
            self.control_panel_layout.addWidget(button)

            graph = GraphWidget(group=group, parent=self)
            self.graphs.append(graph)

        self.buttons[-1].click()

    @pyqtSlot()
    def update_layout(self):
        count = self.buttons.index(self.sender()) + 1
        plan = self.LAYOUT_PLAN[count - 1]
        for i in reversed(range(len(self.LAYOUT_PLAN))):
            graph = self.graphs[i]
            if i < count:
                graph.setVisible(True)
                self.containe_grid_layout.addWidget(graph, plan[i][0], plan[i][1], plan[i][2], plan[i][3])
            else:
                graph.setVisible(False)
                self.containe_grid_layout.removeWidget(graph)


if __name__ == '__main__':
    import sys
    import data_manager

    app = QApplication(sys.argv)

    m, groups = data_manager._test()
    w = GraphGroup(groups[0])
    w.show()

    sys.exit(app.exec_())