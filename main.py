
import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from pyqtconfig import ConfigManager
from pyhocon import ConfigFactory

from device import Manager_Base, Serial_Manager, Bluetooth_Manager
from graph import Coordinatograph
from chart_widget import Chart_List, Param_List


class Meta_UI(QtWidgets.QTabWidget):

    def __init__(self):
        super(Meta_UI, self).__init__()
        self.communicate_manager = Manager_Base('')

        self.home_tab = QWidget()
        self.param_adjust_tab = QWidget()

        self.addTab(self.home_tab, 'Home')
        self.addTab(self.param_adjust_tab, 'Param')

        self.home_tab_setup()
        self.param_adjust_tab_setup()

        self.setWindowTitle('Meta Terminal III')
        self.setWindowIcon(QtGui.QIcon('res/meta_logo.jpeg'))

    def home_tab_setup(self):
        # Elements setup
        connection_port_combo = QComboBox()
        connection_port_list = ['serial', 'bluetooth 5.0']
        connection_port_combo.addItems(connection_port_list)

        port_device_text = QLineEdit()
        port_device_text.setPlaceholderText('port/device')

        connection_button = QPushButton()
        connection_button.setText('Connect')

        clear_data_button = QPushButton()
        clear_data_button.setText('Clear Data')

        terminal_display = QTextBrowser()
        terminal_display.resize(640, 480)

        command_line = QLineEdit()

        send_button = QPushButton()
        send_button.setText('send')

        hello_button = QPushButton()
        hello_button.setText('hello')

        # Layouts setup
        control_button_layout = QHBoxLayout()
        control_button_layout.addWidget(connection_port_combo)
        control_button_layout.addWidget(port_device_text)
        control_button_layout.addWidget(connection_button)
        control_button_layout.addWidget(clear_data_button)

        command_line_layout = QHBoxLayout()
        command_line_layout.addWidget(command_line)
        command_line_layout.addWidget(send_button)

        pre_define_command_layout = QGridLayout()
        pre_define_command_layout.addWidget(hello_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(control_button_layout)
        main_layout.addWidget(terminal_display)
        main_layout.addLayout(command_line_layout)
        main_layout.addLayout(pre_define_command_layout)

        # Event Callback Setup
        def update_terminal_display(input_str:str):
            cursor = terminal_display.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(input_str)
            terminal_display.setTextCursor(cursor)

        def process_feedback(feedback:bytes):
            update_terminal_display(feedback.decode(encoding='utf-8'))

        def update_connect_button(set_on:bool):
            if set_on:
                connection_button.setText('Disconnect')
            else:
                connection_button.setText('Connect')

        # Connections setup
        def send_msg():
            msg = command_line.text()
            try:
                self.communicate_manager.SendData(bytes(msg, encoding='utf-8'))
            except Exception as err:
                print(err)
                msg = 'Fail to send message!'
            update_terminal_display(msg + '\n')
            command_line.clear()

        def connection_button_clicked():
            if connection_button.text() == 'Connect':
                method = connection_port_combo.currentText()
                device = port_device_text.text()
                if method == 'serial':
                    self.communicate_manager = Serial_Manager(device)
                else:
                    return
                self.communicate_manager.device_signal.connect(process_feedback)
                self.communicate_manager.connection_signal.connect(update_connect_button)
                self.communicate_manager.start()
            else:
                if self.communicate_manager is not None:
                    self.communicate_manager.stop()

        send_button.clicked.connect(send_msg)
        connection_button.clicked.connect(connection_button_clicked)

        self.home_tab.setLayout(main_layout)

    def param_adjust_tab_setup(self):
        
        self.title_text = QLabel()
        title_font = QFont('Times New Roman', 20, QFont.Bold)
        self.title_text.setFont(title_font)
        self.title_text.setText('Temp')

        self.global_func_combo = QComboBox()

        self.global_func_param_list = Param_List(self.param_adjust_tab, ['temp_param'])
        self.global_func_param_list.flow
        self.global_func_send_button = QPushButton()
        self.global_func_send_button.setText('Send')

        self.load_config_file_button = QPushButton()
        self.load_config_file_button.setText('Load config')
        self.load_config_file_button.clicked.connect(self.open_file)

        global_func_layout = QHBoxLayout()
        global_func_layout.addWidget(self.global_func_combo)
        global_func_layout.addWidget(self.global_func_param_list)
        global_func_layout.addWidget(self.global_func_send_button)

        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_text)
        title_layout.addLayout(global_func_layout)
        title_layout.addWidget(self.load_config_file_button)

        self.chart_list = Chart_List(self.param_adjust_tab, [{'name':'temp'}])

        self.motor_combo = QComboBox()
        self.motor_enable_button = QPushButton()
        self.motor_enable_button.setText('Enable')
        self.func_combo = QComboBox()
        self.func_send_button = QPushButton()
        self.func_send_button.setText('Send')
        tool_layout_1 = QHBoxLayout()
        tool_layout_1.addWidget(self.motor_combo)
        tool_layout_1.addWidget(self.motor_enable_button)
        tool_layout_1.addWidget(self.func_combo)
        tool_layout_1.addWidget(self.func_send_button)

        self.param_input = QLineEdit()
        tool_layout_2 = QHBoxLayout()
        tool_layout_2.addWidget(self.param_input)

        self.clear_param_button = QPushButton()
        self.clear_param_button.setText('Clear')
        self.save_button = QPushButton()
        self.save_button.setText('Save')
        self.delete_button = QPushButton()
        self.delete_button.setText('Delete')
        tool_layout_3 = QHBoxLayout()
        tool_layout_3.addWidget(self.clear_param_button)
        tool_layout_3.addWidget(self.save_button)
        tool_layout_3.addWidget(self.delete_button)

        param_history_list = QListView()

        tool_layout_4 = QVBoxLayout()
        tool_layout_4.addLayout(tool_layout_2)
        tool_layout_4.addLayout(tool_layout_3)

        tool_layout_5 = QHBoxLayout()
        tool_layout_5.addLayout(tool_layout_4)
        tool_layout_5.addWidget(param_history_list)

        tool_layout_6 = QVBoxLayout()
        tool_layout_6.addLayout(tool_layout_1)
        tool_layout_6.addLayout(tool_layout_5)

        param_adjust_layout = QVBoxLayout()
        param_adjust_layout.addLayout(title_layout)
        param_adjust_layout.addWidget(self.chart_list)
        param_adjust_layout.addLayout(tool_layout_6)

        
        self.param_adjust_tab.setLayout(param_adjust_layout)
    
    def open_file(self):
        fileName,fileType = QtWidgets.QFileDialog.getOpenFileName(None, "choose file", os.getcwd(), "All Files(*)")
        if not fileName:
            return
        
        # Read the config file
        config_dict = ConfigFactory.parse_file(fileName)
        project_title = getattr(config_dict, 'project', 'temp')
        motor_config = getattr(config_dict, 'motor_config')
        if motor_config is None:
            return
        self.motors = []
        for i, m_config in enumerate(motor_config):
            motor = {}
            motor['id'] = getattr(m_config, 'motor_id', i)
            motor['name'] = getattr(m_config, 'motor_name', 'motor_%d' % (i))
            motor['status'] = getattr(m_config, 'motor_status', False)
            pids = []
            pid_config = getattr(m_config, 'pid_config', [])
            for j, p_config in enumerate(pid_config):
                pid = {}
                pid['id'] = getattr(p_config, 'pid_id', j)
                pid['name'] = getattr(p_config, 'pid_name', 'pid_%d' % (j))
                pids.append(pid)
            motor['pids'] = pids
            motor['pid_id2idx'] = {pid['id']:i for i, pid in enumerate(pids)}
            self.motors.append(motor)
        self.id2idx = {motor['id']:i for i, motor in enumerate(self.motors)}

        # feedback_status = getattr(config_dict, 'feedback_status', False)
        
        enable_command = getattr(config_dict, 'enable_command', '')
        set_pid_command = getattr(config_dict, "set_pid_command", '')
        feedback_command = getattr(config_dict, "feedback_command", '')
        if not enable_command or not set_pid_command or not feedback_command:
            return
        self_defined_command = list(getattr(config_dict, 'self_defined_command', []))
        self.global_funcs = {}
        commands = [enable_command, set_pid_command, feedback_command] + self_defined_command
        for command in commands:
            items = command.split()
            command_name = items[0]
            if len(items) == 1 or (items[1] != '{motor_id}' and '->' not in items[1:]):
                self.global_funcs[command_name] = items[1:]
        self.global_func_combo.clear()
        self.global_func_combo.addItems(list(self.global_funcs.keys()))
        self.global_func_param_list.setup_list(self.global_funcs[self.global_func_combo.currentText()])

        # Read config done. Build structure
        
        self.title_text.setText(project_title)
        self.chart_list.setup_list_rows(self.motors)
        self.motor_combo.clear()
        self.motor_combo.addItems([motor['name'] for motor in self.motors])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Meta_UI()
    demo.show()
    sys.exit(app.exec_())