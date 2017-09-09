#############################################################################
#                                                                           #
#   Name:                                                                   #
#       renamer.py                                                          #
#                                                                           #
#   Desc:                                                                   #
#       Renames objects quickly.                                            #
#                                                                           #
#   Author:                                                                 #
#       Matt Jenkins                                                        #
#                                                                           #
#############################################################################

import renamerUI as customUI
import maya.cmds as cmds
import maya.OpenMayaUI as omUi
import re
from shiboken2 import wrapInstance
from functools import partial
from PySide2 import QtCore, QtGui, QtWidgets
from maya import OpenMaya

reload(customUI)

def maya_main_window():
    main_window_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def main():
    global myWindow
    global radValue
    global renameValue
    global findValue
    global replaceValue
    global prefixValue
    global prefixSymbol
    global suffixValue
    global replaceFix
    global objs
    radValue = 1
    renameValue = None
    findValue = None
    replaceValue = None
    prefixValue = None
    prefixSymbol = '_'
    suffixValue = None
    replaceFix = 0
    objs = None

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

        #Radio Buttons - All, Selected, Hierachy
        self.ui.all_Rad.clicked.connect(partial(self.updateRad,'all'))
        self.ui.selected_Rad.clicked.connect(partial(self.updateRad,'selected'))
        self.ui.heirachy_Rad.clicked.connect(partial(self.updateRad,'heirachy'))

        #Rename
        self.ui.rename_Ledit.textChanged.connect(self.updateRenameLedit)
        self.ui.rename_Btn.released.connect(self.updateRenameBtn)

        self.ui.clear_Btn.released.connect(self.updateClearBtn)

        #Find & Replace
        self.ui.find_Ledit.textChanged.connect(self.updateFindLedit)
        self.ui.replace_Ledit.textChanged.connect(self.updateReplaceLedit)
        self.ui.replace_Btn.released.connect(self.updateReplaceBtn)

        # Prefix & Suffix
        self.ui.prefix_Ledit.textChanged.connect(self.updatePrefixLedit)
        self.ui.prefix_Btn.released.connect(self.updatePrefixBtn)
        self.ui.suffix_Ledit.textChanged.connect(self.updateSuffixLedit)
        self.ui.suffix_Btn.released.connect(self.updateSuffixBtn)

        #Preset Suffix Buttons
        self.ui.loc_Btn.released.connect(self.updateLocBtn)
        self.ui.grp_Btn.released.connect(self.updateGrpBtn)
        self.ui.geo_Btn.released.connect(self.updateGeoBtn)
        self.ui.ctrl_Btn.released.connect(self.updateCtrlBtn)
        self.ui.hdl_Btn.released.connect(self.updateHdlBtn)
        self.ui.jnt_Btn.released.connect(self.updateJntBtn)
        self.ui.eff_Btn.released.connect(self.updateEffBtn)
        self.ui.bind_Btn.released.connect(self.updateBindBtn)
        self.ui.crv_Btn.released.connect(self.updateCrvBtn)
        self.ui.replaceFix_Chk.stateChanged.connect(self.updateReplaceFixChk)

        #Preset Prefix Buttons
        self.ui.prefixL_Btn.released.connect(self.updatePreLBtn)
        self.ui.prefixR_Btn.released.connect(self.updatePreRBtn)

        #Strip Buttons
        self.ui.stripL_Btn.released.connect(self.updateStripLBtn)
        self.ui.stripR_Btn.released.connect(self.updateStripRBtn)

        #Left Right Replace Buttons
        self.ui.L2R_Btn.released.connect(self.updateL2RBtn)
        self.ui.R2L_Btn.released.connect(self.updateR2LBtn)

        #Prefix Context Menu
        #self.ui.prefix_Btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.ui.prefix_Btn.customContextMenuRequested.connect(self.prefixBtnContext)


    def prefixBtnContext(self, pos):
        menu = QtGui.QMenu()
        menu.addAction("Set Prefix Symbol to '_'", lambda:self._prefixSymbol('_'))
        menu.addAction("Set Prefix Symbol to ':'", lambda:self._prefixSymbol(':'))
        menu.exec_(QtGui.QCursor.pos())

    def _prefixSymbol(self,symbol):
        global prefixSymbol
        prefixSymbol=symbol

