import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ikFunctions as ikFn
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules import fileFunctions as fileFn
from Jenks.scripts.rigModules import miscFunctions as miscFn
from Jenks.scripts.rigModules import apiFuncitons as apiFn
from Jenks.scripts.rigModules.suffixDictionary import suffix
from Jenks.scripts.rigModules import defaultBodyOptions
from Jenks.scripts.rigModules import orientJoints

reload(orientJoints)
reload(utils)
reload(ikFn)
reload(ctrlFn)
reload(miscFn)
reload(defaultBodyOptions)


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
            '{}clavicle{}'.format(self.moduleName, jntSuffix),
            '{}shoulder{}'.format(self.moduleName, jntSuffix),
            '{}elbow{}'.format(self.moduleName, jntSuffix),
            '{}wrist{}'.format(self.moduleName, jntSuffix),
            '{}handEnd{}'.format(self.moduleName, jntSuffix),
        ]
        col = utils.getColors(self.side)
        cmds.parent(jnts[0], self.rig.skelGrp.name)
        armCtrlsGrp = utils.newNode('group', name='{}armCtrls'.format(extraName), side=self.side,
                                    parent=self.rig.ctrlsGrp.name, skipNum=True)
        armMechGrp = utils.newNode('group', name='{}armMech'.format(extraName),
                                   side=self.side, skipNum=True, parent=self.rig.mechGrp.name)
        if not parent:
            parentCtrl = ctrlFn.ctrl(name='{}armParent'.format(extraName), side=self.side,
                                     parent=armCtrlsGrp.name, guide=jnts[0], skipNum=True)
            parentCtrl.modifyShape(shape='sphere', color=col['col1'])
            parent = parentCtrl.ctrlEnd
        else:
            parentCtrl = None
        if options['IK']:
            armMechSkelGrp = utils.newNode('group', name='{}armMechSkel'.format(extraName),
                                           side=self.side, skipNum=True, parent=armMechGrp.name)
        ## orient joints
        if autoOrient:
            orientJoints.doOrientJoint(jointsToOrient=jnts[1:],
                                       aimAxis=(1 if not self.side == 'R' else -1, 0, 0),
                                       upAxis=(0, 1, 0),
                                       worldUp=(0, 1 if not self.side == 'R' else -1, 0),
                                       guessUp=1)
        ## ik/fk
        if options['IK'] and options['FK']:
            clavChild = armMechSkelGrp.name
            ikJnts, fkJnts, jnts, ikCtrlGrp, fkCtrlGrp = miscFn.ikfkMechanics(self, extraName, jnts,
                                                                       armMechSkelGrp, armCtrlsGrp,
                                                                       moduleType='arm', rig=self.rig)
        else:
            ikJnts = jnts
            fkJnts = jnts
            ikCtrlGrp = armCtrlsGrp
            fkCtrlGrp = armCtrlsGrp
            # clavChild = jnts[0]
        # cmds.parentConstraint(clavJnts[1], clavChild, mo=1)
        self.handJnt = jnts[3]
        ## ik
        if options['IK']:
            ##- mechanics
            armIK = ikFn.ik(ikJnts[1], ikJnts[3], name='{}armIK'.format(extraName),
                            side=self.side)
            armIK.createIK(parent=armMechGrp.name)
            handIK = ikFn.ik(ikJnts[3], ikJnts[4], name='{}handIK'.format(extraName),
                             side=self.side)
            handIK.createIK(parent=armMechGrp.name)
            ##- controls
            if self.side == 'R':
                tmpJnt = cmds.duplicate(ikJnts[3], po=1)
                cmds.xform(tmpJnt, r=1, ro=(0, 0, 180))
                self.handIKCtrl = ctrlFn.ctrl(name='{}handIK'.format(extraName), side=self.side,
                                          guide=tmpJnt, skipNum=True, parent=ikCtrlGrp.name,
                                          deleteGuide=True, scaleOffset=self.rig.scaleOffset,
                                          rig=self.rig)
            else:
                self.handIKCtrl = ctrlFn.ctrl(name='{}handIK'.format(extraName), side=self.side,
                                              guide=ikJnts[3], skipNum=True, parent=ikCtrlGrp.name,
                                              scaleOffset=self.rig.scaleOffset, rig=self.rig)
            self.handIKCtrl.modifyShape(shape='cube', color=col['col1'], scale=(0.6, 0.6, 0.6))
            self.handIKCtrl.lockAttr(attr=['s'])
            if options['softIK']:
                # fileFn.loadPlugin('mjSoftIK', '.py')
                softIk = utils.newNode('mjSoftIK', name='{}armIK'.format(extraName),
                                       side=self.side)
                jntLoc = utils.newNode('locator', name='{}armJntBase'.format(extraName),
                                       side=self.side, skipNum=True,
                                       parent=cmds.listRelatives(jnts[1], p=1))
                jntLoc.matchTransforms(jnts[1])
                softIk.connect('sm', '{}.wm'.format(jntLoc.name), 'to')
                softIk.connect('cm', '{}.wm'.format(self.handIKCtrl.ctrlEnd), 'to')
                cmds.setAttr('{}.cl'.format(softIk.name), abs(cmds.getAttr('{}.tx'.format(jnts[2]))
                             + cmds.getAttr('{}.tx'.format(jnts[3]))))
                softIk.connect('ot', '{}.t'.format(armIK.grp))
                self.handIKCtrl.addAttr(name='softIKSep', nn='___   Soft IK', typ='enum',
                                        enumOptions=['___'])
                self.handIKCtrl.addAttr(name='softIKTog', nn='Toggle Soft IK', typ='enum',
                                        enumOptions=['Off', 'On'])
                cmds.connectAttr(self.handIKCtrl.ctrl.softIKTog, '{}.tog'.format(softIk.name))
                self.handIKCtrl.addAttr(name='softIKDist', nn='Soft IK Distance', defaultVal=0.2)
                cmds.connectAttr(self.handIKCtrl.ctrl.softIKDist, '{}.sd'.format(softIk.name))
            else:
                self.handIKCtrl.constrain(armIK.grp)
            self.handIKCtrl.constrain(handIK.grp)
            self.handIKCtrl.spaceSwitching([self.rig.globalCtrl.ctrl.name,
                                            parent],
                                           # niceNames=['World', 'Chest', 'Clavicle'],
                                           dv=0)
            ##-- PoleVector
            pvGuide = '{}armPV{}'.format(self.moduleName, suffix['locator'])
            cmds.delete(cmds.aimConstraint(ikJnts[2], pvGuide))
            self.pvCtrl = ctrlFn.ctrl(name='{}armPV'.format(extraName), side=self.side,
                                      guide=pvGuide,
                                      skipNum=True, deleteGuide=True, parent=ikCtrlGrp.name,
                                      scaleOffset=self.rig.scaleOffset, rig=self.rig)
            self.pvCtrl.modifyShape(shape='crossPyramid', color=col['col1'], rotation=(0, 180, 0),
                                    scale=(0.4, 0.4, 0.4))
            self.pvCtrl.lockAttr(['r', 's'])
            self.pvCtrl.constrain(armIK.hdl, typ='poleVector')
            self.pvCtrl.spaceSwitching([self.rig.globalCtrl.ctrlEnd, self.handIKCtrl.ctrlEnd],
                                           niceNames=['World', 'Hand'], dv=0)
            ## clav
            self.clavIKCtrl = ctrlFn.ctrl(name='{}clavicleIK'.format(extraName), side=self.side,
                                          guide=jnts[0], skipNum=True,
                                          deleteGuide=False, parent=ikCtrlGrp.name,
                                          scaleOffset=self.rig.scaleOffset, rig=self.rig)
            self.clavIKCtrl.modifyShape(shape='pin', color=col['col2'], mirror=True,
                                        scale=(2, 2, 2))
            clavIKCtrlPiv = cmds.xform(parent, q=1, t=1, ws=1)
            cmds.xform(self.clavIKCtrl.ctrl.name, piv=clavIKCtrlPiv, ws=1)
            self.clavIKCtrl.lockAttr(attr=['t', 's'])
            ## autoClav
            if options['autoClav'] and not parentCtrl:
                self.clavIKCtrl.addAttr(name='autoClav', nn='Automatic Clavicle Switch',
                                        defaultVal=1, minVal=0, maxVal=1)
                autoClavMechGrp = utils.newNode('group', name='{}autoClavMech'.format(extraName),
                                                side=self.side, parent=armMechGrp.name,
                                                skipNum=True)
                cmds.parentConstraint(parent, autoClavMechGrp.name)
                ## create dupe arm
                dupeArmJnts = []
                dupeArmPar = autoClavMechGrp.name
                for jnt in jnts[1:-1]:
                    if '_result_' in jnt:
                        newJntName = jnt.replace('_result_', '_autoClav_')
                    else:
                        newJntName = '{}_autoClav{}'.format(jnt.rstrip(suffix['joint']),
                                                            suffix['joint'])
                    newJnt = cmds.duplicate(jnt, po=1, n=newJntName)[0]
                    if dupeArmPar is None:
                        cmds.parent(newJnt, w=1)
                    else:
                        cmds.parent(newJnt, dupeArmPar)
                    dupeArmJnts.append(newJnt)
                    dupeArmPar = newJnt
                ## create elbow locators
                nonBindElbow = utils.newNode('locator', name='{}autoClavElbow'.format(extraName),
                                             side=self.side)
                nonBindElbow.parent(dupeArmJnts[1], relative=True)
                bindElbow = utils.newNode('locator', name='{}autoClavElbowBind'.format(extraName),
                                          side=self.side, parent=autoClavMechGrp.name)
                bindElbow.matchTransforms(dupeArmJnts[1])
                ## ik
                dupeArmIK = ikFn.ik(sj=dupeArmJnts[0], ej=dupeArmJnts[-1],
                                    name='autoclavArmIK', side=self.side)
                dupeArmIK.createIK(parent=autoClavMechGrp.name)
                ## parent constrain to hand ctrl
                self.handIKCtrl.constrain(dupeArmIK.grp)
                ## pole vector to arm pv
                self.pvCtrl.constrain(dupeArmIK.hdl, typ='pv')
                ## create duplicate spine joint + clav
                newClavJnts = []
                newClavJnts.append(utils.newNode('joint',
                                                 name='{}autoClavSpine'.format(extraName),
                                                 side=self.side, skipNum=True,
                                                 parent=autoClavMechGrp.name))
                newClavJnts.append(utils.newNode('joint',
                                                 name='{}autoClavClavicle'.format(extraName),
                                                 side=self.side, skipNum=True,
                                                 parent=newClavJnts[0].name))
                newClavJnts[0].matchTransforms(parent)
                newClavJnts[0] = newClavJnts[0].name
                newClavJnts[1].matchTransforms(jnts[0])
                newClavJnts[1] = newClavJnts[1].name
                # autoClavSwConstr = cmds.parentConstraint(parent, newClavJnts[1], ikJnts[0], mo=1)
                cmds.parentConstraint(newClavJnts[1], ikJnts[0], mo=1)
                ## ik
                autoClavClavIK = ikFn.ik(sj=newClavJnts[0], ej=newClavJnts[-1], side=self.side,
                                         name='{}autoClavClavicleIK'.format(extraName))
                autoClavClavIK.createIK(parent=autoClavMechGrp.name)
                ## parent constrain clavIK
                self.clavIKCtrl.constrain(autoClavClavIK.grp)
                ## create autoclav jnts (spine and elbow)
                aCMechJnts = []
                aCMechJnts.append(utils.newNode('joint',
                                                name='{}autoClavMechSpine'.format(extraName),
                                                side=self.side, skipNum=True,
                                                parent=autoClavMechGrp.name))
                aCMechJnts.append(utils.newNode('joint',
                                                name='{}autoClavMechElbow'.format(extraName),
                                                side=self.side, skipNum=True,
                                                parent=aCMechJnts[0].name))
                aCMechJnts[0].matchTransforms(parent)
                aCMechJnts[0] = aCMechJnts[0].name
                aCMechJnts[1].matchTransforms(jnts[2])
                aCMechJnts[1] = aCMechJnts[1].name
                ## ik
                autoClavMechIK = ikFn.ik(sj=aCMechJnts[0], ej=aCMechJnts[-1], side=self.side,
                                         name='{}autoClavMechIK'.format(extraName))
                autoClavMechIK.createIK(parent=autoClavMechGrp.name)
                ## constrain ik
                aCMechParConstr = cmds.parentConstraint(bindElbow.name, nonBindElbow.name,
                                                        autoClavMechIK.grp, mo=1)[0]
                cmds.setAttr('{}.interpType'.format(aCMechParConstr), 2)
                ## constrain clav ctrl
                autoClavSwCtrlConstr = cmds.parentConstraint(parent, aCMechJnts[-1],
                                                             self.clavIKCtrl.offsetGrps[0].name,
                                                             mo=1)[0]
                revNd = utils.newNode('reverse', name='{}autoClavSw'.format(extraName),
                                      side=self.side)
                revNd.connect('inputX', self.clavIKCtrl.ctrl.autoClav, mode='to')
                cmds.connectAttr(self.clavIKCtrl.ctrl.autoClav,
                                 '{}.{}W1'.format(autoClavSwCtrlConstr, aCMechJnts[-1]))
                revNd.connect('outputX', '{}.{}W0'.format(autoClavSwCtrlConstr, parent))

            else:
                clavIK = ikFn.ik(sj=ikJnts[0], ej=ikJnts[1], side=self.side,
                                 name='{}clavicleIK'.format(extraName))
                clavIK.createIK(parent=armMechGrp.name)
                self.clavIKCtrl.constrain(clavIK.grp)

        ## fk
        if options['FK']:
            ##- controls
            self.clavFKCtrl = ctrlFn.ctrl(name='{}clavicleFK'.format(extraName), side=self.side,
                                          guide=jnts[0], skipNum=True, parent=fkCtrlGrp.name,
                                          scaleOffset=self.rig.scaleOffset, rig=self.rig)
            self.clavFKCtrl.modifyShape(shape='pringle', color=col['col2'], mirror=True)
            self.clavFKCtrl.lockAttr(attr=['t', 's'])
            cmds.parentConstraint(parent, self.clavFKCtrl.offsetGrps[0].name, mo=1)
            self.clavFKCtrl.constrain(fkJnts[0])
            self.shoulderFKCtrl = ctrlFn.ctrl(name='{}shoulderFK'.format(extraName),
                                              side=self.side, guide=fkJnts[1], skipNum=True,
                                              parent=self.clavFKCtrl.ctrlEnd, rig=self.rig,
                                              scaleOffset=self.rig.scaleOffset)
            self.shoulderFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.shoulderFKCtrl.lockAttr(attr=['s'])
            self.shoulderFKCtrl.constrain(fkJnts[1], typ='parent')

            self.elbowFKCtrl = ctrlFn.ctrl(name='{}elbowFK'.format(extraName), side=self.side,
                                           guide=fkJnts[2], skipNum=True,
                                           parent=self.shoulderFKCtrl.ctrlEnd,
                                           scaleOffset=self.rig.scaleOffset,
                                           rig=self.rig)
            self.elbowFKCtrl.modifyShape(color=col['col2'], shape='circle',
                                         scale=(0.6, 0.6, 0.6))
            self.elbowFKCtrl.lockAttr(attr=['s'])
            self.elbowFKCtrl.constrain(fkJnts[2], typ='parent')

            self.wristFKCtrl = ctrlFn.ctrl(name='{}wristFK'.format(extraName), side=self.side,
                                          guide=fkJnts[3], skipNum=True,
                                          parent=self.elbowFKCtrl.ctrlEnd,
                                          scaleOffset=self.rig.scaleOffset,
                                          rig=self.rig)
            self.wristFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                         scale=(0.6, 0.6, 0.6))
            self.wristFKCtrl.lockAttr(attr=['s'])
            self.wristFKCtrl.constrain(fkJnts[3], typ='parent')
        ## stretchy
        if options['stretchy']:
            if options['IK']:
                armIK.addStretch(customStretchNode=customNodes,
                                 globalScaleAttr='{}.sy'.format(self.rig.globalCtrl.ctrl.name))
                self.handIKCtrl.addAttr('stretchSep', nn='___   Stretch',
                                        typ='enum', enumOptions=['___'])
                self.handIKCtrl.addAttr('stretchySwitch', nn='Stretch Switch',
                                         minVal=0, maxVal=1, defaultVal=1)
                cmds.connectAttr(self.handIKCtrl.ctrl.stretchySwitch, armIK.stretchToggleAttr)
            if options['FK']:
                print '## add proper stretch to arm fk'
        ## ribbon
        if options['ribbon']:
            print '## do arm ribbon'

        ## arm parent stuff
        if parent:
            armParentLoc = utils.newNode('locator', name='{}armParent'.format(extraName),
                                         side=self.side, skipNum=True, parent=parent)
            armParentLoc.matchTransforms(jnts[0])
            # cmds.parentConstraint(armParentLoc.name, jnts[0], mo=1)
            # cmds.parentConstraint(armParentLoc.name, self.clavIKCtrl.rootGrp.name, mo=1)
        return True


