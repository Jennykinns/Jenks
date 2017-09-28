import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ikFunctions as ikFn
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules.suffixDictionary import suffix
from Jenks.scripts.rigModules import defaultBodyOptions
from Jenks.scripts.rigModules import orientJoints

reload(orientJoints)
reload(utils)
reload(ikFn)
reload(ctrlFn)
reload(defaultBodyOptions)
#reload(suffixDictionary)

def ikfkMechanics(module, extraName, jnts, mechSkelGrp, ctrlGrp, moduleType):
    jntSuffix = suffix['joint']
    newJntChains = []
    ## create duplicate chains
    for chain in ['IK', 'FK']:
        newJnts = utils.duplicateJntChain(chain, jnts, parent=mechSkelGrp.name)
        newJntChains.append(newJnts)
    ikJnts = newJntChains[0]
    fkJnts = newJntChains[1]
    for i, each in enumerate(jnts):
        newName = '{}_result{}'.format(each.rsplit('_', 1)[0], jntSuffix)
        jnts[i] = cmds.rename(each, newName)
    ## settings control
    module.settingCtrl = ctrlFn.ctrl(name='{}{}Settings'.format(extraName, moduleType),
                                     guide='{}{}Settings{}'.format(module.moduleName,
                                                                   moduleType, suffix['locator']),
                                     deleteGuide=True, side=module.side, skipNum=True,
                                     parent=module.rig.settingCtrlsGrp.name)
    module.settingCtrl.makeSettingCtrl(ikfk=True, parent=jnts[2])
    ## parent constraints
    for jnt, ikJnt, fkJnt in zip(jnts, ikJnts, fkJnts):
        parConstr = cmds.parentConstraint(ikJnt, fkJnt, jnt)
        cmds.connectAttr(module.settingCtrl.ctrl.ikfkSwitch, '{}.{}W1'.format(parConstr[0], fkJnt))
        swRev = utils.newNode('reverse', name='{}{}IKFKSw'.format(extraName, moduleType),
                              side=module.side)
        swRev.connect('inputX', module.settingCtrl.ctrl.ikfkSwitch, mode='to')
        swRev.connect('outputX', '{}.{}W0'.format(parConstr[0], ikJnt), mode='from')
    ## control vis groups
    ikCtrlGrp = utils.newNode('group', name='{}{}IKCtrls'.format(extraName, moduleType),
                              side=module.side, parent=ctrlGrp.name, skipNum=True)
    fkCtrlGrp = utils.newNode('group', name='{}{}FKCtrls'.format(extraName, moduleType),
                              side=module.side, parent=ctrlGrp.name, skipNum=True)
    cmds.setDrivenKeyframe(ikCtrlGrp.name, at='visibility',
                           cd=module.settingCtrl.ctrl.ikfkSwitch, dv=0.999, v=1)
    cmds.setDrivenKeyframe(ikCtrlGrp.name, at='visibility',
                           cd=module.settingCtrl.ctrl.ikfkSwitch, dv=1, v=0)
    cmds.setDrivenKeyframe(fkCtrlGrp.name, at='visibility',
                           cd=module.settingCtrl.ctrl.ikfkSwitch, dv=0.001, v=1)
    cmds.setDrivenKeyframe(fkCtrlGrp.name, at='visibility',
                           cd=module.settingCtrl.ctrl.ikfkSwitch, dv=0, v=0)
    return ikJnts, fkJnts, ikCtrlGrp, fkCtrlGrp


