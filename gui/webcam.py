from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QGridLayout, QLabel, QHBoxLayout, QLineEdit, QCheckBox, QPushButton, QStackedLayout, QTreeWidget, QComboBox, QMessageBox, QFileDialog, QTreeWidgetItem, QApplication, QAction, QMenuBar, QProgressBar
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont, QIcon, QBrush, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QThread, Qt, pyqtSignal, pyqtSlot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import os
import time
import uuid
import cv2
from multiprocessing import Process
from threading import Thread
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from src.controls import Arduino, Camera

class MyThread(QThread):
    def __init__(self, target=None):
        super().__init__()
        self.target = target
    
    def run(self):
        if self.target:
            self.target()


class ProgressThread(QThread):
    _signal = pyqtSignal(list)
    def __init__(self):
        super(ProgressThread, self).__init__()

    def __del__(self):
        self.wait()

    def setApp(self, app):
        self.app = app

    def run(self):
        while not self.app.all_files_saved:
            time.sleep(1)
            try:
                self._signal.emit([len(self.app.frames), len(os.listdir(self.app.directory))])
            except Exception as err:
                print(err)
                self._signal.emit([0,0])

class ImageThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_index = ex.arduino.frame_index
                #print(frame_index)
                if frame_index > 0 and ex.directory_save_files_checkbox.isChecked() and ex.stop_acquisition_signal is False:
                    ex.frames.append(frame)
                    ex.indices.append(frame_index-1)
                    #
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(960, 540, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


class PlotWindow(QDialog):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Webcam Acquisition'
        self.left = 10
        self.top = 10
        self.frames = []
        self.indices = []
        #self.width = 600
        #self.height = 800
        self.cwd = os.path.dirname(os.path.dirname(__file__))
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, *args, **kwargs):
        self.stop_live()

    def initUI(self):
        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)
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
        self.directory_choose_button = QPushButton("Select Directory")
        self.directory_choose_button.setIcon(QIcon(os.path.join(self.cwd, "gui", "icons", "folder-plus.png")))
        self.directory_choose_button.setDisabled(True)
        self.directory_choose_button.clicked.connect(self.choose_directory)
        self.directory_window.addWidget(self.directory_choose_button)
        self.directory_cell = QLineEdit("")
        self.directory_cell.setMinimumWidth(150)
        self.directory_cell.setReadOnly(True)
        self.directory_window.addWidget(self.directory_cell)
        self.save_button = QPushButton("Stop Acquisition")
        self.save_button.clicked.connect(self.open_save_thread)
        self.directory_window.addWidget(self.save_button)
        self.settings_window.addLayout(self.directory_window)
        self.save_button.setEnabled(False)

        self.main_layout.addLayout(self.settings_window)
        
        self.progress_bar = QProgressBar()
        self.main_layout.addWidget(self.progress_bar)

        self.preview_window = QVBoxLayout()
        self.preview_label = QLabel("Webcam Preview")
        self.preview_window.addWidget(self.preview_label)

        #self.plot_image = plt.imshow(self.numpy)
        #self.plot_image.axes.get_xaxis().set_visible(False)
        #self.plot_image.axes.axes.get_yaxis().set_visible(False)
        #self.preview_window.addWidget(self.image_view)

        self.main_layout.addLayout(self.preview_window)

        self.arduino = Arduino("/dev/tty.usbmodem1301", "leo")

        self.label = QLabel(self)
        self.all_files_saved = False
        #self.label.move(280, 120)
        #self.label.resize(640, 480)
        self.preview_window.addWidget(self.label)
        th = ImageThread(self)
        th.changePixmap.connect(self.setImage)
        th.start()
        self.show()
        self.launch_camera()
        self.open_live_preview_thread()
        self.open_progress_bar_thread()
        #self.open_camera_process()
        self.stop_acquisition_signal = False

    def open_progress_bar_thread(self):
        self.progress_bar_thread = ProgressThread()
        self.progress_bar_thread.setApp(self)
        self.progress_bar_thread._signal.connect(self.signal_accept)
        self.progress_bar_thread.start()

    def signal_accept(self, msg):
        self.progress_bar.setMaximum(int(msg[0]))
        self.progress_bar.setValue(int(msg[1]))

    def open_live_preview_thread(self):
        self.live_preview_thread = Thread(target=self.start_live)
        self.live_preview_thread.start()

    def start_live(self):
        while True:
            try:
                images_number = len(os.listdir(self.directory))
                #self.progress_bar.setText(f"{images_number}/{len(self.frames)} Images Saved")
                #self.progress_bar.setRange(0, len(self.frames))
                #self.progress_bar.setValue(images_number)
                #print("____________________________")
                #print(len(ex.frames))
                #print(images_number)
                #print("____________________________")
                if len(self.frames) > images_number:
                    cv2.imwrite(f'{self.directory}/{time.time()}-{ex.indices[images_number]}.jpg', ex.frames[images_number])
                else:
                    if self.stop_acquisition_signal:
                        break
            except Exception as err:
                print(err)
        self.all_files_saved = True
        print("Frames saved")

    def stop_live(self):
        self.camera.video_running = False
        self.camera.rval = False
        self.arduino.acquisition_running = False

    def launch_camera(self):
        self.camera = Camera("port", "name")
        self.camera.video_running = True
    def open_camera_process(self):
        self.camera_process = Process(target=self.camera_loop)
        self.camera_process.start()
       
    def camera_loop(self):
        self.camera.loop2()
    
    def choose_directory(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.save_button.setEnabled(True)
        self.directory_cell.setText(folder)
        self.directory = os.path.join(folder, self.experiment_name_cell.text())
        try:
            os.mkdir(self.directory)
        except Exception:
            pass

    def enable_directory(self):
        self.files_saved = self.directory_save_files_checkbox.isChecked()
        self.directory_choose_button.setEnabled(self.files_saved)
        self.directory_cell.setEnabled(self.files_saved)

    def open_save_thread(self):
        self.save_thread = Thread(target=self.save)
        self.save_thread.start()

    def save(self):
        """Save the acquired frames (reduced if necessary) to a 3D NPY file

        Args:
            directory (str): The location in which to save the NPY file
        """
        self.save_button.setEnabled(False)
        self.arduino.acquisition_running = False
        self.stop_acquisition_signal = True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont()
    font.setFamily("IBM Plex Sans")
    app.setFont(font)
    ex = App()
    sys.exit(app.exec_())
