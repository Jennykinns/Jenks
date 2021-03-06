import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ikFunctions as ikFn
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules import fileFunctions as fileFn
from Jenks.scripts.rigModules import mechFunctions as mechFn
from Jenks.scripts.rigModules import apiFunctions as apiFn
from Jenks.scripts.rigModules.suffixDictionary import suffix
from Jenks.scripts.rigModules import defaultBodyOptions
from Jenks.scripts.rigModules import orientJoints

reload(orientJoints)
reload(utils)
reload(ikFn)
reload(ctrlFn)
reload(mechFn)
reload(defaultBodyOptions)


class armModule:

    """ Create an arm rig. """

    def __init__(self, rig, extraName='', side='C'):
        """ Setup the initial variables to use when creating the arm.
        [Args]:
        rig (class) - The rig class to use
        extraName (string) - The extra name of the module
        side (string) - The side of the module ('C', 'R' or 'L')
        """
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, options={}, autoOrient=False,
               customNodes=False, parent=None):
        """ Create the arm rig.
        [Args]:
        options (dictionary) - A dictionary of options for the arm
        autoOrient (bool) - Toggles auto orienting the joints
        customNodes (bool) - Toggles the use of custom nodes
        parent (string) - The name of the parent
        [Returns]
        True
        """
        overrideOptions = options
        options = defaultBodyOptions.arm
        options.update(overrideOptions)

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
        # cmds.setAttr('{}.it'.format(armMechGrp.name), 0)
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
            # orientJoints.doOrientJoint(jointsToOrient=jnts[1:],
            #                            aimAxis=(1 if not self.side == 'R' else -1, 0, 0),
            #                            upAxis=(0, 1, 0),
            #                            worldUp=(0, 1, 0),
            #                            guessUp=1)
            utils.orientJoints(jnts[1:], aimAxis=(1 if not self.side == 'R' else -1, 0, 0))

        for jnt in jnts:
            utils.addJntToSkinJnt(jnt, self.rig)

        ## ik/fk
        if options['IK'] and options['FK']:
            clavChild = armMechSkelGrp.name
            ikJnts, fkJnts, jnts, ikCtrlGrp, fkCtrlGrp = mechFn.ikfkMechanics(self, extraName, jnts,
                                                                       armMechSkelGrp, armCtrlsGrp,
                                                                       moduleType='arm', rig=self.rig)
        else:
            ikJnts = jnts
            fkJnts = jnts
            ikCtrlGrp = armCtrlsGrp
            fkCtrlGrp = armCtrlsGrp
            # clavChild = jnts[0]

        self.ikCtrlGrp = ikCtrlGrp
        self.fkCtrlGrp = fkCtrlGrp

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
                cmds.xform(tmpJnt, r=1, ro=(180, 0, 0))
                self.ikCtrl = ctrlFn.ctrl(name='{}handIK'.format(extraName), side=self.side,
                                          guide=tmpJnt, skipNum=True, parent=ikCtrlGrp.name,
                                          deleteGuide=True, scaleOffset=self.rig.scaleOffset,
                                          rig=self.rig)
            else:
                self.ikCtrl = ctrlFn.ctrl(name='{}handIK'.format(extraName), side=self.side,
                                              guide=ikJnts[3], skipNum=True, parent=ikCtrlGrp.name,
                                              scaleOffset=self.rig.scaleOffset, rig=self.rig)
            self.ikCtrl.modifyShape(shape='cube', color=col['col1'], scale=(0.6, 0.6, 0.6))
            self.ikCtrl.lockAttr(attr=['s'])
            if options['softIK']:
                # fileFn.loadPlugin('mjSoftIK', '.py')
                softIk = utils.newNode('mjSoftIK', name='{}armIK'.format(extraName),
                                       side=self.side)
                jntLoc = utils.newNode('locator', name='{}armJntBase'.format(extraName),
                                       side=self.side, skipNum=True,
                                       parent=cmds.listRelatives(jnts[1], p=1))
                jntLoc.matchTransforms(jnts[1])
                softIk.connect('sm', '{}.wm'.format(jntLoc.name), 'to')
                softIk.connect('cm', '{}.wm'.format(self.ikCtrl.ctrlEnd), 'to')
                cmds.setAttr('{}.cl'.format(softIk.name), abs(cmds.getAttr('{}.tx'.format(jnts[2]))
                             + cmds.getAttr('{}.tx'.format(jnts[3]))))
                softIk.connect('ot', '{}.t'.format(armIK.grp))
                self.ikCtrl.addAttr(name='softIKSep', nn='___   Soft IK', typ='enum',
                                        enumOptions=['___'])
                self.ikCtrl.addAttr(name='softIKTog', nn='Toggle Soft IK', typ='enum',
                                        enumOptions=['Off', 'On'])
                cmds.connectAttr(self.ikCtrl.ctrl.softIKTog, '{}.tog'.format(softIk.name))
                self.ikCtrl.addAttr(name='softIKDist', nn='Soft IK Distance', defaultVal=0.2)
                cmds.connectAttr(self.ikCtrl.ctrl.softIKDist, '{}.sd'.format(softIk.name))
            else:
                self.ikCtrl.constrain(armIK.grp)
            self.ikCtrl.constrain(handIK.grp)
            self.ikCtrl.spaceSwitching([self.rig.globalCtrl.ctrl.name,
                                            parent],
                                           # niceNames=['World', 'Chest', 'Clavicle'],
                                           dv=0)
            ##-- PoleVector
            pvGuide = '{}armPV{}'.format(self.moduleName, suffix['locator'])
            mechFn.poleVector(pvGuide, jnts[2], self, extraName, 'arm', self.moduleName, armIK)

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
                self.ikCtrl.constrain(dupeArmIK.grp)
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
                                              parent=fkCtrlGrp.name, rig=self.rig,
                                              scaleOffset=self.rig.scaleOffset, gimbal=True)
            self.shoulderFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.shoulderFKCtrl.lockAttr(attr=['s'])
            self.shoulderFKCtrl.spaceSwitching(parents=[parent, self.clavFKCtrl.ctrlEnd])
            self.shoulderFKCtrl.constrain(fkJnts[1], typ='parent')

            self.elbowFKCtrl = ctrlFn.ctrl(name='{}elbowFK'.format(extraName), side=self.side,
                                           guide=fkJnts[2], skipNum=True,
                                           parent=self.shoulderFKCtrl.ctrlEnd,
                                           scaleOffset=self.rig.scaleOffset,
                                           rig=self.rig, gimbal=True)
            self.elbowFKCtrl.modifyShape(color=col['col2'], shape='circle',
                                         scale=(0.6, 0.6, 0.6))
            self.elbowFKCtrl.lockAttr(attr=['s'])
            self.elbowFKCtrl.constrain(fkJnts[2], typ='parent')

            self.wristFKCtrl = ctrlFn.ctrl(name='{}wristFK'.format(extraName), side=self.side,
                                          guide=fkJnts[3], skipNum=True,
                                          parent=self.elbowFKCtrl.ctrlEnd,
                                          scaleOffset=self.rig.scaleOffset,
                                          rig=self.rig, gimbal=True)
            self.wristFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                         scale=(0.6, 0.6, 0.6))
            self.wristFKCtrl.lockAttr(attr=['s'])
            self.wristFKCtrl.constrain(fkJnts[3], typ='parent')
        ## stretchy
        if options['stretchy']:
            if options['IK']:
                armIK.addStretch(customStretchNode=customNodes,
                                 globalScaleAttr='{}.sy'.format(self.rig.globalCtrl.ctrl.name))
                self.ikCtrl.addAttr('stretchSep', nn='___   Stretch',
                                        typ='enum', enumOptions=['___'])
                self.ikCtrl.addAttr('stretchySwitch', nn='Stretch Switch',
                                         minVal=0, maxVal=1, defaultVal=1)
                cmds.connectAttr(self.ikCtrl.ctrl.stretchySwitch, armIK.stretchToggleAttr)
            if options['FK']:
                print '## add proper stretch to arm fk'
        ## ribbon
        if options['ribbon']:
            mechFn.bendyJoints(jnts[1], jnts[2], jnts[3], 'arm', self)
        else:
            ## add forearm twist
            twistJnt = utils.newNode('joint', name='{}forearmTwist'.format(extraName),
                                     side=self.side)
            twistJnt.parent(jnts[2], relative=True)
            utils.addJntToSkinJnt(twistJnt.name, rig=self.rig)
            cmds.pointConstraint(jnts[2], jnts[3], twistJnt.name)
            orConstr = cmds.orientConstraint(jnts[2], jnts[3], twistJnt.name, sk=['y', 'z'])
            cmds.setAttr('{}.interpType'.format(orConstr[0]), 2)

        ## arm parent stuff
        if parent:
            armParentLoc = utils.newNode('locator', name='{}armParent'.format(extraName),
                                         side=self.side, skipNum=True, parent=parent)
            armParentLoc.matchTransforms(jnts[0])
            # cmds.parentConstraint(armParentLoc.name, jnts[0], mo=1)
            # cmds.parentConstraint(armParentLoc.name, self.clavIKCtrl.rootGrp.name, mo=1)
        return True


