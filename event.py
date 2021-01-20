from typing import Callable
from eventpy import eventqueue
# import multiprocessing
import threading

class Event:
    def __init__(self):
        self.__shouldStop = True
        # self.__process = multiprocessing.Process(target=self.__eventqueue_process)
        self.__process = threading.Thread(target=self.__eventqueue_process)
        self.__queue = eventqueue.EventQueue()

    def add_listener(self, event_id:int, callback:Callable):
        self.__queue.appendListener(event_id, callback)

    def enqueue_event(self, *args, **kwargs):
        self.__queue.enqueue(args, kwargs)

    def __eventqueue_process(self):
        while not self.__shouldStop :
            self.__queue.wait()
            print('1')
            self.__queue.process();

    def start(self):
        self.__shouldStop = False
        self.__process.setDaemon(True)
        self.__process.start()

    def stop(self):
        self.__shouldStop = True
        self.__process.join()