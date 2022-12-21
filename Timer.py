from time import time

class clTimer():

    def __init__(self):
        self.name = ''
        self.EN = False
        self.DN = True  # при создании, таймер как бы досчитал
        self.SP = 0
        self.ACC = 0
        self.__ST = 0

    def start(self):
        if self.DN:
            self.DN = False
        if self.EN:
            self.DN = False
            self.ACC = round((time() - self.__ST)*1000) #секунды//1000 = миллисекунды
            if self.ACC >= self.SP:
                self.DN = True
                self.EN = False
                self.ACC = self.SP # для красоты, что бы по истечении времени ACC = SP
        else:
            self.__ST = time()

