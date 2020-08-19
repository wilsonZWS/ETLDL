from threading import Condition


class CountDownLatch(object):

    def __init__(self, count):
        self.__count = count
        self.__condition = Condition()

    def await_countdown(self):
        try:
            self.__condition.acquire()
            while self.__count > 0:
                self.__condition.wait()
        finally:
            self.__condition.release()

    def countdown(self):
        try:
            self.__condition.acquire()
            self.__count -= 1
            self.__condition.notifyAll()
        finally:
            self.__condition.release()
