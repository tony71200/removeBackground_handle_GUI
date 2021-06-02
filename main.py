import sys
import codecs
import os.path
import platform
import subprocess
from functools import partial
import threading
import cv2 as cv
import imutils
import removalBackground_utils as remove

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    if sys.version_info.major >= 3:
        import sip
        sip.setapi('QVariant', 2)
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from libraries import utils
from libraries.toolBar import ToolBar
from libraries.ustr import ustr
from libraries.slider import Slider
from libraries.groupSlider import GroupSlider

__appname__ = 'removal Background (leaf) Handlde '

class WindowMixin(object):

    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            utils.addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            utils.addActions(toolbar, actions)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        return toolbar

class Color(QWidget):

    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)
        
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QMainWindow, WindowMixin):
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = list(range(3))

    def __init__(self, defaultFilename=None,  defaultSaveDir=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle(__appname__)
        # self.resize(800,600)
        
        #Save as Direction
        self.defaultSaveDir= defaultSaveDir

        #Application state
        self.filePath = ustr(defaultFilename)

        #Image Processing
        self.image_raw = None
        self.image_backup = None
        self.image_save = None

        #Actions
        action = partial(utils.newAction, self)
        open_action = action(text='Open File', function=self.openFile, 
                            shortcut='Crt+O', icon='open',
                            tip='Open Image File', )
        quit_action = action('Exit', self.close, 'Ctrl+Q', 'quit')
        self.save_action = action('Save', self.saveFileAs, 'Ctrl+S', "save", 
                            "Save current File", enabled= False)
        self.reset_action = action("Reset", self.reset, 'Ctrl+R', 'resetall', enabled=False)
        self.tools = self.toolbar('toolbar', (open_action, self.save_action, self.reset_action, quit_action))
        
        # Image Area
        scroll = QScrollArea()
        # scroll.setFixedSize(640,640)
        self.image_frame = QLabel()
        scroll.setWidget(self.image_frame)
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignCenter)
        self.scroll_Area = scroll
        self.setCentralWidget(scroll)
        self.image_frame.setScaledContents(True)

        # Create Parameter Dock
        param_layout = QVBoxLayout()

        self.hsv_convert_btn = QPushButton("HSV convert")
        self.hsv_convert_btn.setEnabled(False)
        param_layout.addWidget(self.hsv_convert_btn)
        self.hsv_convert_btn.clicked.connect(self.convertHSV)

        self.group_low = GroupSlider("HSV Low", ['Hue', "Saturation", "Value"], enable=False, function= self.selectRange, default=[0,80,0])
        self.group_high = GroupSlider('HSV High', ['Hue', "Saturation", "Value"], enable=False, function= self.selectRange, default=[100,255,255])
        self.threshold = GroupSlider('Thresholds', ['Threshold'], [(0,255)], False, function=self._thresholdChanged, default=[125])

        self.low = self.group_low.default
        self.high = self.group_high.default
        self.threshold_value = self.threshold.default
        # mainWidget.setLayout(main_layout)
        param_layout.addWidget(self.group_low)
        param_layout.addWidget(self.group_high)

        self.mask_cvt = QPushButton('Convert Mask')
        param_layout.addWidget(self.mask_cvt)
        self.mask_cvt.clicked.connect(self._convertMask)

        param_layout.addWidget(self.threshold)
        self.crop_btn = QPushButton('Crop')
        param_layout.addWidget(self.crop_btn)
        self.crop_btn.clicked.connect(self._crop)

        param_widget = QWidget()
        param_widget.setLayout(param_layout)
        
        self.dock = QDockWidget('Parameter')
        self.dock.setWidget(param_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dockFeatures = QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable
        self.dock.setFeatures(self.dock.features() ^ self.dockFeatures)
        # self.resize(640,480)
    def showValue(self, value):
        print(value)

    def setPhoto(self, image):
        image_show = imutils.resize(image, width=640) if image.shape[1]>= image.shape[0] else imutils.resize(image, height=640)
        if len(image.shape) == 3:
            image_show = QImage(image_show, image_show.shape[1], image_show.shape[0], image_show.strides[0], QImage.Format_RGB888).rgbSwapped()
        else:
            image_show = QImage(image_show, image_show.shape[1], image_show.shape[0], QImage.Format_Grayscale8)
        self.image_frame.setPixmap(QPixmap.fromImage(image_show))
		
    def reset(self):
        self.image_raw = self.image_backup.copy()
        # self.hsv_convert_btn.setEnabled(False)
        self.group_low.setEnabled(False)
        self.group_high.setEnabled(False)
        self.threshold.setEnabled(False)
        self.setPhoto(self.image_raw)
    
    def openFile(self, _value=False):
        self.hsv_convert_btn.setEnabled(False)
        self.group_low.setEnabled(False)
        self.group_high.setEnabled(False)
        self.threshold.setEnabled(False)
        self.mask_cvt.setEnabled(False)
        self.crop_btn.setEnabled(False)
        path = self.currentPath()
        formats = ['*.%s' % fmt.data().decode("ascii").lower() for fmt in QImageReader.supportedImageFormats()]
        filters = "Image files (%s)" % ' '.join(formats)
        filename = QFileDialog.getOpenFileName(self, '%s - Choose Image file' % __appname__, path, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.loadFile(filename)
            self.filePath = filename
            # print(filename)
        self.save_action.setEnabled(True)


    def loadFile(self, filePath= None):
        
        if filePath is not None:
            filePath = ustr(filePath) 

            unicodeFilePath = ustr(filePath)
            unicodeFilePath = os.path.abspath(unicodeFilePath)

            self.image_raw = cv.imread(unicodeFilePath)
            self.image_backup = self.image_raw.copy()
            self.setPhoto(self.image_raw)

            self.hsv_convert_btn.setEnabled(True)
            return True
        return False
    def currentPath(self):
        return os.path.dirname(self.filePath) if self.filePath else '.'        

    def saveFileAs(self, _value=False):
        assert not self.image_save is None, "cannot save empty image"
        self._saveFile(self.saveFileDialog(False))

    def saveFileDialog(self, removeExt=True):
        caption = '%s - Choose File' % __appname__
        formats = ['*.%s' % fmt.data().decode("ascii").lower() for fmt in QImageReader.supportedImageFormats()]
        filters = "Image files (%s)" % ' '.join(formats)
        if self.defaultSaveDir is None:
            openDialogPath = self.currentPath()
        else:
            openDialogPath = self.defaultSaveDir
        dlg = QFileDialog(self, caption, openDialogPath, filters)
        dlg.setDefaultSuffix('.jpg')
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        filenameWithoutExtension = os.path.splitext(self.filePath)[0]
        dlg.selectFile(filenameWithoutExtension)
        dlg.setOption(QFileDialog.DontUseNativeDialog, False)
        if dlg.exec_():
            fullFilePath = ustr(dlg.selectedFiles()[0])
            # print(fullFilePath)
            self.defaultSaveDir = os.path.splitext(fullFilePath)[0]
            if removeExt:
                return os.path.splitext(fullFilePath)[0] # Return file path without the extension.
            else:
                return fullFilePath
        return ''

    def _saveFile(self, annotationFilePath):
        if annotationFilePath:
            print("Path:", annotationFilePath)
            try:
                cv.imwrite(annotationFilePath, self.image_save)
            except:
                print("ERROR")
            # self.setClean()
            # self.statusBar().showMessage('Saved to  %s' % annotationFilePath)
            # self.statusBar().show()

    def convertHSV(self):
        self.hsv_convert_btn.setEnabled(False)
        self.group_low.setEnabled(True)
        self.group_high.setEnabled(True)
        image = cv.cvtColor(self.image_raw, cv.COLOR_BGR2HSV)
        self.setPhoto(image)
        self.reset_action.setEnabled(True)
        self.image_save = image
        # th = ModifyColor(self)
        # th.changePixmap.connect(self.setImage)
        # th.start()

    def selectRange(self, value):
    
        if value['title'] == self.group_low.title:
            self.low[0] = value['Hue']
            self.low[1] = value['Saturation']
            self.low[2] = value['Value']
        elif value['title'] == self.group_high.title:
            self.high[0] = value['Hue']
            self.high[1] = value['Saturation']
            self.high[2] = value['Value']
        print("Low: {}, High: {}".format(self.low, self.high))
        print("Title low: {}, high: {}".format(self.group_low.title, self.group_high.title))
        self.image_range, image = remove.rangeGreen(self.image_raw, self.low, self.high)
        self.image_save = image
        self.setPhoto(image)
        self.mask_cvt.setEnabled(True)

    def _convertMask(self):
        self.group_low.setEnabled(False)
        self.group_high.setEnabled(False)
        self.threshold.setEnabled(True)
        self.BGR_image = cv.cvtColor(self.image_range, cv.COLOR_HSV2BGR)
        self.setPhoto(self.BGR_image)
        self.image_save = self.BGR_image
        print("RGB shape: ", self.BGR_image.shape)
        print("raw shape: ", self.image_raw.shape)

    def _thresholdChanged(self, value):
        if value['title'] == self.threshold.title:
            self.threshold_value[0] = value['Threshold']
        print("Threshold:", self.threshold_value, value)
        self.threshold_image = remove.remove_background(self.BGR_image, self.image_raw, self.threshold_value[0])
        threshold_image = cv.cvtColor(self.threshold_image, cv.COLOR_BGRA2BGR)
        # cv.imshow("thresh", self.threshold_image)
        # cv.waitKey(1)
        self.setPhoto(threshold_image)
        self.image_save = threshold_image
        self.crop_btn.setEnabled(True)
        self.mask_cvt.setEnabled(False)

    def _crop(self):
        self.backGround = remove.crop(self.threshold_image)
        self.image_save = self.backGround
        self.setPhoto(self.backGround)
    
def read(filename, default=None):
    try:
        reader = QImageReader(filename)
        reader.setAutoTransform(True)
        return reader.read()
    except:
        return default

def get_main_app(argv=[]):
    """
    Standard boilerplate Qt application code.
    Do everything but app.exec_() -- so that we can test the application in one thread
    """
    app = QApplication(argv)
    app.setApplicationName(__appname__)
    app.setWindowIcon(utils.newIcon('app'))
    win = MainWindow()
    win.show()
    return app, win


def main():
    app, win = get_main_app(sys.argv)
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
