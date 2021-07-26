import pyqtgraph
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QToolButton
from graph_widget_ui import Ui_GraphWidget
from data_manager import GroupData, PlotChannelData, PlotGraphData
from typing import Optional


class GraphWidget(QWidget, Ui_GraphWidget):

    def __init__(self, group: GroupData, parent=None) -> None:
        super(QWidget, self).__init__(parent)
        self.setupUi(self)
        self.group = group
        self.motor: Optional[PlotChannelData] = None
        self.graph: Optional[PlotGraphData] = None
        self.plts: [pyqtgraph.PlotItem] = []

        self.pw.addLegend()
        # self.pw.setConfigOptions(leftButtonPan=False)
        # self.pw.setConfigOption('background', 'w')
        # self.pw.setConfigOption('foreground', 'k')

        self.clear_button.clicked.connect(self.clear_graph)

        # Add motor switches
        for i, motor in enumerate(group.channels):
            motor_radio = QToolButton(parent=self.motor_container)
            motor_radio.setText(motor.name)
            motor_radio.setCheckable(True)
            motor_radio.setAutoExclusive(True)
            motor_radio.setProperty("motor_id", i)
            motor_radio.toggled.connect(self.handle_motor_radio_toggled)
            self.motor_container_layout.addWidget(motor_radio)
            motor_radio.show()
            if i == 0:
                motor_radio.click()

    @pyqtSlot(bool)
    def handle_motor_radio_toggled(self, checked: bool):
        if checked:
            # Remove all graph radio
            for i in reversed(range(self.graph_container_layout.count())):
                self.graph_container_layout.itemAt(i).widget().setParent(None)

            # Update current motor info
            sender = self.sender()
            motor_id = sender.property("motor_id")
            self.motor = self.group.channels[motor_id]

            # Add graph switches
            for i, graph in enumerate(self.group.channels[motor_id].graphs):
                graph_radio = QToolButton(parent=self.graph_container)
                graph_radio.setText(graph.name)
                graph_radio.setCheckable(True)
                graph_radio.setAutoExclusive(True)
                graph_radio.setProperty("graph_id", i)
                graph_radio.toggled.connect(self.handle_graph_radio_toggled)
                self.graph_container_layout.addWidget(graph_radio)
                graph_radio.show()
                if i == 0:
                    graph_radio.click()

    @pyqtSlot(bool)
    def handle_graph_radio_toggled(self, checked: bool):
        if checked:
            # Disconnect from previous graph info
            if self.graph is not None:
                self.graph.data_updated.disconnect(self.update_plots)

            # Update graph info
            sender = self.sender()
            graph_id = sender.property("graph_id")
            self.graph = self.motor.graphs[graph_id]

            # Connect with graph update signal
            self.graph.data_updated.connect(self.update_plots)

            # Prepare pyqtGraph plots
            self.plts.clear()
            for _ in self.graph.series:
                plt = self.pw.plot()
                self.plts.append(plt)

            # Trigger slot manually
            self.update_plots()

    @pyqtSlot()
    def update_plots(self):
        for i, series in enumerate(self.graph.series):
            self.plts[i].setData(series.data, name=series.name)

    @pyqtSlot()
    def clear_graph(self):
        for series in self.graph.series:
            series.data.clear()
        self.update_plots()


if __name__ == '__main__':
    import sys
    import data_manager

    app = QApplication(sys.argv)

    m, groups = data_manager._test()
    w = GraphWidget(groups[1])
    w.show()

    sys.exit(app.exec_())