#

    def updateRad(self,value,*args):
        global radValue
        if value == 'all':
            radValue=0
        elif value == 'selected':
            radValue=1
        elif value == 'heirachy':
            radValue=2

    def updateClearBtn(self,*args):
        self.clearFields()

    def updateRenameLedit(self,*args):
        global renameValue
        renameValue = self.ui.rename_Ledit.text()

    def updateRenameBtn(self,*args):
        self.rename(renameValue)

    def updateFindLedit(self,*args):
        global findValue
        findValue = self.ui.find_Ledit.text()

    def updateReplaceLedit(self,*args):
        global replaceValue
        replaceValue = self.ui.replace_Ledit.text()

    def updateReplaceBtn(self,*args):
        self.findReplace(findValue,replaceValue)

    def updatePrefixLedit(self,*args):
        global prefixValue
        prefixValue = self.ui.prefix_Ledit.text()

    def updatePrefixBtn(self,*args):
        self.prefixChange(prefixValue)

    def updateSuffixLedit(self,*args):
        global suffixValue
        suffixValue = self.ui.suffix_Ledit.text()

    def updateSuffixBtn(self,*args):
        self.suffixChange(suffixValue)

    def updateReplaceFixChk(self,value,*args):
        global replaceFix
        if value == 0:
            replaceFix = False
        else:
            replaceFix = True

    def updateLocBtn(self,*args):
        self.suffixChange('LOC')

    def updateGrpBtn(self,*args):
        self.suffixChange('GRP')

    def updateGeoBtn(self,*args):
        self.suffixChange('GEO')

    def updateCtrlBtn(self,*args):
        self.suffixChange('CTRL')

    def updateHdlBtn(self,*args):
        self.suffixChange('HDL')

    def updateJntBtn(self,*args):
        self.suffixChange('JNT')

    def updateEffBtn(self,*args):
        self.suffixChange('EFF')

    def updateBindBtn(self,*args):
        self.suffixChange('BIND')

    def updateCrvBtn(self,*args):
        self.suffixChange('CRV')

    def updatePreLBtn(self,*args):
        self.prefixChange('L')

    def updatePreRBtn(self,*args):
        self.prefixChange('R')

    def updateL2RBtn(self,*args):
        self.findReplace('L_','R_')

    def updateR2LBtn(self,*args):
        self.findReplace('R_','L_')

    def updateStripLBtn(self,*args):
        self.stripChars('left')

    def updateStripRBtn(self,*args):
        self.stripChars('right')


    def _getSelection(self,*args):
        objs=list()
        sel=list()
        if radValue == 0:
            cmds.select(all=True,hi=True)
        sList = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(sList)
        for i in range(sList.length()):
            mObj = OpenMaya.MObject()
            sList.getDependNode(i, mObj)
            objs.append(mObj)
        if radValue == 2:
            objs=self._getHierarchy(objs,sel)
        return objs

    def _getHierarchy(self,objs,sel,*args):
        for x in objs:
            children=list()
            sel.append(x)
            if x.hasFn(OpenMaya.MFn.kTransform):
                x=OpenMaya.MFnDagNode(x)
                numChildren = x.childCount()
            else:
                numChildren = 0
            for i in range(numChildren):
                child=x.child(i)
                if child.hasFn(OpenMaya.MFn.kTransform):
                    children.append(child)
            self._getHierarchy(children,sel)
        return sel

    def _getPath(self,obj,*args):
        if obj.hasFn(OpenMaya.MFn.kTransform) or obj.hasFn(OpenMaya.MFn.kShape):
            dagNode = OpenMaya.MFnDagNode(obj)
            dagPath = OpenMaya.MDagPath()
            dagNode.getPath(dagPath)
            objPath = dagPath.fullPathName()
            objName=objPath.rpartition('|')
            objName=objName[-1]
        else:
            depNode = OpenMaya.MFnDependencyNode(obj)
            objPath = depNode.name()
            objName=objPath

        return objPath,objName

    def _swapDigits(self,n,i=0,*args):
        minDigitLength=0
        bufferChar=''
        findHashes = re.findall("(#+)", n)
        newN=n
        if findHashes:
            minDigitLength=len(findHashes[0])
            bufferChar=findHashes[0]
            newN=str(i+1).zfill(minDigitLength).join(n.split(bufferChar))
            while cmds.objExists(newN):
                i=i+1
                newN=str(i+1).zfill(minDigitLength).join(n.split(bufferChar))
        return newN

    def rename(self,newName,*args):
        if newName:
            objs=self._getSelection()
            oldNewName=newName
            for i,x in enumerate(objs):
                lN,sN=self._getPath(x)
                newName=self._swapDigits(oldNewName,i)
                num=1
                while cmds.objExists(newName):
                    newName = oldNewName+str(num)
                    num=num+1
                cmds.rename(lN, newName)

    def findReplace(self,f,r,*args):
        objs=self._getSelection()
        for i,x in enumerate(objs):
            lN,sN=self._getPath(x)
            newR=self._swapDigits(r,i)
            newName=sN.replace(f,newR)
            try:
                cmds.rename(lN,newName)
            except:
                continue

    def prefixChange(self,p,*args):
        objs=self._getSelection()
        for i,x in enumerate(objs):
            lN,sN=self._getPath(x)
            oldName=sN
            if replaceFix:
                if prefixSymbol in sN:
                    oldPartName = list(sN.partition(prefixSymbol))
                    sN=oldPartName[-1]
            newP=self._swapDigits(p,i)
            newName=newP+prefixSymbol+sN
            print(newName)
            if not newName == oldName:
                oldNewName=newName
                num=1
                while cmds.objExists(newName):
                    newName = oldNewName+str(num)
                    num=num+1
                try:
                    cmds.rename(lN,newName)
                except:
                    continue

    def suffixChange(self,s,*args):
        objs=self._getSelection()
        for i,x in enumerate(objs):
            lN,sN=self._getPath(x)
            oldName=sN
            if replaceFix:
                if '_' in sN:
                    oldPartName = list(sN.rpartition('_'))
                    sN=oldPartName[0]
            newS=self._swapDigits(s,i)
            newName=sN+'_'+newS
            if not newName == oldName:
                num=1
                while cmds.objExists(newName):
                    newName = sN+str(num)+'_'+newS
                    num=num+1
                try:
                    cmds.rename(lN,newName)
                except:
                    continue

    def stripChars(self,side,*args):
        objs=self._getSelection()
        for i,x in enumerate(objs):
            lN,sN=self._getPath(x)
            strippedName = sN
            if side == 'right':
                strippedName = sN[:-1]
            elif side == 'left':
                strippedName = sN[1:]
            num = 1
            newName=strippedName
            while cmds.objExists(newName):
                newName = strippedName+str(num)
                num=num+1
            try:
                cmds.rename(lN,newName)
            except:
                continue

    def clearFields(self,*args):
        self.ui.rename_Ledit.clear()
        self.ui.find_Ledit.clear()
        self.ui.replace_Ledit.clear()
        self.ui.suffix_Ledit.clear()
        self.ui.prefix_Ledit.clear()



main()