class armModule:
    def __init__(self, rig, extraName='', side='C'):
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, options=defaultBodyOptions.arm, autoOrient=False,
               customNodes=False, parent=None):
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        jntSuffix = suffix['joint']
        jnts = [
            '{}shoulder{}'.format(self.moduleName, jntSuffix),
            '{}elbow{}'.format(self.moduleName, jntSuffix),
            '{}wrist{}'.format(self.moduleName, jntSuffix),
            '{}handEnd{}'.format(self.moduleName, jntSuffix),
        ]
        clavJnts = [
            '{}clavicle{}'.format(self.moduleName, jntSuffix),
            '{}clavicleEnd{}'.format(self.moduleName, jntSuffix),
        ]
        col = utils.getColors(self.side)
        cmds.parent(clavJnts[0], self.rig.skelGrp.name)
        armCtrlsGrp = utils.newNode('group', name='{}armCtrls'.format(extraName), side=self.side,
                                    parent=self.rig.ctrlsGrp.name, skipNum=True)
        armMechGrp = utils.newNode('group', name='{}armMech'.format(extraName),
                                   side=self.side, skipNum=True, parent=self.rig.mechGrp.name)
        if options['IK']:
            armMechSkelGrp = utils.newNode('group', name='{}armMechSkel'.format(extraName),
                                           side=self.side, skipNum=True, parent=armMechGrp.name)
        ## orient joints
        if autoOrient:
            orientJoints.doOrientJoint(jointsToOrient=jnts,
                                       aimAxis=(1 if not self.side == 'R' else -1, 0, 0),
                                       upAxis=(0, 1, 0),
                                       worldUp=(0, 1 if not self.side == 'R' else -1, 0),
                                       guessUp=1)
        ## clav stuff
        clavIK = ikFn.ik(clavJnts[0], clavJnts[1],
                         name='{}clavicleIK'.format(extraName), side=self.side)
        clavIK.createIK(parent=armMechGrp.name)
        self.clavIKCtrl = ctrlFn.ctrl(name='{}clavicle'.format(extraName), side=self.side,
                                      guide=clavJnts[0], skipNum=True, parent=armCtrlsGrp.name)
        self.clavIKCtrl.modifyShape(shape='pringle', color=col['col2'], mirror=True)
        self.clavIKCtrl.lockAttr(attr=['t', 's'])
        self.clavIKCtrl.constrain(clavIK.grp)
        ## ik/fk
        if options['IK'] and options['FK']:
            clavChild = armMechSkelGrp.name
            newJntChains = []
            ##- result chain
            for chain in ['IK', 'FK']:
                newJnts = []
                newChainJnts = cmds.duplicate(jnts[0], rc=1)
                for each in newChainJnts:
                    newName = '{}_{}{}'.format(each.rsplit('_', 1)[0], chain, jntSuffix)
                    newJnts.append(cmds.rename(each, newName))
                newJntChains.append(newJnts)
            ikJnts = newJntChains[0]
            fkJnts = newJntChains[1]
            cmds.parent(ikJnts[0], fkJnts[0], armMechSkelGrp.name)
            for i, each in enumerate(jnts):
                newName = '{}_result{}'.format(each.rsplit('_', 1)[0], jntSuffix)
                jnts[i] = cmds.rename(each, newName)
            ##- create setting control
            self.settingCtrl = ctrlFn.ctrl(name='{}armSettings'.format(extraName),
                                           guide='{}armSettings{}'.format(self.moduleName,
                                                                          suffix['locator']),
                                           deleteGuide=True, side=self.side, skipNum=True,
                                           parent=self.rig.settingCtrlsGrp.name)
            self.settingCtrl.makeSettingCtrl(ikfk=True, parent=jnts[2])
            ##- parent constraints
            for jnt, ikJnt, fkJnt in zip(jnts, ikJnts, fkJnts):
                parConstr = cmds.parentConstraint(ikJnt, fkJnt, jnt)
                cmds.connectAttr(self.settingCtrl.ctrl.ikfkSwitch,
                                 '{}.{}W1'.format(parConstr[0], fkJnt))
                swRev = utils.newNode('reverse', name='{}armIKFKSw'.format(self.extraName),
                                      side=self.side)
                cmds.connectAttr(self.settingCtrl.ctrl.ikfkSwitch,
                                 '{}.inputX'.format(swRev.name))
                cmds.connectAttr('{}.outputX'.format(swRev.name),
                                 '{}.{}W0'.format(parConstr[0], ikJnt))
            ##- control vis grps
            ikCtrlGrp = utils.newNode('group', name='{}armIKCtrls'.format(extraName),
                                      side=self.side, parent=armCtrlsGrp.name, skipNum=True)
            fkCtrlGrp = utils.newNode('group', name='{}armFKCtrls'.format(extraName),
                                      side=self.side, parent=self.clavIKCtrl.ctrlEnd,
                                      skipNum=True)
            cmds.setDrivenKeyframe(ikCtrlGrp.name, at='visibility',
                                   cd=self.settingCtrl.ctrl.ikfkSwitch, dv=0.999, v=1)
            cmds.setDrivenKeyframe(ikCtrlGrp.name, at='visibility',
                                   cd=self.settingCtrl.ctrl.ikfkSwitch, dv=1, v=0)
            cmds.setDrivenKeyframe(fkCtrlGrp.name, at='visibility',
                                   cd=self.settingCtrl.ctrl.ikfkSwitch, dv=0.001, v=1)
            cmds.setDrivenKeyframe(fkCtrlGrp.name, at='visibility',
                                   cd=self.settingCtrl.ctrl.ikfkSwitch, dv=0, v=0)
        else:
            ikJnts = jnts
            fkJnts = jnts
            ikCtrlGrp = armCtrlsGrp
            fkCtrlGrp = armCtrlsGrp
            clavChild = jnts[0]
        cmds.parentConstraint(clavJnts[1], clavChild, mo=1)
        self.handJnt = jnts[2]
        ## ik
        if options['IK']:
            ##- mechanics
            armIK = ikFn.ik(ikJnts[0], ikJnts[2], name='{}armIK'.format(extraName),
                            side=self.side)
            armIK.createIK(parent=armMechGrp.name)
            handIK = ikFn.ik(ikJnts[2], ikJnts[3], name='{}handIK'.format(extraName),
                             side=self.side)
            handIK.createIK(parent=armMechGrp.name)
            ##- controls
            if self.side == 'R':
                tmpJnt = cmds.duplicate(ikJnts[2], po=1)
                cmds.xform(tmpJnt, r=1, ro=(0, 0, 180))
                self.handIKCtrl = ctrlFn.ctrl(name='{}handIK'.format(extraName), side=self.side,
                                          guide=tmpJnt, skipNum=True, parent=ikCtrlGrp.name,
                                          deleteGuide=True)
            else:
                self.handIKCtrl = ctrlFn.ctrl(name='{}handIK'.format(extraName), side=self.side,
                                              guide=ikJnts[2], skipNum=True, parent=ikCtrlGrp.name)
            self.handIKCtrl.modifyShape(shape='cube', color=col['col1'], scale=(0.6, 0.6, 0.6))
            self.handIKCtrl.lockAttr(attr=['s'])
            self.handIKCtrl.constrain(armIK.grp)
            self.handIKCtrl.constrain(handIK.grp)
            # self.handIKCtrl.spaceSwitching([self.rig.globalCtrl.ctrl.name,
            #                                 *TORSO*,
            #                                 self.clavIKCtrl.name],
            #                                niceNames=['World', 'Chest', 'Clavicle'], dv=0)
            ##-- PoleVector
            pvGuide = '{}armPV{}'.format(self.moduleName, suffix['locator'])
            cmds.delete(cmds.aimConstraint(ikJnts[1], pvGuide))
            self.pvCtrl = ctrlFn.ctrl(name='{}armPV'.format(extraName), side=self.side,
                                      guide=pvGuide,
                                      skipNum=True, deleteGuide=True, parent=ikCtrlGrp.name)
            self.pvCtrl.modifyShape(shape='crossPyramid', color=col['col1'], rotation=(0, 180, 0),
                                    scale=(0.4, 0.4, 0.4))
            self.pvCtrl.constrain(armIK.hdl, typ='poleVector')
            self.pvCtrl.spaceSwitching([self.rig.globalCtrl.ctrl.name, self.handIKCtrl.ctrlEnd],
                                           niceNames=['World', 'Hand'], dv=0)

            ## autoClav
            if options['autoClav']:
                print '## do auto clav'
        ## fk
        if options['FK']:
            ##- controls
            self.shoulderFKCtrl = ctrlFn.ctrl(name='{}shoulderFK'.format(extraName),
                                              side=self.side, guide=fkJnts[0], skipNum=True,
                                              parent=fkCtrlGrp.name)
            self.shoulderFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.shoulderFKCtrl.lockAttr(attr=['s'])
            self.shoulderFKCtrl.constrain(fkJnts[0], typ='parent')

            self.elbowFKCtrl = ctrlFn.ctrl(name='{}elbowFK'.format(extraName), side=self.side,
                                           guide=fkJnts[1], skipNum=True,
                                           parent=self.shoulderFKCtrl.ctrlEnd)
            self.elbowFKCtrl.modifyShape(color=col['col2'], shape='circle',
                                         scale=(0.6, 0.6, 0.6))
            self.elbowFKCtrl.lockAttr(attr=['s'])
            self.elbowFKCtrl.constrain(fkJnts[1], typ='parent')

            self.wristFKCtrl = ctrlFn.ctrl(name='{}wristFK'.format(extraName), side=self.side,
                                          guide=fkJnts[2], skipNum=True,
                                          parent=self.elbowFKCtrl.ctrlEnd)
            self.wristFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                         scale=(0.6, 0.6, 0.6))
            self.wristFKCtrl.lockAttr(attr=['s'])
            self.wristFKCtrl.constrain(fkJnts[2], typ='parent')
        ## stretchy
        if options['stretchy']:
            if options['IK']:
                armIK.addStretch(customStretchNode=customNodes,
                                 globalScaleAttr='{}.sy'.format(self.rig.globalCtrl.ctrl.name))
                self.handIKCtrl.addAttr('stretchySwitch', nn='Stretch Switch',
                                         minVal=0, maxVal=1, defaultVal=1)
                cmds.connectAttr(self.handIKCtrl.ctrl.stretchySwitch, armIK.stretchToggleAttr)
            if options['FK']:
                print '## add proper stretch to arm fk'
        ## softIK
        if options['softIK']:
            print '## do arm soft IK'
        ## ribbon
        if options['ribbon']:
            print '## do arm ribbon'

        ## arm parent stuff
        if parent:
            armParentLoc = utils.newNode('locator', name='{}armParent'.format(extraName),
                                         side=self.side, skipNum=True, parent=parent)
            armParentLoc.matchTransforms(clavJnts[0])
            cmds.parentConstraint(armParentLoc.name, clavJnts[0], mo=1)
            cmds.parentConstraint(armParentLoc.name, self.clavIKCtrl.rootGrp.name, mo=1)
        return True


