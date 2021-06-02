try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

class GroupSlider(QGroupBox):
    def __init__(self, title, 
                slider_names=[], 
                ranges=[(0,180), (0,255), (0,255)], 
                enable = True, 
                function = None, 
                default = [0, 0 ,0]):
        super(GroupSlider, self).__init__(title=title)
        self.setEnabled(enable)
        self.layout = QGridLayout()
        self.slider_names = slider_names
        self.title =title
        self.ranges = ranges
        self.value_labels = []
        self.value = {}
        self.function = function
        self.value['title'] = self.title
        self.default = default

        for index, slider_name in enumerate(self.slider_names):
            self.layout.addWidget(QLabel(slider_name), index+1, 1)
            slider = QSlider(Qt.Horizontal)
            slider.setRange(self.ranges[index][0], self.ranges[index][1])
            slider.setFocusPolicy(Qt.StrongFocus)
            slider.setTickPosition(QSlider.TicksBothSides)
            slider.setPageStep(10)
            slider.setValue(self.default[index])
            value_label = QLabel(str(default[index]))
            # value_label.setObjectName(slider_name)
            self.value_labels.append(value_label)
            slider.setObjectName(slider_name)
            setattr(self, slider_name, self.value_labels[index])
            self.layout.addWidget(slider, index+1, 2)
            self.layout.addWidget(self.value_labels[index], index+1, 3)
            slider.valueChanged[int].connect(self.__valueChange)
            self.value[slider_name] = slider.value()
        self.setLayout(self.layout)

    def __valueChange(self, value):
        sender = self.sender()
        label = getattr(self, sender.objectName())
        label.setText(str(value))
        self.value[sender.objectName()] = value
        # print(self.value)
        if self.function is not None:
            self.function(self.value)

    # def setFunctionChanged(self)
        
        