class spineModule:

    """ Create a spine rig. """

    def __init__(self, rig, extraName='', side='C'):
        """ Setup the ititial variables to use when creating the spine.
        [Args]:
        rig (class) - The rig class to use
        extraName (string) - The extraName of the module
        side (string) - The side of the module ('C', 'R' or 'L')
        """
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def createFromJnts(self, autoOrient=False, extraCtrl=False):
        """ Create the spine from joints.
        [Args]:
        autoOrient (bool) - Toggles auto orienting the joints
        """
        jntSuffix = suffix['joint']
        spineJnts = utils.getChildrenBetweenObjs('{}spine_base{}'.format(self.moduleName,
                                                                        jntSuffix),
                                                 '{}spine_end{}'.format(self.moduleName,
                                                                       jntSuffix))
        self.spineMech(autoOrient, spineJnts, extraCtrl=extraCtrl)


    def createFromCrv(self, crv, numOfJnts=7, extraCtrl=False):
        """ Create the spine from a curve.
        [Args]:
        crv (string) - The name of the curve to create from
        numOfJnts (int) - The amount of joints to create for the spine
        """
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
        self.spineMech(autoOrient=False, spineJnts=spineJnts, crv=crv, extraCtrl=extraCtrl)


    def spineMech(self, autoOrient, spineJnts, crv=None, extraCtrl=False):
        """ Create the mechanics for the spine.
        [Args]:
        autoOrient (bool) - Toggles auto orienting the joints
        spineJnts (list)(string) - A list of the names of the joints to
                                   create the mechanics on
        crv (string) - The curve to use for the spline IK (if None a
                       new curve will be made)
        """
        jntSuffix = suffix['joint']
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        col = utils.getColors('C')
        for each in spineJnts:
            utils.addJntToSkinJnt(each, self.rig)

        spineMechGrp = utils.newNode('group', name='{}spineMech'.format(self.extraName),
                                     side=self.side, skipNum=True, parent=self.rig.mechGrp.name)
        # cmds.setAttr('{}.it'.format(spineMechGrp.name), 0)
        ## orient joints
        if autoOrient:
            # orientJoints.doOrientJoint(jointsToOrient=spineJnts, aimAxis=(1, 0, 0),
            #                            upAxis=(0, 1, 0), worldUp=(0, 1, 0), guessUp=1)
            utils.orientJoints(spineJnts)
        cmds.parent(spineJnts[0], self.rig.skelGrp.name)
        chestJnt = spineJnts[len(spineJnts)/2]
        self.armJnt = spineJnts[int(len(spineJnts)-(len(spineJnts)/3.5))]
        self.baseJnt = spineJnts[0]
        self.endJnt = spineJnts[-1]
        ## splineIK
        spineIK = ikFn.ik(spineJnts[0], spineJnts[-1], name='spineIK', side=self.side)
        if crv:
            spineIK.createSplineIK(parent=spineMechGrp.name, crv=crv)
        else:
            spineIK.createSplineIK(parent=spineMechGrp.name)
        spineIK.addStretch(globalScaleAttr=self.rig.scaleAttr, mode='length', operation='both')
        ## bind jnts
        hipBindJnt = utils.newNode('joint', side=self.side, parent=spineMechGrp.name,
                                    name='{}spineIK_hipsBind'.format(extraName))
        hipBindJnt.matchTransforms(spineJnts[0])
        chestBindJnt = utils.newNode('joint', side=self.side, parent=spineMechGrp.name,
                                     name='{}spineIK_chestBind'.format(extraName))
        chestBindJnt.matchTransforms(chestJnt)
        upperChestPar = chestBindJnt.name if not extraCtrl else spineMechGrp.name
        upperChestBindJnt = utils.newNode('joint', side=self.side, parent=upperChestPar,
                                          name='{}spineIK_upperChestBind'.format(extraName))
        upperChestBindJnt.matchTransforms(self.endJnt)
        ## skin bindJnts to crv
        spineSkin = cmds.skinCluster(hipBindJnt.name, chestBindJnt.name, upperChestBindJnt.name, spineIK.crv)
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
        if not extraCtrl:
            cmds.skinCluster(spineSkin, e=1, ri=upperChestBindJnt.name)
            cmds.delete(upperChestBindJnt.name)
            self.upperChestCtrl = None
            endSpineLocPar = chestBindJnt.name
        else:
            self.upperChestCtrl = ctrlFn.ctrl(name='{}upperChest'.format(extraName),
                                              side=self.side, guide=upperChestBindJnt.name,
                                              skipNum=True, parent=self.bodyCtrl.ctrlEnd,
                                              scaleOffset=self.rig.scaleOffset, rig=self.rig)
            self.upperChestCtrl.modifyShape(shape='sphere', color=col['col1'])
            self.upperChestCtrl.spaceSwitching([self.chestCtrl.ctrlEnd, self.bodyCtrl.ctrlEnd],
                                               ['Chest', 'Body'])
            self.upperChestCtrl.lockAttr(['s'])
            self.upperChestCtrl.constrain(upperChestBindJnt.name)
            endSpineLocPar = upperChestBindJnt.name
        ## IK Adv twist
        spineIKStartLoc = utils.newNode('locator', name='{}spineStart'.format(extraName),
                                      side=self.side, parent=hipBindJnt.name)
        spineIKStartLoc.matchTransforms(spineJnts[0])
        spineIKEndLoc = utils.newNode('locator', name='{}spineEnd'.format(extraName),
                                      side=self.side, parent=endSpineLocPar)
        spineIKEndLoc.matchTransforms(spineJnts[-1])
        if extraCtrl:
            orient = cmds.orientConstraint(upperChestBindJnt.name, chestBindJnt.name,
                                           spineIKEndLoc.name, mo=1)
            cmds.setAttr('{}.{}W1'.format(orient[0], chestBindJnt.name), 0.5)
            cmds.setAttr('{}.interpType'.format(orient[0]), 2)
        spineIK.advancedTwist(spineIKStartLoc.name, spineIKEndLoc.name, wuType=4)
        print '## add world switching to spine ctrls?'


