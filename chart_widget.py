import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from graph import Coordinatograph


class Chart_List(QWidget):

    def __init__(self, parent:QWidget=None, motor_config:list=None):
        super(Chart_List, self).__init__(parent=parent)

        self.listWidget = QListWidget()
        if motor_config is not None:
            self.setup_list_rows(motor_config)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.listWidget)
        self.setLayout(main_layout)

    def setup_list_rows(self, motor_config:list):
        self.listWidget.clear()
        for motor_dict in motor_config:
            chart_row_item = Chart_Row_Item(self.listWidget, title=motor_dict['name'])
            self.listWidget.addItem(chart_row_item)
            self.listWidget.setItemWidget(chart_row_item, chart_row_item.widget)


class Chart_Row_Item(QListWidgetItem):
    def __init__(self, parent:QListWidget=None, title:str='temp'):
        super(Chart_Row_Item, self).__init__(parent=parent)
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
        self.widget.setLayout(widget_layout)
        self.setSizeHint(self.widget.sizeHint())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    temp_motor_config = [{'name':'motor_0'}, {'name':'motor_1'}]
    demo = Chart_List(motor_config=temp_motor_config)
    demo.show()
    sys.exit(app.exec_())