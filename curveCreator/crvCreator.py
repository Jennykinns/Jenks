import crvCreatorUI_qt5 as customUI
import maya.OpenMayaUI as omUi
import maya.cmds as cmds
import re
import sys
from functools import partial

try:
    from PySide import QtGui, QtCore
    import PySide.QtGui as QtWidgets
    from shiboken import wrapInstance
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets
    from shiboken2 import wrapInstance

import zGlobalControl as crv1
import zSettingsCog as crv2
import zCircle as crv3
import zTriCross as crv4
import zGlobe as crv5
import zCrossedCircle as crv6
import zEyes as crv7
import zFoot as crv8
import zPringle as crv9
import zArrow as crv10
import zCube as crv11
import zDualArrow as crv12
import zFatCross as crv13
import zFlatPringle as crv14
import zHand as crv15
import zLips as crv16
import zQuadArrow as crv17
import zThinCross as crv18
import zMattJenkins as crv19
import zWing as crv20
import zDynamicsCog as crv21
import zPin as crv22
import zGlobe_single as crv23



reload(customUI)

def maya_main_window():
    main_window_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def main():
    global myWindow

    global shapeActive
    global selShape
    global nameTxt
    global grpNum
    global locNum
    global selColour
    global cpMirror
    global gimbalCtrl
    global transLockChk
    global rotLockChk
    global scaleLockChk
    global transLock
    global rotLock
    global scaleLock
    global visAttr
    shapeActive = True
    selShape = 1
    nameTxt = None
    grpNum = 1
    locNum = 1
    selColour = 1
    cpMirror = False
    gimbalCtrl = False
    transLockChk = [True,True,True]
    rotLockChk = [True,True,True]
    scaleLockChk = [True,True,True]
    transLock = False
    rotLock = False
    scaleLock = False
    visAttr = False

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

        self.ui.shapes_Grp.toggled.connect(self.updateShapeGrp)
        self.ui.shape01_Btn.clicked.connect(partial(self.updateShapeBtn, 1))
        self.ui.shape02_Btn.clicked.connect(partial(self.updateShapeBtn, 2))
        self.ui.shape03_Btn.clicked.connect(partial(self.updateShapeBtn, 3))
        self.ui.shape04_Btn.clicked.connect(partial(self.updateShapeBtn, 4))
        self.ui.shape05_Btn.clicked.connect(partial(self.updateShapeBtn, 5))
        self.ui.shape06_Btn.clicked.connect(partial(self.updateShapeBtn, 6))
        self.ui.shape07_Btn.clicked.connect(partial(self.updateShapeBtn, 7))
        self.ui.shape08_Btn.clicked.connect(partial(self.updateShapeBtn, 8))
        self.ui.shape09_Btn.clicked.connect(partial(self.updateShapeBtn, 9))
        self.ui.shape10_Btn.clicked.connect(partial(self.updateShapeBtn, 10))
        self.ui.shape11_Btn.clicked.connect(partial(self.updateShapeBtn, 11))
        self.ui.shape13_Btn.clicked.connect(partial(self.updateShapeBtn, 13))
        self.ui.shape14_Btn.clicked.connect(partial(self.updateShapeBtn, 14))
        self.ui.shape15_Btn.clicked.connect(partial(self.updateShapeBtn, 15))
        self.ui.shape16_Btn.clicked.connect(partial(self.updateShapeBtn, 16))
        self.ui.shape17_Btn.clicked.connect(partial(self.updateShapeBtn, 17))
        self.ui.shape18_Btn.clicked.connect(partial(self.updateShapeBtn, 18))
        self.ui.shape19_Btn.clicked.connect(partial(self.updateShapeBtn, 19))
        self.ui.shape20_Btn.clicked.connect(partial(self.updateShapeBtn, 20))
        self.ui.shape21_Btn.clicked.connect(partial(self.updateShapeBtn, 21))
        self.ui.shape22_Btn.clicked.connect(partial(self.updateShapeBtn, 22))
        self.ui.shape23_Btn.clicked.connect(partial(self.updateShapeBtn, 23))
        self.ui.shape24_Btn.clicked.connect(partial(self.updateShapeBtn, 24))
        self.ui.shape25_Btn.clicked.connect(partial(self.updateShapeBtn, 25))
        self.ui.shape26_Btn.clicked.connect(partial(self.updateShapeBtn, 26))
        self.ui.shape27_Btn.clicked.connect(partial(self.updateShapeBtn, 27))
        self.ui.shape28_Btn.clicked.connect(partial(self.updateShapeBtn, 28))
        self.ui.shape29_Btn.clicked.connect(partial(self.updateShapeBtn, 29))
        self.ui.shape30_Btn.clicked.connect(partial(self.updateShapeBtn, 30))
        self.ui.shape31_Btn.clicked.connect(partial(self.updateShapeBtn, 31))
        self.ui.shape32_Btn.clicked.connect(partial(self.updateShapeBtn, 32))
        self.ui.shape33_Btn.clicked.connect(partial(self.updateShapeBtn, 33))
        self.ui.shape34_Btn.clicked.connect(partial(self.updateShapeBtn, 34))
        self.ui.shape35_Btn.clicked.connect(partial(self.updateShapeBtn, 35))
        self.ui.shape36_Btn.clicked.connect(partial(self.updateShapeBtn, 36))
        self.ui.shape37_Btn.clicked.connect(partial(self.updateShapeBtn, 37))
        self.ui.shape38_Btn.clicked.connect(partial(self.updateShapeBtn, 38))
        self.ui.shape39_Btn.clicked.connect(partial(self.updateShapeBtn, 39))
        self.ui.shape40_Btn.clicked.connect(partial(self.updateShapeBtn, 40))
        self.ui.shape41_Btn.clicked.connect(partial(self.updateShapeBtn, 41))
        self.ui.shape42_Btn.clicked.connect(partial(self.updateShapeBtn, 42))
        self.ui.shape43_Btn.clicked.connect(partial(self.updateShapeBtn, 43))

        self.ui.name_Ledit.textChanged.connect(self.updateNameLedit)
        self.ui.grpNum_Cmb.currentIndexChanged.connect(self.updateGrpNumCmb)
        self.ui.locNum_Cmb.currentIndexChanged.connect(self.updateLocNumCmb)
        self.ui.create_Btn.clicked.connect(self.updateCreateBtn)

        self.ui.colour01_Btn.clicked.connect(partial(self.updateColourBtn, 1))
        self.ui.colour02_Btn.clicked.connect(partial(self.updateColourBtn, 2))
        self.ui.colour03_Btn.clicked.connect(partial(self.updateColourBtn, 3))
        self.ui.colour04_Btn.clicked.connect(partial(self.updateColourBtn, 4))
        self.ui.colour05_Btn.clicked.connect(partial(self.updateColourBtn, 5))
        self.ui.colour06_Btn.clicked.connect(partial(self.updateColourBtn, 6))
        self.ui.colour07_Btn.clicked.connect(partial(self.updateColourBtn, 7))
        self.ui.colour08_Btn.clicked.connect(partial(self.updateColourBtn, 8))
        self.ui.colour09_Btn.clicked.connect(partial(self.updateColourBtn, 9))
        self.ui.colour10_Btn.clicked.connect(partial(self.updateColourBtn, 10))
        self.ui.colour11_Btn.clicked.connect(partial(self.updateColourBtn, 11))
        self.ui.colour12_Btn.clicked.connect(partial(self.updateColourBtn, 12))
        self.ui.colour13_Btn.clicked.connect(partial(self.updateColourBtn, 13))
        self.ui.colour14_Btn.clicked.connect(partial(self.updateColourBtn, 14))
        self.ui.colour15_Btn.clicked.connect(partial(self.updateColourBtn, 15))
        self.ui.colour16_Btn.clicked.connect(partial(self.updateColourBtn, 16))
        self.ui.colour17_Btn.clicked.connect(partial(self.updateColourBtn, 17))
        self.ui.colour18_Btn.clicked.connect(partial(self.updateColourBtn, 18))
        self.ui.colour19_Btn.clicked.connect(partial(self.updateColourBtn, 19))
        self.ui.colour20_Btn.clicked.connect(partial(self.updateColourBtn, 20))
        self.ui.colour21_Btn.clicked.connect(partial(self.updateColourBtn, 21))
        self.ui.colour22_Btn.clicked.connect(partial(self.updateColourBtn, 22))
        self.ui.colour23_Btn.clicked.connect(partial(self.updateColourBtn, 23))
        self.ui.colour24_Btn.clicked.connect(partial(self.updateColourBtn, 24))
        self.ui.colour25_Btn.clicked.connect(partial(self.updateColourBtn, 25))
        self.ui.colour26_Btn.clicked.connect(partial(self.updateColourBtn, 26))
        self.ui.colour27_Btn.clicked.connect(partial(self.updateColourBtn, 27))
        self.ui.colour28_Btn.clicked.connect(partial(self.updateColourBtn, 28))
        self.ui.colour29_Btn.clicked.connect(partial(self.updateColourBtn, 29))
        self.ui.colour30_Btn.clicked.connect(partial(self.updateColourBtn, 30))
        self.ui.colour31_Btn.clicked.connect(partial(self.updateColourBtn, 31))
        self.ui.colour32_Btn.clicked.connect(partial(self.updateColourBtn, 32))
        self.ui.colour33_Btn.clicked.connect(partial(self.updateColourBtn, 33))

        self.ui.default_Btn.clicked.connect(self.updateDefaultBtn)
        self.ui.override_Btn.clicked.connect(self.updateOverrideBtn)

        self.ui.x_Btn.clicked.connect(self.updateXBtn)
        self.ui.y_Btn.clicked.connect(self.updateYBtn)
        self.ui.z_Btn.clicked.connect(self.updateZBtn)
        self.ui.copyMirror_Chk.stateChanged.connect(self.updateMirrorCopyChk)

        self.ui.transAttr_Grp.toggled.connect(self.updateTransAttrGrp)
        self.ui.transXAttr_Chk.stateChanged.connect(self.updateTransXAttrChk)
        self.ui.transYAttr_Chk.stateChanged.connect(self.updateTransYAttrChk)
        self.ui.transZAttr_Chk.stateChanged.connect(self.updateTransZAttrChk)
        self.ui.rotAttr_Grp.toggled.connect(self.updateRotAttrGrp)
        self.ui.rotXAttr_Chk.stateChanged.connect(self.updateRotXAttrChk)
        self.ui.rotYAttr_Chk.stateChanged.connect(self.updateRotYAttrChk)
        self.ui.rotZAttr_Chk.stateChanged.connect(self.updateRotZAttrChk)
        self.ui.scaleAttr_Grp.toggled.connect(self.updateScaleAttrGrp)
        self.ui.scaleXAttr_Chk.stateChanged.connect(self.updateScaleXAttrChk)
        self.ui.scaleYAttr_Chk.stateChanged.connect(self.updateScaleYAttrChk)
        self.ui.scaleZAttr_Chk.stateChanged.connect(self.updateScaleZAttrChk)
        self.ui.visAttr_Chk.stateChanged.connect(self.updateVisAttrChk)
        self.ui.attrApply_Btn.clicked.connect(self.updateAttrApplyBtn)

        self.ui.pivot_Btn.clicked.connect(self.updatePivotBtn)
        self.ui.freeze_Btn.clicked.connect(self.updateFreezeBtn)
        self.ui.combine_Btn.clicked.connect(self.updateCombineBtn)
        self.ui.double_Btn.clicked.connect(self.updateDoubleBtn)

    def updateShapeGrp(self,value,*args):
        global shapeActive
        shapeActive = value

    def updateShapeBtn(self,value,*args):
        global selShape
        selShape = value

    def updateNameLedit(self,value,*args):
        global nameTxt
        nameTxt = value

    def updateGrpNumCmb(self,value,*args):
        global grpNum
        grpNum = value

    def updateLocNumCmb(self,value,*args):
        global locNum
        locNum = value

    def updateCreateBtn(self,*args):
        global oldSel
        oldSel=cmds.ls(sl=True,l=True)
        if shapeActive:
            self.createCtrlShape(nameTxt,selShape)
        cmds.select(cl=True)
        for x in oldSel:
                cmds.select(x,add=True)
        self.createBuffer(nameTxt,locNum,grpNum)

    def updateColourBtn(self,value,*args):
        global selColour
        selColour = value

    def updateDefaultBtn(self,*args):
        s=self._getSelection()
        self.overrideColour(s,1)

    def updateOverrideBtn(self,*args):
        s=self._getSelection()
        self.overrideColour(s,selColour)

    def updateXBtn(self,*args):
        s=self._getSelection()
        self.mirror([-1,1,1],s)

    def updateYBtn(self,*args):
        s=self._getSelection()
        self.mirror([1,-1,1],s)

    def updateZBtn(self,*args):
        s=self._getSelection()
        self.mirror([1,1,-1],s)

    def updateMirrorCopyChk(self,value,*args):
        global cpMirror
        if value == 0:
            cpMirror = False
        else:
            cpMirror = True
        print(cpMirror)

    def updateTransAttrGrp(self,value,*args):
        global transLock
        transLock = value

    def updateRotAttrGrp(self,value,*args):
        global rotLock
        rotLock = value

    def updateScaleAttrGrp(self,value,*args):
        global scaleLock
        scaleLock = value

    def updateTransXAttrChk(self,value,*args):
        global transLockChk
        if value == 0:
            transLockChk[0] = False
        else:
            transLockChk[0] = True

    def updateTransYAttrChk(self,value,*args):
        global transLockChk
        if value == 0:
            transLockChk[1] = False
        else:
            transLockChk[1] = True

    def updateTransZAttrChk(self,value,*args):
        global transLockChk
        if value == 0:
            transLockChk[2] = False
        else:
            transLockChk[2] = True

    def updateRotXAttrChk(self,value,*args):
        global rotLockChk
        if value == 0:
            rotLockChk[0] = False
        else:
            rotLockChk[0] = True

    def updateRotYAttrChk(self,value,*args):
        global rotLockChk
        if value == 0:
            rotLockChk[1] = False
        else:
            rotLockChk[1] = True

    def updateRotZAttrChk(self,value,*args):
        global rotLockChk
        if value == 0:
            rotLockChk[2] = False
        else:
            rotLockChk[2] = True

    def updateScaleXAttrChk(self,value,*args):
        global scaleLockChk
        if value == 0:
            scaleLockChk[0] = False
        else:
            scaleLockChk[0] = True

    def updateScaleYAttrChk(self,value,*args):
        global scaleLockChk
        if value == 0:
            scaleLockChk[1] = False
        else:
            scaleLockChk[1] = True

    def updateScaleZAttrChk(self,value,*args):
        global scaleLockChk
        if value == 0:
            scaleLockChk[2] = False
        else:
            scaleLockChk[2] = True

    def updateVisAttrChk(self,value,*args):
        global visAttr
        if value == 0:
            visAttr = False
        else:
            visAttr = True

    def updateAttrApplyBtn(self,*args):

        sel=self._getSelection()
        self.lockHideAttrs('a',sel)


    def updatePivotBtn(self,*args):
        sel=self._getSelection()
        for x in sel:
            cmds.xform(x,cp=True)

    def updateFreezeBtn(self,*args):
        sel=self._getSelection()
        for x in sel:
            cmds.makeIdentity(x,a=True,t=True,r=True,s=True)

    def updateCombineBtn(self,*args):
        self.combineCrv()

    def updateDoubleBtn(self,*args):
        self.doubleCrv()



    def _getSelection(self,*args):
        sel=list()
        sel=zip(cmds.ls(sl=True,l=True),cmds.ls(sl=True))
        return sel

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


    def createBuffer(self,n,loc,grp,*args):
        if not n:
            n='curve'

        rootCtrlName = str(n)+"Ctrl_ROOT"
        ctrlParentName = str(n)+"Ctrl_PAR"
        spareCtrlParentName = str(n)+"CtrlPar#_PAR"
        ctrlName = str(n)+"_CTRL"
        constGrpName = str(n)+"Const_GRP"
        gimbalCtrlName = str(n)+"Gimbal_CTRL"

        sel = cmds.ls(sl=True)

        buffers = []
        for i,x in enumerate(sel):
            if not i > 0:
                prevBuff=None
                if grp == 0 and loc == 0:
                    cmds.parentConstraint(x,ctrlName,mo=False)
                    cmds.delete(ctrlName+'_parentConstraint1')
                    cmds.makeIdentity(ctrlName,a=True,t=True,s=True,r=True)
                else:
                    for y in range(grp+loc):
                        if y == 0:
                            buffName = rootCtrlName
                        elif y ==1:
                            buffName = ctrlParentName
                        else:
                            buffName = spareCtrlParentName
                        buffName = self._swapDigits(buffName,y-2)
                        if y < grp:
                            cmds.group(em=True,n=buffName)
                        else:
                            cmds.spaceLocator(n=buffName)
                            cmds.setAttr(buffName+'Shape'+'.overrideEnabled', True)
                            cmds.setAttr(buffName+'Shape'+'.overrideVisibility', 0)
                            locPath=zip(cmds.ls(buffName,l=True),buffName)
                            #self.overrideColour(locPath,2)


                        cmds.parentConstraint(x,buffName,mo=False)
                        cmds.delete(buffName+'_parentConstraint1')
                        if y == 0:
                            cmds.makeIdentity(buffName,a=True,t=True,s=True,r=True)
                        else:
                            cmds.makeIdentity(buffName,a=True,t=True,s=True)
                        buffers.append(buffName)


                    for y in range(len(buffers)):
                        if y > 0:
                            cmds.parent(buffers[y],buffers[y-1])

                    cmds.parentConstraint(buffers[-1],ctrlName,mo=False)
                    cmds.delete(ctrlName+'_parentConstraint1')
                    cmds.parent(ctrlName,buffers[-1])
                    cmds.makeIdentity(ctrlName,a=True,t=True,s=True,r=True)


                    if gimbalCtrl:
                        constGrpPar = gimbalCtrlName
                        self.createGimbalCtrl(n)
                    else:
                        constGrpPar = ctrlName


                    cmds.group(em=True,n=constGrpName)
                    cmds.parentConstraint(constGrpPar,constGrpName,mo=False)
                    cmds.delete(constGrpName+'_parentConstraint1')
                    cmds.parent(constGrpName,constGrpPar)
                    cmds.makeIdentity(a=True,t=True,s=True,r=True)



    def createCtrlShape(self,n,s,*args):
        if not n:
            n='curve'
        ctrlName = n+"_CTRL"
        try:
            curveNum=eval('crv'+str(s))
            crvs=curveNum.create(n,'_CTRL')
            cmds.select(cl=True)
            for x in crvs:
                cmds.select(x,add=True)
            self.combineCrv()
        except:
            return

    def combineCrv(self,*args):
        c=self._getSelection()
        for i,x in enumerate(c):
            lN,sN=x
            if not i > 0:
                parent=lN
                parentSn=sN
            else:
                cmds.rename(lN,parentSn+str(i+1))
        newC=self._getSelection()
        for i,x in enumerate(newC):
            lN,sN=x
            if i > 0:
                cs=zip(cmds.listRelatives(lN,s=True,f=True),cmds.listRelatives(lN,s=True))
                for i2,y in enumerate(cs):
                    lCs,sCs=y
                    cmds.parent(lCs,parent,s=True,r=True)
                cmds.delete(lN)

    def overrideColour(self,sel,col,*args):
        for x in sel:
            lN,sN=x
            try:
                ss=zip(cmds.listRelatives(lN,s=True,f=True),cmds.listRelatives(lN,s=True))
                for y in ss:
                    sLN,sSN=y
                    try:
                        cmds.setAttr(sLN+'.overrideEnabled', True)
                        if not col == 33:
                            cmds.setAttr(sLN+'.overrideColor', col-1)
                            cmds.setAttr(sLN+'.overrideVisibility', 1)
                        else:
                            cmds.setAttr(sLN+'.overrideVisibility', 0)
                    except:
                        cmds.warning('Cannot override object'+sSN)
            except:
                cmds.warning('No selected shapes to override.')

    def mirror(self,axis,sel,*args):
        if cpMirror:
            cmds.duplicate()
        mGrp=cmds.group()
        try:
            cmds.makeIdentity(a=True,t=True,r=True,s=True,n=False)
            cmds.xform(os=True,piv=(0,0,0),s=(axis))
            cmds.ungroup(mGrp)
            cmds.makeIdentity(a=True,t=True,r=True,s=True,n=False)
        except:
            cmds.ungroup(mGrp)
            cmds.warning('Cannot mirror selection - Make sure transform attributes are unlocked.')


    def doubleCrv(self,*args):
        c=self._getSelection()
        for x in c:
            lN,sN=x
            crvParent = cmds.listRelatives(lN,parent=True)
            crvChildren=cmds.listRelatives(lN)
            crvShapeNodes=cmds.listRelatives(lN,s=True)
            for i,x in enumerate(crvShapeNodes):
                crvChildren.remove(x)
                if not i>0:
                    crvCol=cmds.getAttr(x+'.overrideColor')
            if crvChildren:
                cmds.parent(crvChildren,w=True)
            offCrv = cmds.offsetCurve(lN,ch=False,rn=False,cl=True,d=0.1,ugn=False)
            lOffCrv=zip(cmds.ls(offCrv,l=True),offCrv)
            self.overrideColour(lOffCrv,crvCol+1)
            cmds.parent(offCrv,crvParent)
            cmds.makeIdentity(lN,a=True,t=True,r=True,s=True)
            cmds.makeIdentity(offCrv,a=True,t=True,r=True,s=True)
            cmds.select(lN,offCrv)
            self.combineCrv()
            if crvChildren:
                cmds.parent(crvChildren,lN)
            cmds.select(lN)

    def lockHideAttrs(self,attrs,sel,lock=True,show=True,*args):
        for lN,sN in sel:
            if transLock:
                cmds.setAttr(str(lN)+'.translateX', lock=transLockChk[0], cb=show)
                cmds.setAttr(str(lN)+'.translateY', lock=transLockChk[1], cb=show)
                cmds.setAttr(str(lN)+'.translateZ', lock=transLockChk[2], cb=show)
            else:
                cmds.setAttr(str(lN)+'.translateX', lock=False, cb=show)
                cmds.setAttr(str(lN)+'.translateY', lock=False, cb=show)
                cmds.setAttr(str(lN)+'.translateZ', lock=False, cb=show)
            if rotLock:
                cmds.setAttr(str(lN)+'.rotateX', lock=rotLockChk[0], cb=show)
                cmds.setAttr(str(lN)+'.rotateY', lock=rotLockChk[1], cb=show)
                cmds.setAttr(str(lN)+'.rotateZ', lock=rotLockChk[2], cb=show)
            else:
                cmds.setAttr(str(lN)+'.rotateX', lock=False, cb=show)
                cmds.setAttr(str(lN)+'.rotateY', lock=False, cb=show)
                cmds.setAttr(str(lN)+'.rotateZ', lock=False, cb=show)
            if scaleLock:
                cmds.setAttr(str(lN)+'.scaleX', lock=scaleLockChk[0], cb=show)
                cmds.setAttr(str(lN)+'.scaleY', lock=scaleLockChk[1], cb=show)
                cmds.setAttr(str(lN)+'.scaleZ', lock=scaleLockChk[2], cb=show)
            else:
                cmds.setAttr(str(lN)+'.scaleX', lock=False, cb=show)
                cmds.setAttr(str(lN)+'.scaleY', lock=False, cb=show)
                cmds.setAttr(str(lN)+'.scaleZ', lock=False, cb=show)
            cmds.setAttr(str(lN)+'.visibility', lock=visAttr, cb=show)

    def createGimbalCtrl(self,n,*args):
        if not n:
            n='curve'

        ctrlName = str(n)+"_CTRL"
        gimbalName = str(n)+"Gimbal"

        self.createCtrlShape(gimbalName,selShape)

        gimbalName = gimbalName+'_CTRL'

        cmds.parentConstraint(ctrlName,gimbalName,mo=False)
        cmds.delete(gimbalName+'_parentConstraint1')
        cmds.parent(gimbalName,ctrlName)
        cmds.xform(s=(0.8,0.8,0.8))
        cmds.makeIdentity(a=True,s=True,t=True,r=True)



main()