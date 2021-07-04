import socket
from PyQt5.QtCore import QThread, pyqtSignal
import serial
from time import sleep
# import bluetooth

class Manager_Base(QThread):

    device_signal = pyqtSignal(bytes)
    connection_signal = pyqtSignal(bool)

    def __init__(self, device_name:str):
        super(Manager_Base, self).__init__()
        self.device_name = device_name

    def run(self):
        pass

    def SendData(self, send_msg):
        pass

    def stop(self):
        pass


meta_serial_baudrate = 115200

class Serial_Manager(Manager_Base):
    
    def __init__(self, device_name:str):
        super(Serial_Manager, self).__init__(device_name=device_name)
        self.__ser = None
        self.alive = False

    def run(self):
        try:
            self.__ser = serial.Serial(port=self.device_name, baudrate=meta_serial_baudrate, timeout=None)
            if self.__ser.isOpen():
                self.connection_signal.emit(True)
                trash = self.__ser.read_all()
                self.alive = True
                while self.alive and self.__ser.isOpen():
                    n = self.__ser.inWaiting()
                    if n:
                        self.device_signal.emit(self.__ser.read_all())
                    sleep(0.016)
        except:
            pass
        self.connection_signal.emit(False)

    def SendData(self, send_msg):
        return self.__ser.write(send_msg)

    def stop(self):
        self.alive = False
        if self.__ser.isOpen():
            self.__ser.close()

meta_port = 2021

class Socket_Manager(Manager_Base):

    def __init__(self, device_name:str):
        super(Socket_Manager, self).__init__(device_name=device_name)
        self.__socket = None
        self.alive = False

    def run(self):
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.connect((self.device_name, meta_port))
            self.connection_signal.emit(True)
            self.alive = True
            while self.alive:
                data = self.__socket.recv(100)
                if len(data) > 0:
                    self.device_signal.emit(data)
                sleep(0.016)
        except Exception as e:
            print(e)
        finally:
            self.__socket.close()
            self.connection_signal.emit(False)
    
    def SendData(self, send_msg):
        return self.__socket.send(send_msg)

    def stop(self):
        self.alive = False


class Bluetooth_Manager(Manager_Base):
    def __init__(self, device_name:str):
        super().__init__(device_name)
        self.__bt = None
        self.alive = False

    def run(self):
        # self.__bt = bluetooth.discover_devices()
        pass
        # while self.alive:
            # n = self.__bt.inWaiting()
            # if n:

    def SendData(self, send_msg):
        # return self.__bt.write(send_msg)
        return None

    def stop(self):
        self.alive = False
        # if self.__bt.isOpen():
        #     self.__bt.close()
