import socket
from time import sleep

meta_port = 2021

if __name__ == '__main__':
    soc_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc_server.bind(('localhost', meta_port))
    soc_server.listen(1)
    try:
        client, addr = soc_server.accept()
        while True:
            data = client.recv(100)
            print(data.decode())
            client.send('hello'.encode('utf-8'))
            sleep(1)
    except Exception as e:
        print(e)
        print('exception')
    finally:
        soc_server.close()