class spineModule:
    def __init__(self, rig, extraName='', side='C'):
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def createFromJnts(self, autoOrient=False):
        jntSuffix = suffix['joint']
        spineJnts = utils.getChildrenBetweenObjs('{}spine_base{}'.format(self.moduleName,
                                                                        jntSuffix),
                                                 '{}spine_end{}'.format(self.moduleName,
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
        for each in spineJnts:
            utils.addJntToSkinJnt(each, self.rig)

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
        tmpEndBindJnt = utils.newNode('joint', parent=chestBindJnt.name)
        tmpEndBindJnt.matchTransforms(self.endJnt)
        ## splineIK
        spineIK = ikFn.ik(spineJnts[0], spineJnts[-1], name='spineIK', side=self.side)
        if crv:
            spineIK.createSplineIK(parent=spineMechGrp.name, crv=crv)
        else:
            spineIK.createSplineIK(parent=spineMechGrp.name)
        spineIK.addStretch(globalScaleAttr=self.rig.scaleAttr, mode='length', operation='both')
        ## skin bindJnts to crv
        spineSkin = cmds.skinCluster(hipBindJnt.name, chestBindJnt.name, tmpEndBindJnt.name, spineIK.crv)
        cmds.skinCluster(spineSkin, e=1, ri=tmpEndBindJnt.name)
        cmds.delete(tmpEndBindJnt.name)
        ## ctrls
        self.bodyCtrl = ctrlFn.ctrl(name='{}body'.format(extraName), side=self.side,
                                    guide=hipBindJnt.name, deleteGuide=False,
                                    skipNum=True, parent=self.rig.ctrlsGrp.name,
                                    scaleOffset=self.rig.scaleOffset,
                                    rig=self.rig)
        cmds.setAttr('{}.r'.format(self.bodyCtrl.rootGrp.name), 0, 0, 0)
        self.bodyCtrl.modifyShape(shape='fatPlus', color=col['col2'])
        self.bodyCtrl.lockAttr(['s'])
        self.hipCtrl = ctrlFn.ctrl(name='{}hips'.format(extraName), side=self.side, gimbal=True,
                                   guide=hipBindJnt.name, deleteGuide=False, skipNum=True,
                                   parent=self.bodyCtrl.ctrlEnd,
                                   scaleOffset=self.rig.scaleOffset,
                                   rig=self.rig)
        self.hipCtrl.modifyShape(shape='sphere', color=col['col1'])
        self.hipCtrl.lockAttr(['s'])
        self.hipCtrl.constrain(hipBindJnt.name)
        self.chestCtrl = ctrlFn.ctrl(name='{}chest'.format(extraName), side=self.side, gimbal=True,
                                     guide=chestBindJnt.name, deleteGuide=False, skipNum=True,
                                     parent=self.bodyCtrl.ctrlEnd,
                                     scaleOffset=self.rig.scaleOffset,
                                     rig=self.rig)
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
            ikJnts, fkJnts, jnts, ikCtrlGrp, fkCtrlGrp = miscFn.ikfkMechanics(self, extraName, jnts,
                                                                       legMechSkelGrp, legCtrlsGrp,
                                                                       moduleType='leg',
                                                                       rig=self.rig)
        else:
            ikJnts = jnts
            fkJnts = jnts
            ikCtrlGrp = legCtrlsGrp
            fkCtrlGrp = legCtrlsGrp

        self.footJnt = jnts[3]

        if options['IK']:
            ## mechanics
            legIK = ikFn.ik(ikJnts[0], ikJnts[2], name='{}legIK'.format(extraName),
                            side=self.side)
            legIK.createIK(parent=legMechGrp.name)
            ## controls
            self.footIKCtrl = ctrlFn.ctrl(name='{}footIK'.format(extraName), side=self.side,
                                          guide='{}footCtrlGuide{}'.format(self.moduleName,
                                                                           suffix['locator']),
                                          skipNum=True, parent=ikCtrlGrp.name, deleteGuide=True,
                                          scaleOffset=self.rig.scaleOffset, rig=self.rig)
            self.footIKCtrl.modifyShape(shape='foot', color=col['col1'], scale=(2, 2, 2))
            self.footIKCtrl.lockAttr(attr=['s'])
            # space switching
            ## polevector ctrl
            pvGuide = '{}legPV{}'.format(self.moduleName, suffix['locator'])
            cmds.delete(cmds.aimConstraint(ikJnts[1], pvGuide))
            self.pvCtrl = ctrlFn.ctrl(name='{}legPV'.format(extraName), side=self.side,
                                      guide=pvGuide, skipNum=True, deleteGuide=True,
                                      parent=ikCtrlGrp.name, scaleOffset=self.rig.scaleOffset,
                                      rig=self.rig)
            self.pvCtrl.modifyShape(shape='crossPyramid', color=col['col1'], rotation=(0, 180, 0),
                                    scale=(0.4, 0.4, 0.4))
            self.pvCtrl.lockAttr(['r', 's'])
            self.pvCtrl.constrain(legIK.hdl, typ='poleVector')
            self.pvCtrl.spaceSwitching([self.rig.globalCtrl.ctrlEnd, self.footIKCtrl.ctrlEnd],
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
                '{}footHeelGuide{}'.format(self.moduleName, suffix['locator']),
                '{}footToesGuide{}'.format(self.moduleName, suffix['locator']),
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
            ##- foot side pivots
            self.footIKCtrl.addAttr('footRollsSep', nn='___   Foot Rolls', typ='enum',
                                    enumOptions=['___'])
            innerPivGrp = utils.newNode('group', name='{}footInnerPivot'.format(extraName),
                                        parent=self.footIKCtrl.ctrlEnd, side=self.side,
                                        skipNum=True)
            innerPivGrp.matchTransforms('{}footInnerGuide{}'.format(self.moduleName, suffix['locator']))
            outerPivGrp = utils.newNode('group', name='{}footOuterPivot'.format(extraName),
                                        parent=innerPivGrp.name, side=self.side, skipNum=True)
            outerPivGrp.matchTransforms('{}footOuterGuide{}'.format(self.moduleName, suffix['locator']))
            self.footIKCtrl.addAttr('sidePiv', nn='Side Pivot')
            sidePivNeg = utils.newNode('condition', name='{}footSidePivNeg'.format(extraName),
                                        side=self.side, operation=3)
            sidePivNeg.connect('firstTerm', self.footIKCtrl.ctrl.sidePiv, mode='to')
            if self.side == 'R':
                negFootPivAttr = utils.newNode('reverse',
                                               name='{}footSidePivNeg'.format(extraName),
                                               side=self.side)
                negFootPivAttr.connect('inputX', self.footIKCtrl.ctrl.sidePiv, mode='to')
                negFootPivAttr = '{}.outputX'.format(negFootPivAttr.name)
            else:
                negFootPivAttr = self.footIKCtrl.ctrl.sidePiv
            sidePivNeg.connect('colorIfTrueR', negFootPivAttr, mode='to')
            sidePivNeg.connect('outColorR', '{}.rz'.format(innerPivGrp.name), mode='from')

            sidePivPos = utils.newNode('condition', name='{}footSidePivPos'.format(extraName),
                                        side=self.side, operation=4)
            sidePivPos.connect('firstTerm', self.footIKCtrl.ctrl.sidePiv, mode='to')
            sidePivPos.connect('colorIfTrueR', self.footIKCtrl.ctrl.sidePiv, mode='to')
            sidePivPos.connect('outColorR', '{}.rz'.format(outerPivGrp.name), mode='from')
            ##- controls
            self.footHeelIKCtrl = ctrlFn.ctrl(name='{}footHeelIK'.format(extraName),
                                              side=self.side, guide=rfJntGuides[0], skipNum=True,
                                              parent=outerPivGrp.name,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig, offsetGrpNum=2)
            self.footHeelIKCtrl.modifyShape(color=col['col2'], shape='pringle', mirror=True,
                                            scale=(0.7, 0.7, 0.7), rotation=(-45, 0, 0))
            self.footHeelIKCtrl.lockAttr(attr=['t', 's'])
            self.footHeelIKCtrl.constrain(rfJnts[0])
            self.footToesFKCtrl = ctrlFn.ctrl(name='{}footToesFK'.format(extraName),
                                              side=self.side, guide=jnts[3], skipNum=True,
                                              parent=self.footHeelIKCtrl.ctrlEnd,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig)
            self.footToesFKCtrl.modifyShape(color=col['col3'], shape='arc', mirror=True,
                                            scale=(0.2, 0.2, 0.2),
                                            translation=(3, 1, 0),
                                            rotation=(90, 0, 0))
            self.footToesFKCtrl.constrain(footToesIK.grp)
            self.footToesFKCtrl.lockAttr(['t', 's'])
            self.footToesIKCtrl = ctrlFn.ctrl(name='{}footToesIK'.format(extraName),
                                              side=self.side, guide=rfJntGuides[1], skipNum=True,
                                              parent=self.footHeelIKCtrl.ctrlEnd,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig, offsetGrpNum=2)
            self.footToesIKCtrl.modifyShape(color=col['col2'], shape='pringle', mirror=True,
                                            scale=(0.7, 0.7, 0.7), rotation=(90, 0, 0),
                                            translation=(0, -1, 0))
            self.footToesIKCtrl.lockAttr(attr=['t', 's'])
            self.footToesIKCtrl.constrain(rfBallIK.grp)

            self.footBallIKCtrl = ctrlFn.ctrl(name='{}footBallIK'.format(extraName),
                                              side=self.side, guide=rfJntGuides[2], skipNum=True,
                                              parent=self.footToesIKCtrl.ctrlEnd,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig, offsetGrpNum=2)
            self.footBallIKCtrl.modifyShape(color=col['col2'], shape='pringle', mirror=True,
                                            scale=(0.7, 0.7, 0.7), translation=(0, 1.5, 0))
            self.footBallIKCtrl.lockAttr(attr=['t', 's'])
            cmds.xform(self.footBallIKCtrl.offsetGrps[0].name, ro=(-90, 0, 90))
            self.footBallIKCtrl.constrain(rfAnkleIK.grp)
            ##-- control attributes
            self.footIKCtrl.addAttr('footCtrlTog', nn='Fine Foot Controls', typ='enum',
                                    defaultVal=1, enumOptions=['Hide', 'Show'])
            cmds.connectAttr(self.footIKCtrl.ctrl.footCtrlTog,
                             '{}.v'.format(self.footHeelIKCtrl.rootGrp.name))
            self.footIKCtrl.addAttr('heelRoll', nn='Heel Roll')
            cmds.connectAttr(self.footIKCtrl.ctrl.heelRoll,
                             '{}.rx'.format(self.footHeelIKCtrl.offsetGrps[1].name))
            self.footIKCtrl.addAttr('heelTwist', nn='Heel Twist')
            cmds.connectAttr(self.footIKCtrl.ctrl.heelTwist,
                             '{}.ry'.format(self.footHeelIKCtrl.offsetGrps[1].name))
            self.footIKCtrl.addAttr('ballRoll', nn='Ball Roll')
            cmds.connectAttr(self.footIKCtrl.ctrl.ballRoll,
                             '{}.rx'.format(self.footBallIKCtrl.offsetGrps[1].name))
            self.footIKCtrl.addAttr('toeRoll', nn='Toe Roll')
            cmds.connectAttr(self.footIKCtrl.ctrl.toeRoll,
                             '{}.rx'.format(self.footToesIKCtrl.offsetGrps[1].name))
            self.footIKCtrl.addAttr('toeTwist', nn='Toe Twist')
            cmds.connectAttr(self.footIKCtrl.ctrl.toeTwist,
                             '{}.ry'.format(self.footToesIKCtrl.offsetGrps[1].name))
            ##- constraints
            # cmds.parentConstraint(rfJnts[1], footToesIK.grp, mo=1)
            cmds.parentConstraint(self.footHeelIKCtrl.ctrlEnd, rfToesIK.grp, mo=1)
            cmds.parentConstraint(rfJnts[1], self.footToesFKCtrl.offsetGrps[0].name, mo=1)
            cmds.parentConstraint(rfJnts[2], footBallIK.grp, mo=1)
            cmds.parentConstraint(rfJnts[3], legIK.grp, mo=1)
            if cmds.objExists('{}footGuides{}'.format(self.moduleName, suffix['group'])):
                cmds.delete('{}footGuides{}'.format(self.moduleName, suffix['group']))
            if options['softIK']:
                # fileFn.loadPlugin('mjSoftIK', '.py')
                softIk = utils.newNode('mjSoftIK', name='{}legIK'.format(extraName),
                                       side=self.side)
                jntLoc = utils.newNode('locator', name='{}legJntBase'.format(extraName),
                                       side=self.side, skipNum=True,
                                       parent=cmds.listRelatives(jnts[0], p=1))
                jntLoc.matchTransforms(jnts[0])
                ctrlLoc = utils.newNode('locator', name='{}legIKCtrl'.format(extraName),
                                        side=self.side, skipNum=True,
                                        parent=self.footIKCtrl.ctrlEnd)
                ctrlLoc.matchTransforms(jnts[2])
                softIk.connect('sm', '{}.wm'.format(jntLoc.name), 'to')
                softIk.connect('cm', '{}.wm'.format(ctrlLoc.name), 'to')
                cmds.setAttr('{}.cl'.format(softIk.name), abs(cmds.getAttr('{}.tx'.format(jnts[1]))
                             + cmds.getAttr('{}.tx'.format(jnts[2]))))
                a = utils.newNode('group', name='{}legSoftIK'.format(extraName), side=self.side,
                                  parent=footMechGrp.name)
                a.matchTransforms(legIK.grp)
                softIk.connect('ot', '{}.t'.format(a.name))
                cmds.parentConstraint(a.name, innerPivGrp.name, mo=1)
                self.footIKCtrl.addAttr(name='softIKSep', nn='___   Soft IK', typ='enum',
                                        enumOptions=['___'])
                self.footIKCtrl.addAttr(name='softIKTog', nn='Toggle Soft IK', typ='enum',
                                        enumOptions=['Off', 'On'])
                cmds.connectAttr(self.footIKCtrl.ctrl.softIKTog, '{}.tog'.format(softIk.name))
                self.footIKCtrl.addAttr(name='softIKDist', nn='Soft IK Distance', defaultVal=0.2)
                cmds.connectAttr(self.footIKCtrl.ctrl.softIKDist, '{}.sd'.format(softIk.name))

        if options['FK']:
            ## controls
            self.hipFKCtrl = ctrlFn.ctrl(name='{}hipFK'.format(extraName),
                                         side=self.side, guide=fkJnts[0], skipNum=True,
                                         parent=fkCtrlGrp.name,
                                         scaleOffset=self.rig.scaleOffset,
                                         rig=self.rig)
            self.hipFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                       scale=(0.6, 0.6, 0.6))
            self.hipFKCtrl.lockAttr(attr=['s'])
            self.hipFKCtrl.constrain(fkJnts[0], typ='parent')

            self.kneeFKCtrl = ctrlFn.ctrl(name='{}kneeFK'.format(extraName),
                                          side=self.side, guide=fkJnts[1], skipNum=True,
                                          parent=self.hipFKCtrl.ctrlEnd,
                                          scaleOffset=self.rig.scaleOffset,
                                          rig=self.rig)
            self.kneeFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                        scale=(0.6, 0.6, 0.6))
            self.kneeFKCtrl.lockAttr(attr=['s'])
            self.kneeFKCtrl.constrain(fkJnts[1], typ='parent')

            self.ankleFKCtrl = ctrlFn.ctrl(name='{}ankleFK'.format(extraName),
                                           side=self.side, guide=fkJnts[2], skipNum=True,
                                           parent=self.kneeFKCtrl.ctrlEnd,
                                           scaleOffset=self.rig.scaleOffset,
                                           rig=self.rig)
            self.ankleFKCtrl.modifyShape(color=col['col2'], shape='circle',
                                         scale=(0.6, 0.6, 0.6))
            self.ankleFKCtrl.lockAttr(attr=['s'])
            self.ankleFKCtrl.constrain(fkJnts[2], typ='parent')

            self.footBallFKCtrl = ctrlFn.ctrl(name='{}footBallFK'.format(extraName),
                                              side=self.side, guide=fkJnts[3], skipNum=True,
                                              parent=self.ankleFKCtrl.ctrlEnd,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig)
            self.footBallFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.footBallFKCtrl.lockAttr(attr=['s'])
            self.footBallFKCtrl.constrain(fkJnts[3], typ='parent')
        if options['stretchy']:
            if options['IK']:
                legIK.addStretch(customStretchNode=customNodes,
                                 globalScaleAttr=self.rig.scaleAttr)
                self.footIKCtrl.addAttr('stretchSep', nn='___   Stretch',
                                        typ='enum', enumOptions=['___'])
                self.footIKCtrl.addAttr('stretchySwitch', nn='Stretch Switch',
                                       minVal=0, maxVal=1, defaultVal=1)
                cmds.connectAttr(self.footIKCtrl.ctrl.stretchySwitch,
                                 legIK.stretchToggleAttr)
            if options['FK']:
                print '## add proper stretch to leg fk'

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
        for each in jnts[1:]:
            utils.addJntToSkinJnt(each, self.rig)
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
                                        guide=jnts[1], skipNum=True, parent=headCtrlsGrp.name,
                                        scaleOffset=self.rig.scaleOffset,
                                        rig=self.rig)
            self.headCtrl.modifyShape(shape='sphere', color=col['col3'], mirror=True,
                                      translation=(2, 0, 0))
            self.headCtrl.lockAttr(['s'])
            self.headCtrl.constrain(headIKsGrp.name)
            self.headCtrl.spaceSwitching(ctrlSpaceSwitches, dv=1)
        else:
            self.neckCtrl = ctrlFn.ctrl(name='{}neck'.format(extraName), side=self.side,
                                        guide=jnts[0], skipNum=True, parent=headCtrlsGrp.name,
                                        scaleOffset=self.rig.scaleOffset,
                                        rig=self.rig)
            self.neckCtrl.modifyShape(shape='circle', color=col['col1'], mirror=True,
                                      scale=(0.4, 0.4, 0.4))
            self.neckCtrl.lockAttr(['s', 't'])
            self.neckCtrl.constrain(jnts[0], typ='orient')
            self.headCtrl = ctrlFn.ctrl(name='{}head'.format(extraName), side=self.side,
                                        guide=jnts[1], skipNum=True, parent=self.neckCtrl.ctrlEnd,
                                        scaleOffset=self.rig.scaleOffset,
                                        rig=self.rig)
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

    def create(self, mode, autoOrient=False, customNodes=False, parent=None, thumb=True):
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        jntSuffix = suffix['joint']
        col = utils.getColors(self.side)
        handCtrlGrp = utils.newNode('group', name='{}{}Ctrls'.format(extraName, mode),
                                    side=self.side, parent=self.rig.ctrlsGrp.name, skipNum=True)
        cmds.parentConstraint(parent, handCtrlGrp.name, mo=1)
        if mode == 'hand':
            typ = 'fngr'
            digitsList = ['Index', 'Middle', 'Ring', 'Pinky']
            if thumb:
                digitsList.append('Thumb')
        else:
            typ = 'toe'
            digitsList = ['Big', 'Index', 'Middle', 'Ring', 'Pinky']
            if thumb:
                digitsList[0] = 'Thumb'

        digitCtrls = {}
        palmMults = []
        utils.matchTransforms('{}{}PalmGuide{}'.format(self.moduleName, mode, suffix['locator']),
                              '{}{}Pinky_base{}'.format(self.moduleName, typ, jntSuffix),
                              skipTrans=True)
        palmCtrl = ctrlFn.ctrl(name='{}{}Palm'.format(extraName, typ),
                               side=self.side,
                               guide='{}{}PalmGuide{}'.format(self.moduleName, mode,
                                                              suffix['locator']),
                               deleteGuide=True, skipNum=True, parent=handCtrlGrp.name,
                               scaleOffset=self.rig.scaleOffset,
                               rig=self.rig)
        palmCtrl.modifyShape(shape='sphere', color=col['col2'], scale=(0.3, 0.2, 0.2))
        palmCtrl.lockAttr(['s'])
        for each in digitsList:
            if each == 'Thumb':
                segments = ['metacarpel', 'base', 'lowMid','tip']
                jnts = [
                    '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[0], jntSuffix),
                    '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[1], jntSuffix),
                    '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[2], jntSuffix),
                    '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[3], jntSuffix),
                ]
            else:
                segments = ['metacarpel', 'base', 'lowMid', 'highMid', 'tip']
                jnts = [
                    '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[0], jntSuffix),
                    '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[1], jntSuffix),
                    '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[2], jntSuffix),
                    '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[3], jntSuffix),
                    '{}{}{}_{}{}'.format(self.moduleName, typ, each, segments[4], jntSuffix),
                ]
            for jnt in jnts:
                utils.addJntToSkinJnt(jnt, self.rig)
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
                                   parent=ctrlParent, scaleOffset=self.rig.scaleOffset,
                                   rig=self.rig)
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
                    utils.addJntToSkinJnt(bJnt, self.rig)
                    bTrans = utils.newNode('multDoubleLinear',
                                           name='{}{}{}_{}BTrans'.format(extraName, typ,
                                                                         each, seg),
                                           side=self.side)
                    bTrans.connect('input1', '{}.tx'.format(jnts[i]), mode='to')
                    cmds.setAttr('{}.input2'.format(bTrans.name), 0.95)
                    bTrans.connect('output', '{}.tx'.format(bJnt))
                    ctrl.constrain(prevJnt, typ='aim', aimWorldUpObject=ctrlParent,
                                   mo=True)
                    distNd = utils.newNode('distanceBetween',
                                           name='{}{}{}_{}'.format(extraName, typ, each, seg),
                                           side=self.side)
                    distNd.connect('point1', '{}.wp'.format(prevLoc.name), mode='to')
                    distNd.connect('point2', '{}.wp'.format(loc.name), mode='to')
                    if self.side == 'R':
                        distRevNd = utils.newNode('multDoubleLinear',
                                                  name='{}{}{}_{}Rev'.format(extraName, typ,
                                                                             each, seg),
                                                  side=self.side)
                        distRevNd.connect('input1', '{}.distance'.format(distNd.name), mode='to')
                        cmds.setAttr('{}.input2'.format(distRevNd.name), -1)
                        distRevNd.connect('output', '{}.tx'.format(jnts[i]))
                    else:
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
        palmLocParGrp = utils.newNode('group', name='{}{}PalmLoc'.format(extraName, mode),
                                      side=self.side, parent=parent)
        palmLoc = utils.newNode('locator', name='{}{}Palm'.format(extraName, mode),
                                side=self.side, parent=palmLocParGrp.name)
        palmLocParGrp.matchTransforms(pinkyBaseJnt)
        cmds.makeIdentity(palmLoc.name, a=1, t=1, r=1)
        oConstr = palmCtrl.constrain(palmLoc.name, typ='orient', mo=True)
        palmCtrl.constrain(palmLoc.name, typ='point', mo=True)
        for digit, multNds in zip(digitsList, palmMults):
            orient, trans = multNds
            if digit == 'Thumb' or digit == 'Index' or digit == 'Big':
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
    def __init__(self, rig, extraName='', side='C'):
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, crv=False, jntNum=16, options=defaultBodyOptions.tail,
               autoOrient=False, parent=None):
        jntSuffix = suffix['joint']
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        col = utils.getColors(self.side)
        if crv:
            jnts = utils.createJntsFromCrv(crv, jntNum, side=self.side,
                                           name='{}tail_'.format(extraName))
        else:
            baseJnt = '{}tail_base{}'.format(self.moduleName, jntSuffix)
            endJnt = '{}tail_tip{}'.format(self.moduleName, jntSuffix)
            jnts = utils.getChildrenBetweenObjs(baseJnt, endJnt)
            if autoOrient:
                orientJoints.doOrientJoint(jointsToOrient=jnts, aimAxis=(1, 0, 0),
                                           upAxis=(0, 1, 0), worldUp=(0, 1, 0), guessUp=1)
        if options['IK']:
            for jnt in jnts:
                utils.addJntToSkinJnt(jnt, self.rig)
            miscFn.createLayeredSplineIK(jnts, 'tail', rig=self.rig, side=self.side,
                                         extraName=self.extraName, parent=parent,
                                         dyn=options['dynamics'])
        else:
            cmds.parent(jnts[0], self.rig.skelGrp.name)
            tailCtrls = []
            ctrlParent = self.rig.ctrlsGrp.name
            for i, jnt in enumerate(jnts):
                utils.addJntToSkinJnt(jnt, self.rig)
                ctrlCol = col['col1'] if i % 2 else col['col2']
                ctrl = ctrlFn.ctrl(name='{}tail'.format(extraName), side=self.side, guide=jnt,
                                   rig=self.rig, parent=ctrlParent,
                                   scaleOffset=self.rig.scaleOffset)
                if i < 1:
                    cmds.parentConstraint(parent, ctrl.offsetGrps[0].name, mo=1)
                ctrl.modifyShape(shape='circle', color=ctrlCol)
                ctrl.constrain(jnt)
                ctrl.lockAttr(['t', 's'])
                ctrlParent = ctrl.ctrlEnd
                tailCtrls.append(ctrl)