class legModule:

    """ Create a leg rig. """

    def __init__(self, rig, extraName='', side='C'):
        """ Setup the initial variables to use when creating the leg.
        [Args]:
        rig (class) - The rig class to use
        extraName (string) - The extra name of the module
        side (string) - The side of the module ('C', 'R' or 'L')
        """
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, options={}, autoOrient=False, customNodes=False,
               parent=None):
        """ Create the leg rig.
        [Args]:
        options (dictionary) - A dictionary of options for the leg
        autoOrient (bool) - Toggles auto orienting the joints
        customNodes (bool) - Toggles the use of custom nodes
        parent (string) - The name of the parent
        """
        overrideOptions = options
        options = defaultBodyOptions.leg
        options.update(overrideOptions)

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
        # cmds.setAttr('{}.it'.format(legMechGrp.name), 0)
        if options['IK']:
            legMechSkelGrp = utils.newNode('group', name='{}legMechSkel'.format(extraName),
                                           side=self.side, skipNum=True, parent=legMechGrp.name)
        if autoOrient:
            # orientJoints.doOrientJoint(jointsToOrient=jnts,
            #                            aimAxis=(1 if not self.side == 'R' else -1, 0, 0),
            #                            upAxis=(0, 1, 0),
            #                            worldUp=(0, 1 if not self.side == 'R' else -1, 0),
            #                            guessUp=1)
            utils.orientJoints(jnts, aimAxis=(1 if not self.side == 'R' else -1, 0, 0))

        for jnt in jnts:
            utils.addJntToSkinJnt(jnt, self.rig)

        ## ik/fk
        if options['IK'] and options['FK']:
            ikJnts, fkJnts, jnts, ikCtrlGrp, fkCtrlGrp = mechFn.ikfkMechanics(self, extraName, jnts,
                                                                              legMechSkelGrp,
                                                                              legCtrlsGrp,
                                                                              moduleType='leg',
                                                                              rig=self.rig)
        else:
            ikJnts = jnts
            fkJnts = jnts
            ikCtrlGrp = legCtrlsGrp
            fkCtrlGrp = legCtrlsGrp

        self.footJnt = jnts[3]
        self.ikCtrlGrp = ikCtrlGrp
        self.fkCtrlGrp = fkCtrlGrp

        if options['IK']:
            ## mechanics
            legIK = ikFn.ik(ikJnts[0], ikJnts[2], name='{}legIK'.format(extraName),
                            side=self.side)
            legIK.createIK(parent=legMechGrp.name)
            ## controls
            footIKGuide = '{}footCtrlGuide{}'.format(self.moduleName, suffix['locator'])
            useGuideLoc = cmds.objExists(footIKGuide)
            if not useGuideLoc:
                footIKGuide = ikJnts[2]
            self.ikCtrl = ctrlFn.ctrl(name='{}footIK'.format(extraName), side=self.side,
                                          guide=footIKGuide, skipNum=True, parent=ikCtrlGrp.name,
                                          deleteGuide=True if useGuideLoc else False,
                                          scaleOffset=self.rig.scaleOffset, rig=self.rig)
            self.ikCtrl.modifyShape(shape='foot', color=col['col1'], scale=(2, 2, 2))
            self.ikCtrl.lockAttr(attr=['s'])
            # space switching
            ## polevector ctrl
            # pvGuide = '{}{}PV{}'.format(self.moduleName, limbType, suffix['locator'])
            pvGuide = '{}legPV{}'.format(self.moduleName, suffix['locator'])
            mechFn.poleVector(pvGuide, jnts[1], self, extraName, 'leg', self.moduleName, legIK)
            ## foot mechanics
            footMechGrp = utils.newNode('group', name='{}footMech'.format(extraName),
                                        side=self.side, parent=legMechGrp.name)
            ##- iks
            footBallIK = ikFn.ik(ikJnts[2], ikJnts[3], side=self.side,
                                 name='{}footBallIK'.format(extraName))
            footBallIK.createIK(parent=footMechGrp.name)
            footToesIK = ikFn.ik(ikJnts[3], ikJnts[4], side=self.side,
                                 name='{}footToesIK'.format(extraName))
            footToesIK.createIK(parent=footMechGrp.name)
            ##- rf joints
            rfMechGrp = utils.newNode('group', name='{}RFMech'.format(extraName),
                                      side=self.side, parent=footMechGrp.name)
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
            self.ikCtrl.addAttr('footRollsSep', nn='___   Foot Rolls', typ='enum',
                                    enumOptions=['___'])
            innerPivGrp = utils.newNode('group', name='{}footInnerPivot'.format(extraName),
                                        parent=self.ikCtrl.ctrlEnd, side=self.side,
                                        skipNum=True)
            innerPivGrp.matchTransforms('{}footInnerGuide{}'.format(self.moduleName, suffix['locator']))
            outerPivGrp = utils.newNode('group', name='{}footOuterPivot'.format(extraName),
                                        parent=innerPivGrp.name, side=self.side, skipNum=True)
            outerPivGrp.matchTransforms('{}footOuterGuide{}'.format(self.moduleName, suffix['locator']))
            self.ikCtrl.addAttr('sidePiv', nn='Side Pivot')
            sidePivNeg = utils.newNode('condition', name='{}footSidePivNeg'.format(extraName),
                                        side=self.side, operation=3)
            sidePivNeg.connect('firstTerm', self.ikCtrl.ctrl.sidePiv, mode='to')
            if self.side == 'R':
                negFootPivAttr = utils.newNode('reverse',
                                               name='{}footSidePivNeg'.format(extraName),
                                               side=self.side)
                negFootPivAttr.connect('inputX', self.ikCtrl.ctrl.sidePiv, mode='to')
                negFootPivAttr = '{}.outputX'.format(negFootPivAttr.name)
            else:
                negFootPivAttr = self.ikCtrl.ctrl.sidePiv
            sidePivNeg.connect('colorIfTrueR', negFootPivAttr, mode='to')
            sidePivNeg.connect('outColorR', '{}.rz'.format(innerPivGrp.name), mode='from')

            sidePivPos = utils.newNode('condition', name='{}footSidePivPos'.format(extraName),
                                        side=self.side, operation=4)
            sidePivPos.connect('firstTerm', self.ikCtrl.ctrl.sidePiv, mode='to')
            sidePivPos.connect('colorIfTrueR', self.ikCtrl.ctrl.sidePiv, mode='to')
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
            self.ikCtrl.addAttr('footCtrlTog', nn='Fine Foot Controls', typ='enum',
                                    defaultVal=1, enumOptions=['Hide', 'Show'])
            cmds.connectAttr(self.ikCtrl.ctrl.footCtrlTog,
                             '{}.v'.format(self.footHeelIKCtrl.rootGrp.name))
            self.ikCtrl.addAttr('heelRoll', nn='Heel Roll')
            cmds.connectAttr(self.ikCtrl.ctrl.heelRoll,
                             '{}.rx'.format(self.footHeelIKCtrl.offsetGrps[1].name))
            self.ikCtrl.addAttr('heelTwist', nn='Heel Twist')
            cmds.connectAttr(self.ikCtrl.ctrl.heelTwist,
                             '{}.ry'.format(self.footHeelIKCtrl.offsetGrps[1].name))
            self.ikCtrl.addAttr('ballRoll', nn='Ball Roll')
            cmds.connectAttr(self.ikCtrl.ctrl.ballRoll,
                             '{}.rx'.format(self.footBallIKCtrl.offsetGrps[1].name))
            self.ikCtrl.addAttr('toeRoll', nn='Toe Roll')
            cmds.connectAttr(self.ikCtrl.ctrl.toeRoll,
                             '{}.rx'.format(self.footToesIKCtrl.offsetGrps[1].name))
            self.ikCtrl.addAttr('toeTwist', nn='Toe Twist')
            cmds.connectAttr(self.ikCtrl.ctrl.toeTwist,
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
                                        parent=self.ikCtrl.ctrlEnd)
                ctrlLoc.matchTransforms(jnts[2])
                softIk.connect('sm', '{}.wm'.format(jntLoc.name), 'to')
                softIk.connect('cm', '{}.wm'.format(ctrlLoc.name), 'to')
                cmds.setAttr('{}.cl'.format(softIk.name), abs(cmds.getAttr('{}.tx'.format(jnts[1]))
                             + cmds.getAttr('{}.tx'.format(jnts[2]))))
                a = utils.newNode('group', name='{}legSoftIK'.format(extraName), side=self.side,
                                  parent=footMechGrp.name)
                a.matchTransforms(legIK.grp)
                softIk.connect('ot', '{}.t'.format(a.name))
                cmds.pointConstraint(a.name, innerPivGrp.name, mo=1)
                self.ikCtrl.addAttr(name='softIKSep', nn='___   Soft IK', typ='enum',
                                        enumOptions=['___'])
                self.ikCtrl.addAttr(name='softIKTog', nn='Toggle Soft IK', typ='enum',
                                        enumOptions=['Off', 'On'])
                cmds.connectAttr(self.ikCtrl.ctrl.softIKTog, '{}.tog'.format(softIk.name))
                self.ikCtrl.addAttr(name='softIKDist', nn='Soft IK Distance', defaultVal=0.2)
                cmds.connectAttr(self.ikCtrl.ctrl.softIKDist, '{}.sd'.format(softIk.name))

        if options['FK']:
            ## controls
            self.hipFKCtrl = ctrlFn.ctrl(name='{}hipFK'.format(extraName),
                                         side=self.side, guide=fkJnts[0], skipNum=True,
                                         parent=fkCtrlGrp.name,
                                         scaleOffset=self.rig.scaleOffset,
                                         rig=self.rig, gimbal=True)
            self.hipFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                       scale=(0.6, 0.6, 0.6))
            self.hipFKCtrl.lockAttr(attr=['s'])
            self.hipFKCtrl.constrain(fkJnts[0], typ='parent')

            self.kneeFKCtrl = ctrlFn.ctrl(name='{}kneeFK'.format(extraName),
                                          side=self.side, guide=fkJnts[1], skipNum=True,
                                          parent=self.hipFKCtrl.ctrlEnd,
                                          scaleOffset=self.rig.scaleOffset,
                                          rig=self.rig, gimbal=True)
            self.kneeFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                        scale=(0.6, 0.6, 0.6))
            self.kneeFKCtrl.lockAttr(attr=['s'])
            self.kneeFKCtrl.constrain(fkJnts[1], typ='parent')

            self.ankleFKCtrl = ctrlFn.ctrl(name='{}ankleFK'.format(extraName),
                                           side=self.side, guide=fkJnts[2], skipNum=True,
                                           parent=self.kneeFKCtrl.ctrlEnd,
                                           scaleOffset=self.rig.scaleOffset,
                                           rig=self.rig, gimbal=True)
            self.ankleFKCtrl.modifyShape(color=col['col2'], shape='circle',
                                         scale=(0.6, 0.6, 0.6))
            self.ankleFKCtrl.lockAttr(attr=['s'])
            self.ankleFKCtrl.constrain(fkJnts[2], typ='parent')

            self.footBallFKCtrl = ctrlFn.ctrl(name='{}footBallFK'.format(extraName),
                                              side=self.side, guide=fkJnts[3], skipNum=True,
                                              parent=self.ankleFKCtrl.ctrlEnd,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig, gimbal=True)
            self.footBallFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.footBallFKCtrl.lockAttr(attr=['s'])
            self.footBallFKCtrl.constrain(fkJnts[3], typ='parent')
        if options['stretchy']:
            if options['IK']:
                legIK.addStretch(customStretchNode=customNodes,
                                 globalScaleAttr=self.rig.scaleAttr)
                self.ikCtrl.addAttr('stretchSep', nn='___   Stretch',
                                        typ='enum', enumOptions=['___'])
                self.ikCtrl.addAttr('stretchySwitch', nn='Stretch Switch',
                                       minVal=0, maxVal=1, defaultVal=1)
                cmds.connectAttr(self.ikCtrl.ctrl.stretchySwitch,
                                 legIK.stretchToggleAttr)
            if options['FK']:
                print '## add proper stretch to leg fk'

        if options['ribbon']:
            mechFn.bendyJoints(jnts[0], jnts[1], jnts[2], 'leg', self)

        ## leg parent stuff
        if parent:
            legParentLoc = utils.newNode('locator', name='{}legParent'.format(extraName),
                                         side=self.side, skipNum=True, parent=parent)
            legParentLoc.matchTransforms(jnts[0])
            cmds.parentConstraint(legParentLoc.name,
                                  '{}legFKCtrls{}'.format(self.moduleName, suffix['group']), mo=1)
            if options['IK'] and options['FK']:
                cmds.parentConstraint(legParentLoc.name, legMechSkelGrp.name, mo=1)


