import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from win32api import GetSystemMetrics

import pygetwindow
import time
import pyautogui
import threading
from socket import create_connection

from BlurWindow.blurWindow import GlobalBlur
import threading
import os 

from win32api import GetSystemMetrics
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtNetwork import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QDialog
from PyQt5.QtMultimedia import *

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, ElementNotInteractableException
from selenium.webdriver import Chrome
from word2number import w2n
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.chrome.service import Service as ChromeService # Similar thing for firefox also!
from subprocess import CREATE_NO_WINDOW 
from time import sleep


def statusWriter(status):
    with open('./assets/status.tru', 'w') as writer:
        writer.write(status)

def retrieveStatus():
    with open('./assets/status.tru', "r") as reader:
        read_ = reader.read()

        return read_

class Server(threading.Thread):
    def __init__(self):
        super().__init__()

        self.query = True

    def run(self):
        while True:
            sleep(0.1)
            while self.query:

                try:
                    reader = retrieveStatus()
                    if "query:" in reader:
                        webdriver_service = Service('./assets/chrome/chromeOld/driver.exe')
                        custom_executable_path = './assets/chrome/chromeOld/chrome.exe'

                        chrome_options = Options()
                        chrome_options.binary_location = custom_executable_path
                        chrome_options.add_argument('--use-fake-ui-for-media-stream')
                        chrome_options.add_argument('--allow-running-insecure-content')
                        chrome_options.add_argument("--window-size=1920,1080")
                        chrome_options.add_argument("--disable-extensions")
                        chrome_options.add_argument("--start-maximized")
                        chrome_options.add_argument('--headless')

                        chrome_options.add_argument('--no-sandbox')
                        chrome_options.add_argument('--ignore-certificate-errors')
                        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
                        chrome_options.add_argument(f'user-agent={user_agent}')

                        chrome_options.add_experimental_option("prefs", {
                            "download.prompt_for_download": False,
                            "download.directory_upgrade": True,
                            "safebrowsing.enabled": True
                        })

                        chrome_service = ChromeService('./assets/chrome/chromeOld/driver.exe')
                        chrome_service.creationflags = CREATE_NO_WINDOW
                        browser = Chrome(service=chrome_service, options=chrome_options)

                        image_path = reader.replace("query:", "")

                        print("#Acquired Image : ", image_path )

                        # APP = os.path.abspath(ima)

                        print("# Generating Caption avg : 15s")

                        browser.get('https://compressjpg.net/image-to-caption/')

                        search_button = browser.find_element(By.CSS_SELECTOR, '#file-input')
                        search_button.send_keys(image_path)

                        search_app = browser.find_element(By.CSS_SELECTOR, '#upload_form > button')
                        search_app.click()

                        sleep(10.0)
                        get_text = browser.find_element(By.CSS_SELECTOR, '#share-myslider-container > strong').text
                        print("#Caption : ",get_text)

                        statusWriter(f"caption:{get_text}")
                    else:
                        sleep(0.5)
                        print("# No Query")

                except Exception as e:
                    print("An error occured, retrying: ", e)
                    break

get_connected = Server()
get_connected.start()

WIDTH_ = GetSystemMetrics(0)
HEIGHT_ = GetSystemMetrics(1)