def getAllChildren(obj):
    jnts = []
    a = cmds.listRelatives(obj, type='joint')
    if a:
        for each in a:
            jnts.append(each)
            jnts.extend(getAllChildren(each))
    return jnts

def renameBodyPartJntGuides(typ, jntNames, side='C', extraName='', chain=False):
    if extraName.endswith('_'):
        extraName = extraName[:-1]
    moduleName = utils.setupBodyPartName(extraName, side)
    partGrp = '{}{}{}'.format(moduleName, typ, suffix['group'])
    partGuidesJnts = getAllChildren(partGrp)
    # partGuidesJnts = cmds.listRelatives(partGrp, type='joint', ad=1)
    # partGuidesJnts.reverse()
    if not chain:
        oldNewNames = zip(partGuidesJnts, jntNames)
    else:
        oldNewNames = []
        for i, each in enumerate(partGuidesJnts):
            if i == 0:
                oldNewNames.append((each, jntNames[0]))
            elif i == (len(partGuidesJnts)-1):
                oldNewNames.append((each, jntNames[-1]))
            else:
                oldNewNames.append((each, jntNames[1]))
    for each, name in oldNewNames:
        cmds.select(each)
        utils.renameSelection(name, side)

def renameBodyPartLocGuides(typ, locNames, side='C', extraName=''):
    if extraName.endswith('_'):
        extraName = extraName[:-1]
    moduleName = utils.setupBodyPartName(extraName, side)
    partGrp = '{}{}{}'.format(moduleName, typ, suffix['group'])
    locators = cmds.listRelatives(partGrp)[1:]
    for each, name in zip(locators, locNames):
        cmds.select(each)
        utils.renameSelection(name, side)
    return locators

