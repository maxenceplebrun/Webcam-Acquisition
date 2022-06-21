import sys
import os
import serial
from threading import Thread


class Arduino():
    def __init__(self, port):
        """A class used to represent a Arduino connected to the computer by a USB connection

        Args:
            port (list of str): A list containg the name of the Arduino Serial Port
        """
        self.port = port
        self.frame_index = 0
        self.serial= serial.Serial(port, 9600, timeout=1)
        self.reset()

    def open_read_serial_thread(self):
        self.acquisition_running = True
        self.read_serial_thread = Thread(target=self.read_serial)
        self.read_serial_thread.start()

    def read_serial(self):
        buffer_string = ''
        while self.acquisition_running:
            buffer_string = buffer_string + self.serial.read(self.serial.inWaiting()).decode("utf-8")
            if '\n' in buffer_string:
                lines = buffer_string.split('\n')
                self.frame_index = int(lines[-2])
                buffer_string = lines[-1]

    def reset(self):
        self.serial.write("reset".encode('utf-8'))
        self.serial.read(self.serial.in_waiting)