class quadripedLegModule:

    """ Create a quadriped leg rig. """

    def __init__(self, rig, extraName='', side='C'):
        """ Setup the initial variables to use when creating the limb.
        [Args]:
        rig (class) - The rig class to use
        extraName (string) - The extra name of the module
        side (string) - The side of the module ('C', 'R' or 'L')
        """
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, options={}, autoOrient=False, customNodes=False, parent=None):
        """ Create the leg rig.
        [Args]:
        options (dictionary) - A dictionary of options for the leg
        autoOrient (bool) - Toggles auto orienting the joints
        customNodes (bool) - Toggles the use of custom nodes
        parent (string) - The name of the parent
        """
        overrideOptions = options
        options = defaultBodyOptions.leg
        options.update(overrideOptions)

        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        jntSuffix = suffix['joint']
        jnts = [
            '{}clavicle{}'.format(self.moduleName, jntSuffix),
            '{}hip{}'.format(self.moduleName, jntSuffix),
            '{}knee{}'.format(self.moduleName, jntSuffix),
            '{}backKnee{}'.format(self.moduleName, jntSuffix),
            '{}ankle{}'.format(self.moduleName, jntSuffix),
            '{}footBall{}'.format(self.moduleName, jntSuffix),
            '{}footToes{}'.format(self.moduleName, jntSuffix),
        ]
        col = utils.getColors(self.side)
        cmds.parent(jnts[0], self.rig.skelGrp.name)
        legCtrlsGrp = utils.newNode('group', name='{}legCtrls'.format(extraName), side=self.side,
                                     parent=self.rig.ctrlsGrp.name, skipNum=True)
        legMechGrp = utils.newNode('group', name='{}legMech'.format(extraName), side=self.side,
                                    parent=self.rig.mechGrp.name, skipNum=True)

        if options['IK']:
            legMechSkelGrp = utils.newNode('group', name='{}legMechSkel'.format(extraName),
                                           side=self.side, parent=legMechGrp.name, skipNum=True)

        if autoOrient:
            utils.orientJoints(jnts[1:], aimAxis=(1 if not self.side == 'R' else -1, 0, 0))

        for jnt in jnts:
            utils.addJntToSkinJnt(jnt, self.rig)

        ## ik/fk
        if options['IK'] and options['FK']:
            ikJnts, fkJnts, jnts, ikCtrlGrp, fkCtrlGrp = mechFn.ikfkMechanics(self, extraName, jnts,
                                                                              legMechSkelGrp,
                                                                              legCtrlsGrp,
                                                                              moduleType='leg',
                                                                              rig=self.rig)
        else:
            ikJnts = jnts
            fkJnts = jnts
            ikCtrlGrp = legCtrlsGrp
            fkCtrlGrp = legCtrlsGrp

        self.footJnt = jnts[5]
        self.ankleJnt = jnts[4]
        self.ikCtrlGrp = ikCtrlGrp
        self.fkCtrlGrp = fkCtrlGrp

        if options['IK']:
            ## mechanics
            upperLegIK = ikFn.ik(ikJnts[0], ikJnts[2], name='{}upperLegIK'.format(extraName),
                                 side=self.side)
            upperLegIK.createIK(parent=legMechGrp.name)
            legIK = ikFn.ik(ikJnts[2], ikJnts[4], name='{}lowerLegIK'.format(extraName),
                            side=self.side)
            legIK.createIK(parent=legMechGrp.name)
            upperLegCtrls = utils.newNode('group', name='{}upperLegCtrls'.format(extraName),
                                          side=self.side, parent=ikCtrlGrp.name, skipNum=True)
            ## clav ctrl
            self.clavicleIKCtrl = ctrlFn.ctrl(name='{}clavicleIK'.format(extraName), side=self.side,
                                              guide=jnts[0], skipNum=True,
                                              parent=upperLegCtrls.name,
                                              scaleOffset=self.rig.scaleOffset, rig=self.rig)
            cmds.xform(self.clavicleIKCtrl.ctrl.name, piv=cmds.xform(parent, q=1, t=1, ws=1), ws=1)
            self.clavicleIKCtrl.modifyShape(shape='pin', color=col['col2'], mirror=True)
            self.clavicleIKCtrl.constrain(ikJnts[0])
            ## hip ctrl
            self.hipIKCtrl = ctrlFn.ctrl(name='{}hipIK'.format(extraName), side=self.side,
                                         guide=jnts[1], skipNum=True,
                                         parent=upperLegCtrls.name,
                                         scaleOffset=self.rig.scaleOffset, rig=self.rig)
            self.hipIKCtrl.modifyShape(shape='pringle', color=col['col1'], mirror=True)
            # self.hipIKCtrl.constrain(upperLegIK.grp)

            a = utils.newNode('transform', parent=self.hipIKCtrl.rootGrp.name)
            cmds.pointConstraint(self.clavicleIKCtrl.ctrlEnd, a.name)
            a.connect('t', '{}.rotatePivot'.format(self.hipIKCtrl.ctrl.name))

            ## hipAim ctrl
            self.hipAimIKCtrl = ctrlFn.ctrl(name='{}hipAimIK'.format(extraName), side=self.side,
                                            guide=jnts[1], skipNum=True,
                                            parent=self.hipIKCtrl.ctrlEnd,
                                            scaleOffset=self.rig.scaleOffset, rig=self.rig)
            self.hipAimIKCtrl.modifyShape(shape='arrowRev', color=col['col2'], mirror=True,
                                          scale=(0.1, 0.1, 0.4), rotation=(90, 0, 0))
            self.hipAimIKCtrl.constrain(upperLegIK.grp)

            ## foot ctrl
            footIKGuide = '{}footCtrlGuide{}'.format(self.moduleName, suffix['locator'])
            useGuideLoc = cmds.objExists(footIKGuide)
            if not useGuideLoc:
                footIKGuide = ikJnts[4]
            self.ikCtrl = ctrlFn.ctrl(name='{}footIK'.format(extraName), side=self.side,
                                      guide=footIKGuide, skipNum=True, parent=ikCtrlGrp.name,
                                      deleteGuide=True if useGuideLoc else False,
                                      scaleOffset=self.rig.scaleOffset, rig=self.rig)
            self.ikCtrl.modifyShape(shape='foot', color=col['col1'], scale=(2, 2, 2))
            self.hipIKCtrl.spaceSwitching([upperLegCtrls.name, self.ikCtrl.ctrlEnd],
                                          [parent, 'Foot'])
            ## pole vector
            pvGuide = '{}legPV{}'.format(self.moduleName, suffix['locator'])
            mechFn.poleVector(pvGuide, jnts[3], self, extraName, 'leg', self.moduleName, legIK)
            ## foot mech
            mechFn.reverseFoot(self, extraName, legMechGrp, ikJnts[4:], legIK)

            ## soft ik
            print '## Add soft IK option to quad leg.'

        if options['FK']:
            ## controls
            self.clavicleFKCtrl = ctrlFn.ctrl(name='{}clavicleFK'.format(extraName),
                                              side=self.side, guide=fkJnts[0], skipNum=True,
                                              parent=fkCtrlGrp.name,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig, gimbal=True)
            self.clavicleFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.clavicleFKCtrl.lockAttr(attr=['s'])
            self.clavicleFKCtrl.constrain(fkJnts[0], typ='parent')

            self.hipFKCtrl = ctrlFn.ctrl(name='{}hipFK'.format(extraName),
                                              side=self.side, guide=fkJnts[1], skipNum=True,
                                              parent=self.clavicleFKCtrl.ctrlEnd,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig, gimbal=True)
            self.hipFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.hipFKCtrl.lockAttr(attr=['s'])
            self.hipFKCtrl.constrain(fkJnts[1], typ='parent')

            self.kneeFKCtrl = ctrlFn.ctrl(name='{}kneeFK'.format(extraName),
                                              side=self.side, guide=fkJnts[2], skipNum=True,
                                              parent=self.hipFKCtrl.ctrlEnd,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig, gimbal=True)
            self.kneeFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.kneeFKCtrl.lockAttr(attr=['s'])
            self.kneeFKCtrl.constrain(fkJnts[2], typ='parent')

            self.backKneeFKCtrl = ctrlFn.ctrl(name='{}backKneeFK'.format(extraName),
                                              side=self.side, guide=fkJnts[3], skipNum=True,
                                              parent=self.kneeFKCtrl.ctrlEnd,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig, gimbal=True)
            self.backKneeFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.backKneeFKCtrl.lockAttr(attr=['s'])
            self.backKneeFKCtrl.constrain(fkJnts[3], typ='parent')

            self.ankleFKCtrl = ctrlFn.ctrl(name='{}ankleFK'.format(extraName),
                                              side=self.side, guide=fkJnts[4], skipNum=True,
                                              parent=self.backKneeFKCtrl.ctrlEnd,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig, gimbal=True)
            self.ankleFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.ankleFKCtrl.lockAttr(attr=['s'])
            self.ankleFKCtrl.constrain(fkJnts[4], typ='parent')

            self.footBallFKCtrl = ctrlFn.ctrl(name='{}footBallFK'.format(extraName),
                                              side=self.side, guide=fkJnts[5], skipNum=True,
                                              parent=self.ankleFKCtrl.ctrlEnd,
                                              scaleOffset=self.rig.scaleOffset,
                                              rig=self.rig, gimbal=True)
            self.footBallFKCtrl.modifyShape(color=col['col1'], shape='circle',
                                            scale=(0.6, 0.6, 0.6))
            self.footBallFKCtrl.lockAttr(attr=['s'])
            self.footBallFKCtrl.constrain(fkJnts[5], typ='parent')

        ##stretchy
        if options['stretchy']:
            if options['IK']:
                upperLegIK.addStretch(customStretchNode=customNodes, sjPar=parent,
                                      globalScaleAttr=self.rig.scaleAttr)
                legIK.addStretch(customStretchNode=customNodes,
                                 globalScaleAttr=self.rig.scaleAttr)
                self.ikCtrl.addAttr('stretchSep', nn='___   Stretch',
                                    typ='enum', enumOptions=['___'])
                self.ikCtrl.addAttr('stretchySwitch', nn='Stretch Switch',
                                    minVal=0, maxVal=1, defaultVal=1)
                cmds.connectAttr(self.ikCtrl.ctrl.stretchySwitch, upperLegIK.stretchToggleAttr)
                cmds.connectAttr(self.ikCtrl.ctrl.stretchySwitch, legIK.stretchToggleAttr)
            if options['FK']:
                print '## add proper stretch to quad leg FK.'
        ##ribbon
        if options['ribbon']:
            # mechFn.bendyJoints(jnts[0], jnts[1], jnts[2], 'leg', self)
            mechFn.bendyJoints(jnts[2], jnts[3], jnts[4], 'leg', self)

        ## leg parent stuff
        if parent:
            legParentLoc = utils.newNode('locator', name='{}legParent'.format(extraName),
                                         side=self.side, skipNum=True, parent=parent)
            legParentLoc.matchTransforms(jnts[0])
            if options['IK']:
                cmds.parentConstraint(legParentLoc.name, upperLegCtrls.name, mo=1)
            if options['FK']:
                cmds.parentConstraint(legParentLoc.name, self.clavicleFKCtrl.rootGrp.name, mo=1)


