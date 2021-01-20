from PyQt5.QtWidgets import *
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QApplication


class LeftDockWidget(QWidget):
    def __init__(self, parent):
        super(LeftDockWidget, self).__init__(parent=parent)
        self.setStyleSheet("QWidget{border: 1px solid #FF0000;}")  # 设置样式
        self.setContentsMargins(0, 0, 0, 0)
        # 创建列表窗口，添加条目
        self.leftlist = QListWidget()
        self.leftlist.insertItem(0, '联系方式')
        self.leftlist.insertItem(1, '个人信息')
        self.leftlist.insertItem(2, '教育程度')
        # 水平布局，添加部件到布局中
        HBox = QHBoxLayout()
        HBox.addWidget(self.leftlist)
        self.setLayout(HBox)

    def left_list_connect(self, s):
        self.leftlist.currentRowChanged.connect(s)


class CentrolWidgetUI(QWidget):
    def __init__(self, parent):
        super(CentrolWidgetUI, self).__init__(parent=parent)
        self.setStyleSheet("QWidget{border: 1px solid #FF0000;}")  # 设置样式
        self.stack1 = QWidget()
        self.stack2 = QWidget()
        self.stack3 = QWidget()
        self.stack1UI()
        self.stack2UI()
        self.stack3UI()
        # 在QStackedWidget对象中填充了三个子控件
        self.stack = QStackedWidget(self)
        self.set_stack(self.stack1, self.stack2, self.stack3)
        # 水平布局，添加部件到布局中
        HBox = QHBoxLayout()
        HBox.addWidget(self.stack)
        self.setLayout(HBox)


    def set_stack(self, *args):
        for stack in args:
            self.stack.addWidget(stack)


    def stack1UI(self):
        layout = QFormLayout()
        layout.addRow('姓名', QLineEdit())
        layout.addRow('地址', QLineEdit())
        self.stack1.setLayout(layout)

    def stack2UI(self):
        # zhu表单布局，次水平布局
        layout = QFormLayout()
        sex = QHBoxLayout()
        # 水平布局添加单选按钮
        sex.addWidget(QRadioButton('男'))
        sex.addWidget(QRadioButton('女'))
        # 表单布局添加控件
        layout.addRow(QLabel('性别'), sex)
        layout.addRow('生日', QLineEdit())
        self.stack2.setLayout(layout)

    def stack3UI(self):
        # 水平布局
        layout = QHBoxLayout()
        # 添加控件到布局中
        layout.addWidget(QLabel('科目'))
        layout.addWidget(QCheckBox('物理'))
        layout.addWidget(QCheckBox('高数'))
        self.stack3.setLayout(layout)

    def display(self, index):
        # 设置当前可见的选项卡的索引
        self.stack.setCurrentIndex(index)



class StackDemo(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.docker_widget = LeftDockWidget(self) #左dock
        self.docker_widget.setContentsMargins(0, 0, 0, 0)
        self.central_widget = CentrolWidgetUI(self) #中心widget
        self.docker_widget.left_list_connect(self.central_widget.display)
        self.dock = QDockWidget('Dock', self)
        self.dock.setWidget(self.docker_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.setCentralWidget(self.central_widget)
        self.resize(600, 400)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = StackDemo()
    demo.show()
    sys.exit(app.exec_())