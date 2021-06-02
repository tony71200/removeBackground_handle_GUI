import hashlib
import sys

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *


def newIcon(icon):
    print('./icon/' + icon)
    return QIcon('./icon/' + icon+'.png')

def addActions(widget, actions):
    for action in actions:
        if action is None:
            widget.addSeparator()
        elif isinstance(action, QMenu):
            widget.addMenu(action)
        else:
            widget.addAction(action)

def newAction(parent, text, function=None, shortcut=None, icon=None,
            tip=None, checkable=False, enabled=True):
    """
        Create a new action
    """
    action = QAction(text, parent)
    if icon is not None:
        action.setIcon(newIcon(icon=icon))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            action.setShortcuts(shortcut)
        else:
            action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    if function is not None:
        action.triggered.connect(function)
    if checkable:
        action.setCheckable(True)
    action.setEnabled(enabled)
    return action