class spineModule:
    def __init__(self, rig, extraName='', side='C'):
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def createFromJnts(self, autoOrient=False):
        jntSuffix = suffix['joint']
        spineJnts = utils.getChildrenBetweenObjs('{}spineBase{}'.format(self.moduleName,
                                                                        jntSuffix),
                                                 '{}spineEnd{}'.format(self.moduleName,
                                                                       jntSuffix))
        self.spineMech(autoOrient, spineJnts)


    def createFromCrv(self, crv, numOfJnts=7):
        ##create jnts
        spineJnts = utils.createJntsFromCrv(crv, numOfJnts, name='{}spine'.format(self.extraName),
                                            side=self.side)
        baseJntName = utils.setupName('spineBase', extraName=self.extraName,
                                      side=self.side, obj='joint', skipNumber=True)
        endJntName = utils.setupName('spineEnd', extraName=self.extraName,
                                      side=self.side, obj='joint', skipNumber=True)
        for i, each in enumerate(spineJnts):
            if i == 0:
                spineJnts[i] = cmds.rename(spineJnts[i], baseJntName)
            elif i == len(spineJnts)-1:
                spineJnts[i] = cmds.rename(spineJnts[i], endJntName)
            else:
                spineJnts[i] = cmds.rename(spineJnts[i],
                                           utils.setupName('spine', extraName=self.extraName,
                                                           side=self.side, obj='joint'))
        ## spine mech
        self.spineMech(autoOrient=False, spineJnts=spineJnts, crv=crv)


    def spineMech(self, autoOrient, spineJnts, crv=None):
        jntSuffix = suffix['joint']
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        col = utils.getColors('C')
        spineMechGrp = utils.newNode('group', name='{}spineMech'.format(self.extraName),
                                     side=self.side, skipNum=True, parent=self.rig.mechGrp.name)
        ## orient joints
        if autoOrient:
            orientJoints.doOrientJoint(jointsToOrient=spineJnts, aimAxis=(1, 0, 0),
                                       upAxis=(0, 1, 0), worldUp=(0, 1, 0), guessUp=1)
        cmds.parent(spineJnts[0], self.rig.skelGrp.name)
        chestJnt = spineJnts[len(spineJnts)/2]
        self.armJnt = spineJnts[int(len(spineJnts)-(len(spineJnts)/3.5))]
        self.baseJnt = spineJnts[0]
        self.endJnt = spineJnts[-1]
        ## bind jnts
        hipBindJnt = utils.newNode('joint', side=self.side, parent=spineMechGrp.name,
                                    name='{}spineIK_hipsBind'.format(extraName))
        hipBindJnt.matchTransforms(spineJnts[0])
        chestBindJnt = utils.newNode('joint', side=self.side, parent=spineMechGrp.name,
                                     name='{}spineIK_chestBind'.format(extraName))
        chestBindJnt.matchTransforms(chestJnt)
        ## splineIK
        spineIK = ikFn.ik(spineJnts[0], spineJnts[-1], name='spineIK', side=self.side)
        if crv:
            spineIK.createSplineIK(parent=spineMechGrp.name, crv=crv)
        else:
            spineIK.createSplineIK(parent=spineMechGrp.name)
        spineIK.addStretch(globalScaleAttr=self.rig.scaleAttr, mode='length', operation='both')
        ## skin bindJnts to crv
        cmds.skinCluster(hipBindJnt.name, chestBindJnt.name, spineIK.crv)
        ## ctrls
        self.bodyCtrl = ctrlFn.ctrl(name='{}body'.format(extraName), side=self.side,
                                    guide=hipBindJnt.name, deleteGuide=False,
                                    skipNum=True, parent=self.rig.ctrlsGrp.name)
        cmds.setAttr('{}.r'.format(self.bodyCtrl.rootGrp.name), 0, 0, 0)
        self.bodyCtrl.modifyShape(shape='fatPlus', color=col['col2'])
        self.bodyCtrl.lockAttr(['s'])
        self.hipCtrl = ctrlFn.ctrl(name='{}hips'.format(extraName), side=self.side, gimbal=True,
                                   guide=hipBindJnt.name, deleteGuide=False, skipNum=True,
                                   parent=self.bodyCtrl.ctrlEnd)
        self.hipCtrl.modifyShape(shape='sphere', color=col['col1'])
        self.hipCtrl.lockAttr(['s'])
        self.hipCtrl.constrain(hipBindJnt.name)
        self.chestCtrl = ctrlFn.ctrl(name='{}chest'.format(extraName), side=self.side, gimbal=True,
                                     guide=chestBindJnt.name, deleteGuide=False, skipNum=True,
                                     parent=self.bodyCtrl.ctrlEnd)
        self.chestCtrl.modifyShape(shape='sphere', color=col['col2'])
        self.chestCtrl.lockAttr(['s'])
        self.chestCtrl.constrain(chestBindJnt.name)
        ## IK Adv twist
        spineIKStartLoc = utils.newNode('locator', name='{}spineStart'.format(extraName),
                                      side=self.side, parent=hipBindJnt.name)
        spineIKStartLoc.matchTransforms(spineJnts[0])
        spineIKEndLoc = utils.newNode('locator', name='{}spineEnd'.format(extraName),
                                      side=self.side, parent=chestBindJnt.name)
        spineIKEndLoc.matchTransforms(spineJnts[-1])
        spineIK.advancedTwist(spineIKStartLoc.name, spineIKEndLoc.name, wuType=4)
        print '## add world switching to spine ctrls?'