class headModule:

    """ Create a head rig. """

    def __init__(self, rig, extraName='', side='C'):
        """ Setup the initial variables to use when creating the head.
        [Args]:
        rig (class) - The rig class to use
        extraName (string) - The extra name of the module
        side (string) - The side of the module ('C', 'R' or 'L')
        """
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, options={}, autoOrient=True,
               parent=None, extraSpaces='', customNodes=False):
        """ Create the head rig.
        [Args]:
        options (dictionary) - A dictionary of options for the arm
        autoOrient (bool) - Toggles auto orienting the joints
        parent (string) - The name of the parent
        extraSpaces (list)(string) - A list of the names of the extra
                                     spaces of the control
        """
        overrideOptions = options
        options = defaultBodyOptions.head
        options.update(overrideOptions)
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        jntSuffix = suffix['joint']

        ctrlSpaceSwitches = [self.rig.globalCtrl.ctrlEnd]
        parJnt = utils.newNode('joint', name='{}headParent'.format(extraName), side=self.side,
                               parent=parent, skipNum=True)
        if parent:
            parJnt.matchTransforms(parent)
            if cmds.listRelatives(parent, p=1):
                gParent = cmds.listRelatives(parent, p=1)[0]
                ctrlSpaceSwitches.append(gParent)
        utils.orientJoints([parJnt.name], aimAxis=(1 if not self.side == 'R' else -1, 0, 0))
        utils.addJntToSkinJnt(parJnt.name, self.rig)
        # else:
        #     cmds.error('FUCK, I DON\'T KNOW WHAT TO DO WITHOUT A PARENT FOR THE HEAD YET.')
        jnts = [
            parJnt.name,
            '{}head{}'.format(self.moduleName, jntSuffix),
            '{}headEnd{}'.format(self.moduleName, jntSuffix),
        ]
        for each in jnts[1:]:
            utils.addJntToSkinJnt(each, self.rig)
        col = utils.getColors(self.side)
        cmds.parent(jnts[1], jnts[0])
        if autoOrient:
            # orientJoints.doOrientJoint(jointsToOrient=jnts,
            #                            aimAxis=(1 if not self.side == 'R' else -1, 0, 0),
            #                            upAxis=(0, 1, 0),
            #                            worldUp=(0, 1 if not self.side == 'R' else -1, 0),
            #                            guessUp=1)
            utils.orientJoints(jnts[1:], aimAxis=(1 if not self.side == 'R' else -1, 0, 0))
        headCtrlsGrp = utils.newNode('group', name='{}headCtrls'.format(extraName), side=self.side,
                                     parent=self.rig.ctrlsGrp.name, skipNum=True)
        if type(extraSpaces) == type(list()) and len(extraSpaces) > 1:
            ctrlSpaceSwitches.extend(extraSpaces)
            if extraSpaces:
                ctrlSpaceSwitches.append(extraSpaces)
        # else:
        #     ctrlSpaceSwitches.append(extraSpaces)
        if options['IK']:
            ## IK mechanics
            headMechGrp = utils.newNode('group', name='{}headMech'.format(extraName),
                                        side=self.side, parent=self.rig.mechGrp.name, skipNum=True)
            # cmds.setAttr('{}.it'.format(headMechGrp.name), 0)
            headIKsGrp = utils.newNode('group', name='{}headIKs'.format(extraName),
                                       side=self.side, parent=headMechGrp.name, skipNum=True)
            neckIK = ikFn.ik(jnts[0], jnts[1], name='{}neckIK'.format(extraName), side=self.side)
            neckIK.createIK(parent=headIKsGrp.name)
            if options['stretchy']:
                neckIK.addStretch(operation='both', customStretchNode=customNodes,
                                  globalScaleAttr=self.rig.scaleAttr, sjPar=parJnt.name)
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
            cmds.parentConstraint(gParent, self.headCtrl.rootGrp.name, mo=1, sr=['x', 'y', 'z'])
            self.headCtrl.spaceSwitching(ctrlSpaceSwitches, dv=1, constraint='parent',
                                         skip={'trans':['x', 'y', 'z']})
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

    """ Create finger or toe rigs. """

    def __init__(self, rig, extraName='', side='C'):
        """ Setup the initial variables to use when creating the digits.
        [Args]:
        rig (class) - The rig class to use
        extraName (string) - The extra name of the module
        side (string) - The side of the module ('C', 'R' or 'L')
        """
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, mode, autoOrient=False, customNodes=False, parent=None, thumb=True,
               skipDigits=None):
        """ Create the arm rig.
        [Args]:
        mode (string) - the mode of the digits ('hand' or 'foot')
        autoOrient (bool) - Toggles auto orienting the joints
        customNodes (bool) - Toggles the use of custom nodes
        parent (string) - The name of the parent
        thumb (bool) - Toggles creating the thumb
        skipDigits (list)(string) - A list of digit names to skip
                                    ('Index', 'Middle', 'Ring',
                                    'Pinky', etc)
        """
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
                digitsList.insert(0, 'Thumb')
        else:
            typ = 'toe'
            digitsList = ['Big', 'Index', 'Middle', 'Ring', 'Pinky']
            if thumb:
                digitsList[0] = 'Thumb'

        if skipDigits:
            for each in skipDigits:
                digitsList.remove(each)

        digitCtrls = {}
        palmMults = []

        utils.matchTransforms('{}{}PalmGuide{}'.format(self.moduleName, mode, suffix['locator']),
                              '{}{}{}_base{}'.format(self.moduleName, typ, digitsList[-1], jntSuffix),
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
        digitJnts = []
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
            digitJnts.append(jnts[0])
            # if each == 'Pinky':
            if each == digitsList[-1]:
                ctrlParent = palmCtrl.ctrlEnd
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
                    scaleNormDiv = utils.newNode('multiplyDivide',
                                                 name='{}{}{}_{}ScaleNorm'.format(extraName, typ,
                                                                                  each, seg),
                                                 side=self.side, operation=2,
                                                 suffixOverride='multiplyDivide_div')
                    scaleNormDiv.connect('input1X', '{}.distance'.format(distNd.name), 'to')
                    scaleNormDiv.connect('input2X', self.rig.scaleAttr, 'to')
                    if self.side == 'R':
                        distRevNd = utils.newNode('multDoubleLinear',
                                                  name='{}{}{}_{}Rev'.format(extraName, typ,
                                                                             each, seg),
                                                  side=self.side)
                        # distRevNd.connect('input1', '{}.distance'.format(distNd.name), mode='to')
                        distRevNd.connect('input1', '{}.outputX'.format(scaleNormDiv.name), 'to')
                        cmds.setAttr('{}.input2'.format(distRevNd.name), -1)
                        distRevNd.connect('output', '{}.tx'.format(jnts[i]))
                    else:
                        # distNd.connect('distance', '{}.tx'.format(jnts[i]))
                        scaleNormDiv.connect('outputX', '{}.tx'.format(jnts[i]), 'from')
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

        for key, val in digitCtrls.iteritems():
            exec('self.{}Ctrls = val'.format(key))

        palmLocParGrp = utils.newNode('group', name='{}{}PalmLoc'.format(extraName, mode),
                                      side=self.side, parent=parent)
        palmLoc = utils.newNode('locator', name='{}{}Palm'.format(extraName, mode),
                                side=self.side, parent=palmLocParGrp.name)
        palmLocParGrp.matchTransforms(digitJnts[-1])
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

    """ Create a tail rig. """

    def __init__(self, rig, extraName='', side='C'):
        """ Setup the initial variables to use when creating the tail.
        [Args]:
        rig (class) - The rig class to use
        extraName (string) - The extra name of the module
        side (string) - The side of the module ('C', 'R' or 'L')
        """
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, crv=False, jntNum=16, options={},
               autoOrient=False, parent=None):
        """ Create the tail rig.
        [Args]:
        crv (string) - The curve to create the tail from (if False
                       create from joints instead)
        jntNum (int) - The number of joints if creating from a curve
        options (dictionary) - A dictionary of options for the arm
        autoOrient (bool) - Toggles auto orienting the joints
        parent (string) - The name of the parent
        """
        overrideOptions = options
        options = defaultBodyOptions.tail
        options.update(overrideOptions)

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
                # orientJoints.doOrientJoint(jointsToOrient=jnts, aimAxis=(1, 0, 0),
                #                            upAxis=(0, 1, 0), worldUp=(0, 1, 0), guessUp=1)
                utils.orientJoints(jnts)
        if options['IK']:
            for jnt in jnts:
                utils.addJntToSkinJnt(jnt, self.rig)
            mechFn.createLayeredSplineIK(jnts, 'tail', rig=self.rig, side=self.side,
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


class simpleLimbModule:

    """ Create a leg rig. """

    def __init__(self, rig, extraName='', side='C'):
        """ Setup the initial variables to use when creating the limb.
        [Args]:
        rig (class) - The rig class to use
        extraName (string) - The extra name of the module
        side (string) - The side of the module ('C', 'R' or 'L')
        """
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, jntNames, options={}, autoOrient=False, customNodes=False,
               parent=None, limbType='limb', ikStartID=0, ikEndID=2, arrowPV=False):
        """ Create the limb rig.
        [Args]:
        options (dictionary) - A dictionary of options for the limb
        autoOrient (bool) - Toggles auto orienting the joints
        customNodes (bool) - Toggles the use of custom nodes
        parent (string) - The name of the parent
        limbType (string) - The name of the type of limb
        ikStartID (int) - The index of the start jnt
        ikEndID (int) - The index of the end jnt
        arrowPV (bool) - Toggles creating an arrow control for the
                         poleVector instead
        """
        overrideOptions = options
        options = defaultBodyOptions.limb
        options.update(overrideOptions)

        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        jntSuffix = suffix['joint']
        jnts = []
        for i in range(len(jntNames)):
            jnts.append('{}{}{}'.format(self.moduleName, jntNames[i], jntSuffix))
        col = utils.getColors(self.side)
        cmds.parent(jnts[0], self.rig.skelGrp.name)
        limbCtrlsGrp = utils.newNode('group', name='{}{}Ctrls'.format(extraName, limbType),
                                     side=self.side, parent=self.rig.ctrlsGrp.name, skipNum=True)
        limbMechGrp = utils.newNode('group', name='{}{}Mech'.format(extraName, limbType),
                                    side=self.side, parent=self.rig.mechGrp.name, skipNum=True)
        if options['IK']:
            limbMechSkelGrp = utils.newNode('group',
                                            name='{}{}MechSkel'.format(extraName, limbType),
                                            side=self.side, skipNum=True, parent=limbMechGrp.name)
        if autoOrient:
            # orientJoints.doOrientJoint(jointsToOrient=jnts,
            #                            aimAxis=(1 if not self.side == 'R' else -1, 0, 0),
            #                            upAxis=(0, 1, 0),
            #                            worldUp=(0, 1 if not self.side == 'R' else -1, 0),
            #                            guessUp=1)
            utils.orientJoints(jnts, aimAxis=(1 if not self.side == 'R' else -1, 0, 0))
        if options['IK'] and options['FK']:
            (ikJnts, fkJnts, jnts,
                ikCtrlGrp, fkCtrlGrp) = mechFn.ikfkMechanics(self, extraName, jnts,
                                                             limbMechSkelGrp, limbCtrlsGrp,
                                                             moduleType=limbType, rig=self.rig)
        else:
            for each in jnts:
                utils.addJntToSkinJnt(each, self.rig)
            ikJnts = jnts
            fkJnts = jnts
            ikCtrlGrp = limbCtrlsGrp
            fkCtrlGrp = limbCtrlsGrp

        self.ikCtrlGrp = ikCtrlGrp
        self.fkCtrlGrp = fkCtrlGrp

        if options['IK']:
            ## mechanics
            limbIK = ikFn.ik(ikJnts[ikStartID], ikJnts[ikEndID], side=self.side,
                             name='{}{}IK'.format(extraName, limbType))
            limbIK.createIK(parent=limbMechGrp.name)

            ## controls
            ikCtrlGuide = '{}{}CtrlGuide{}'.format(self.moduleName, limbType, suffix['locator'])
            self.ikCtrl = ctrlFn.ctrl(name='{}{}IK'.format(extraName, limbType), side=self.side,
                                      guide=ikCtrlGuide, skipNum=True, parent=ikCtrlGrp.name,
                                      deleteGuide=True, scaleOffset=self.rig.scaleOffset,
                                      rig=self.rig)
            self.ikCtrl.modifyShape(shape='cube', color=col['col1'])
            self.ikCtrl.lockAttr(attr=['s'])
            self.ikCtrl.constrain(limbIK.grp)
            # space switching?
            ## polevector ctrl
            pvGuide = '{}{}PV{}'.format(self.moduleName, limbType, suffix['locator'])
            mechFn.poleVector(pvGuide, jnts[1], self, extraName, limbType, self.moduleName, limbIK,
                              arrow=arrowPV, parent=parent)

            if options['softIK']:
                softIK = utils.newNode('mjSoftIK', name='{}{}IK'.format(extraName, limbType),
                                       side=self.side)
                jntLoc = utils.newNode('locator', name='{}{}JntBase'.format(extraName, limbType),
                                       parent=cmds.listRelatives(jnts[0], p=1))
                jntLoc.matchTransforms(jnts[0])
                ctrlLoc = utils.newNode('locator', name='{}{}IKCtrl'.format(extraName, limbType),
                                            side=self.side, skipNum=True,
                                            parent=self.ikCtrl.ctrlEnd)
                ctrlLoc.matchTransforms(jnts[2])
                softIK.connect('sm', '{}.wm'.format(jntLoc.name), 'to')
                softIK.connect('cm', '{}.wm'.format(ctrlLoc.name), 'to')
                cmds.setAttr('{}.cl'.format(softIK.name), abs(cmds.getAttr('{}.tx'.format(jnts[1]))
                             + cmds.getAttr('{}.tx'.format(jnts[2]))))
                a = utils.newNode('group', name='{}{}SoftIK'.format(extraName, limbType),
                                  side=self.side, parent=footMechGrp.name)
                a.matchTransforms(limbIK.grp)
                softIK.connect('ot', '{}.t'.format(a.name))
                cmds.pointConstraint(a.name, innerPivGrp.name, mo=1)
                self.ikCtrl.addAttr(name='softIKSep', nn='___   Soft IK', typ='enum',
                                        enumOptions=['___'])
                self.ikCtrl.addAttr(name='softIKTog', nn='Toggle Soft IK', typ='enum',
                                        enumOptions=['Off', 'On'])
                cmds.connectAttr(self.ikCtrl.ctrl.softIKTog, '{}.tog'.format(softIK.name))
                self.ikCtrl.addAttr(name='softIKDist', nn='Soft IK Distance', defaultVal=0.2)
                cmds.connectAttr(self.ikCtrl.ctrl.softIKDist, '{}.sd'.format(softIK.name))

        if options['FK']:
            fkCtrlPar = fkCtrlGrp.name
            ## controls
            for i, each in enumerate(jntNames[:-1]):
                fkCtrl = ctrlFn.ctrl(name='{}{}FK'.format(extraName, each),
                                     side=self.side, guide=fkJnts[i], skipNum=True,
                                     parent=fkCtrlPar, rig=self.rig, gimbal=True,
                                     scaleOffset=self.rig.scaleOffset)
                fkCtrl.modifyShape(shape='circle', color=col['col1'], scale=(0.6, 0.6, 0.6))
                fkCtrl.lockAttr(attr=['s'])
                fkCtrl.constrain(fkJnts[i])
                fkCtrlPar = fkCtrl.ctrlEnd

                exec('self.{}FKCtrl = fkCtrl'.format(each))

        if options['stretchy']:
            if options['IK']:
                limbIK.addStretch(customStretchNode=customNodes,
                                  globalScaleAttr=self.rig.scaleAttr)
                self.ikCtrl.addAttr('stretchSep', nn='___   Stretch',
                                    typ='enum', enumOptions=['___'])
                self.ikCtrl.addAttr('stretchySwitch', nn='Stretch Switch',
                                    minVal=0, maxVal=1, defaultVal=1)
                cmds.connectAttr(self.ikCtrl.ctrl.stretchySwitch, limbIK.stretchToggleAttr)
            if options['FK']:
                print '## add proper stretch to limb fk'

        if options['ribbon']:
            mechFn.bendyJoints(jnts[0], jnts[1], jnts[2], limbType, self)

        if parent:
            limbParentLoc = utils.newNode('locator', name='{}{}Parent'.format(extraName, limbType),
                                          side=self.side, skipNum=True, parent=parent)
            limbParentLoc.matchTransforms(jnts[0])
            cmds.parentConstraint(limbParentLoc.name, fkCtrlGrp.name, mo=1)
            if options['IK'] and options['FK']:
                cmds.parentConstraint(limbParentLoc.name, limbMechSkelGrp.name, mo=1)