def renameLegGuides(side='C', extraName=''):
    moduleName = utils.setupBodyPartName(extraName, side)
    if extraName:
        extraName = '{}_'.format(extraName)
    legGrp = '{}leg{}'.format(moduleName, suffix['group'])
    jntNameList = [
        '{}hip'.format(extraName),
        '{}knee'.format(extraName),
        '{}ankle'.format(extraName),
        '{}footBall'.format(extraName),
        '{}footToes'.format(extraName),
        '{}toeBig_metacarpel'.format(extraName),
        '{}toeBig_base'.format(extraName),
        '{}toeBig_lowMid'.format(extraName),
        '{}toeBig_highMid'.format(extraName),
        '{}toeBig_tip'.format(extraName),
        '{}toeIndex_metacarpel'.format(extraName),
        '{}toeIndex_base'.format(extraName),
        '{}toeIndex_lowMid'.format(extraName),
        '{}toeIndex_highMid'.format(extraName),
        '{}toeIndex_tip'.format(extraName),
        '{}toeMiddle_metacarpel'.format(extraName),
        '{}toeMiddle_base'.format(extraName),
        '{}toeMiddle_lowMid'.format(extraName),
        '{}toeMiddle_highMid'.format(extraName),
        '{}toeMiddle_tip'.format(extraName),
        '{}toeRing_metacarpel'.format(extraName),
        '{}toeRing_base'.format(extraName),
        '{}toeRing_lowMid'.format(extraName),
        '{}toeRing_highMid'.format(extraName),
        '{}toeRing_tip'.format(extraName),
        '{}toePinky_metacarpel'.format(extraName),
        '{}toePinky_base'.format(extraName),
        '{}toePinky_lowMid'.format(extraName),
        '{}toePinky_highMid'.format(extraName),
        '{}toePinky_tip'.format(extraName),
    ]
    locList = [
        '{}legPV'.format(extraName),
        '{}legSettings'.format(extraName),
    ]
    if len(cmds.listRelatives(legGrp)) > 4:
        locList.append('{}footPalmGuide'.format(extraName))
    renameBodyPartJntGuides('leg', jntNameList, side, extraName)

    locators = renameBodyPartLocGuides('leg', locList, side, extraName)

    footGuides = cmds.listRelatives(locators[-1])
    cmds.select(locators[-1])
    utils.renameSelection('{}footGuides'.format(extraName), side)
    footGuideNames = [
        '{}footCtrlGuide'.format(extraName),
        '{}footHeelGuide'.format(extraName),
        '{}footToesGuide'.format(extraName),
        '{}footInnerGuide'.format(extraName),
        '{}footOuterGuide'.format(extraName),
    ]
    for each, name in zip(footGuides, footGuideNames):
        cmds.select(each)
        utils.renameSelection(name, side)

    cmds.parent(cmds.listRelatives(legGrp), w=1)
    cmds.delete(legGrp)
    cmds.select(cl=1)