class legModule:
    def __init__(self, rig, extraName='', side='C'):
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, options=defaultBodyOptions.leg, autoOrient=False,
               customNodes=False, parent=None):
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        jntSuffix = suffix['joint']
        jnts = [
            '{}hip{}'.format(self.moduleName, jntSuffix),
            '{}knee{}'.format(self.moduleName, jntSuffix),
            '{}ankle{}'.format(self.moduleName, jntSuffix),
            '{}footBall{}'.format(self.moduleName, jntSuffix),
            '{}footToes{}'.format(self.moduleName, jntSuffix),
        ]
        col = utils.getColors(self.side)
        cmds.parent(jnts[0], self.rig.skelGrp.name)
        legCtrlsGrp = utils.newNode('group', name='{}legCtrls'.format(extraName), side=self.side,
                                    parent=self.rig.ctrlsGrp.name, skipNum=True)
        legMechGrp = utils.newNode('group', name='{}legMech'.format(extraName),
                                   side=self.side, skipNum=True, parent=self.rig.mechGrp.name)
        if options['IK']:
            legMechSkelGrp = utils.newNode('group', name='{}legMechSkel'.format(extraName),
                                           side=self.side, skipNum=True, parent=legMechGrp.name)
        if autoOrient:
            orientJoints.doOrientJoint(jointsToOrient=jnts,
                                       aimAxis=(1 if not self.side == 'R' else -1, 0, 0),
                                       upAxis=(0, 1, 0),
                                       worldUp=(0, 1 if not self.side == 'R' else -1, 0),
                                       guessUp=1)
        ## ik/fk
        if options['IK'] and options['FK']:
            ikJnts, fkJnts, ikCtrlGrp, fkCtrlGrp = ikfkMechanics(self, extraName, jnts,
                                                                 legMechSkelGrp, legCtrlsGrp,
                                                                 moduleType='leg')
        else:
            ikJnts = jnts
            fkJnts = jnts
            ikCtrlGrp = legCtrlsGrp
            fkCtrlGrp = legCtrlsGrp

        if options['IK']:
            ## mechanics
            legIK = ikFn.ik(ikJnts[0], ikJnts[2], name='{}legIK'.format(extraName),
                            side=self.side)
            legIK.createIK(parent=legMechGrp.name)
            ## controls
            self.footIKCtrl = ctrlFn.ctrl(name='{}footIK'.format(extraName), side=self.side,
                                          guide='{}footCtrlGuide{}'.format(self.moduleName,
                                                                           suffix['locator']),
                                          skipNum=True, parent=ikCtrlGrp.name, deleteGuide=True)
            self.footIKCtrl.modifyShape(shape='foot', color=col['col1'], scale=(2, 2, 2))
            self.footIKCtrl.lockAttr(attr=['s'])
            # space switching
            ## polevector ctrl
            pvGuide = '{}legPV{}'.format(self.moduleName, suffix['locator'])
            cmds.delete(cmds.aimConstraint(ikJnts[1], pvGuide))
            self.pvCtrl = ctrlFn.ctrl(name='{}legPV'.format(extraName), side=self.side,
                                      guide=pvGuide, skipNum=True, deleteGuide=True,
                                      parent=ikCtrlGrp.name)
            self.pvCtrl.modifyShape(shape='crossPyramid', color=col['col1'], rotation=(0, 180, 0),
                                    scale=(0.4, 0.4, 0.4))
            self.pvCtrl.constrain(legIK.hdl, typ='poleVector')
            self.pvCtrl.spaceSwitching([self.rig.globalCtrl.ctrl.name, self.footIKCtrl.ctrlEnd],
                                       niceNames=['World', 'Foot'], dv=0)
            ## foot mechanics
            footMechGrp = utils.newNode('group', name='{}footMech'.format(extraName),
                                        side=self.side, parent=legMechGrp.name)
            rfMechGrp = utils.newNode('group', name='{}RFMech'.format(extraName),
                                      side=self.side, parent=footMechGrp.name)
            ##- iks
            footBallIK = ikFn.ik(ikJnts[2], ikJnts[3], side=self.side,
                                 name='{}footBallIK'.format(extraName))
            footBallIK.createIK(parent=footMechGrp.name)
            footToesIK = ikFn.ik(ikJnts[3], ikJnts[4], side=self.side,
                                 name='{}footToesIK'.format(extraName))
            footToesIK.createIK(parent=footMechGrp.name)
            ##- rf joints
            rfJntGuides = [
                '{}footHeelGuide_LOC'.format(self.moduleName),
                '{}footToesGuide_LOC'.format(self.moduleName),
                ikJnts[3],
                ikJnts[2],
            ]
            rfJntNames = [
                'footHeel',
                'footToes',
                'footBall',
                'ankle',
            ]
            rfJnts = utils.createJntChainFromObjs(rfJntGuides, 'RF', side=self.side,
                                                  extraName=extraName, jntNames=rfJntNames,
                                                  parent=rfMechGrp.name)
            ##- rf iks
            rfToesIK = ikFn.ik(rfJnts[0], rfJnts[1], side=self.side,
                               name='{}RF_footToesIK'.format(extraName))
            rfToesIK.createIK(parent=rfMechGrp.name)
            rfBallIK = ikFn.ik(rfJnts[1], rfJnts[2], side=self.side,
                               name='{}RF_footBallIK'.format(extraName))
            rfBallIK.createIK(parent=rfMechGrp.name)
            rfAnkleIK = ikFn.ik(rfJnts[2], rfJnts[3], side=self.side,
                               name='{}RF_ankleIK'.format(extraName))
            rfAnkleIK.createIK(parent=rfMechGrp.name)
            ##- constraints
            cmds.parentConstraint(rfJnts[1], footToesIK.grp, mo=1)
            cmds.parentConstraint(rfJnts[2], footBallIK.grp, mo=1)
            cmds.parentConstraint(rfJnts[3], legIK.grp, mo=1)
            ##- controls
            self.footHeelIKCtrl = ctrlFn.ctrl(name='{}footHeelIK'.format(extraName),
                                              side=self.side, guide=rfJntGuides[0], skipNum=True,
                                              parent=self.footIKCtrl.ctrlEnd)
            self.footHeelIKCtrl.modifyShape(color=col['col2'], shape='pringle', mirror=True,
                                            scale=(0.7, 0.7, 0.7), rotation=(-45, 0, 0))
            self.footHeelIKCtrl.lockAttr(attr=['t', 's'])
            self.footHeelIKCtrl.constrain(rfToesIK.grp)
            self.footHeelIKCtrl.constrain(rfJnts[0])

            self.footToesIKCtrl = ctrlFn.ctrl(name='{}footToesIK'.format(extraName),
                                              side=self.side, guide=rfJntGuides[1], skipNum=True,
                                              parent=self.footHeelIKCtrl.ctrlEnd)
            self.footToesIKCtrl.modifyShape(color=col['col2'], shape='pringle', mirror=True,
                                            scale=(0.7, 0.7, 0.7), rotation=(90, 0, 0),
                                            translation=(0, -1, 0))
            self.footToesIKCtrl.lockAttr(attr=['t', 's'])
            self.footToesIKCtrl.constrain(rfBallIK.grp)

            self.footBallIKCtrl = ctrlFn.ctrl(name='{}footBallIK'.format(extraName),
                                              side=self.side, guide=rfJntGuides[2], skipNum=True,
                                              parent=self.footToesIKCtrl.ctrlEnd)
            self.footBallIKCtrl.modifyShape(color=col['col2'], shape='pringle', mirror=True,
                                            scale=(0.7, 0.7, 0.7), translation=(0, 1.5, 0))
            self.footBallIKCtrl.lockAttr(attr=['t', 's'])
            cmds.xform(self.footBallIKCtrl.offsetGrps[0].name, ro=(-90, 0, 90))
            self.footBallIKCtrl.constrain(rfAnkleIK.grp)
            print ('## probably should add a ctrl for the ik toes to just'
                   +' bend the toes without any of the foot')
            if cmds.objExists('{}footGuides{}'.format(self.moduleName, suffix['group'])):
                cmds.delete('{}footGuides{}'.format(self.moduleName, suffix['group']))

        if options['FK']:
            ## controls
            self.hipFKCtrl = ctrlFn.ctrl(name='{}hipFK'.format(extraName),
                                         side=self.side, guide=fkJnts[0], skipNum=True,
                                         parent=fkCtrlGrp.name)
            self.hipFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                       scale=(0.6, 0.6, 0.6))
            self.hipFKCtrl.lockAttr(attr=['s'])
            self.hipFKCtrl.constrain(fkJnts[0], typ='parent')

            self.kneeFKCtrl = ctrlFn.ctrl(name='{}kneeFK'.format(extraName),
                                          side=self.side, guide=fkJnts[1], skipNum=True,
                                          parent=self.hipFKCtrl.ctrlEnd)
            self.kneeFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                        scale=(0.6, 0.6, 0.6))
            self.kneeFKCtrl.lockAttr(attr=['s'])
            self.kneeFKCtrl.constrain(fkJnts[1], typ='parent')

            self.ankleFKCtrl = ctrlFn.ctrl(name='{}ankleFK'.format(extraName),
                                           side=self.side, guide=fkJnts[2], skipNum=True,
                                           parent=self.kneeFKCtrl.ctrlEnd)
            self.ankleFKCtrl.modifyShape(color=col['col2'], shape='circle',
                                         scale=(0.6, 0.6, 0.6))
            self.ankleFKCtrl.lockAttr(attr=['s'])
            self.ankleFKCtrl.constrain(fkJnts[2], typ='parent')

            self.footBallFKCtrl = ctrlFn.ctrl(name='{}footBallFK'.format(extraName),
                                              side=self.side, guide=fkJnts[3], skipNum=True,
                                              parent=self.ankleFKCtrl.ctrlEnd)
            self.footBallFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.footBallFKCtrl.lockAttr(attr=['s'])
            self.footBallFKCtrl.constrain(fkJnts[3], typ='parent')
        if options['stretchy']:
            if options['IK']:
                legIK.addStretch(customStretchNode=customNodes,
                                 globalScaleAttr=self.rig.scaleAttr)
                self.footIKCtrl.addAttr('stretchySwitch', nn='Stretch Switch',
                                       minVal=0, maxVal=1, defaultVal=1)
                cmds.connectAttr(self.footIKCtrl.ctrl.stretchySwitch,
                                 legIK.stretchToggleAttr)
            if options['FK']:
                print '## add proper stretch to leg fk'

        if options['softIK']:
            print '## do leg softIK stuff'

        if options['ribbon']:
            print '## do leg ribbon stuff'

        ## leg parent stuff
        if parent:
            legParentLoc = utils.newNode('locator', name='{}legParent'.format(extraName),
                                         side=self.side, skipNum=True, parent=parent)
            legParentLoc.matchTransforms(jnts[0])
            cmds.parentConstraint(legParentLoc.name, ikJnts[0], mo=1)
            cmds.parentConstraint(legParentLoc.name, fkJnts[0], mo=1)


