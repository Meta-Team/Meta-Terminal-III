import sys
from typing import List

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from time import time
from math import *

class Command_Panel(QWidget):
    
    def __init__(self, parent:QWidget=None, command_list:list=[], predefined:dict={}, send_callback=print):
        super(Command_Panel, self).__init__(parent=parent)

        self.vlistWidget = QListWidget()
        self.vlistWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.vlistWidget.setDefaultDropAction(Qt.MoveAction)
        self.vlistWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.hlistLayout = QHBoxLayout()
        self.button_list = []
        self.space_holder = QSpacerItem(10,10, QSizePolicy.Expanding)
        self.hlistLayout.addSpacerItem(self.space_holder)
        
        if command_list:
            self.setup_list_rows(command_list, predefined=predefined, send_callback=send_callback)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.hlistLayout)
        main_layout.addWidget(self.vlistWidget)
        self.setLayout(main_layout)

    def setup_list_rows(self, command_list:list, predefined:dict={}, send_callback=print):
        self.vlistWidget.clear()
        for widget in self.button_list:
            self.hlistLayout.removeWidget(widget)
        self.hlistLayout.removeItem(self.space_holder)
        self.button_list = []

        for command in command_list:
            tokens = command.split()
            if len(tokens) == 0:
                continue
            if len(tokens) == 1 or all([param in predefined for param in tokens[1:]]):
                command_widget = Command_Widget_Button(self, command=command, predefined=predefined, send_callback=send_callback)
                self.hlistLayout.addWidget(command_widget)
                self.button_list.append(command_widget)
            else:
                command_widget = Command_Widget_Line(self.vlistWidget, command=command, predefined=predefined, send_callback=send_callback)
                self.vlistWidget.addItem(command_widget)
                self.vlistWidget.setItemWidget(command_widget, command_widget.widget)
        self.hlistLayout.addSpacerItem(self.space_holder)
    
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

class param_widget(QWidget):
    def __init__(self, param_text, maximumWidth=80, parent=None):
        super(param_widget, self).__init__(parent=parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        param_layout = QVBoxLayout(self)
        param_layout.setContentsMargins(0,0,0,0)
        param_layout.sizeConstraint()
        self.setLayout(param_layout)
        self.new_label = QLabel(param_text, parent=self)
        self.new_label.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.new_widget = QLineEdit(self)
        self.new_widget.setMaximumSize(maximumWidth, 25)
        param_layout.addWidget(self.new_label)
        param_layout.addWidget(self.new_widget)
        param_layout.setAlignment(self.new_label, Qt.AlignHCenter)
        param_layout.setAlignment(self.new_widget, Qt.AlignHCenter)

    def get_param(self):
        return self.new_widget.text()
    
    def set_param(self, text:str):
        self.new_widget.setText(text)

class Command_Widget_Line(QListWidgetItem):
    
    def __init__(self, parent:QWidget=None, command:str='', predefined:dict={}, send_callback=print):
        super(Command_Widget_Line, self).__init__(parent=parent)

        self.send_callback = send_callback

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

        self.command_str_format = ' '.join(command_tokens)

        main_layout = QHBoxLayout()

        self.time_param = param_widget('t(ms)', maximumWidth=40)
        self.process_bar = QProgressBar()
        self.process_bar.setMaximumSize(80, 25)
        self.process_bar.setVisible(False)
        self.timer = QTimer()
        self.start_time = time()
        self.duration = 0
        self.timer.timeout.connect(self.__timeout_callback)

        self.send_button = QPushButton('send')
        self.send_button.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.label = QLabel(command_name)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        main_layout.addWidget(self.time_param)
        main_layout.addWidget(self.process_bar)
        main_layout.addWidget(self.send_button)
        main_layout.addWidget(self.label)
        
        self.widget_list = []
        if param_list:
            for param_text in param_list:
                param_block = param_widget(param_text=param_text)
                self.widget_list.append(param_block)
                main_layout.addWidget(param_block)
        
        main_layout.addStretch()

        self.send_button.clicked.connect(self.__send_button_clicked)

        self.widget = QWidget()
        self.widget.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.widget.setLayout(main_layout)
        self.setSizeHint(self.widget.sizeHint())
        left_margin, right_margin = main_layout.contentsMargins().left(), main_layout.contentsMargins().right()
        main_layout.setContentsMargins(left_margin, 0, right_margin, 0)

    def __timeout_callback(self):
        t = (time() - self.start_time) * 1000
        step = int(t / self.duration * 100)
        if step >= 100:
            self.timer.stop()
            self.process_bar.setVisible(False)
            self.send_button.setEnabled(True)
        else:
            self.send_callback(self.command_str_format % self.get_params(t))
            self.process_bar.setValue(step)

    def __send_button_clicked(self):
        time_str = self.time_param.get_param()
        if time_str == '':
            self.send_callback(self.command_str_format % self.get_params())
        else:
            self.duration = int(time_str)
            self.send_button.setEnabled(False)
            self.process_bar.setValue(0)
            self.process_bar.setVisible(True)
            self.start_time = time()
            self.timer.start(20)

    def get_params(self, t:float=-1):
        if t < 0:
            params = (widget.get_param() for widget in self.widget_list)
        else:
            params = []
            for widget in self.widget_list:
                params.append(str(eval(widget.get_param())))
        return tuple(params)

    def set_params(self, params:List[str]):
        if len(params) != len(self.widget_list):
            return
        for param, widget in zip(params, self.widget_list):
            widget.set_param(param)

    def clear_params(self):
        for widget in self.widget_list:
            widget.set_param('')

class Command_Widget_Button(QPushButton):
    
    def __init__(self, parent:QWidget=None, command:str='', predefined:dict={}, send_callback=print):
        super(Command_Widget_Button, self).__init__(parent=parent)

        items = command.split()
        if len(items) <= 1:
            command_name, params = command, []
        else:
            command_name, params = items[0], items[1:]

        command_tokens = []
        command_tokens.append(command_name)
        for param in params:
            command_tokens.append(str(predefined[param]))
        command_str = ' '.join(command_tokens)

        def call_callback():
            send_callback(command_str)

        self.clicked.connect(call_callback)
        self.setText(command_name)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Command_Panel(command_list=['test_command motor_id test', 'test_command_2 test_2 input2', 'single_command motor_id', 'single_command_2 motor_id'], predefined={'motor_id':41})
    demo.show()
    sys.exit(app.exec_())