def renameBodyPartJntGuides(typ, jntNames, side='C', extraName='', chain=False, sideList=None):
    """ Rename module guide joints.
    [Args]:
    typ (string) - The type of module ('arm', 'leg', 'spine', etc)
    jntNames (list)(string) - A list of new joint names
    side (string) - The side of the module
    extraName (string) - The extra name of the module
    chain (bool) - Toggles renaming the entire hierarchy chain
    """
    if extraName.endswith('_'):
        extraName = extraName[:-1]
    moduleName = utils.setupBodyPartName(extraName, side)
    partGrp = '{}{}{}'.format(moduleName, typ, suffix['group'])
    partGuidesJnts = utils.getAllChildren(partGrp)
    # partGuidesJnts = cmds.listRelatives(partGrp, type='joint', ad=1)
    # partGuidesJnts.reverse()
    if not chain:
        oldNewNames = zip(partGuidesJnts, jntNames)
        print oldNewNames
    else:
        oldNewNames = []
        for i, each in enumerate(partGuidesJnts):
            if i == 0:
                oldNewNames.append((each, jntNames[0]))
            elif i == (len(partGuidesJnts)-1):
                oldNewNames.append((each, jntNames[-1]))
            else:
                oldNewNames.append((each, jntNames[1]))
    if not sideList:
        for each, name in oldNewNames:
            cmds.select(each)
            utils.renameSelection(name, side)
    else:
        for i, onn in enumerate(oldNewNames):
            each, name = onn
            print name
            cmds.select(each)
            utils.renameSelection(name, sideList[i])