class headModule:
    def __init__(self, rig, extraName='', side='C'):
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, options=defaultBodyOptions.head, autoOrient=True,
               parent=None, extraSpaces=''):
        if parent:
            gParent = cmds.listRelatives(parent, p=1)[0]
            ctrlSpaceSwitches = [self.rig.globalCtrl.ctrlEnd, gParent]
        else:
            cmds.error('FUCK, I DON\'T KNOW WHAT TO DO WITHOUT A PARENT FOR THE HEAD YET.')
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        jntSuffix = suffix['joint']
        jnts = [
            parent,
            '{}head{}'.format(self.moduleName, jntSuffix),
            '{}headEnd{}'.format(self.moduleName, jntSuffix),
        ]
        col = utils.getColors(self.side)
        cmds.parent(jnts[1], jnts[0])
        if autoOrient:
            orientJoints.doOrientJoint(jointsToOrient=jnts,
                                       aimAxis=(1 if not self.side == 'R' else -1, 0, 0),
                                       upAxis=(0, 1, 0),
                                       worldUp=(0, 1 if not self.side == 'R' else -1, 0),
                                       guessUp=1)
        headCtrlsGrp = utils.newNode('group', name='{}headCtrls'.format(extraName), side=self.side,
                                     parent=self.rig.ctrlsGrp.name, skipNum=True)
        if type(extraSpaces) == type(list()) and len(extraSpaces) > 1:
            ctrlSpaceSwitches.extend(extraSpaces)
        else:
            ctrlSpaceSwitches.append(extraSpaces)
        if options['IK']:
            ## IK mechanics
            headMechGrp = utils.newNode('group', name='{}headMech'.format(extraName),
                                        side=self.side, parent=self.rig.mechGrp.name, skipNum=True)
            headIKsGrp = utils.newNode('group', name='{}headIKs'.format(extraName),
                                       side=self.side, parent=headMechGrp.name, skipNum=True)
            neckIK = ikFn.ik(jnts[0], jnts[1], name='{}neckIK'.format(extraName), side=self.side)
            neckIK.createIK(parent=headIKsGrp.name)
            headIK = ikFn.ik(jnts[1], jnts[2], name='{}headIK'.format(extraName), side=self.side)
            headIK.createIK(parent=headIKsGrp.name)
            ## IK Control
            self.headCtrl = ctrlFn.ctrl(name='{}head'.format(extraName), side=self.side,
                                        guide=jnts[1], skipNum=True, parent=headCtrlsGrp.name)
            self.headCtrl.modifyShape(shape='sphere', color=col['col3'], mirror=True,
                                      translation=(2, 0, 0))
            self.headCtrl.lockAttr(['s'])
            self.headCtrl.constrain(headIKsGrp.name)
            self.headCtrl.spaceSwitching(ctrlSpaceSwitches, dv=1)
        else:
            self.neckCtrl = ctrlFn.ctrl(name='{}neck'.format(extraName), side=self.side,
                                        guide=jnts[0], skipNum=True, parent=headCtrlsGrp.name)
            self.neckCtrl.modifyShape(shape='circle', color=col['col1'], mirror=True,
                                      scale=(0.4, 0.4, 0.4))
            self.neckCtrl.lockAttr(['s', 't'])
            self.neckCtrl.constrain(jnts[0], typ='orient')
            self.headCtrl = ctrlFn.ctrl(name='{}head'.format(extraName), side=self.side,
                                        guide=jnts[1], skipNum=True, parent=self.neckCtrl.ctrlEnd)
            self.headCtrl.modifyShape(shape='sphere', color=col['col3'], mirror=True,
                                      translation=(2, 0, 0))
            self.headCtrl.lockAttr(['s', 't'])
            self.headCtrl.constrain(jnts[1])
            self.neckCtrl.spaceSwitching(ctrlSpaceSwitches, dv=1)


