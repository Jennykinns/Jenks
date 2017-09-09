import maya.cmds as cmds
import ikSplineCreatorUI as customUI
import maya.OpenMayaUI as omUi
from functools import partial

try:
    from PySide import QtGui, QtCore
    import PySide.QtGui as QtWidgets
    from shiboken import wrapInstance
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets
    from shiboken2 import wrapInstance

reload(customUI)

def maya_main_window():
    main_window_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def main():
    global myWindow
    global ctrlNameLeditValue
    global ikNameLeditValue
    ctrlNameLeditValue = None
    ikNameLeditValue = 'splineIK'

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

        self.ui.ctrlName_ledit.textChanged.connect(self.updateCtrlNameLedit)
        self.ui.ikName_ledit.textChanged.connect(self.updateIkNameLedit)
        self.ui.set_btn.clicked.connect(self.updateSetBtn)
        self.ui.create_btn.clicked.connect(self.updateCreateBtn)

    def updateCtrlNameLedit(self,*args):
        global ctrlNameLeditValue
        ctrlNameLeditValue = self.ui.ctrlName_ledit.text()
        if cmds.objExists(ctrlNameLeditValue):
            self.ui.ctrlName_ledit.setStyleSheet('background-color: rgb(90, 150, 50);')
        else:
            self.ui.ctrlName_ledit.setStyleSheet('background-color: rgb(110, 90, 90);')

    def updateIkNameLedit(self,*args):
        global ikNameLeditValue
        ikNameLeditValue = self.ui.ikName_ledit.text()

    def updateSetBtn(self,*args):
        sel = cmds.ls(sl=True)
        self.ui.ctrlName_ledit.setText(sel[0])

    def updateCreateBtn(self,*args):
        global ikNameLeditValue
        global ctrlNameLeditValue
        self.createSplineIK(ikNameLeditValue,ctrlNameLeditValue)

    def _getSelection(*args):
        sel=[]
        sel=zip(cmds.ls(sl=True,l=True),cmds.ls(sl=True))
        return sel

    def _getChildren(self,joint,*args):
        sNChildren=[]
        children=cmds.listRelatives(joint,typ='joint',f=True, ad=True)
        if children:
            for x in children:
                sN=x.split('|')
                sNChildren.append(sN[-1])
            children=zip(sNChildren,children)
        return children

    def _getParents(self,joint,*args):
        parents=[]
        sNParents=[]
        curPar=joint
        for i in range(500):
            curPar=cmds.listRelatives(curPar,typ='joint',f=True, p=True)
            if not curPar:
                break
            sN=curPar[0].split('|')
            sNParents.append(sN[-1])
            parents.append(curPar[0])
        parents=zip(sNParents,parents)
        return parents

    def createSplineIK(self,ikName='splineIK',controlName='',*args):
        ## setup name variables
        hdlName=ikName+'_HDL'
        effName=ikName+'_EFF'
        crvName=ikName+'_CRV'
        crvInfoName=ikName+'Crv_INFO'
        crvGlobalScaleName=ikName+'CrvGlobalScale_MULT'
        crvStretchName=ikName+'CrvStretch_DIV'

        if cmds.objExists(hdlName) or cmds.objExists(effName) or cmds.objExists(crvName):
            cmds.warning('Name Invalid - Existing Object(s) match chosen name')
            return

        ## get start and end joints
        sel=self._getSelection()

        if not sel:
            cmds.warning('Nothing selected - Select Joints to IK')
            return

        startJntLN,startJntSN=sel[0]
        endJntLN,endJntSN=sel[-1]

        if startJntLN == endJntLN:
            cmds.warning('Invalid selection - Select at least two Joints to IK')
            return
        if not cmds.objectType(startJntLN) == 'joint' and  not cmds.objectType(endJntLN) == 'joint':
            cmds.warning('Invalid selection - Select only Joints to IK')
            return

        ## get effected joints

        #startJntChildren=self._getChildren(startJntLN)
        startJntParents=self._getParents(startJntLN)
        #endJntChildren=self._getChildren(endJntLN)
        endJntParents=self._getParents(endJntLN)
        #if endJntChildren:
        #    eC = list(set(startJntChildren) - set(endJntChildren))
        #else:
        #    eC=startJntChildren
        if startJntParents:
            eP = list(set(endJntParents)-set(startJntParents))
        else:
            eP=endJntParents
        effectedJnts=eP

        ## create IK
        try:
            ikH,ikE,ikC=cmds.ikHandle(n=hdlName, sj=startJntLN, ee=endJntLN, solver='ikSplineSolver', parentCurve=False, simplifyCurve=False)
        except:
            cmds.warning('IK creation failed - Check for potential overlapping IKs')
            return
        if not cmds.objExists(effName):
            cmds.rename(ikE,effName)
        if not cmds.objExists(crvName):
            cmds.rename(ikC,crvName)

        ## create curve info node
        crvInf=cmds.arclen(crvName, ch=True)
        if not cmds.objExists(crvInfoName):
            cmds.rename(crvInf,crvInfoName)

        ## create global scale mult node
        crvGlobalScaleNode=cmds.createNode('multDoubleLinear', n=crvGlobalScaleName, ss=True)
        if cmds.objExists(controlName):
            cmds.connectAttr(controlName+'.scaleY',crvGlobalScaleNode+'.input1')
        else:
            cmds.setAttr(crvGlobalScaleNode+'.input1', 1)
        ikCrvLength=cmds.getAttr(crvInfoName+'.arcLength')
        cmds.setAttr(crvGlobalScaleNode+'.input2',ikCrvLength)

        ## create curve stretch divide node
        crvStretchNode=cmds.createNode('multiplyDivide', n=crvStretchName)
        cmds.setAttr(crvStretchNode+'.operation', 2) # 1=multiply 2=divide
        cmds.connectAttr(crvGlobalScaleNode+'.output', crvStretchNode+'.input2X')
        cmds.connectAttr(crvInfoName+'.arcLength', crvStretchNode+'.input1X')

        ## create stretch mult node for each effected joint
        for sN,lN in effectedJnts:
            jntStretchName=ikName+sN+'Stretch_MULT'
            jntStretchNode=cmds.createNode('multDoubleLinear', n=jntStretchName)
            jointTransX=cmds.getAttr(lN+'.translateX')
            cmds.setAttr(jntStretchNode+'.input1', jointTransX)
            cmds.connectAttr(crvStretchNode+'.outputX', jntStretchNode+'.input2')
            cmds.connectAttr(jntStretchNode+'.output', lN+'.translateX')


main()