def renameArmGuides(side='C', extraName=''):
    moduleName = utils.setupBodyPartName(extraName, side)
    if extraName:
        extraName = '{}_'.format(extraName)
    armGrp = '{}arm{}'.format(moduleName, suffix['group'])
    jntNameList = [
        '{}clavicle'.format(extraName),
        '{}shoulder'.format(extraName),
        '{}elbow'.format(extraName),
        '{}wrist'.format(extraName),
        '{}handEnd'.format(extraName),
        '{}fngrThumb_metacarpel'.format(extraName),
        '{}fngrThumb_base'.format(extraName),
        '{}fngrThumb_lowMid'.format(extraName),
        '{}fngrThumb_tip'.format(extraName),
        '{}fngrIndex_metacarpel'.format(extraName),
        '{}fngrIndex_base'.format(extraName),
        '{}fngrIndex_lowMid'.format(extraName),
        '{}fngrIndex_highMid'.format(extraName),
        '{}fngrIndex_tip'.format(extraName),
        '{}fngrMiddle_metacarpel'.format(extraName),
        '{}fngrMiddle_base'.format(extraName),
        '{}fngrMiddle_lowMid'.format(extraName),
        '{}fngrMiddle_highMid'.format(extraName),
        '{}fngrMiddle_tip'.format(extraName),
        '{}fngrRing_metacarpel'.format(extraName),
        '{}fngrRing_base'.format(extraName),
        '{}fngrRing_lowMid'.format(extraName),
        '{}fngrRing_highMid'.format(extraName),
        '{}fngrRing_tip'.format(extraName),
        '{}fngrPinky_metacarpel'.format(extraName),
        '{}fngrPinky_base'.format(extraName),
        '{}fngrPinky_lowMid'.format(extraName),
        '{}fngrPinky_highMid'.format(extraName),
        '{}fngrPinky_tip'.format(extraName),
    ]
    locList = [
        '{}armPV'.format(extraName),
        '{}armSettings'.format(extraName),
        '{}handPalmGuide'.format(extraName),
    ]
    renameBodyPartJntGuides('arm', jntNameList, side, extraName)
    renameBodyPartLocGuides('arm', locList, side, extraName)

    cmds.parent(cmds.listRelatives(armGrp), w=1)
    cmds.delete(armGrp)
    cmds.select(cl=1)