def renameBodyPartLocGuides(typ, locNames, side='C', extraName=''):
    """ Rename module guide locators.
    [Args]:
    typ (string) - The type of module ('arm', 'leg', 'spine', etc)
    locNames (list)(string) - A list of new locator names
    side (string) - The side of the module
    extraName (string) - The extra name of the module
    """
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
    """ Rename the guides for a leg.
    [Args]:
    side (string) - The side of the leg
    extraName (string) - The extra name of the leg
    """
    moduleName = utils.setupBodyPartName(extraName, side)
    if extraName:
        extraName = '{}_'.format(extraName)
    legGrp = '{}leg{}'.format(moduleName, suffix['group'])
    if cmds.objExists(legGrp):
        quadLeg = False
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
    elif cmds.objExists('{}quadLeg{}'.format(moduleName, suffix['group'])):
        legGrp = '{}quadLeg{}'.format(moduleName, suffix['group'])
        quadLeg = True
        jntNameList = [
            '{}clavicle'.format(extraName),
            '{}hip'.format(extraName),
            '{}knee'.format(extraName),
            '{}backKnee'.format(extraName),
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
    if quadLeg:
        legName = 'quadLeg'
    else:
        legName = 'leg'
    if len(cmds.listRelatives(legGrp)) > 4:
        locList.append('{}footPalmGuide'.format(extraName))
    renameBodyPartJntGuides(legName, jntNameList, side, extraName)

    locators = renameBodyPartLocGuides(legName, locList, side, extraName)

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
    """ Rename the guides for an arm.
    [Args]:
    side (string) - The side of the arm
    extraName (string) - The extra name of the arm
    """
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
    """ Rename the guides a spine.
    [Args]:
    side (string) - The side of the spine
    extraName (string) - The extra name of the spine
    """
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
    """ Rename the guides for a head.
    [Args]:
    side (string) - The side of the head
    extraName (string) - The extra name of the head
    """
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

def renameFaceGuides(side='C', extraName=''):
    """ Rename the guides for a face.
    [Args]:
    side (string) - The side of the face
    extraName (string) - The extraName of the face
    """
    moduleName = utils.setupBodyPartName(extraName, side)
    if extraName:
        extraName += '_'
    faceGrp = '{}faceJnts{}'.format(moduleName, suffix['group'])
    jntNameList = [
        '{}jawLower'.format(extraName),
        '{}jawLowerEnd'.format(extraName),
        '{}jawUpper'.format(extraName),
        '{}lipLower'.format(extraName),
        '{}lipUpper'.format(extraName),
        '{}mouthCorner'.format(extraName),
        '{}mouthCorner'.format(extraName),
        '{}noseCorner'.format(extraName),
        '{}noseCorner'.format(extraName),
        '{}cheek'.format(extraName),
        '{}cheek'.format(extraName),
        '{}eyebrowInner'.format(extraName),
        '{}eyebrowMid'.format(extraName),
        '{}eyebrowOuter'.format(extraName),
        '{}eyebrowInner'.format(extraName),
        '{}eyebrowMid'.format(extraName),
        '{}eyebrowOuter'.format(extraName),
        '{}eye'.format(extraName),
        '{}eyelidUpper'.format(extraName),
        '{}eyelidLower'.format(extraName),
        '{}eye'.format(extraName),
        '{}eyelidUpper'.format(extraName),
        '{}eyelidLower'.format(extraName),
    ]
    sideList = [
        'C',
        'C',
        'C',
        'C',
        'C',
        'L',
        'R',
        'L',
        'R',
        'L',
        'R',
        'L',
        'L',
        'L',
        'R',
        'R',
        'R',
        'L',
        'L',
        'L',
        'R',
        'R',
        'R',
    ]
    renameBodyPartJntGuides('faceJnts', jntNameList, sideList=sideList)
    cmds.select(cl=1)

def renameTailGuides(side='C', extraName=''):
    """ Rename the guides for a tail.
    [Args]:
    side (string) - The side of the tail
    extraName (string) - The extra name of the tail
    """
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
    """ Rename all body modules in the current scene based on their
    parent group name.
    """
    cmds.select(cmds.ls(l=1))
    sceneMObjs = apiFn.getSelectionAsMObjs()
    for each in sceneMObjs:
        lN, sN = apiFn.getPath(each, returnString=True)
        side = sN[0]
        if len(sN.split('_')) > 3:
            extraName = sN.split('_', 2)[1]
        else:
            extraName = ''
        if '_leg{}'.format(suffix['group']) in sN or '_quadLeg{}'.format(suffix['group']) in sN:
            renameLegGuides(side, extraName)
        elif '_arm{}'.format(suffix['group']) in sN:
            renameArmGuides(side, extraName)
        elif '_spine{}'.format(suffix['group']) in sN:
            renameSpineGuides(side, extraName)
        elif '_head{}'.format(suffix['group']) in sN:
            renameHeadGuides(side, extraName)
        elif '_tail{}'.format(suffix['group']) in sN:
            renameTailGuides(side, extraName)
        elif '_faceJnts{}'.format(suffix['group']) in sN:
            renameFaceGuides(side, extraName)