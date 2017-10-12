import re
from shiboken2 import wrapInstance
from functools import partial
from PySide2 import QtCore, QtGui, QtWidgets

import maya.cmds as cmds
import maya.OpenMayaUI as omUi

import renamerUI as customUI

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
    myWindow.show()

class myTool(QtWidgets.QDialog):
    def __init__(self, parent=None):
        reload(customUI)
        print('Loaded')
        super(myTool, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = customUI.Ui_MainWindow()
        self.ui.setupUi(self)

        self.radVal = None
        self.renameVal = None
        self.findVal = None
        self.replaceVal = None
        # self.prefixVal = None
        # self.suffixVal = None

        ## Radio Buttons - All, Selected, Hierachy
        self.ui.all_Rad.clicked.connect(partial(self.updateRad,'all'))
        self.ui.selected_Rad.clicked.connect(partial(self.updateRad,'selected'))
        self.ui.heirachy_Rad.clicked.connect(partial(self.updateRad,'heirachy'))
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
        # self.ui.prefix_Ledit.textChanged.connect(self.updatePrefixLedit)
        # self.ui.prefix_Btn.released.connect(self.updatePrefixBtn)
        # self.ui.suffix_Ledit.textChanged.connect(self.updateSuffixLedit)
        # self.ui.suffix_Btn.released.connect(self.updateSuffixBtn)

        ## Preset Prefix Buttons
        # self.ui.prefixL_Btn.released.connect(self.updatePreLBtn)
        # self.ui.prefixR_Btn.released.connect(self.updatePreRBtn)

        ## Strip Buttons
        self.ui.stripL_Btn.released.connect(self.nameStripL)
        self.ui.stripR_Btn.released.connect(self.nameStripR)

        ## Left Right Replace Buttons
        self.ui.L2R_Btn.released.connect(self.nameLeftToRight)
        self.ui.R2L_Btn.released.connect(self.nameRightToLeft)

    def updateRad(self, val, *args):
        if val == 'all':
            self.radVal = 0
        elif val == 'selected':
            self.radVal = 1
        else:
            self.radVal = 2

    def updateRenameLedit(self, *args):
        self.renameVal = self.ui.rename_Ledit.text()

    def updateFindLedit(self, *args):
        self.findVal = self.ui.find_Ledit.text()

    def updateReplaceLedit(self, *args):
        self.replaceVal = self.ui.replace_Ledit.text()


    def renameSelection(self, *args):
        ## do rename
        utils.renameSelection(self.renameVal)

    def findReplaceSelection(self, *args):
        ## do findReplace
        utils.findReplaceSelection(self.findVal, self.replaceVal)

    def nameStripL(self, *args):
        ## do L strip
        utils.stripNameSelection()

    def nameStripR(self, *args):
        ## do R strip
        utils.stripNameSelection(stripFromRight=True)

    def nameLeftToRight(self, *args):
        ## do L -> R
        utils.swapSideSelection('R')

    def nameRightToLeft(self, *args):
        ## do R -> L
        utils.swapSideSelection('L')

    def clearFields(self,*args):
        self.ui.rename_Ledit.clear()
        self.ui.find_Ledit.clear()
        self.ui.replace_Ledit.clear()
        self.ui.suffix_Ledit.clear()
        self.ui.prefix_Ledit.clear()