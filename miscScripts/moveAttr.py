import moveAttrUI_qt5 as customUI
import maya.OpenMayaUI as omUi
import maya.cmds as cmds
import sys
import maya.mel  as mel
from shiboken2 import wrapInstance
from functools import partial
from PySide2 import QtCore, QtGui, QtWidgets

reload(customUI)

def maya_main_window():
    main_window_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def main():
    global myWindow

    try:
        myWindow.close()
    except: pass
    myWindow = myTool(parent=maya_main_window())
    myWindow.show()


class myTool(QtWidgets.QDialog):
    def __init__(self,parent = None):

        reload(customUI)
        print("loaded")

        super(myTool, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui =  customUI.Ui_MainWindow()

        self.ui.setupUi(self)

        self.ui.up_Btn.clicked.connect(self.updateUpBtn)
        self.ui.down_Btn.clicked.connect(self.updateDownBtn)

    def updateUpBtn(self,*args):
        self.sk_attShiftProc(1)
    def updateDownBtn(self,*args):
        self.sk_attShiftProc(0)



    def sk_attShiftProc(self, mode, *args):
        print(mode)
        obj = cmds.channelBox('mainChannelBox',q=True,mol=True)
        if obj:
            attr = cmds.channelBox('mainChannelBox',q=True,sma=True)
            if attr:
                for eachObj in obj:
                    udAttr = cmds.listAttr(eachObj,ud=True)
                    if not attr[0] in udAttr:
                        sys.exit('selected attribute is static and cannot be shifted')
                    #temp unlock all user defined attributes
                    attrLock = cmds.listAttr(eachObj,ud=True,l=True)
                    if attrLock:
                        for alck in attrLock:
                            cmds.setAttr(eachObj + '.' + alck,lock=0)
                    #shift down
                    if mode == 0:
                        if len(attr) > 1:
                            attr.reverse()
                            sort = attr
                        if len(attr) == 1:
                            sort = attr
                        for i in sort:
                            attrLs = cmds.listAttr(eachObj,ud=True)
                            attrSize = len(attrLs)
                            attrPos = attrLs.index(i)
                            cmds.deleteAttr(eachObj,at=attrLs[attrPos])
                            cmds.undo()
                            for x in range(attrPos+2,attrSize,1):
                                cmds.deleteAttr(eachObj,at=attrLs[x])
                                cmds.undo()
                    #shift up
                    if mode == 1:
                        for i in attr:
                            attrLs = cmds.listAttr(eachObj,ud=True)
                            attrSize = len(attrLs)
                            attrPos = attrLs.index(i)
                            if attrLs[attrPos-1]:
                                cmds.deleteAttr(eachObj,at=attrLs[attrPos-1])
                                cmds.undo()
                            for x in range(attrPos+1,attrSize,1):
                                cmds.deleteAttr(eachObj,at=attrLs[x])
                                cmds.undo()
                    #relock all user defined attributes
                    if attrLock:
                        for alck in attrLock:
                            cmds.setAttr(eachObj + '.' + alck,lock=1)

main()