def renameSpineGuides(side='C', extraName=''):
    moduleName = utils.setupBodyPartName(extraName, side)
    if extraName:
        extraName += '_'
    spineGrp = '{}spine{}'.format(moduleName, suffix['group'])
    jntNameList = [
        '{}spine_base'.format(extraName),
        '{}spine_##'.format(extraName),
        '{}spine_end'.format(extraName),
    ]
    renameBodyPartJntGuides('spine', jntNameList, chain=True)
    cmds.parent(cmds.listRelatives(spineGrp), w=1)
    cmds.delete(spineGrp)
    cmds.select(cl=1)

def renameHeadGuides(side='C', extraName=''):
    moduleName = utils.setupBodyPartName(extraName, side)
    if extraName:
        extraName += '_'
    headGrp = '{}head{}'.format(moduleName, suffix['group'])
    jntNameList = [
        '{}head'.format(extraName),
        '{}headEnd'.format(extraName),
    ]
    renameBodyPartJntGuides('head', jntNameList)
    cmds.parent(cmds.listRelatives(headGrp), w=1)
    cmds.delete(headGrp)
    cmds.select(cl=1)

def renameTailGuides(side='C', extraName=''):
    moduleName = utils.setupBodyPartName(extraName, side)
    if extraName:
        extraName += '_'
    tailGrp = '{}tail{}'.format(moduleName, suffix['group'])
    jntNameList = [
        '{}tail_base'.format(extraName),
        '{}tail_##'.format(extraName),
        '{}tail_tip'.format(extraName),
    ]
    renameBodyPartJntGuides('tail', jntNameList, chain=True)
    childs = cmds.listRelatives(tailGrp)
    if len(childs) > 1:
        cmds.select(childs[1])
        utils.renameSelection('{}tailSettings'.format(extraName), side)
    cmds.parent(cmds.listRelatives(tailGrp), w=1)
    cmds.delete(tailGrp)
    cmds.select(cl=1)

def renameAllBodyPartGuides():
    cmds.select(cmds.ls(l=1))
    sceneMObjs = apiFn.getSelectionAsMObjs()
    for each in sceneMObjs:
        lN, sN = apiFn.getPath(each, returnString=True)
        side = sN[0]
        if len(sN.split('_')) > 3:
            extraName = sN.split('_', 2)[1]
        else:
            extraName = ''
        if '_leg{}'.format(suffix['group']) in sN:
            renameLegGuides(side, extraName)
        elif '_arm{}'.format(suffix['group']) in sN:
            renameArmGuides(side, extraName)
        elif '_spine{}'.format(suffix['group']) in sN:
            renameSpineGuides(side, extraName)
        elif '_head{}'.format(suffix['group']) in sN:
            renameHeadGuides(side, extraName)
        elif '_tail{}'.format(suffix['group']) in sN:
            renameTailGuides(side, extraName)