import pyqtgraph
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QToolButton
from graph_widget_ui import Ui_GraphWidget
from data_manager import GroupData, PlotChannelData, PlotGraphData
from typing import Optional

pyqtgraph.setConfigOptions(leftButtonPan=False)
pyqtgraph.setConfigOption('background', 'w')
pyqtgraph.setConfigOption('foreground', 'k')


class GraphWidget(QWidget, Ui_GraphWidget):
    COLOR_PALETTE = ['b', 'r', 'g', 'c', 'm', 'k', 'w']

    def __init__(self, group: GroupData, parent=None) -> None:
        super(QWidget, self).__init__(parent)
        self.setupUi(self)
        self.group = group
        self.motor: Optional[PlotChannelData] = None
        self.graph: Optional[PlotGraphData] = None
        self.plts: [pyqtgraph.PlotItem] = []

        self.plt_item: pyqtgraph.PlotItem = self.pw.getPlotItem()
        self.plt_item.setMenuEnabled(False)
        self.plt_item.setMouseEnabled(x=False, y=False)
        self.plt_item.hideButtons()
        self.plt_item.addLegend()
        self.plt_item.legend.anchor((0, 0), (0, 0))

        # Add channel switches
        for i, channel in enumerate(group.channels):
            channel_radio = QToolButton(parent=self.channel_container)
            channel_radio.setText(channel.pretty_name)
            channel_radio.setCheckable(True)
            channel_radio.setAutoExclusive(True)
            channel_radio.setProperty("motor_id", i)
            channel_radio.toggled.connect(self.handle_motor_radio_toggled)
            self.channel_container_layout.addWidget(channel_radio)
            channel_radio.show()
            if i == 0:
                channel_radio.click()

    @pyqtSlot(bool)
    def handle_motor_radio_toggled(self, checked: bool):
        if checked:
            self.plts.clear()
            self.plt_item.clear()

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
            self.plts.clear()
            self.plt_item.clear()

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
            for i, series in enumerate(self.graph.series):
                plt = self.plt_item.plot(pen=self.COLOR_PALETTE[i], name=series.name)
                self.plts.append(plt)

            # Trigger slot manually
            self.update_plots()

    @pyqtSlot()
    def update_plots(self):
        for i, series in enumerate(self.graph.series):
            self.plts[i].setData(series.data)


if __name__ == '__main__':
    import sys
    import data_manager

    app = QApplication(sys.argv)

    m, groups = data_manager._test()
    w = GraphWidget(groups[1])
    w.show()

    sys.exit(app.exec_())
