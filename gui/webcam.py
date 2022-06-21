from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QLineEdit, QCheckBox, QPushButton, QFileDialog, QApplication, QProgressBar
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

class ProgressThread(QThread):
    _signal = pyqtSignal(list)
    def __init__(self):
        super(ProgressThread, self).__init__()

    def __del__(self):
        self.wait()

    def setApp(self, app):
        self.app = app

    def run(self):
        while not self.app.all_files_saved and not self.app.close_signal:
            time.sleep(0.5)
            try:
                self._signal.emit([len(self.app.frames), len(os.listdir(self.app.directory))])
            except Exception:
                pass

class ImageThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while not ex.close_signal:
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_index = ex.arduino.frame_index
                if frame_index > 0 and ex.directory_save_files_checkbox.isChecked() and ex.stop_acquisition_signal is False:
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
        self.frames = []
        self.indices = []
        self.width = 600
        self.height = 800
        self.stop_acquisition_signal = False
        self.close_signal = False
        self.cwd = os.path.dirname(os.path.dirname(__file__))
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

        self.experiment_label = QLabel("Experiment Settings")
        self.settings_window.addWidget(self.experiment_label)

        self.experiment_name_window = QHBoxLayout()
        self.experiment_name = QLabel('Experiment Name')
        self.experiment_name_window.addWidget(self.experiment_name)
        self.experiment_name_cell = QLineEdit()
        self.experiment_name_window.addWidget(self.experiment_name_cell)
        self.settings_window.addLayout(self.experiment_name_window)

        self.directory_window = QHBoxLayout()
        self.directory_save_files_checkbox = QCheckBox()
        self.directory_save_files_checkbox.setText("Save")
        self.directory_save_files_checkbox.stateChanged.connect(self.enable_directory)
        self.directory_window.addWidget(self.directory_save_files_checkbox)

        self.directory_cell = QLineEdit()
        self.directory_cell.setMinimumWidth(150)
        self.directory_cell.setReadOnly(True)
        self.directory_window.addWidget(self.directory_cell)
        self.stop_button = QPushButton("Stop Acquisition")
        self.stop_button.clicked.connect(self.stop)
        self.directory_window.addWidget(self.stop_button)
        self.settings_window.addLayout(self.directory_window)
        self.stop_button.setEnabled(False)

        self.main_layout.addLayout(self.settings_window)
        
        self.progress_bar = QProgressBar()
        #self.main_layout.addWidget(self.progress_bar)

        self.preview_window = QVBoxLayout()
        self.preview_label = QLabel("Webcam Preview")
        self.preview_window.addWidget(self.preview_label)
        self.label = QLabel(self)
        self.preview_window.addWidget(self.label)
        self.main_layout.addLayout(self.preview_window)

        self.arduino = Arduino("/dev/tty.usbmodem1301")

        #self.label.move(280, 120)
        #self.label.resize(640, 480)
        self.show()
        self.open_acquisition_thread()

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
            images_size = len(os.listdir(self.directory))
            #if len(self.frames) > images_size:
                #cv2.imwrite(f'{self.directory}/{time.time()}-{ex.indices[images_size]}.jpg', ex.frames[images_size])
            if len(self.frames) > 0:
                self.video_feed.write(self.frames.pop(0))
            else:
                if self.stop_acquisition_signal:
                    break
        self.video_feed.release()
        
    def enable_directory(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.directory = os.path.join(folder, self.experiment_name_cell.text())
        self.directory_cell.setText(self.directory)
        self.directory_save_files_checkbox.setEnabled(False)
        self.stop_button.setEnabled(True)
        try:
            os.mkdir(self.directory)
        except Exception:
            pass
        self.video_feed = cv2.VideoWriter(f"{self.directory}/output_video.mp4",cv2.VideoWriter_fourcc(*'mp4v'), 30, (1920, 1080))
        self.open_read_serial_thread()
        self.open_save_images_thread()
        #self.open_progress_bar_thread()

    def stop(self):
        self.stop_acquisition_signal = True
        self.arduino.acquisition_running = False
        self.stop_button.setEnabled(False)
        self.video_feed.release()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont()
    font.setFamily("IBM Plex Sans")
    app.setFont(font)
    ex = App()
    sys.exit(app.exec_())
