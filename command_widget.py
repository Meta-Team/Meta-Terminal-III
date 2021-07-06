import sys
from typing import List

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from time import time
from math import *


class CommandPanel(QListWidget):

    def __init__(self, parent: QWidget = None, command_list: list = [], predefined: dict = {}, send_callback=print):
        super().__init__(parent=parent)

        self.hlist_item = None

        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        if command_list:
            self.setup_list_rows(command_list, predefined=predefined, send_callback=send_callback)

    def setup_list_rows(self, command_list: list, predefined: dict = {}, send_callback=print):
        self.hlist_item = None
        self.clear()

        for command in command_list:
            tokens = command.split()
            if len(tokens) == 0:
                continue
            if len(tokens) == 1 or all([param in predefined for param in tokens[1:]]):
                if self.hlist_item is None:
                    self.hlist_item = QWidget()
                    self.hlist_item.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
                    self.hlist_layout = QHBoxLayout()

                command_widget = CommandWidgetButton(self, command=command, predefined=predefined,
                                                     send_callback=send_callback)
                self.hlist_layout.addWidget(command_widget)
            else:
                command_widget = CommandWidgetLine(self, command=command, predefined=predefined,
                                                   send_callback=send_callback)
                self.addItem(command_widget)
                self.setItemWidget(command_widget, command_widget.widget)

        if self.hlist_item is not None:
            # Add spacer and set layout
            space_holder = QSpacerItem(10, 10, QSizePolicy.Expanding)
            self.hlist_layout.addSpacerItem(space_holder)
            self.hlist_item.setLayout(self.hlist_layout)

            # Add to the first of the QListWidgetItem
            list_item = QListWidgetItem()
            list_item.setSizeHint(self.hlist_item.sizeHint())
            self.insertItem(0, list_item)
            self.setItemWidget(list_item, self.hlist_item)

    def get_elements(self):
        current_items = self.selectedItems()
        ret = []
        for item in current_items:
            command_name = item.command_name
            params = item.get_params()
            ret.append((command_name, params))
        return ret

    def set_elements(self, elements: List[str]):
        elements_dict = {}
        for element in elements:
            command_name, params = element.split(' ', 1)
            elements_dict[command_name] = params
        for i in range(self.count()):
            command_name = self.item(i).command_name
            if command_name in elements_dict:
                self.item(i).set_params(elements_dict[command_name].split())

    def clear_elements(self):
        for item in self.selectedItems():
            item.clear_params()


class ParamWidget(QLineEdit):
    def __init__(self, param_text, maximum_width=80, parent=None):
        super(QLineEdit, self).__init__(parent=parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.setMaximumSize(maximum_width, 25)
        self.setPlaceholderText(param_text)
        self.setToolTip(param_text)

    def get_param(self):
        return self.text()

    def set_param(self, text: str):
        self.setText(text)


class CommandWidgetLine(QListWidgetItem):

    def __init__(self, parent: QWidget = None, command: str = '', predefined: dict = {}, send_callback=print):
        super().__init__(parent=parent)

        self.send_callback = send_callback

        items = command.split()
        if len(items) <= 1:
            command_name, params = command, []
        else:
            command_name, params = items[0], items[1:]
        self.command_name = command_name

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

        self.time_param = ParamWidget('t (ms)', maximum_width=50)

        self.process_bar = QProgressBar()
        self.process_bar.setMaximumSize(80, 25)
        self.process_bar.setVisible(False)

        self.timer = QTimer()
        self.start_time = time()
        self.duration = 0
        self.timer.timeout.connect(self.__timeout_callback)

        self.send_button = QPushButton(command_name)
        self.send_button.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))

        main_layout.addWidget(self.time_param)
        main_layout.addWidget(self.send_button)

        self.widget_list = []
        if param_list:
            for param_text in param_list:
                param_block = ParamWidget(param_text=param_text)
                self.widget_list.append(param_block)
                main_layout.addWidget(param_block)

        main_layout.addWidget(self.process_bar)
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

    def get_params(self, t: float = -1):
        if t < 0:
            params = (widget.get_param() for widget in self.widget_list)
        else:
            params = []
            for widget in self.widget_list:
                params.append(str(eval(widget.get_param())))
        return tuple(params)

    def set_params(self, params: List[str]):
        if len(params) != len(self.widget_list):
            return
        for param, widget in zip(params, self.widget_list):
            widget.set_param(param)

    def clear_params(self):
        for widget in self.widget_list:
            widget.set_param('')


class CommandWidgetButton(QPushButton):

    def __init__(self, parent: QWidget = None, command: str = '', predefined: dict = {}, send_callback=print):
        super(CommandWidgetButton, self).__init__(parent=parent)

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
    demo = CommandPanel(
        command_list=['test_command motor_id test', 'test_command_2 test_2 input2', 'single_command motor_id',
                      'single_command_2 motor_id'], predefined={'motor_id': 41})
    demo.show()
    sys.exit(app.exec_())
