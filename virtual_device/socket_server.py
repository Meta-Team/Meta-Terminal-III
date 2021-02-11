import socketserver
from time import sleep

meta_port = 2021

class MyHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            try:
                data = self.request.recv(100)
                print(data.decode().strip())
                self.request.send('hello\n'.encode('utf-8'))
                sleep(1)
            except:
                break
        self.request.close()


if __name__ == '__main__':
    socket_server = socketserver.ThreadingTCPServer(('localhost', meta_port), MyHandler)
    socket_server.serve_forever()