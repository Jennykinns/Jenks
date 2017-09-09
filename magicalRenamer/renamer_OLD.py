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
from shiboken import wrapInstance
from functools import partial
from PySide import QtCore, QtGui
from maya import OpenMaya

reload(customUI)

def maya_main_window():
    main_window_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

def main():
    global myWindow
    global radValue
    global renameValue
    global findValue
    global replaceValue
    global prefixValue
    global suffixValue
    global replaceFix
    global objs
    radValue = 1
    renameValue = None
    findValue = None
    replaceValue = None
    prefixValue = None
    suffixValue = None
    replaceFix = 0
    objs = None

    try:
        myWindow.close()
    except: pass
    myWindow = myTool(parent=maya_main_window())
    myWindow.show()


class myTool(QtGui.QDialog):
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

        #Find & Replace
        self.ui.find_Ledit.textChanged.connect(self.updateFindLedit)
        self.ui.replace_Ledit.textChanged.connect(self.updateReplaceLedit)
        self.ui.replace_Btn.released.connect(self.updateReplaceBtn)

        # Prefix & Suffix
        self.ui.prefix_Ledit.textChanged.connect(self.updatePrefixLedit)
        self.ui.prefix_Btn.released.connect(self.updatePrefixBtn)
        self.ui.suffix_Ledit.textChanged.connect(self.updateSuffixLedit)
        self.ui.suffix_Btn.released.connect(self.updateSuffixBtn)

        #Bottom Buttons
        self.ui.loc_Btn.released.connect(self.updateLocBtn)
        self.ui.grp_Btn.released.connect(self.updateGrpBtn)
        self.ui.geo_Btn.released.connect(self.updateGeoBtn)
        self.ui.ctrl_Btn.released.connect(self.updateCtrlBtn)
        self.ui.hdl_Btn.released.connect(self.updateHdlBtn)
        self.ui.jnt_Btn.released.connect(self.updateJntBtn)
        self.ui.replaceFix_Chk.stateChanged.connect(self.updateReplaceFixChk)
        self.ui.clear_Btn.released.connect(self.updateClearBtn)

        #Left Right Replace Buttons
        self.ui.L2R_Btn.released.connect(self.updateL2RBtn)
        self.ui.R2L_Btn.released.connect(self.updateR2LBtn)



    def updateRad(self,value,*args):
        global radValue
        if value == 'all':
            radValue=0
        elif value == 'selected':
            radValue=1
        elif value == 'heirachy':
            radValue=2

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

    def updateClearBtn(self,*args):
        self._clearFields()

    def updateL2RBtn(self,*args):
        self.findReplace('_L_','_R_')

    def updateR2LBtn(self,*args):
        self.findReplace('_R_','_L_')



    def suffixChange(self,s,*args):
        global objs
        objs=self._getObjects()
        if replaceFix:
            for i, x in enumerate(objs):
                if not radValue == 0:
                    lN,sN=x
                    newName = list(sN.rpartition('_'))
                    try:
                        newName.remove('_')
                        newName[1]=s
                        newName[1] = self._swapDigits(newName[1],i)
                        newName='_'.join(newName)
                        cmds.rename(lN,newName)
                    except:
                        try:
                            newS = self._swapDigits(s,i)
                            cmds.rename(lN, sN +"_"+newS)
                        except:
                            continue
                else:
                    newName = list(x.rpartition('_'))
                    try:
                        newName.remove('_')
                        newName[1]=s
                        newName[1] = self._swapDigits(newName[1],i)
                        newName='_'.join(newName)
                        cmds.rename(x,newName)
                    except:
                        try:
                            newS = self._swapDigits(s,i)
                            cmds.rename(x, x +"_"+newS)
                        except:
                            continue
        else:
            for i, x in enumerate(objs):
                if not radValue == 0:
                    lN,sN=x
                    try:
                        newS = self._swapDigits(s,i)
                        cmds.rename(lN, sN +"_"+newS)
                    except:
                            continue
                else:
                    try:
                        newS = self._swapDigits(s,i)
                        cmds.rename(x, x +"_"+newS)
                    except:
                            continue

    def prefixChange(self,p,*args):
        global objs
        objs=self._getObjects()
        if replaceFix:
            for i, x in enumerate(objs):
                if not radValue == 0:
                    lN,sN=x
                    newName = list(sN.partition('_'))
                    try:
                        newName.remove('_')
                        newName[0]=p
                        newName[0] = self._swapDigits(newName[0],i)
                        newName='_'.join(newName)
                        cmds.rename(lN,newName)
                    except:
                        try:
                            newP = self._swapDigits(p,i)
                            cmds.rename(lN, newP+"_"+ sN)
                        except:
                            continue
                else:
                    newName = list(x.partition('_'))
                    try:
                        newName.remove('_')
                        newName[0]=p
                        newName[0] = self._swapDigits(newName[0],i)
                        newName='_'.join(newName)
                        cmds.rename(x,newName)
                    except:
                        continue
        for i, x in enumerate(objs):
            if not radValue == 0:
                lN,sN=x
                try:
                    newP = self._swapDigits(p,i)
                    cmds.rename(lN, newP+"_"+ sN)
                except:
                    continue
            else:
                try:
                    newP = self._swapDigits(p,i)
                    cmds.rename(x, newP+"_"+ x)
                except:
                    continue

    def findReplace(self,f,r,*args):
        global objs
        objs=self._getObjects()
        for i, x in enumerate(objs):
            if not radValue == 0:
                lN,sN=x
                try:
                    newR=self._swapDigits(r,i)
                    newName=sN.replace(f,newR)
                    cmds.rename(lN,newName)
                except:
                    continue
            else:
                try:
                    newR=self._swapDigits(r,i)
                    newName=x.replace(f,newR)
                    cmds.rename(x,newName)
                except:
                    continue

    def rename(self,ren,*args):
        global objs
        if ren:
            objs=self._getObjects()
            for i, x in enumerate(objs):
                if not radValue == 0:
                    lN,sN=x
                    newName = ren
                    self._swapDigits(newName,i)
                    try:
                        newName = ren
                        newName = self._swapDigits(newName,i)
                        cmds.rename(lN,newName)
                    except:
                        continue
                else:
                    newName = ren
                    self._swapDigits(newName,i)
                    try:
                        newName = ren
                        newName = self._swapDigits(newName,i)
                        cmds.rename(x,newName)
                    except:
                        continue



    def _getObjects(self,*args):
        sel=list()
        if radValue == 0:
            #sel=zip(cmds.ls(l=True),cmds.ls())
            sel=cmds.ls()
        elif radValue == 1:
            sel=zip(cmds.ls(sl=True,l=True),cmds.ls(sl=True))
            sel.sort(reverse=True)
        elif radValue == 2:
            parent=cmds.ls(sl=True,l=True)
            cmds.select(parent,hi=True)
            sel=zip(cmds.ls(sl=True,l=True,tr=True),cmds.ls(sl=True,tr=True))
            sel.sort(reverse=True)
            cmds.select(parent)
        return sel

    def _swapDigits(self,n,i=0,*args):
        minDigitLength=0
        bufferChar=''
        findHashes = re.findall("(#+)", n)
        if findHashes:
            minDigitLength=len(findHashes[0])
            bufferChar=findHashes[0]
            if not radValue==2:
                n=str(i+1).zfill(minDigitLength).join(n.split(bufferChar))
            else:
                objsLength=len(objs)+1
                print(objsLength)
                newI=objsLength-i
                n=str(newI-1).zfill(minDigitLength).join(n.split(bufferChar))
        return n

    def _clearFields(self,*args):
        self.ui.rename_Ledit.clear()
        self.ui.find_Ledit.clear()
        self.ui.replace_Ledit.clear()
        self.ui.suffix_Ledit.clear()
        self.ui.prefix_Ledit.clear()



main()