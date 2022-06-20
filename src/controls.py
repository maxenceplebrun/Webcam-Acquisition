import sys
import os
import numpy as np
import serial
import time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pylablib.devices import IMAQ


class Instrument:
    def __init__(self, port, name):
        """A class used to represent a analog or digital instrument controlled by a DAQ

        Args:
            port (str): The associated physical port
            name (str): The name of the instrument
        """
        self.port = port
        self.name = name

class Arduino(Instrument):
    def __init__(self, port, name):
        """A class used to represent a Arduino connected to the computer by a USB connection

        Args:
            port (list of str): A list containg the names of the acquisition and frame trigger ports
            name (str): The name of the Arduino (can be found using NI-MAX)
        """
        super().__init__(port, name)
        self.serial= serial.Serial(port, 9600, timeout=1)
        self.acquisition_running = True

    def read_serial(self):
        while True:
            if self.serial.in_waiting:
                self.frame_index = int(self.serial.readline())

    def reset(self):
        self.serial.write("reset".encode('utf-8'))

class Camera(Instrument):
    def __init__(self, port, name):
        """A class used to represent a physical camera connected to the computer by a USB connection

        Args:
            port (str): The name of the camera physical trigger port
            name (str): The name of the camera (can be found using NI-MAX)
        """
        super().__init__(port, name)
        self.frames = []
        self.video_running = False
        self.cam = IMAQ.IMAQCamera("img0")
        self.cam.setup_acquisition(nframes=100)
        self.cam.start_acquisition()

    def loop(self, arduino):
        """While camera is running, add each acquired frame to a frames list

        Args:
            task (Task): The nidaqmx task used to track if acquisition is finished
        """
        while arduino.check_acquisition():
            try:
                self.cam.wait_for_frame(timeout=0.1)
                self.frames += self.cam.read_multiple_images()
                self.video_running = True
            except Exception:
                pass
        self.frames += self.cam.read_multiple_images()
        self.video_running = False
    
    def save(self, directory):
        """Save the acquired frames (reduced if necessary) to a 3D NPY file

        Args:
            directory (str): The location in which to save the NPY file
        """
        np.save(f"{directory}/webcam-data", self.frames)



leo = Arduino("/dev/tty.usbmodem1101", "name")
time.sleep(2)
leo.check_acquisition()
leo.reset()
print("reset passed")
leo.check_acquisition()