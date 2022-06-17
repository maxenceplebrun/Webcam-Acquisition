from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QGridLayout, QLabel, QHBoxLayout, QLineEdit, QCheckBox, QPushButton, QStackedLayout, QTreeWidget, QComboBox, QMessageBox, QFileDialog, QTreeWidgetItem, QApplication, QAction, QMenuBar, QProgressBar
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont, QIcon, QBrush, QColor
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import os
import time
from threading import Thread
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from src.controls import Arduino

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
        self.start_acquisition_thread()
        self.initUI()

    def closeEvent(self, *args, **kwargs):
        self.acquisition_running = False
        print("Closed")

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

        self.numpy = np.zeros((1024, 1024))
        self.image_view = PlotWindow()
        self.image_view.setMinimumHeight(200)
        self.plot_image = plt.imshow(self.numpy, cmap="binary_r", vmin=0, vmax=4096)
        self.plot_image.axes.get_xaxis().set_visible(False)
        self.plot_image.axes.axes.get_yaxis().set_visible(False)
        self.preview_window.addWidget(self.image_view)

        self.main_layout.addLayout(self.preview_window)

        self.show()

    def choose_directory(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.directory_cell.setText(folder)

    def enable_directory(self):
        self.files_saved = self.directory_save_files_checkbox.isChecked()
        self.directory_choose_button.setEnabled(self.files_saved)
        self.directory_cell.setEnabled(self.files_saved)

    def start_acquisition_thread(self):
        self.acquisition_running = True
        self.start_acquisition_thread = Thread(target=self.start_acquisition)
        self.start_acquisition_thread.start()

    def start_acquisition(self):
        self.arduino = Arduino(["port1, port2"], "dev0")
        while self.acquisition_running:
            print(time.time())
            time.sleep(1)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont()
    font.setFamily("IBM Plex Sans")
    app.setFont(font)
    ex = App()
    sys.exit(app.exec_())