class AiImageCaptioning(QDialog):
    def __init__(self):
        super().__init__()

        self.pyqt_ui = uic.loadUi('./image_captioning_ui.ui', self)
        self.pyqt_ui.setWindowTitle('.')
        self.pyqt_ui.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.pyqt_ui.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.pyqt_ui.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        
        self.pyqt_ui.move(int(WIDTH_ / 6.0), int(HEIGHT_ / 3.2))
        self.pyqt_ui.drop.setText("Drag & Drop File Here")
        # self.pyqt_ui.image.setVisible(False)

        GlobalBlur(self.pyqt_ui.winId(), Dark=True, Acrylic=False)
        self.pyqt_ui.reset_ui.setVisible(False)

        self.pyqt_ui.reset_ui.clicked.connect(self.reset)
        self.pyqt_ui.close_ui.clicked.connect(self.hide)

        #Reset
        statusWriter("Null")
        self.setAcceptDrops(True)

        self.pyqt_ui.drop.setStyleSheet("color: white;")
        self.pyqt_ui.status.setWordWrap(True)
        self.caption_timer = QTimer()
        self.caption_timer.setInterval(1000)
        self.caption_timer.timeout.connect(self.set_text)
        self.caption_timer.start()

    def reset(self):

        font = QFont()
        font.setPointSize(36)  # Set the font size

        self.pyqt_ui.status.setFont(font)
        self.pyqt_ui.status.setText("AI Image Caption")

        self.pyqt_ui.status.setFont(font)
        self.pyqt_ui.drop.setText("Drag & Drop File Here")
        self.pyqt_ui.drop.setVisible(True)
        self.pyqt_ui.reset_ui.setVisible(False)

        # self.pyqt_ui.resize(int(WIDTH_ / 1.5), int(HEIGHT_ / 1.5))
        self.pyqt_ui.move(int(WIDTH_ / 6.0), int(HEIGHT_ / 3.2))

    def set_text(self):
        get_text = retrieveStatus()

        self.pyqt_ui.resize(int(WIDTH_ / 2.01), int(HEIGHT_ / 2.01))
        if "caption:" in get_text:
            text=get_text.replace("caption:", "").title()
            font = QFont()
            font.setPointSize(20)  # Set the font size
            self.pyqt_ui.status.setFont(font)
            self.pyqt_ui.status.setText(text)
            self.pyqt_ui.reset_ui.setVisible(True)
            self.pyqt_ui.showMaximized()
            statusWriter("Null")

    def set_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.pyqt_ui.drop.setPixmap(pixmap)
        self.pyqt_ui.drop.setScaledContents(True)

    def generator(self, path):
        absolute_path = os.path.abspath(path)
        statusWriter(f"query:{absolute_path}")
        print("Absolute Path : ", absolute_path)

    def dragEnterEvent(self, event):
        # This event is triggered when a file is dragged over the widget
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # This event is triggered when a file is dropped onto the widget
        file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
        if file_paths:
            self.handle_dropped_files(file_paths)

    def handle_dropped_files(self, file_paths):
        # Handle the dropped file paths here
        print("Dropped files:")
        for file_path in file_paths:
            print("File : ", file_path)
            self.pyqt_ui.resize(int(WIDTH_ / 2.01), int(HEIGHT_ / 2.01))
            self.pyqt_ui.move(int(WIDTH_ / 6.0), int(HEIGHT_ / 8.7))
            self.generator(file_path)
            self.set_image(file_path)
            self.pyqt_ui.status.setText("Generating..")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
        painter.drawRoundedRect(QRectF(self.rect()), 20, 20)
        painter.end()

    def mouseMoveEvent(self, event):
        # Calculate the window movement or resizing based on the initial click position
        try:
            if self.dragPos:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
            elif self.resizePos:
                diff = event.globalPos() - self.resizePos
                self.resize(QSize(self.resizeSize.width() + diff.x(), self.resizeSize.height() + diff.y()))
        except AttributeError:
            pass

    def mousePressEvent(self, event):
        # Remember the initial click position to calculate the window movement or resizing
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
        elif event.button() == Qt.RightButton:
            self.resizePos = event.globalPos()
            self.resizeSize = self.size()

    def mouseReleaseEvent(self, event):
        # Reset the click position when the mouse button is released
        if event.button() == Qt.LeftButton:
            self.dragPos = None
        elif event.button() == Qt.RightButton:
            self.resizePos = None

    def mouseDoubleClickEvent(self, event):
        self.showNormal()

    def resizeEvent(self, event: QResizeEvent):
        self.update()

app = QApplication(sys.argv)
window = AiImageCaptioning()
window.show()
sys.exit(app.exec_())
