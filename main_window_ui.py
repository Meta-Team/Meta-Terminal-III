# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(813, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.left_container = QtWidgets.QWidget(self.splitter)
        self.left_container.setObjectName("left_container")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.left_container)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.splitter_2 = QtWidgets.QSplitter(self.left_container)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.terminal_container = QtWidgets.QWidget(self.splitter_2)
        self.terminal_container.setObjectName("terminal_container")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.terminal_container)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget = QtWidgets.QWidget(self.terminal_container)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.comboBox = QtWidgets.QComboBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_2.addWidget(self.comboBox)
        self.comboBox_2 = QtWidgets.QComboBox(self.widget)
        self.comboBox_2.setEditable(True)
        self.comboBox_2.setFrame(True)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.horizontalLayout_2.addWidget(self.comboBox_2)
        self.pushButton = QtWidgets.QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.verticalLayout_2.addWidget(self.widget)
        self.textEdit = QtWidgets.QTextEdit(self.terminal_container)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_2.addWidget(self.textEdit)
        self.widget_2 = QtWidgets.QWidget(self.terminal_container)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lineEdit = QtWidgets.QLineEdit(self.widget_2)
        self.lineEdit.setFrame(False)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_3.addWidget(self.lineEdit)
        self.pushButton_2 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_3.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_3.addWidget(self.pushButton_3)
        self.verticalLayout_2.addWidget(self.widget_2)
        self.widget_2.raise_()
        self.textEdit.raise_()
        self.widget.raise_()
        self.control_panel_container = QtWidgets.QWidget(self.splitter_2)
        self.control_panel_container.setObjectName("control_panel_container")
        self.gridLayout_2.addWidget(self.splitter_2, 0, 0, 1, 1)
        self.right_container = QtWidgets.QWidget(self.splitter)
        self.right_container.setObjectName("right_container")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.right_container)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.general_control_container = QtWidgets.QWidget(self.right_container)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.general_control_container.sizePolicy().hasHeightForWidth())
        self.general_control_container.setSizePolicy(sizePolicy)
        self.general_control_container.setObjectName("general_control_container")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.general_control_container)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(347, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.general_control_container)
        self.graph_group_container = QtWidgets.QWidget(self.right_container)
        self.graph_group_container.setObjectName("graph_group_container")
        self.verticalLayout.addWidget(self.graph_group_container)
        self.gridLayout.addWidget(self.splitter, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.comboBox.setCurrentText(_translate("MainWindow", "TCP"))
        self.comboBox.setItemText(0, _translate("MainWindow", "TCP"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Serial"))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "meta-jeton-nano-1.local"))
        self.comboBox_2.setItemText(1, _translate("MainWindow", "meta-jetson-nano-2.local"))
        self.comboBox_2.setItemText(2, _translate("MainWindow", "meta-jetson-nano-3.local"))
        self.pushButton.setText(_translate("MainWindow", "Connect"))
        self.pushButton_2.setText(_translate("MainWindow", "Send"))
        self.pushButton_3.setText(_translate("MainWindow", "Clear"))