from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QApplication, QComboBox, QMessageBox
from PyQt5.QtGui import QFont, QIcon, QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, Qt, pyqtSignal, pyqtSlot
import sys
import os
import cv2
import numpy as np
import json
from threading import Thread
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.controls import Arduino

class ImageThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        """Acquire webcam images and emit signal to update image"""
        ex.cap = cv2.VideoCapture(0)
        ex.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        ex.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        while not ex.close_signal:
            ret, frame = ex.cap.read()
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
        """Initialize the application"""
        super().__init__()
        self.title = 'Webcam Acquisition'
        self.cwd = os.path.dirname(os.path.dirname(__file__))
        self.left = 10
        self.top = 10
        self.width = 600
        self.height = 800
        self.open_acquisition_thread()
        self.frames = []
        self.indices = []
        self.stop_acquisition_signal = False
        self.close_signal = False
        with open(os.path.join(self.cwd, "config.json"), "r") as file:
            self.config = json.load(file)
        self.arduino = Arduino(self.config["arduino_port"])
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        """Update the image in the GUI"""
        self.label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, *args, **kwargs):
        """Close the application"""
        self.video_feed.release()
        self.arduino.acquisition_running = False
        self.close_signal = True

    def initUI(self):
        """Initialize the GUI"""
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
        self.resolution_combo = QComboBox()
        self.resolution_combo.currentIndexChanged.connect(self.change_resolution)
        self.resolution_combo.addItem("1080p")
        self.resolution_combo.addItem("720p")
        self.resolution_combo.addItem("480p")
        self.experiment_name_window.addWidget(self.resolution_combo)
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

    def change_resolution(self):
        try:
            if self.resolution_combo.currentText() == "1080p":
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            if self.resolution_combo.currentText() == "720p":
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            if self.resolution_combo.currentText() == "480p":
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        except Exception:
            pass
    def open_acquisition_thread(self):
        """Start the thread responsible for acquiring webcam frames"""
        print("acquisition thread open")
        self.acquisition_thread = ImageThread(self)
        self.acquisition_thread.changePixmap.connect(self.setImage)
        self.acquisition_thread.start()

    def open_read_serial_thread(self):
        """Start the thread responsible for reading the Arduino serial output"""
        print("serial thread open")
        self.arduino.open_read_serial_thread()

    def open_save_images_thread(self):
        """Start the thread responsible for image saving"""
        print("save images thread open")
        self.save_images_thread = Thread(target=self.save_images)
        self.save_images_thread.start()

    def save_images(self):
        """Add buffered frames to the video and release it when done. Save indices array."""
        while not self.close_signal:
            if len(self.frames) > 0:
                self.video_feed.write(self.frames.pop(0))
            else:
                if self.stop_acquisition_signal:
                    print("about to break")
                    break
        try:
            self.video_feed.release()
            np.save(os.path.join(self.directory,self.experiment_name_cell.text(),"indices.npy"), self.indices)
        except Exception:
            pass

    def verify_name(self):
        """Verify that experiment name is not empty"""
        self.directory_save_files_button.setEnabled(self.experiment_name_cell.text() != "")
        
    def enable_directory(self):
        """Choose the directory in which to save the video and start the serial read and image saving threads."""
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if self.check_override:
            self.directory_cell.setText(self.directory)
            self.directory_save_files_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.video_feed = cv2.VideoWriter(os.path.join(self.directory, self.experiment_name_cell.text(), f"{self.experiment_name_cell.text()}.mp4"), cv2.VideoWriter_fourcc(*'mp4v'), 30, (int(self.cap.get(3)),int(self.cap.get(4))))
            self.open_read_serial_thread()
            self.open_save_images_thread()

    def check_override(self):
        """ Check if experiment with the same name already exists"""
        if os.path.isdir(
            os.path.join(
                self.directory,
                self.experiment_name_cell.text()
            )
        ):
            button = QMessageBox.question(
                self,
                "Directory already exists",
                "Directory already exists. \n Do you want to continue?",
            )
            if button == QMessageBox.Yes:
                return True
            else:
                return False
        else:
            return True

    def stop(self):
        """Send a signal to stop acquiring new frames"""
        print("stop signal")
        self.stop_acquisition_signal = True
        self.arduino.acquisition_running = False
        self.stop_button.setEnabled(False)
        print(self.stop_acquisition_signal)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    font = QFont()
    font.setFamily("IBM Plex Sans")
    app.setFont(font)
    sys.exit(app.exec_())
