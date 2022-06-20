from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QGridLayout, QLabel, QHBoxLayout, QLineEdit, QCheckBox, QPushButton, QStackedLayout, QTreeWidget, QComboBox, QMessageBox, QFileDialog, QTreeWidgetItem, QApplication, QAction, QMenuBar, QProgressBar
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont, QIcon, QBrush, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import os
import time
import cv2
from threading import Thread
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from src.controls import Arduino, Camera


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
        self.width = 600
        self.height = 800
        self.cwd = os.path.dirname(os.path.dirname(__file__))
        self.initUI()

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
        self.settings_window.addLayout(self.directory_window)

        self.main_layout.addLayout(self.settings_window)

        self.preview_window = QVBoxLayout()
        self.preview_label = QLabel("Webcam Preview")
        self.preview_window.addWidget(self.preview_label)

        self.numpy = np.zeros((1080, 1920))
        self.image_view = PlotWindow()
        self.image_view.setMinimumHeight(200)
        self.plot_image = plt.imshow(self.numpy, cmap="binary_r", vmin=0, vmax=4096)
        self.plot_image.axes.get_xaxis().set_visible(False)
        self.plot_image.axes.axes.get_yaxis().set_visible(False)
        self.preview_window.addWidget(self.image_view)

        self.main_layout.addLayout(self.preview_window)

        self.arduino = Arduino("/dev/tty.usbmodem1301", "leo")
        self.show()
        self.launch_camera()
        self.open_live_preview_thread()

    def open_live_preview_thread(self):
        self.live_preview_thread = Thread(target=self.start_live)
        self.live_preview_thread.start()

    def start_live(self):
        plt.ion()
        while len(self.camera.frames) == 0 and self.camera.video_running is True:
            print("hey")
            pass
        while self.camera.video_running is True:
            self.plot_image.set_array(np.array(self.camera.frames[-1]))
    def stop_live(self):
        self.camera.video_running = False
        self.camera.rval = False
        self.arduino.acquisition_running = False

    def launch_camera(self):
        self.camera = Camera("port", "name")
        self.camera.video_running = True
        self.camera.loop2()
    
    def choose_directory(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.directory_cell.setText(folder)

    def enable_directory(self):
        self.files_saved = self.directory_save_files_checkbox.isChecked()
        self.directory_choose_button.setEnabled(self.files_saved)
        self.directory_cell.setEnabled(self.files_saved)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont()
    font.setFamily("IBM Plex Sans")
    app.setFont(font)
    ex = App()
    sys.exit(app.exec_())
