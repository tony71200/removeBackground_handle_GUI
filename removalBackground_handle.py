import sys
import codecs
import os.path
import platform
import subprocess
from functools import partial
import threading
import cv2 as cv

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
               
        
        #Actions
        action = partial(utils.newAction, self)
        open_action = action(text='Open File', function=self.openFile, 
                            shortcut='Crt+O', icon='open',
                            tip='Open Image File', )
        quit_action = action('Exit', self.close, 'Ctrl+Q', 'quit')
        save_action = action('Save', self.saveFile, 'Ctrl+S', "save", 
                            "Save current File", enabled= False)
        
        self.tools = self.toolbar('toolbar', (open_action, save_action, quit_action))
        mainWidget = QWidget()

        param_layout = QVBoxLayout()
        param_layout.addLayout(self.createCustomSlider("Hue Low", self.valueChange))
        param_layout.addLayout(self.createCustomSlider("Saturation Low", self.valueChange, (0,255)))
        param_layout.addLayout(self.createCustomSlider("Value Low", self.valueChange, (0,255)))

        param_layout.addLayout(self.createCustomSlider("Hue High", self.valueChange))
        param_layout.addLayout(self.createCustomSlider("Saturation High", self.valueChange, (0,255)))
        param_layout.addLayout(self.createCustomSlider("Value HIgh", self.valueChange, (0,255)))

        param_layout.addLayout(self.createCustomSlider("Threshold", self.valueChange, (0,255)))

        main_layout = QHBoxLayout()
        # main_layout.setGeometry((1000, 500))
        main_layout.addWidget(Color('Green'))
        main_layout.addLayout(param_layout)

        
        mainWidget.setLayout(main_layout)
        self.setCentralWidget(mainWidget)

    def createCustomSlider(self, title, function=None, range=(0,180)):
        layout = QHBoxLayout()
        title_name = QLabel(title)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(range[0], range[1])
        slider.setMaximumWidth(200)
        slider.setPageStep(1)
        self.value_label = QLabel('0')
        self.value_label.setObjectName(title)
        slider.setObjectName(title)

        setattr(self, title, self.value_label)

        layout.addWidget(title_name)
        layout.addWidget(slider)
        layout.addWidget(self.value_label)
        slider.valueChanged[int].connect(function)

        # slider.valueChanged.connect(function)
        return layout

    def valueChange(self, value):
        sender = self.sender()
        label = getattr(self, sender.objectName())
        label.setText(str(value))

    def openFile(self, _value=False):
        path = os.path.dirname(ustr(self.filePath)) if self.filePath else '.'
        formats = ['*.%s' % fmt.data().decode("ascii").lower() for fmt in QImageReader.supportedImageFormats()]
        filters = "Image files (%s)" % ' '.join(formats)
        filename = QFileDialog.getOpenFileName(self, '%s - Choose Image file' % __appname__, path, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            # self.loadFile(filename)
            print(filename)

    def saveFile(self, _value=False):
        if self.defaultSaveDir is not None and len(ustr(self.defaultSaveDir)):
            if self.filePath:
                imgFileName = os.path.basename(self.filePath)
                savedFileName = os.path.splitext(imgFileName)[0]
                savedPath = os.path.join(ustr(self.defaultSaveDir), savedFileName)
                self._saveFile(savedPath)
        else:
            imgFileDir = os.path.dirname(self.filePath)
            imgFileName = os.path.basename(self.filePath)
            savedFileName = os.path.splitext(imgFileName)[0]
            savedPath = os.path.join(imgFileDir, savedFileName)
            new_path = self.saveFileDialog(removeExt=False)
            print(new_path)
            # self._saveFile(savedPath if self.labelFile
            #                else self.saveFileDialog(removeExt=False))
    
    def saveFileDialog(self, removeExt=True):
        caption = '%s - Choose File' % __appname__
        filters = 'File (*%s)' % LabelFile.suffix
        openDialogPath = self.currentPath()
        dlg = QFileDialog(self, caption, openDialogPath, filters)
        dlg.setDefaultSuffix(LabelFile.suffix[1:])
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        filenameWithoutExtension = os.path.splitext(self.filePath)[0]
        dlg.selectFile(filenameWithoutExtension)
        dlg.setOption(QFileDialog.DontUseNativeDialog, False)
        if dlg.exec_():
            fullFilePath = ustr(dlg.selectedFiles()[0])
            if removeExt:
                return os.path.splitext(fullFilePath)[0] # Return file path without the extension.
            else:
                return fullFilePath
        return ''

    def _saveFile(self, annotationFilePath):
        if annotationFilePath and self.saveLabels(annotationFilePath):
            self.setClean()
            self.statusBar().showMessage('Saved to  %s' % annotationFilePath)
            self.statusBar().show()
    
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
