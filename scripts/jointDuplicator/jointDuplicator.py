#############################################################################
#                                                                           #
#   Name:                                                                   #
#       jointDuplicator.py                                             #
#                                                                           #
#   Desc:                                                                   #
#       Creates duplicate sets of joints with an attribute to control       #
#       the blend.                                                          #
#                                                                           #
#   Author:                                                                 #
#       Matt Jenkins                                                        #
#                                                                           #
#############################################################################


import jointDuplicatorUI as customUI
import maya.OpenMayaUI as omUi
import maya.cmds as mc
from functools import partial

try:
    from PySide import QtGui, QtCore
    import PySide.QtGui as QtWidgets
    from shiboken import wrapInstance
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets
    from shiboken2 import wrapInstance


def maya_main_window():
    main_window_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def main():
    global myWindow
    global ctrlCrvBoxValue
    global suffixABoxValue
    global suffixBBoxValue
    global attrNameBoxValue
    global attrNiceNameBoxValue
    global curSuffixBoxValue
    global heirachyMode
    ctrlCrvBoxValue = None
    suffixABoxValue = 'IK'
    suffixBBoxValue = 'FK'
    attrNameBoxValue = 'IKFKSwitch'
    attrNiceNameBoxValue = 'IK / FK Switch'
    curSuffixBoxValue = 'result'
    heirachyMode = False

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
        self.ui =  customUI.Ui_MainWindow() #Define UI class in module

        self.ui.setupUi(self) # start window

        self.ui.ctrlCrvBox.textChanged.connect(self.updateCtrlCrvBox)
        self.ui.setCtrlCrvBtn.released.connect(self.updateCtrlCrvBtn)
        self.ui.createBtn.released.connect(self.updateCreateBtn)
        self.ui.modeSelRad.clicked.connect(partial(self.updateModeRad, 'modeSel'))
        self.ui.modeHeirRad.clicked.connect(partial(self.updateModeRad, 'modeHeir'))
        self.ui.suffixABox.textChanged.connect(self.updateSuffixABox)
        self.ui.suffixBBox.textChanged.connect(self.updateSuffixBBox)
        self.ui.attrNameBox.textChanged.connect(self.updateAttrNameBox)
        self.ui.attrNiceNameBox.textChanged.connect(self.updateAttrNiceNameBox)
        self.ui.curSuffixBox.textChanged.connect(self.updateCurSuffixBox)

    def updateSuffixABox(self, *args):
        global suffixABoxValue
        suffixABoxValue = self.ui.suffixABox.text()

    def updateSuffixBBox(self, *args):
        global suffixBBoxValue
        suffixBBoxValue = self.ui.suffixBBox.text()

    def updateAttrNameBox(self, *args):
        global attrNameBoxValue
        attrNameBoxValue = self.ui.attrNameBox.text()

    def updateAttrNiceNameBox(self, *args):
        global attrNiceNameBoxValue
        attrNiceNameBoxValue = self.ui.attrNiceNameBox.text()

    def updateCurSuffixBox(self, *args):
        global curSuffixBoxValue
        curSuffixBoxValue = self.ui.curSuffixBox.text()

    def updateCtrlCrvBox(self, *args):
        global ctrlCrvBoxValue
        ctrlCrvBoxValue = self.ui.ctrlCrvBox.text()
        if mc.objExists(ctrlCrvBoxValue):
            self.ui.ctrlCrvBox.setStyleSheet("background-color: rgb(90, 150, 50);")
        else:
            self.ui.ctrlCrvBox.setStyleSheet("background-color: rgb(110, 90, 90);")

    def updateCtrlCrvBtn(self, *args):
        crvSelection = mc.ls(sl=True)
        crvSelection = str(crvSelection)
        crvSelection = crvSelection.replace("[u'",'')
        crvSelection = crvSelection.replace("']",'')
        crvSelection = crvSelection.replace("[",'')
        crvSelection = crvSelection.replace("]",'')
        self.ui.ctrlCrvBox.setText(crvSelection)

    def updateModeRad(self, value, *args):
        global heirachyMode
        if value == 'modeSel':
            heirachyMode = False
        elif value == 'modeHeir':
            heirachyMode = True

    def updateCreateBtn(self, *args):
        self.createAttr()

        if heirachyMode:
            #-- Joint Hierachy Mode
            selJoints = mc.ls(sl=True, type='joint')

            if not selJoints:
                            mc.confirmDialog(title='ERROR', message='Select valid Joint(s)', button=['Ok'])
                            return

            for curjoint in selJoints:
                previousJoint=None
                jointTree = mc.listRelatives(curjoint, s=False, typ='joint', ad=True)
                jointTree.append(curjoint)
                jointTree.reverse()
                self.createJoints(jointTree)

        else:
            #-- Selected Joints Mode
            previousJoint=None
            selJoints = mc.ls(sl=True, type='joint')
            if not selJoints:
                mc.confirmDialog(title='ERROR', message='Select valid Joint(s)', button=['Ok'])
                return
            self.createJoints(selJoints)

    def createJoints(self, joints):
        #-- Set Suffix Values
        if not suffixABoxValue or not suffixBBoxValue:
            mc.confirmDialog(title='ERROR', message='Enter a valid suffix value', button=['Ok'])
            return
        suffixA = '_'+suffixABoxValue+'_'
        suffixB = '_'+suffixBBoxValue+'_'
        if not curSuffixBoxValue:
            mc.confirmDialog(title='ERROR', message='Enter a valid current suffix value', button=['Ok'])
            return
        curSuffix = '_'+curSuffixBoxValue+'_'

        #-- Main Code

        for x in joints:
            if curSuffix not in x:
                if '_JNT' not in x:
                    mc.confirmDialog(title='ERROR', message='One or more incorrectly named Joints selected', button=['Ok'])
                    return

                #-- Rename current Joint
                resultJointName = x.replace('_JNT', curSuffix+'JNT')
                if mc.objExists(resultJointName):
                    mc.confirmDialog(title='ERROR', message='New Joint name already exists', button=['Ok'])
                    return

                mc.rename(x,resultJointName)
                x=resultJointName

            #-- Names from current Joint
            blendSuffix = '_'+suffixABoxValue+suffixBBoxValue[:1].upper() + suffixBBoxValue[1:]
            ikJointName = x.replace(curSuffix, suffixA)
            fkJointName = x.replace(curSuffix, suffixB)
            blendRName = x.replace(curSuffix+'JNT', blendSuffix+'Rot_BLND')
            blendTName = x.replace(curSuffix+'JNT', blendSuffix+'Trans_BLND')
            blendSName = x.replace(curSuffix+'JNT', blendSuffix+'Scale_BLND')

            #-- Duplicate Joints
            if mc.objExists(ikJointName) or mc.objExists(fkJointName):
                mc.confirmDialog(title='ERROR', message='Joint(s) already exist', button=['Ok'])
                return
            ikJoints = mc.duplicate(x, n=ikJointName, po=True)
            fkJoints = mc.duplicate(x, n=fkJointName, po=True)

            #-- Parent Duplicated Joints
            resultParent=mc.listRelatives(x, p=True, c=False)
            if resultParent:
                for p in resultParent:
                    if curSuffix in p:
                        ikParent=p.replace(curSuffix, suffixA)
                        fkParent=p.replace(curSuffix, suffixB)
                        mc.parent(ikJointName, ikParent)
                        mc.parent(fkJointName, fkParent)

            #-- Create and attach Blends
            mc.createNode('blendColors', n=blendRName)
            mc.createNode('blendColors', n=blendTName)
            mc.createNode('blendColors', n=blendSName)
                #--Inputs
            mc.connectAttr(ikJointName + '.rotate', blendRName + '.color2')
            mc.connectAttr(fkJointName + '.rotate', blendRName + '.color1')
            mc.connectAttr(ikJointName + '.translate', blendTName + '.color2')
            mc.connectAttr(fkJointName + '.translate', blendTName + '.color1')
            mc.connectAttr(ikJointName + '.scale', blendSName + '.color2')
            mc.connectAttr(fkJointName + '.scale', blendSName + '.color1')
            mc.connectAttr(ctrlCrv + '.' + attrName, blendRName + '.blender')
            mc.connectAttr(ctrlCrv + '.' + attrName, blendTName + '.blender')
            mc.connectAttr(ctrlCrv + '.' + attrName, blendSName + '.blender')
                #--Outputs
            mc.connectAttr(blendRName + '.output', x + '.rotate')
            mc.connectAttr(blendTName + '.output', x + '.translate')
            mc.connectAttr(blendSName + '.output', x + '.scale')

    def createAttr(self):
        #--Set attribute names
        if not attrNameBoxValue:
            mc.confirmDialog(title='ERROR', message='Enter a valid attribute name', button=['Ok'])
            return
        if not attrNiceNameBoxValue:
            mc.confirmDialog(title='ERROR', message='Enter a valid nice name', button=['Ok'])
            return

        if not ctrlCrvBoxValue or not mc.objExists(ctrlCrvBoxValue):
            mc.confirmDialog(title='ERROR', message='Select valid Control Curve', button=['Ok'])
            return

        global attrName
        global attrNiceName
        global ctrlCrv
        attrName = attrNameBoxValue
        attrNiceName = attrNiceNameBoxValue
        ctrlCrv=ctrlCrvBoxValue

        if not mc.attributeQuery(attrName, node=ctrlCrv, exists=True):
            mc.addAttr(ctrlCrv, ln=attrName, nn=attrNiceName, min=0, max=1, at='float', dv=0, k=True)




main()