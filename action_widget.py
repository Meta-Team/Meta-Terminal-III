import sys
from typing import List

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Action_Panel(QWidget):
    
    def __init__(self, parent:QWidget=None, command_list:list=[], predefined:dict={}, send_callback=print):
        super(Action_Panel, self).__init__(parent=parent)

        self.vlistWidget = QListWidget()
        self.vlistWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.vlistWidget.setDefaultDropAction(Qt.MoveAction)
        self.vlistWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        if command_list:
            self.setup_list_rows(command_list, predefined=predefined, send_callback=send_callback)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.vlistWidget)
        self.setLayout(main_layout)

    def setup_list_rows(self, command_list:list, predefined:dict={}, send_callback=print):
        self.vlistWidget.clear()

        for command in command_list:
            command_widget = Action_Widget_Line(self.vlistWidget, command=command, predefined=predefined, send_callback=send_callback)
            self.vlistWidget.addItem(command_widget)
            self.vlistWidget.setItemWidget(command_widget, command_widget.widget)
    
    def get_elements(self):
        current_items = self.vlistWidget.selectedItems()
        ret = []
        for item in current_items:
            command_name = item.widget.findChild(QLabel).text()
            params = item.get_params()
            ret.append((command_name, params))
        return ret

    def set_elements(self, elements:List[str]):
        elements_dict = {}
        for element in elements:
            command_name, params = element.split(' ', 1)
            elements_dict[command_name] = params
        for i in range(self.vlistWidget.count()):
            command_name = self.vlistWidget.item(i).widget.findChild(QLabel).text()
            if command_name in elements_dict:
                self.vlistWidget.item(i).set_params(elements_dict[command_name].split())

    def clear_elements(self):
        for item in self.vlistWidget.selectedItems():
            item.clear_params()

class Action_Widget_Line(QListWidgetItem):
    
    def __init__(self, parent:QWidget=None, command:str='', predefined:dict={}, send_callback=print):
        super(Action_Widget_Line, self).__init__(parent=parent)

        items = command.split()
        if len(items) <= 1:
            command_name, params = command, []
        else:
            command_name, params = items[0], items[1:]
        
        command_tokens = []
        param_list = []
        command_tokens.append(command_name)
        for param in params:
            if param in predefined:
                command_tokens.append(str(predefined[param]))
            else:
                command_tokens.append('%s')
                param_list.append(param)

        main_layout = QHBoxLayout()
        send_button = QPushButton('send')
        send_button.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        label = QLabel(command_name)
        label.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        main_layout.addWidget(send_button)
        main_layout.addWidget(label)
        
        self.widget_list = []
        if param_list:
            for param_text in param_list:
                param_block = QWidget()
                param_block.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
                param_layout = QVBoxLayout(param_block)
                param_layout.setContentsMargins(0,0,0,0)
                param_layout.sizeConstraint()
                param_block.setLayout(param_layout)
                new_label = QLabel(param_text, parent=param_block)
                new_label.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
                new_widget = QLineEdit(param_block)
                new_widget.setMaximumSize(80, 25)
                param_layout.addWidget(new_label)
                param_layout.addWidget(new_widget)
                param_layout.setAlignment(new_label, Qt.AlignHCenter)
                param_layout.setAlignment(new_widget, Qt.AlignHCenter)
                self.widget_list.append(new_widget)
                main_layout.addWidget(param_block)
        
        main_layout.addStretch()

        command_str_format = ' '.join(command_tokens)
        def call_callback():
            send_callback(command_str_format % self.get_params())

        send_button.clicked.connect(call_callback)

        self.widget = QWidget()
        self.widget.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.widget.setLayout(main_layout)
        self.setSizeHint(self.widget.sizeHint())
        left_margin, right_margin = main_layout.contentsMargins().left(), main_layout.contentsMargins().right()
        main_layout.setContentsMargins(left_margin, 0, right_margin, 0)

    def get_params(self):
        params = (widget.text() for widget in self.widget_list)
        return tuple(params)

    def set_params(self, params:List[str]):
        if len(params) != len(self.widget_list):
            return
        for param, widget in zip(params, self.widget_list):
            widget.setText(param)

    def clear_params(self):
        for widget in self.widget_list:
            widget.setText('')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Action_Panel(command_list=['test_command motor_id test', 'test_command_2 test_2 input2', 'single_command motor_id', 'single_command motor_id'], predefined={'motor_id':41})
    demo.show()
    sys.exit(app.exec_())