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
reload(suffixDictionary)

class armModule:
    def __init__(self, rig, extraName='', side='C'):
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, options=defaultBodyOptions.arm, autoOrient=False, customNodes=False):
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        jntSuffix = suffix['joint']
        jnts = [
            '{}shoulder{}'.format(self.moduleName, jntSuffix),
            '{}elbow{}'.format(self.moduleName, jntSuffix),
            '{}wrist{}'.format(self.moduleName, jntSuffix),
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
            orientJoints.doOrientJoint(jointsToOrient=jnts, aimAxis=(1, 0, 0), upAxis=(0, 1, 0),
                                       worldUp=(0, 1, 0), guessUp=1)
        ## clav stuff
        clavIK = ikFn.ik(clavJnts[0], clavJnts[1],
                         name='{}clavicleIK'.format(extraName), side=self.side)
        clavIK.createIK(parent=armMechGrp.name)
        # cmds.parentConstraint(clavJnts[1], clavChild, mo=1)
        self.clavIKCtrl = ctrlFn.ctrl(name='{}clavicle'.format(extraName), side=self.side,
                                      guide=clavJnts[0], skipNum=True, parent=armCtrlsGrp.name)
        self.clavIKCtrl.modifyShape(shape='pringle', color=col['col2'])
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
            self.settingCtrl.makeSettingCtrl(ikfk=True, parent=jnts[-1])
            ##- parent constraints
            for jnt, ikJnt, fkJnt in zip(jnts, ikJnts, fkJnts):
                parConstr = cmds.parentConstraint(ikJnt, fkJnt, jnt)
                cmds.connectAttr(self.settingCtrl.ctrl.ikfkSwitch,
                                 '{}.{}W1'.format(parConstr[0], fkJnt))
                swRev = utils.newNode('reverse', name='{}armIKFKSw'.format(self.extraName),
                                      side=self.side)
                cmds.connectAttr(self.settingCtrl.ctrl.ikfkSwitch,
                                 '{}.inputX'.format(swRev.name))
                cmds.connectAttr('{}.outputX'.format(swRev.name), '{}.{}W0'.format(parConstr[0], ikJnt))
            ##- control vis grps
            ikCtrlGrp = utils.newNode('group', name='{}armIKCtrls'.format(extraName), side=self.side,
                                      parent=self.clavIKCtrl.ctrlEnd, skipNum=True)
            fkCtrlGrp = utils.newNode('group', name='{}armFKCtrls'.format(extraName), side=self.side,
                                      parent=self.clavIKCtrl.ctrlEnd, skipNum=True)
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
        ## ik
        if options['IK']:
            ##- mechanics
            armIK = ikFn.ik(ikJnts[0], ikJnts[2],
                            name='{}armIK'.format(extraName), side=self.side)
            armIK.createIK(parent=armMechGrp.name)
            ##- controls
            self.handIKCtrl = ctrlFn.ctrl(name='{}handIK'.format(extraName), side=self.side,
                                          guide=ikJnts[2], skipNum=True, parent=ikCtrlGrp.name)
            self.handIKCtrl.modifyShape(shape='cube', color=col['col1'], scale=(0.6, 0.6, 0.6))
            self.handIKCtrl.lockAttr(attr=['s'])
            self.handIKCtrl.constrain(armIK.grp)
            ##-- PoleVector
            pvGuide = '{}armPV{}'.format(self.moduleName, suffix['locator'])
            cmds.delete(cmds.aimConstraint(ikJnts[1], pvGuide))
            self.pvCtrl = ctrlFn.ctrl(name='{}PV'.format(extraName), side=self.side,
                                      guide=pvGuide,
                                      skipNum=True, deleteGuide=True, parent=ikCtrlGrp.name)
            self.pvCtrl.modifyShape(shape='crossPyramid', color=col['col1'], rotation=(0, 180, 0),
                                    scale=(0.4, 0.4, 0.4))
            self.pvCtrl.constrain(armIK.hdl, typ='poleVector')
            print '## add space switch for arm poleVector'

            ## autoClav
            if options['autoClav']:
                print '## do auto clav'
        ## fk
        if options['FK']:
            ##- controls
            self.shoulderFKCtrl = ctrlFn.ctrl(name='{}shoulderFK'.format(extraName),
                                              side=self.side, guide=fkJnts[0], skipNum=True,
                                              parent=fkCtrlGrp.name)
            self.shoulderFKCtrl.modifyShape(color=col['col1'], shape='circle', scale=(0.6, 0.6, 0.6))
            self.shoulderFKCtrl.lockAttr(attr=['s'])
            self.shoulderFKCtrl.constrain(fkJnts[0], typ='parent')

            self.elbowFKCtrl = ctrlFn.ctrl(name='{}elbowFK'.format(extraName), side=self.side,
                                           guide=fkJnts[1], skipNum=True,
                                           parent=self.shoulderFKCtrl.ctrlEnd)
            self.elbowFKCtrl.modifyShape(color=col['col2'], shape='circle', scale=(0.6, 0.6, 0.6))
            self.elbowFKCtrl.lockAttr(attr=['s'])
            self.elbowFKCtrl.constrain(fkJnts[1], typ='parent')

            self.wristFKCtrl = ctrlFn.ctrl(name='{}wristFK'.format(extraName), side=self.side,
                                          guide=fkJnts[2], skipNum=True,
                                          parent=self.elbowFKCtrl.ctrlEnd)
            self.wristFKCtrl.modifyShape(color=col['col1'], shape='circle', scale=(0.6, 0.6, 0.6))
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
                print '## add proper stretch to fk'
        ## softIK
        if options['softIK']:
            print '## do soft IK'
        ## ribbon
        if options['ribbon']:
            print '## do ribbon'
        return True



class legModule:
    def __init__(self):
        print '## leg'


class spineModule:
    def __init__(self):
        print '## spine'


class headModule:
    def __init__(self):
        print '## head'


class digitsModule:
    def __init__(self):
        print '## digits'


class tailModule:
    def __init__(self):
        print '## tail'
