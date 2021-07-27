import typing
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from graph_widget import GraphWidget
from data_manager import GroupData


class GraphGroup(QWidget):
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
        self.glayout = QGridLayout(self)
        self.glayout.setContentsMargins(0, 0, 0, 0)
        self.graphs: [GraphWidget] = []
        for i in range(len(self.LAYOUT_PLAN)):  # create maximal number of graphs
            graph = GraphWidget(group=group, parent=self)
            self.graphs.append(graph)

    @pyqtSlot(int)
    def update_layout(self, plan_id: int):
        plan = self.LAYOUT_PLAN[plan_id]
        for i in reversed(range(len(self.LAYOUT_PLAN))):
            graph = self.graphs[i]
            if i < len(plan):
                graph.setVisible(True)
                self.glayout.addWidget(graph, plan[i][0], plan[i][1], plan[i][2], plan[i][3])
            else:
                graph.setVisible(False)
                self.glayout.removeWidget(graph)


if __name__ == '__main__':
    import sys
    import data_manager

    app = QApplication(sys.argv)

    m, groups = data_manager._test()
    w = GraphGroup(groups[0])
    w.update_layout(1)
    w.show()

    sys.exit(app.exec_())