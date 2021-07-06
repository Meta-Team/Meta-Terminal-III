import sys
from typing import List

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from graph import Coordinatograph


class ChartList(QListWidget):

    def __init__(self, parent: QWidget = None, motor_config: list = None):
        super(ChartList, self).__init__(parent=parent)

        self.name2idx = {}
        if motor_config is not None:
            self.setup_list_rows(motor_config)

    def setup_list_rows(self, motor_config: list):
        self.clear()
        self.name2idx = {}
        for i, motor_dict in enumerate(motor_config):
            chart_row_item = ChartRowItem(self, title=motor_dict['name'])
            self.addItem(chart_row_item)
            self.setItemWidget(chart_row_item, chart_row_item.widget)
            self.name2idx[motor_dict['name']] = i

    def update_chart(self, data_lines: List[str]):
        if data_lines[0] in self.name2idx:
            item = self.item(self.name2idx[data_lines[0]])
            item.update_row(data_lines[1:])

    def set_chart_height(self, height: int):
        for i in range(self.count()):
            self.item(i).set_chart_height(height)

    def set_chart_visibilities(self, angle: bool, velocity: bool, current: bool):
        for i in range(self.count()):
            self.item(i).set_chart_visibilities(angle, velocity, current)


class ChartRowItem(QListWidgetItem):

    def __init__(self, parent: QListWidget = None, title: str = 'temp'):
        super(ChartRowItem, self).__init__(parent=parent)
        self.title = QLabel(title)
        self.title.resize(30, 100)
        self.angle_coord = Coordinatograph(title='Angle', xLabel='angle', xUnit='degree', yLabel='time', yUnit='s')
        self.velocity_coord = Coordinatograph(title='Velocity', xLabel='velocity', xUnit='degree/s', yLabel='time', yUnit='s')
        self.current_coord = Coordinatograph(title='Current', xLabel='current', xUnit='mA', yLabel='time', yUnit='s')
        widget_layout = QHBoxLayout()
        widget_layout.addWidget(self.title)
        widget_layout.addWidget(self.angle_coord)
        widget_layout.addWidget(self.velocity_coord)
        widget_layout.addWidget(self.current_coord)
        self.widget = QWidget()
        self.widget.setObjectName(title)
        self.widget.setLayout(widget_layout)
        self.widget.setFixedHeight(250)
        self.setSizeHint(self.widget.size())

    def set_chart_height(self, height: int):
        self.widget.setFixedHeight(height)
        self.setSizeHint(self.widget.size())

    def set_chart_visibilities(self, angle: bool, velocity: bool, current: bool):
        self.angle_coord.setVisible(angle)
        self.velocity_coord.setVisible(velocity)
        self.current_coord.setVisible(current)

    def update_row(self, params: list):
        if len(params) != 6:
            return
        param_int = list(map(float, params))
        self.angle_coord.update_value(param_int[0], param_int[1])
        self.velocity_coord.update_value(param_int[2], param_int[3])
        self.current_coord.update_value(param_int[4], param_int[5])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    temp_motor_config = [{'name': 'motor_0'}, {'name': 'motor_1'}]
    demo = ChartList(motor_config=temp_motor_config)
    demo.show()
    sys.exit(app.exec_())
