import testUI as customUI
import maya.OpenMayaUI as omUi
from shiboken import wrapInstance
from functools import partial
from PySide import QtCore, QtGui

reload(customUI)

def maya_main_window():
    main_window_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

def main():
    global myWindow

    try:
        myWindow.close()
    except: pass
    myWindow = myTool(parent=maya_main_window())
    myWindow.show()

def context():
    global cWindow

    try:
        cWindow.close()
    except: pass
    cWindow = contextTool(parent=maya_main_window())
    cWindow.show()


class myTool(QtGui.QDialog):
    def __init__(self,parent = None):

        reload(customUI)
        print("loaded")

        super(myTool, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui =  customUI.Ui_MainWindow()

        self.ui.setupUi(self)

    def contextMenuEvent(self,event):
        menu = QtGui.QMenu(self)
        quitAction = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAction:
            context()

class contextTool(QtGui.QDialog):
    def __init__(self,parent=None):

        reload(customUI)

        super(contextTool,self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = customUI.Ui_MainWindow()

        self.ui.setupUi(self)

main()