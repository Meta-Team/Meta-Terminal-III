import socket
from PyQt5.QtCore import QThread, pyqtSignal
import serial
from time import sleep


class ConnectionBase(QThread):
    user_message = pyqtSignal(str)
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
                    n = self._serial.read_all()
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
            self.user_message.emit(f"TCP socket error: {str(e)}")
        finally:
            self._socket.close()
            self.connection_changed.emit(False)

    def send_data(self, send_msg):
        return self._socket.send(send_msg)

    def stop(self):
        self._alive = False


class _TestConnection(ConnectionBase):

    def __init__(self, device_name: str):
        super().__init__(device_name)
        self._alive = False

    def run(self):
        self._alive = True
        self.connection_changed.emit(True)
        while self._alive:
            sleep(0.2)
        self.connection_changed.emit(False)

    def reply_line(self, line: str):
        print("<", line)
        self.data_received.emit((line + "\r\n").encode("utf-8"))

    def send_data(self, send_msg: bytes):
        import random
        command = send_msg.decode("utf-8").strip()
        print(">", command)
        if command == "help":
            self.reply_line("hello stats _s _s_enable_fb _s_pid _g _g_enable_fb")
        elif command == "_s":
            self.reply_line("_s:Shoot")
            self.reply_line("_s/Bullet:Angle{Target,Actual} Velocity{Target,Actual} Current{Target,Actual}")
            self.reply_line("_s/FW_Left:Velocity{Target,Actual} Current{Target,Actual}")
            self.reply_line("_s/FW_Right:Velocity{Target,Actual} Current{Target,Actual}")
        elif command == "_s_enable_fb ?":
            self.reply_line("Usage: _s_enable_fb Channel/All Feedback{Disabled,Enabled}")
        elif command == "_s_enable_fb 0 1":
            for _ in range(20):
                self.reply_line(f"_s0 {' '.join([str(random.randint(0, 100)) for _ in range(6)])}")
                self.reply_line(f"_s1 {' '.join([str(random.randint(0, 100)) for _ in range(4)])}")
                self.reply_line(f"_s2 {' '.join([str(random.randint(0, 100)) for _ in range(4)])}")
                sleep(0.02)
        elif command == "_s_pid ?":
            self.reply_line("Usage: _s_pid Channel PID{A2V,V2I} [kp] [ki] [kd] [i_limit] [out_limit]")
        elif command == "_g":
            self.reply_line("_g:Gimbal")
            self.reply_line("_g/Yaw:Angle{Target,Actual} Velocity{Target,Actual} Current{Target,Actual}")
            self.reply_line("_g/Pitch:Angle{Target,Actual} Velocity{Target,Actual} Current{Target,Actual}")
            self.reply_line("_g/Sub_Pitch:Angle{Target,Actual} Velocity{Target,Actual} Current{Target,Actual}")
        elif command == "_g_enable_fb ?":
            self.reply_line("Usage: _g_enable_fb Channel/All")
        elif command == "hello":
            self.reply_line("Hello world from ChibiOS")
        else:
            print("?", f"Unknown command {command}")

    def stop(self):
        self._alive = False