import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Param_List(QWidget):
    
    def __init__(self, parent:QWidget=None, param_list:list=[]):
        super(Param_List, self).__init__(parent=parent)

        
        self.listWidget = QListWidget()
        self.setup_list(param_list=param_list)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.listWidget)
        self.setLayout(main_layout)

    def setup_list(self, param_list:list):
        self.listWidget.clear()
        for param_text in param_list:
            param_item = Param_Item(self.listWidget, placeholder=param_text)
            self.listWidget.addItem(param_item)
            self.listWidget.setItemWidget(param_item, param_item.widget)

class Param_Item(QListWidgetItem):
    def __init__(self, parent:QListWidget=None, placeholder:str='temp'):
        super(Param_Item, self).__init__(parent=parent)
        self.param_box = QLineEdit()
        self.param_box.setPlaceholderText(placeholder)
        widget_layout = QHBoxLayout()
        widget_layout.addWidget(self.param_box)
        self.widget = QWidget()
        self.widget.setLayout(widget_layout)
        self.setSizeHint(self.widget.sizeHint())