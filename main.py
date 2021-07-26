import sys
import os

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from pyhocon import ConfigFactory

from connection import ConnectionBase, SerialConnection, SocketConnection, BluetoothConnection
from graph_widget import Coordinatograph
from chart_widget import ChartList
from command_widget import CommandPanel


class Meta_UI(QWidget):

    def __init__(self):
        super(Meta_UI, self).__init__()
        self.received_data = ''
        self.communicate_manager = ConnectionBase('')

        self.terminal_widget = QWidget(self)
        self.param_adjust_tab = QWidget(self)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.terminal_widget)
        main_splitter.addWidget(self.param_adjust_tab)
        main_layout = QHBoxLayout()
        # main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        self.setup_terminal_widget()
        self.setup_param_adjust_tab()

        # self.resize(500, 500)

        self.setWindowTitle('Meta Terminal III')
        self.setWindowIcon(QtGui.QIcon('res/meta_logo.jpeg'))

    def setup_terminal_widget(self):

        # Elements setup
        connection_port_combo = QComboBox()
        connection_port_list = ['TCP', 'Serial']
        connection_port_combo.addItems(connection_port_list)

        port_device_text = QLineEdit()
        port_device_text.setPlaceholderText('Port/Device')

        connection_button = QPushButton()
        connection_button.setText('Connect')

        self.terminal_display = QTextBrowser()
        self.terminal_display.resize(640, 480)

        command_line = QLineEdit()

        send_button = QPushButton()
        send_button.setText('Send')

        clear_data_button = QPushButton()
        clear_data_button.setText('Clear')

        self.project_title = 'Meta'
        self.project_label = QLabel(self.project_title)
        title_font = QFont('Times New Roman', 30, QFont.Bold)
        self.project_label.setFont(title_font)

        title_spacer = QSpacerItem(100, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.load_config_file_button = QPushButton()
        # self.load_config_file_button.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.load_config_file_button.setText('Load Config')
        self.load_config_file_button.clicked.connect(self.open_file)

        self.export_button = QPushButton()
        # self.export_button.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.export_button.setText('Export Params')
        self.export_button.clicked.connect(self.save_file)

        # Layout setup
        file_buttons_layout = QVBoxLayout()
        file_buttons_layout.setContentsMargins(0, 0, 0, 0)
        file_buttons_layout.addWidget(self.load_config_file_button)
        file_buttons_layout.addWidget(self.export_button)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(self.project_label, alignment=Qt.AlignTop)
        header_layout.addItem(title_spacer)
        header_layout.addLayout(file_buttons_layout)

        control_button_layout = QHBoxLayout()
        control_button_layout.setContentsMargins(0, 0, 0, 0)
        control_button_layout.addWidget(connection_port_combo)
        control_button_layout.addWidget(port_device_text)
        control_button_layout.addWidget(connection_button)

        command_line_layout = QHBoxLayout()
        command_line_layout.setContentsMargins(0, 0, 0, 0)
        command_line_layout.addWidget(command_line)
        command_line_layout.addWidget(send_button)
        command_line_layout.addWidget(clear_data_button)

        terminal_part_layout = QVBoxLayout()
        terminal_part_layout.addLayout(header_layout)
        terminal_part_layout.addLayout(control_button_layout)
        terminal_part_layout.addWidget(self.terminal_display)
        terminal_part_layout.addLayout(command_line_layout)

        # Event Callback Setup

        def update_connect_button(set_on: bool):
            if set_on:
                connection_button.setText('Disconnect')
            else:
                connection_button.setText('Connect')

        def clear_data():
            self.terminal_display.clear()

        # Connections setup
        def command_line_send_msg():
            msg = command_line.text()
            self.send_msg(msg)
            command_line.clear()

        def connection_button_clicked():
            if connection_button.text() == 'Connect':
                method = connection_port_combo.currentText()
                device = port_device_text.text()
                if method == 'Serial':
                    self.communicate_manager = SerialConnection(device)
                elif method == 'TCP':
                    self.communicate_manager = SocketConnection(device)
                else:
                    return
                self.received_data = ''
                self.communicate_manager.data_received.connect(self.process_feedback)
                self.communicate_manager.connection_changed.connect(update_connect_button)
                self.communicate_manager.start()
            else:
                if self.communicate_manager is not None:
                    self.communicate_manager.stop()

        send_button.clicked.connect(command_line_send_msg)
        connection_button.clicked.connect(connection_button_clicked)
        clear_data_button.clicked.connect(clear_data)
        self.terminal_widget.setLayout(terminal_part_layout)

    def setup_param_adjust_tab(self):

        main_splitter = QSplitter(Qt.Vertical)

        # ***************************************** Global Function Section ****************************************** #
        self.global_func_panel = CommandPanel(parent=self,
                                              command_list=['temp_global temp_global_param', 'temp_button'],
                                              send_callback=self.send_msg)

        global_func_layout = QVBoxLayout()
        global_func_layout.addWidget(self.global_func_panel)
        global_func_container = QWidget()
        global_func_container.setLayout(global_func_layout)

        main_splitter.addWidget(global_func_container)

        # ******************************************* Chart Display Section ****************************************** #
        self.chart_list = ChartList(self.param_adjust_tab, [{'name': 'temp'}])

        chart_height_label = QLabel("Chart Height")
        self.chart_height_spin = QSpinBox()
        self.chart_height_spin.setRange(0, 9999)
        self.chart_height_spin.setSingleStep(50)
        self.chart_height_spin.setValue(250)
        self.chart_height_spin.valueChanged.connect(self.chart_list.set_chart_height)

        chart_control_spacer = QSpacerItem(100, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.angle_visibility_check = QCheckBox()
        self.angle_visibility_check.setText("Angle")
        self.angle_visibility_check.setChecked(True)
        self.angle_visibility_check.stateChanged.connect(self.set_chart_visibilities)
        self.velocity_visibility_check = QCheckBox()
        self.velocity_visibility_check.setText("Velocity")
        self.velocity_visibility_check.setChecked(True)
        self.velocity_visibility_check.stateChanged.connect(self.set_chart_visibilities)
        self.current_visibility_check = QCheckBox()
        self.current_visibility_check.setText("Current")
        self.current_visibility_check.setChecked(True)
        self.current_visibility_check.stateChanged.connect(self.set_chart_visibilities)

        chart_layout = QGridLayout()
        chart_layout.addWidget(chart_height_label, 0, 0, 1, 1)
        chart_layout.addWidget(self.chart_height_spin, 0, 1, 1, 1)
        chart_layout.addItem(chart_control_spacer, 0, 2, 1, 1)
        chart_layout.addWidget(self.angle_visibility_check, 0, 3, 1, 1)
        chart_layout.addWidget(self.velocity_visibility_check, 0, 4, 1, 1)
        chart_layout.addWidget(self.current_visibility_check, 0, 5, 1, 1)
        chart_layout.addWidget(self.chart_list, 1, 0, 1, 6)
        chart_container = QWidget()
        chart_container.setLayout(chart_layout)

        main_splitter.addWidget(chart_container)

        # ***************************************** Motor Function Section ******************************************* #
        self.motor_combo = QComboBox()
        self.clear_param_button = QPushButton()
        self.clear_param_button.setText('Clear')
        self.clear_param_button.clicked.connect(self.clear_params)
        self.save_button = QPushButton()
        self.save_button.setText('Save')
        self.save_button.clicked.connect(self.save_params)
        self.reload_button = QPushButton()
        self.reload_button.setText('Reload')
        self.reload_button.clicked.connect(self.reload_params)
        self.delete_button = QPushButton()
        self.delete_button.setText('Delete')
        self.delete_button.clicked.connect(self.delete_history)

        tool_layout = QGridLayout()

        tool_layout.addWidget(self.motor_combo, 0, 0, 1, 1)
        tool_layout.addWidget(self.clear_param_button, 0, 1, 1, 1)
        tool_layout.addWidget(self.save_button, 0, 2, 1, 1)
        tool_layout.addWidget(self.reload_button, 0, 3, 1, 1)
        tool_layout.addWidget(self.delete_button, 0, 4, 1, 1)

        self.motor_stacked_layout = QStackedLayout()
        self.setup_motor_panel(motor_config=[])

        tool_layout.addLayout(self.motor_stacked_layout, 1, 0, 1, 5)
        tool_widget = QWidget()
        tool_widget.setLayout(tool_layout)
        main_splitter.addWidget(tool_widget)

        main_splitter.setSizes([150, 400, 300])

        param_adjust_layout = QVBoxLayout()
        param_adjust_layout.setContentsMargins(0, 0, 0, 0)  # each section has its own margin
        param_adjust_layout.addWidget(main_splitter)

        self.param_adjust_tab.setLayout(param_adjust_layout)

    def setup_motor_panel(self, motor_config):
        for widget in self.motor_stacked_layout.children():
            self.motor_stacked_layout.removeWidget(widget)
        self.motor_combo.clear()
        self.motor_combo.addItems((motor['name'] for motor in motor_config))
        for motor in motor_config:
            # widget = QWidget()
            # widget_layout = QHBoxLayout(widget)
            splitter = QSplitter(Qt.Horizontal)
            command_panel = CommandPanel(splitter, command_list=motor['commands'], predefined=motor['predefined'],
                                         send_callback=self.send_msg)
            command_panel.setObjectName('command_panel')
            param_history = QListWidget(splitter)
            param_history.setDragDropMode(QAbstractItemView.DragDrop)
            param_history.setDefaultDropAction(Qt.MoveAction)
            param_history.setSelectionMode(QAbstractItemView.ExtendedSelection)
            # param_history.doubleClicked.connect(print)
            param_history.setObjectName('param_history')
            # splitter.addWidget(command_panel)
            # splitter.addWidget(param_history)
            # widget_layout.addWidget(command_panel)
            # widget_layout.addWidget(param_history)
            # self.motor_stacked_layout.addWidget(widget)
            self.motor_stacked_layout.addWidget(splitter)
        self.motor_combo.currentIndexChanged.connect(self.motor_stacked_layout.setCurrentIndex)

    def set_chart_visibilities(self):
        self.chart_list.set_chart_visibilities(
            self.angle_visibility_check.isChecked(),
            self.velocity_visibility_check.isChecked(),
            self.current_visibility_check.isChecked()
        )

    def open_file(self):
        fileName, fileType = QtWidgets.QFileDialog.getOpenFileName(None, "choose file", os.getcwd(), "All Files(*)")
        if not fileName:
            return

        # Read the config file
        config_dict = ConfigFactory.parse_file(fileName)
        self.project_title = getattr(config_dict, 'project', 'temp')
        motor_config = getattr(config_dict, 'motor_config')
        if motor_config is None:
            return
        motors = []
        for i, m_config in enumerate(motor_config):
            motor = {}
            motor['id'] = getattr(m_config, 'motor_id', i)
            motor['name'] = getattr(m_config, 'motor_name', 'motor_%d' % (i))
            motor['predefined'] = {'motor_id': motor['id']}
            motor['commands'] = []
            motors.append(motor)
        self.id2idx = {motor['id']: i for i, motor in enumerate(motors)}
        self.name2idx = {motor['name']: i for i, motor in enumerate(motors)}

        commands = list(getattr(config_dict, 'commands', []))
        global_funcs = []
        for command in commands:
            if '->' in command:
                command, motor_names = command.split('->', 1)
                motor_names = motor_names.split()
                for name in motor_names:
                    if name in self.name2idx:
                        motors[self.name2idx[name]]['commands'].append(command)
            elif 'motor_id' in command:
                for motor in motors:
                    motor['commands'].append(command)
            else:
                global_funcs.append(command)
        self.global_func_panel.setup_list_rows(global_funcs, send_callback=self.send_msg)

        # Read config done. Build structure

        self.project_label.setText(self.project_title)
        self.chart_list.setup_list_rows(motors)
        self.setup_motor_panel(motors)

    def save_params(self):
        current_motor_splitter = self.motor_stacked_layout.currentWidget()
        command_panel = current_motor_splitter.findChild(CommandPanel)
        param_history = current_motor_splitter.findChild(QListWidget)
        commands = command_panel.get_elements()
        new_historys = ['%s %s' % (command_name, ' '.join(params)) for command_name, params in commands]
        param_history.addItems(new_historys)

    def reload_params(self):
        current_motor = self.motor_stacked_layout.currentWidget()
        command_panel = current_motor.findChild(CommandPanel)
        param_history = current_motor.findChild(QListWidget)
        items = param_history.selectedItems()
        elements = [item.text() for item in items]
        command_panel.set_elements(elements)

    def clear_params(self):
        current_motor = self.motor_stacked_layout.currentWidget()
        command_panel = current_motor.findChild(CommandPanel)
        command_panel.clear_elements()

    def delete_history(self):
        current_motor = self.motor_stacked_layout.currentWidget()
        param_history = current_motor.findChild(QListWidget)
        for item in param_history.selectedItems():
            row = param_history.row(item)
            param_history.takeItem(row)

    def process_feedback(self, feedback: bytes):
        self.received_data += feedback.decode(encoding='utf-8')
        if '\n' in self.received_data:
            fine_data, self.received_data = self.received_data.rsplit('\n', 1)
            lines = fine_data.split('\n')
            for line in lines:
                tokens = line.split()
                if not tokens:
                    continue
                elif tokens[0] == 'fb':
                    self.chart_list.update_chart(tokens[1:])
                else:
                    self.update_terminal_display(line + '\n')

    def update_terminal_display(self, input_str: str):
        cursor = self.terminal_display.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(input_str)
        self.terminal_display.setTextCursor(cursor)

    def send_msg(self, msg):
        try:
            self.communicate_manager.send_data(bytes(msg + '\r\n', encoding='utf-8'))
        except Exception as err:
            print(err)
            msg = 'Fail to send user_message!'
        self.update_terminal_display(msg + '\n')

    def save_file(self):
        fileName, fileType = QtWidgets.QFileDialog.getSaveFileName(None, "choose file", os.path.join(os.getcwd(),
                                                                                                     self.project_title + '_param.txt'),
                                                                   "All Files(*)")
        if not fileName:
            return

        with open(fileName, 'w', encoding='utf-8') as file_save:
            content = []
            content.append(self.project_title)
            content.append('')

            content.append('Global Function Parameters')
            global_func_count = self.global_func_panel.vlistWidget.count()
            for i in range(global_func_count):
                item = self.global_func_panel.vlistWidget.item(i)
                content.append('%s %s' % (item.widget.findChild(QLabel).text(), ' '.join(item.get_params())))
            content.append('')

            motor_count = self.motor_combo.count()
            for i in range(motor_count):
                content.append(self.motor_combo.itemText(i) + ' Function Parameters')
                current_motor = self.motor_stacked_layout.widget(i)
                command_panel = current_motor.findChild(CommandPanel)
                motor_func_count = command_panel.vlistWidget.count()
                for j in range(motor_func_count):
                    item = command_panel.vlistWidget.item(j)
                    content.append('%s %s' % (item.widget.findChild(QLabel).text(), ' '.join(item.get_params())))
                content.append('')

            file_save.write('\n'.join(content))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Meta_UI()
    demo.show()
    sys.exit(app.exec_())
