
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
 
 
class Coordinatograph(QWidget):
    def __init__(self, title:str='', xLabel:str='', xUnit:str='', yLabel:str='', yUnit:str=''):
        super(Coordinatograph, self).__init__()
        self.resize(300, 150)
        pg.setConfigOptions(leftButtonPan=False)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.pw = pg.PlotWidget(self)
        pltItem = self.pw.getPlotItem()
        xAxis = pltItem.getAxis('left')
        yAxis = pltItem.getAxis('bottom')
        pltItem.setTitle(title)
        labelStyle = {'color': '#000', 'font-size': '10pt'}
        xAxis.setLabel(xLabel, units=xUnit, **labelStyle)
        yAxis.setLabel(yLabel, units=yUnit, **labelStyle)

        self.plot_data = self.pw.plot()
        self.plot_target = self.pw.plot()
        self.data_y = np.zeros(1000, dtype=np.float)
        self.target_y = np.zeros(1000, dtype=np.float)
        self.x_axis = np.linspace(0, 10, 1000, endpoint=False)
        self.pause = False
 
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.pw)
        self.setLayout(self.v_layout)
 
    def pause_plot(self):
        self.pause = True

    def start_plot(self):
        self.pause = False

    def update_value(self, new_data:float=0, new_target:float=0):
        if self.pause:
            return
        self.data_y = np.append(self.data_y[1:], new_data)
        self.target_y = np.append(self.target_y[1:], new_target)
        self.plot_data.setData(self.x_axis, self.data_y, pen='b')
        self.plot_target.setData(self.x_axis, self.target_y, pen='r')
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Coordinatograph('test', 'time', 's', 'value', 'A')
    demo.update_value()
    demo.show()
    sys.exit(app.exec_())