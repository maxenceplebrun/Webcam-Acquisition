from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QApplication, QProgressBar
from PyQt5.QtGui import QFont, QIcon, QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, Qt, pyqtSignal, pyqtSlot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import os
import time
import cv2
import numpy as np
from multiprocessing import Process
from threading import Thread
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.controls import Arduino

class ImageThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while not ex.close_signal:
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_index = ex.arduino.frame_index
                if frame_index > 0 and ex.stop_acquisition_signal is False:
                    ex.frames.append(frame)
                    ex.indices.append(frame_index-1)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(960, 540, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Webcam Acquisition'
        self.left = 10
        self.top = 10
        self.width = 600
        self.height = 800
        self.open_acquisition_thread()
        self.frames = []
        self.indices = []
        self.stop_acquisition_signal = False
        self.close_signal = False
        self.arduino = Arduino("/dev/tty.usbmodem1301")
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, *args, **kwargs):
        self.arduino.acquisition_running = False
        self.close_signal = True

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setAlignment(Qt.AlignTop)

        self.settings_window = QVBoxLayout()
        self.settings_window.setAlignment(Qt.AlignTop)

        self.experiment_name_window = QHBoxLayout()
        self.experiment_name = QLabel('Experiment Name')
        self.experiment_name_window.addWidget(self.experiment_name)
        self.experiment_name_cell = QLineEdit()
        self.experiment_name_cell.textChanged.connect(self.verify_name)
        self.experiment_name_window.addWidget(self.experiment_name_cell)
        self.settings_window.addLayout(self.experiment_name_window)

        self.directory_window = QHBoxLayout()
        self.directory_label = QLabel("Directory")
        self.directory_window.addWidget(self.directory_label)
        self.directory_cell = QLineEdit()
        self.directory_cell.setMinimumWidth(150)
        self.directory_cell.setReadOnly(True)
        self.directory_window.addWidget(self.directory_cell)
        self.directory_save_files_button = QPushButton("Start Acquisition")
        self.directory_save_files_button.setIcon(QIcon(os.path.join("gui","icons","player-play.png")))
        self.directory_save_files_button.setEnabled(False)
        self.directory_save_files_button.clicked.connect(self.enable_directory)
        self.directory_window.addWidget(self.directory_save_files_button)
        self.stop_button = QPushButton("Stop Acquisition")
        self.stop_button.setIcon(QIcon(os.path.join("gui","icons","player-stop.png")))
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop)
        self.directory_window.addWidget(self.stop_button)
        self.settings_window.addLayout(self.directory_window)

        self.main_layout.addLayout(self.settings_window)

        self.preview_window = QVBoxLayout()
        self.preview_label = QLabel("Webcam Preview")
        self.preview_window.addWidget(self.preview_label)
        self.label = QLabel(self)
        self.preview_window.addWidget(self.label)
        self.main_layout.addLayout(self.preview_window)

        self.show()

    def open_acquisition_thread(self):
        self.acquisition_thread = ImageThread(self)
        self.acquisition_thread.changePixmap.connect(self.setImage)
        self.acquisition_thread.start()

    def open_read_serial_thread(self):
        self.arduino.open_read_serial_thread()

    def open_save_images_thread(self):
        self.save_images_thread = Thread(target=self.save_images)
        self.save_images_thread.start()

    def save_images(self):
        while not self.close_signal:
            if len(self.frames) > 0:
                self.video_feed.write(self.frames.pop(0))
            else:
                if self.stop_acquisition_signal:
                    break
        self.video_feed.release()
        np.save(f"{self.directory}/indices.npy", self.indices)

    def verify_name(self):
        self.directory_save_files_button.setEnabled(self.experiment_name_cell.text() != "")
        
    def enable_directory(self):
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.directory_cell.setText(self.directory)
        self.directory_save_files_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        try:
            os.mkdir(self.directory)
        except Exception:
            pass
        self.video_feed = cv2.VideoWriter(f"{self.directory}/{self.experiment_name_cell.text()}.mp4",cv2.VideoWriter_fourcc(*'mp4v'), 30, (1920, 1080))
        self.open_read_serial_thread()
        self.open_save_images_thread()

    def stop(self):
        self.stop_acquisition_signal = True
        self.arduino.acquisition_running = False
        self.stop_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont()
    font.setFamily("IBM Plex Sans")
    app.setFont(font)
    ex = App()
    sys.exit(app.exec_())
