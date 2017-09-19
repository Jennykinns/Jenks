import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils

class ik:
    """
    Create and manipulate Ik handles.
    """
    def __init__(self, sj, ej, name='IK', side='C'):
        ## initial variables
        self.sj = sj
        self.ej = ej
        self.name = name
        self.side = side

    def createIK(self, solver='ikRPsolver', parent=None):
        ## ik creation
        ik = cmds.ikHandle(sj=self.sj, ee=self.ej, sol=solver)
        self.hdl = cmds.rename(ik[0], utils.setupName(self.name, obj='ikHandle', side=self.side))
        self.eff = cmds.rename(ik[1], utils.setupName(self.name, obj='ikEffector', side=self.side))
        self.grp = cmds.group(self.hdl, name=utils.setupName(self.name, obj='group', side=self.side))
        if parent:
            cmds.parent(self.grp, parent)
        grpCP = cmds.xform(self.hdl, q=1, t=1, ws=1)
        cmds.xform(self.grp, piv=grpCP, ws=1)
        ## set effected joints
        self.jnts = utils.getChildrenBetweenObjs(self.sj, self.ej)
        cmds.select(cl=1)


    def createSplineIK(self, crv=None, autoCrvSpans=0, rootOnCrv=True, parent=None):
        ## ik creation
        if crv:
            ik = cmds.ikHandle(sj=self.sj, ee=self.ej, sol='ikSplineSolver', c=crv, ccv=False)
            self.crv = crv
        else:
            if autoCrvSpans:
                scv = True
            else:
                scv = False
            ik = cmds.ikHandle(sj=self.sj, ee=self.ej, sol='ikSplineSolver', ccv=True,
                               scv=scv, ns=autoCrvSpans)
            self.crv = cmds.rename(ik[2], utils.setupName(self.name, obj='nurbsCrv', side=self.side))
        self.hdl = cmds.rename(ik[0], utils.setupName(self.name, obj='ikHandle', side=self.side))
        self.eff = cmds.rename(ik[1], utils.setupName(self.name, obj='ikEffector', side=self.side))
        self.grp = utils.newNode('group', name=self.name, side=self.side, parent=parent).name
        cmds.parent(self.hdl, self.crv, self.grp)
        cmds.setAttr('{}.it'.format(self.crv), 0)
        grpCP = cmds.xform(self.hdl, q=1, t=1, ws=1)
        cmds.xform(self.grp, piv=grpCP, ws=1)
        ## set effected joints
        self.jnts = utils.getChildrenBetweenObjs(self.sj, self.ej)


    def advancedTwist(self, startObj, endObj=None, wuType=3,
                      upVector=(0, 1, 0), upVectorEnd=(0, 1, 0), forwardAxis=0, upAxis=0):
        cmds.setAttr('{}.dTwistControlEnable'.format(self.hdl), 1)
        cmds.setAttr('{}.dWorldUpType'.format(self.hdl), wuType)
        cmds.setAttr('{}.dForwardAxis'.format(self.hdl), forwardAxis)
        cmds.setAttr('{}.dWorldUpAxis'.format(self.hdl), upAxis)
        # 3, 4, 5, 6 = 1st vector
        # 4, 6 = 2nd vector
        # 1, 2, 3, 4  = 1st matrix
        # 2, 4 = 2nd matrix
        if wuType > 2 and wuType < 7:
            cmds.setAttr('{}.dWorldUpVector'.format(self.hdl), upVector[0],
                         upVector[1], upVector[2])
            if wuType == 6 or wuType == 4:
                cmds.setAttr('{}.dWorldUpVectorEnd'.format(self.hdl), upVectorEnd[0],
                             upVectorEnd[1], upVectorEnd[2])
        if wuType > 0 and wuType < 5:
            cmds.connectAttr('{}.wm'.format(startObj), '{}.dWorldUpMatrix'.format(self.hdl))
            if wuType == 2 or wuType == 4:
                cmds.connectAttr('{}.wm'.format(endObj), '{}.dWorldUpMatrixEnd'.format(self.hdl))


    def addStretch(self, operation='greater', customStretchNode=False,
                   globalScaleAttr=None, mode='distance'):
        if customStretchNode:
            if operation == 'greater':
                op=1
            elif operation == 'lesser':
                op=2
            else:
                op=0
            ## check for plugin enabled
            ## create node
            ## connect node
        else:
            if operation == 'greater':
                op = 2
            elif operation == 'lesser':
                op = 4
            else:
                op = 5
            if mode == 'distance':
                ## locators
                startLoc = utils.newNode('locator', name='{}Start'.format(self.name))
                cmds.delete(cmds.parentConstraint(self.jnts[0], startLoc.name))
                sjPar = cmds.listRelatives(self.jnts[0], p=1)
                if sjPar:
                    cmds.parent(startLoc.name, sjPar)
                endLoc = utils.newNode('locator', name='{}End'.format(self.name))
                cmds.delete(cmds.parentConstraint(self.jnts[-1], endLoc.name))
                cmds.parent(endLoc.name, self.grp)
                ## distance between locs
                distNd = utils.newNode('distanceBetween', name=self.name)
                cmds.connectAttr('{}.wp'.format(startLoc.name), '{}.point1'.format(distNd.name))
                cmds.connectAttr('{}.wp'.format(endLoc.name), '{}.point2'.format(distNd.name))
                distanceAttr = '{}.distance'.format(distNd.name)
            elif mode == 'length':
                ## crv info
                crvInfo = utils.newNode('curveInfo', name=self.crv)
                cmds.connectAttr('{}.ws'.format(self.crv), '{}.inputCurve'.format(crvInfo.name))
                distanceAttr = '{}.arcLength'.format(crvInfo.name)
            ##  global scale mult
            gsMult = utils.newNode('multDoubleLinear', name='{}GlobalScale'.format(self.name))
            if globalScaleAttr:
                cmds.connectAttr(globalScaleAttr, '{}.input2'.format(gsMult.name))
            else:
                cmds.setAttr('{}.input2'.format(gsMult.name), 1)
            chainLength = 0
            for jnt in self.jnts[1:]:
                length = cmds.getAttr('{}.translateX'.format(jnt))
                chainLength += length
            cmds.setAttr('{}.input1'.format(gsMult.name), chainLength)
            ## distance / globalScaleMult
            divNd = utils.newNode('multiplyDivide', name='{}Dist'.format(self.name),
                                  suffixOverride='multiplyDivide_div', operation=2)
            cmds.connectAttr(distanceAttr, '{}.input1X'.format(divNd.name))
            cmds.connectAttr('{}.output'.format(gsMult.name), '{}.input2X'.format(divNd.name))
            ## condition; distance -> first, globalScaleMult -> second, div -> colorIfTrue
            condNd = utils.newNode('condition', name='{}Stretch'.format(self.name),
                                   operation=op)
            cmds.connectAttr(distanceAttr,
                             '{}.firstTerm'.format(condNd.name))
            cmds.connectAttr('{}.output'.format(gsMult.name),
                             '{}.secondTerm'.format(condNd.name))
            cmds.connectAttr('{}.output'.format(divNd.name),
                             '{}.colorIfTrue'.format(condNd.name))
            ## toggle (with power node)
            disablePowNode = utils.newNode('multiplyDivide',
                                           name='{}StretchToggle'.format(self.name),
                                           suffixOverride='multiplyDivide_pow', operation=3)
            disablePowNode.connect('input1X', '{}.outColorR'.format(condNd.name), mode='to')
            self.stretchToggleAttr = '{}.input2X'.format(disablePowNode.name)
            ## mult for each joint
            for jnt in self.jnts[1:]:
                transMult = utils.newNode('multDoubleLinear', name='{}{}'.format(self.name, jnt))
                cmds.setAttr('{}.input1'.format(transMult.name),
                             cmds.getAttr('{}.tx'.format(jnt)))
                cmds.connectAttr('{}.outputX'.format(disablePowNode.name),
                                 '{}.input2'.format(transMult.name))
                cmds.connectAttr('{}.output'.format(transMult.name), '{}.tx'.format(jnt))
