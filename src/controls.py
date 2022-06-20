from asyncore import loop
import sys
import os
from tracemalloc import start
import numpy as np
import serial
import time
import cv2
from threading import Thread
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
        self.reset()
        self.open_read_serial_thread()

    def open_read_serial_thread(self):
        self.read_serial_thread = Thread(target=self.read_serial)
        self.read_serial_thread.start()

    def read_serial(self):
        while self.acquisition_running:
            if self.serial.in_waiting:
                try:
                    self.frame_index = int(self.serial.readline())
                except ValueError:
                    pass

    def reset(self):
        self.serial.write("reset".encode('utf-8'))
        self.serial.read(self.serial.in_waiting)

    def stop(self):
        self.reset()
        self.acquisition_running = False


class Camera(Instrument):
    def __init__(self, port, name):
        """A class used to represent a physical camera connected to the computer by a USB connection

        Args:
            port (str): The name of the camera physical trigger port
            name (str): The name of the camera (can be found using NI-MAX)
        """
        super().__init__(port, name)
        self.frames = []
        self.indices = []
        self.video_running = False
        #self.cam = IMAQ.IMAQCamera("img0")
        #self.cam.setup_acquisition(nframes=100)
        #self.cam.start_acquisition()

    def loop(self, arduino):
        """While camera is running, add each acquired frame to a frames list

        Args:
            task (Task): The nidaqmx task used to track if acquisition is finished
        """
        while arduino.check_acquisition():
            try:
                self.cam.wait_for_frame(timeout=0.1)
                self.frames += self.cam.read_multiple_images()
                self.indices += [arduino.frame_index]*(len(self.frames)-len(self.indices))
                self.video_running = True
            except Exception:
                pass
        self.frames += self.cam.read_multiple_images()
        self.video_running = False

    def loop2(self):
        self.vc = cv2.VideoCapture(0)
        self.vc.set(cv2.CAP_PROP_FPS, 10)
        if self.vc.isOpened(): # try to get the first frame
            self.rval, frame = self.vc.read()
            if frame is not None:
                self.frames.append(frame)
        else:
            self.rval = False
        if self.rval:
            self.open_loop_thread()

    def open_loop_thread(self):
        self.loop_thread = Thread(target=self.loop3)
        self.loop_thread.start()

    def loop3(self):
        self.rval = True
        while self.rval:
            self.rval, frame = self.vc.read()
            if frame is not None:
                self.frames.append(frame)
                cv2.imshow('frame_2',frame)
            key = cv2.waitKey(1)
        #self.vc.release()