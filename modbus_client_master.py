from time import sleep
from PyQt5.QtCore import pyqtSignal, QObject, QThread
from pymodbus.client import (
    ModbusSerialClient,
    ModbusTcpClient,
    ModbusUdpClient,
)

class cl_modbus(QThread):
    mb_finished = pyqtSignal()

    def __init__(self, spin, mainwindow, parent=None):
        super().__init__()
        self.th_spin = spin # <-- data которая нужна для расчетов, и которую получим из основного потока
        self.mainwindiw = mainwindow
        #from app import MW #обращение к глобальной переменной из app
        #MW[1] = 0
        #self.client = ModbusTcpClient("127.0.0.1", 502)
        self.client = self.setup_sync_client()
        #self.client.connect()

    def run(self):
        while True: # БЕСКОНЕЧНЫЙ ЦИКЛ
            try:
                from app import rdMW, wrMW #обращение к глобальной переменной из app
                self.client.write_registers(0, wrMW, slave=1)
                response = self.client.read_holding_registers(130, len(rdMW), slave=1)

                # self.client.write_registers(127, wrMW, slave=1)
                # response = self.client.read_holding_registers(100, len(rdMW), slave=1)
                #
                # self.client.write_registers(254, wrMW, slave=1)
                # response = self.client.read_holding_registers(100, len(rdMW), slave=1)

                for i in range(len(response.registers)):
                    rdMW[i] = response.registers[i]
                #print(*response.registers)

                if self.mainwindiw.text_2 != "<h3 style='color: green;'>Modbus запущен</h3>":
                    self.mainwindiw.text_2 = "<h3 style='color: green;'>Modbus запущен</h3>"
                    self.mainwindiw.mbLabel.setText(f"{self.mainwindiw.text_2}")
                    self.mainwindiw.statusbar.update()
            except Exception:
                print("Сервер ModbusTCP не отвечает.")
                #self.mainwindiw.statusbar.showMessage("Сервер ModbusTCP не отвечает.", 1000)
                if self.mainwindiw.text_2 != "<h3 style='color: red;'>Сервер ModbusTCP не отвечает.</h3>":
                    self.mainwindiw.text_2 = "<h3 style='color: red;'>Сервер ModbusTCP не отвечает.</h3>"
                    self.mainwindiw.mbLabel.setText(f"{self.mainwindiw.text_2}")
                    self.mainwindiw.statusbar.update()

            sleep(0.1) # 100 мс

    def setup_sync_client(self):
        """Run client setup."""
        client = ModbusTcpClient(
                "127.0.0.1",
                port=502,
                # Common optional paramers:
                #    framer=socket,
                #    timeout=10,
                #    retries=3,
                #    retry_on_empty=False,y
                #    close_comm_on_error=False,
                #    strict=True,
                # TCP setup parameters
                #    source_address=("localhost", 0),
            )
        return client