class digitsModule:
    def __init__(self, rig, extraName='', side='C'):
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, mode, options=defaultBodyOptions.digits, autoOrient=False, customNodes=False,
               parent=None, thumb=True):
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        jntSuffix = suffix['joint']
        col = utils.getColors(self.side)
        handCtrlGrp = utils.newNode('group', name='{}{}Ctrls'.format(extraName, mode),
                                    side=self.side, parent=self.rig.ctrlsGrp.name, skipNum=True)
        cmds.parentConstraint(parent, handCtrlGrp.name, mo=1)
        if mode == 'hand':
            typ = 'fngr'
        else:
            typ = 'toe'
        digitsList = ['Index', 'Middle', 'Ring', 'Pinky']
        if thumb:
            digitsList.append('Thumb')
        digitCtrls = {}
        palmMults = []
        palmCtrl = ctrlFn.ctrl(name='{}{}Palm'.format(extraName, typ),
                               side=self.side,
                               guide='{}{}PalmGuide{}'.format(self.moduleName, mode,
                                                              suffix['locator']),
                               deleteGuide=True, skipNum=True, parent=handCtrlGrp.name)
        palmCtrl.modifyShape(shape='sphere', color=col['col2'], scale=(0.2, 0.2, 0.3))
        for each in digitsList:
            segments = ['metacarpel', 'base', 'lowMid', 'highMid', 'tip']
            jnts = [
                '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[0], jntSuffix),
                '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[1], jntSuffix),
                '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[2], jntSuffix),
                '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[3], jntSuffix),
                '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[4], jntSuffix),
            ]
            ctrlParent = handCtrlGrp.name
            if each == 'Pinky':
                pinkyBaseJnt = jnts[0]
                ctrlParent = palmCtrl.ctrlEnd
            elif each == 'Index':
                indexBaseJnt = jnts[0]
            prevJnt = None
            segmentCtrls = []
            for i, seg in enumerate(segments):
                ctrl = ctrlFn.ctrl(name='{}{}{}_{}'.format(extraName, typ, each, seg),
                                   side=self.side, guide=jnts[i], skipNum=True,
                                   parent=ctrlParent)
                segmentCtrls.append(ctrl)
                ctrlCol = col['col3']
                ctrlShape = 'circle'
                ctrlScale = (0.1, 0.1, 0.1)
                if seg == 'metacarpel':
                    if each == 'Thumb':
                        ctrlShape = 'sphere'
                        ctrlScale = (0.3, 0.2, 0.2)
                        ctrlCol = col['col2']
                    else:
                        ctrlCol = None

                ctrl.modifyShape(shape=ctrlShape, scale=ctrlScale, color=ctrlCol)
                loc = utils.newNode('locator', name='{}{}{}_{}'.format(extraName, typ, each, seg),
                                    side=self.side)
                utils.setShapeColor(loc.name, color=None)
                loc.parent(ctrl.ctrlEnd, relative=True)
                ctrl.lockAttr(['s'])
                if i > 0:
                    bJnt = cmds.duplicate(jnts[i], po=1)[0]
                    bJnt = cmds.rename(bJnt, '{}{}{}_{}B{}'.format(self.moduleName, typ, each,
                                                                seg, jntSuffix))
                    bTrans = utils.newNode('multDoubleLinear',
                                           name='{}{}{}_{}BTrans'.format(extraName, typ,
                                                                         each, seg),
                                           side=self.side)
                    bTrans.connect('input1', '{}.tx'.format(jnts[i]), mode='to')
                    cmds.setAttr('{}.input2'.format(bTrans.name), 0.95)
                    bTrans.connect('output', '{}.tx'.format(bJnt))
                    ctrl.constrain(prevJnt, typ='aim', aimWorldUpObject=ctrlParent)
                    distNd = utils.newNode('distanceBetween',
                                           name='{}{}{}_{}'.format(extraName, typ, each, seg),
                                           side=self.side)
                    distNd.connect('point1', '{}.wp'.format(prevLoc.name), mode='to')
                    distNd.connect('point2', '{}.wp'.format(loc.name), mode='to')
                    distNd.connect('distance', '{}.tx'.format(jnts[i]))
                else:
                    palmOrientMult = utils.newNode('multiplyDivide',
                                                   name='{}{}{}_baseOrient'.format(extraName, typ,
                                                                                   each),
                                                   side=self.side,
                                                   suffixOverride='multiplyDivide_mult')
                    palmOrientMult.connect('output', '{}.r'.format(ctrl.offsetGrps[0].name))
                    if not each == 'Pinky':
                        palmTransMult = utils.newNode('multiplyDivide',
                                                      name='{}{}{}_baseTrans'.format(extraName, typ,
                                                                                     each),
                                                      side=self.side,
                                                      suffixOverride='multiplyDivide_mult')
                        palmTransMult.connect('output', '{}.t'.format(ctrl.offsetGrps[0].name))
                    else:
                        palmTransMult = False
                    palmMults.append((palmOrientMult, palmTransMult))

                prevJnt = jnts[i]
                prevLoc = loc
                ctrlParent = ctrl.ctrlEnd
            digitCtrls[each] = segmentCtrls
        self.indexCtrls = digitCtrls['Index']
        self.middleCtrls = digitCtrls['Middle']
        self.ringCtrls = digitCtrls['Ring']
        self.pinkyCtrls = digitCtrls['Pinky']
        if thumb:
            self.thumbCtrls = digitCtrls['Thumb']

        palmLoc = utils.newNode('locator', name='{}{}Palm'.format(extraName, mode),
                                side=self.side, parent=parent)
        palmLoc.matchTransforms(pinkyBaseJnt)
        cmds.makeIdentity(palmLoc.name, a=1, t=1)
        oConstr = palmCtrl.constrain(palmLoc.name, typ='orient')
        cmds.setAttr('{}.offsetY'.format(oConstr), (cmds.getAttr('{}.offsetY'.format(oConstr))-360))
        palmCtrl.constrain(palmLoc.name, typ='point')
        for digit, multNds in zip(digitsList, palmMults):
            orient, trans = multNds
            if digit == 'Thumb' or digit == 'Index':
                pass
            else:
                if digit == 'Pinky':
                    val = 1
                elif digit == 'Ring':
                    val = 0.667
                elif digit == 'Middle':
                    val = 0.333
                cmds.setAttr('{}.input2'.format(orient.name), val, val, val)
                orient.connect('input1', '{}.r'.format(palmLoc.name), mode='to')
                if trans:
                    cmds.setAttr('{}.input2'.format(trans.name), val, val, val)
                    trans.connect('input1', '{}.t'.format(palmLoc.name), mode='to')




class tailModule:
    def __init__(self):
        print '## tail'
