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

class Slider(QLayout):

    def __init__(self, title, maximum, default= 20, parent = None ):
        super(Slider, self).__init__(parent)

        layout = QVBoxLayout()
        self.title = QLabel(title)
        layout.addWidget(self.title)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(maximum)
        self.slider.setValue(default)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setMaximumWidth = 100
        layout.addWidget(self.slider)

        self.value = QLabel('0')
        layout.addWidget(self.value)
        self.slider.valueChanged.connect(self.valueChange)

    def valueChange(self):
        value = self.slider.value()
        self.value.setValue(value)



