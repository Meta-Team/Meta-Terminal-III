import socket
from PyQt5.QtCore import QThread, pyqtSignal
import serial
from time import sleep


class ConnectionBase(QThread):
    data_received = pyqtSignal(bytes)
    connection_changed = pyqtSignal(bool)

    def __init__(self, device_name: str):
        super(ConnectionBase, self).__init__()
        self.device_name = device_name

    def run(self):
        pass

    def send_data(self, send_msg):
        pass

    def stop(self):
        pass


META_SERIAL_BAUDRATE = 115200


class SerialConnection(ConnectionBase):

    def __init__(self, device_name: str):
        super(SerialConnection, self).__init__(device_name=device_name)
        self._serial = None
        self._alive = False

    def run(self):
        try:
            self._serial = serial.Serial(port=self.device_name, baudrate=META_SERIAL_BAUDRATE, timeout=None)
            if self._serial.isOpen():
                self.connection_changed.emit(True)
                _ = self._serial.read_all()  # discard all existing user_message
                self._alive = True
                while self._alive and self._serial.isOpen():
                    n = self._serial.inWaiting()
                    if n:
                        self.data_received.emit(self._serial.read_all())
                    sleep(0.016)
        except:
            pass
        self.connection_changed.emit(False)

    def send_data(self, msg):
        return self._serial.write(msg)

    def stop(self):
        self._alive = False
        if self._serial.isOpen():
            self._serial.close()


META_PORT = 2021


class SocketConnection(ConnectionBase):

    def __init__(self, device_name: str):
        super(SocketConnection, self).__init__(device_name=device_name)
        self._socket = None
        self._alive = False

    def run(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.device_name, META_PORT))
            self.connection_changed.emit(True)
            self._alive = True
            while self._alive:
                data = self._socket.recv(100)
                if len(data) > 0:
                    self.data_received.emit(data)
        except Exception as e:
            print(e)
        finally:
            self._socket.close()
            self.connection_changed.emit(False)

    def send_data(self, send_msg):
        return self._socket.send(send_msg)

    def stop(self):
        self._alive = False