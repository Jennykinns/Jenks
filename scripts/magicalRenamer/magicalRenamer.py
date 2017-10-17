import re
from shiboken2 import wrapInstance
from functools import partial
from PySide2 import QtCore, QtGui, QtWidgets

import maya.cmds as cmds
import maya.OpenMayaUI as omUi

import magicalRenamerUI as customUI
import magicalRenamerSmallUI as smallUI

from Jenks.scripts.rigModules import utilityFunctions as utils


reload(customUI)
reload(utils)

def maya_main_window():
    main_window_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def main():
    try:
        myWindow.close()
    except:
        pass
    myWindow = myTool(parent=maya_main_window())
    print('Loaded')
    myWindow.show()

def getSelection(radVal):
    oldSel = cmds.ls(sl=1)
    if radVal == 'heirachy':
        cmds.select(cl=1)
        for each in oldSel:
            allChilds = cmds.listRelatives(each, ad=1, f=1)
            shapeChilds = cmds.listRelatives(each, ad=1, f=1, type='shape')
            allChilds.reverse()
            cmds.select(each, add=1)
            cmds.select(allChilds, add=1)
            cmds.select(shapeChilds, d=1)

class myTool(QtWidgets.QDialog):
    def __init__(self, parent, radVal=None, renVal='', sideVal='C', findVal=None, replVal=None):
        reload(customUI)
        super(myTool, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = customUI.Ui_MainWindow()
        self.ui.setupUi(self)

        self.radVal = radVal
        self.renameVal = renVal
        self.sideVal = sideVal
        self.findVal = findVal
        self.replaceVal = replVal

        self.ui.rename_Ledit.setText(self.renameVal)
        self.ui.side_Cbox.setCurrentText(self.sideVal)
        self.ui.find_Ledit.setText(self.findVal)
        self.ui.replace_Ledit.setText(self.replaceVal)
        if self.radVal == 'heirachy':
            self.ui.heirachy_Rad.click()

        ## Radio Buttons - Selected, Hierachy
        # self.ui.all_Rad.clicked.connect(partial(self.updateRad,'all'))
        self.ui.selected_Rad.clicked.connect(partial(self.updateRad,'selected'))
        self.ui.heirachy_Rad.clicked.connect(partial(self.updateRad,'heirachy'))
        ## Side ComboBox
        self.ui.side_Cbox.currentIndexChanged.connect(self.updateSideCbox)
        ## Rename
        self.ui.rename_Ledit.textChanged.connect(self.updateRenameLedit)
        self.ui.rename_Btn.released.connect(self.renameSelection)
        ## Clear
        self.ui.clear_Btn.released.connect(self.clearFields)
        ## Find & Replace
        self.ui.find_Ledit.textChanged.connect(self.updateFindLedit)
        self.ui.replace_Ledit.textChanged.connect(self.updateReplaceLedit)
        self.ui.replace_Btn.released.connect(self.findReplaceSelection)
        ## Prefix & Suffix
        self.ui.prefix_Btn.released.connect(self.addPrefix)
        self.ui.suffix_Btn.released.connect(self.addSuffix)
        ## Strip Buttons
        self.ui.stripL_Btn.released.connect(self.nameStripL)
        self.ui.stripR_Btn.released.connect(self.nameStripR)

        ## Mini Button
        self.ui.mini_Btn.released.connect(self.minify)

    def updateRad(self, val, *args):
        self.radVal = val

    def updateRenameLedit(self, *args):
        self.renameVal = self.ui.rename_Ledit.text()

    def updateFindLedit(self, *args):
        self.findVal = self.ui.find_Ledit.text()

    def updateReplaceLedit(self, *args):
        self.replaceVal = self.ui.replace_Ledit.text()

    def updateSideCbox(self, *args):
        self.sideVal = self.ui.side_Cbox.currentText()


    def doSelection(self):
        getSelection(self.radVal)


    def renameSelection(self, *args):
        ## do renameself.doSelection()
        self.doSelection()
        utils.renameSelection(self.renameVal, self.sideVal)

    def findReplaceSelection(self, *args):
        ## do findReplace
        self.doSelection()
        utils.findReplaceSelection(self.findVal, self.replaceVal)

    def addSuffix(self, *args):
        self.doSelection()
        utils.addSuffixToSelection()

    def addPrefix(self, *args):
        self.doSelection()
        utils.swapSideSelection(self.sideVal)

    def nameStripL(self, *args):
        self.doSelection()
        ## do L strip
        utils.stripNameSelection()

    def nameStripR(self, *args):
        self.doSelection()
        ## do R strip
        utils.stripNameSelection(stripFromRight=True)

    def clearFields(self,*args):
        self.ui.rename_Ledit.clear()
        self.ui.find_Ledit.clear()
        self.ui.replace_Ledit.clear()

    def minify(self, *args):
        pos = self.pos()
        self.close()
        myWindow = smallMyTool(maya_main_window(), self.radVal, self.renameVal,
                               self.sideVal, self.findVal, self.replaceVal)
        myWindow.move(pos)
        myWindow.show()


class smallMyTool(QtWidgets.QDialog):
    def __init__(self, parent, radVal=None, renVal='', sideVal='C', findVal=None, replVal=None):
        reload(smallUI)
        super(smallMyTool, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = smallUI.Ui_MainWindow()
        self.ui.setupUi(self)

        self.radVal = radVal
        self.renameVal = renVal
        self.sideVal = sideVal
        self.findVal = findVal
        self.replaceVal = replVal

        self.ui.rename_Ledit.setText(self.renameVal)
        self.ui.side_Cbox.setCurrentText(self.sideVal)

        ## Side ComboBox
        self.ui.side_Cbox.currentIndexChanged.connect(self.updateSideCbox)
        ## Rename
        self.ui.rename_Ledit.textChanged.connect(self.updateRenameLedit)
        self.ui.rename_Btn.released.connect(self.renameSelection)

        ## magnify
        self.ui.mini_Btn.released.connect(self.magnify)


    def updateRenameLedit(self, *args):
        self.renameVal = self.ui.rename_Ledit.text()

    def updateSideCbox(self, *args):
        self.sideVal = self.ui.side_Cbox.currentText()


    def doSelection(self):
        getSelection(self.radVal)

    def renameSelection(self, *args):
        ## do renameself.doSelection()
        self.doSelection()
        utils.renameSelection(self.renameVal, self.sideVal)

    def magnify(self, *args):
        pos = self.pos()
        self.close()
        myWindow = myTool(maya_main_window(), self.radVal, self.renameVal,
                          self.sideVal, self.findVal, self.replaceVal)
        myWindow.move(pos)
        myWindow.show()