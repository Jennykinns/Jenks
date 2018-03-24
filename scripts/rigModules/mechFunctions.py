import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ikFunctions as ikFn
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules.suffixDictionary import suffix
from Jenks.scripts.rigModules import orientJoints

reload(utils)
reload(orientJoints)

def ikfkMechanics(module, extraName, jnts, mechSkelGrp, ctrlGrp, moduleType, rig):
    """ Create the mechanics for a IK/FK setup.
    [Args]:
    module (class) - The class of the body part module
    extraName (string) - The extra name for the setup
    jnts (list)(string) - A list of jnts to create the mechanics on
    mechSkelGrp (string) - The name of the mechanics skeleton group
    ctrlGrp (string) - The name of the control group
    moduleType (string) - The type of module ('arm', 'leg', etc)
    rig (class) - The rig class to use
    [Returns]:
    ikJnts (list)(string) - The names of the IK joints
    fkJnts (list)(string) - The names of the FK joints
    jnts (list)(string) - The names of the result joints
    ikCtrlGrp (string) - The name of the IK controls group
    fkCtrlGrp (string) - The name of the FK controls group
    """
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
        # utils.addJntToSkinJnt(jnts[i], rig=rig)
    ## settings control
    module.settingCtrl = ctrlFn.ctrl(name='{}{}Settings'.format(extraName, moduleType),
                                     guide='{}{}Settings{}'.format(module.moduleName,
                                                                   moduleType, suffix['locator']),
                                     deleteGuide=True, side=module.side, skipNum=True,
                                     parent=module.rig.settingCtrlsGrp.name,
                                     scaleOffset=rig.scaleOffset, rig=rig)
    if moduleType == 'arm':
        settingJnt = jnts[3]
    else:
        settingJnt = jnts[2]
    module.settingCtrl.makeSettingCtrl(ikfk=True, parent=settingJnt)
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
    return ikJnts, fkJnts, jnts, ikCtrlGrp, fkCtrlGrp

def poleVector(pvGuide, jnt, module, extraName, limbType, moduleName, limbIK,
               arrow=False, parent=None):
    """ Create a polevector control for an ik handle.
    [Args]:
    pvGuide (string) - The name of the poleVector guide locator
    jnt (string) - The name of the joint to aim at
    module (class) - The limb module class
    extraName (string) - The extra name of the module
    limbType (string) - The name of the limb type
    moduleName (string) - The module name
    limbIK (class) - The ik class
    arrow (bool) - Toggles creating an arrow from the start of the joint chain instead
    """
    col = utils.getColors(module.side)
    cmds.delete(cmds.aimConstraint(jnt, pvGuide))
    if not arrow:
        module.pvCtrl = ctrlFn.ctrl(name='{}{}PV'.format(extraName, limbType), side=module.side,
                                    guide=pvGuide, skipNum=True, deleteGuide=True,
                                    parent=module.ikCtrlGrp.name, scaleOffset=module.rig.scaleOffset,
                                    rig=module.rig)
        module.pvCtrl.modifyShape(shape='3dArrow', color=col['col1'], rotation=(0, 180, 0),
                                  scale=(0.4, 0.4, 0.4))
        module.pvCtrl.lockAttr(['r', 's'])
        module.pvCtrl.constrain(limbIK.hdl, typ='poleVector')
        module.pvCtrl.spaceSwitching([module.rig.globalCtrl.ctrlEnd, module.ikCtrl.ctrlEnd])
        pvCrv = cmds.curve(d=1,
                           p=[cmds.xform(module.pvCtrl.ctrl.name, q=1, ws=1, t=1),
                           cmds.xform(jnt, q=1, ws=1, t=1)])
        cmds.setAttr('{}.it'.format(pvCrv), 0)
        cmds.parent(pvCrv, module.pvCtrl.offsetGrps[0].name, r=1)
        pvCrv = cmds.rename(pvCrv, '{}{}PVLine{}'.format(moduleName,
                            limbType, suffix['nurbsCrv']))
        cmds.setAttr('{}Shape.overrideEnabled'.format(pvCrv), 1)
        cmds.setAttr('{}Shape.overrideDisplayType'.format(pvCrv), 1)
        cmds.select(cl=1)
        cmds.select('{}.cv[1]'.format(pvCrv))
        pvJntCluHdl = utils.newNode('cluster', name='{}{}PVJnt'.format(extraName, limbType),
                                     side=module.side, parent=jnt)
        cmds.select('{}.cv[0]'.format(pvCrv))
        pvCtrlCluHdl = utils.newNode('cluster', name='{}{}PVCtrl'.format(extraName, limbType),
                                     side=module.side, parent=module.pvCtrl.ctrlEnd)
        utils.setColor(pvJntCluHdl.name, color=None)
        utils.setColor(pvCtrlCluHdl.name, color=None)
    else:
        ikStartJnt = cmds.listRelatives(jnt, p=1)[0]
        module.pvCtrl = ctrlFn.ctrl(name='{}{}PV'.format(extraName, limbType), side=module.side,
                                    guide=ikStartJnt, skipNum=True, parent=module.ikCtrlGrp.name,
                                    scaleOffset=module.rig.scaleOffset, rig=module.rig)
        module.pvCtrl.modifyShape(shape='pvArrow', color=col['col2'], scale=(0.4, 0.4, 0.4))
        module.pvCtrl.lockAttr(['t', 's', 'rx'])
        cmds.delete(cmds.aimConstraint(pvGuide, module.pvCtrl.rootGrp.name))
        if parent:
            cmds.parentConstraint(parent, module.pvCtrl.rootGrp.name, mo=1)
        cmds.parent(pvGuide, module.pvCtrl.ctrlEnd)
        cmds.poleVectorConstraint(pvGuide, limbIK.hdl)
        utils.setShapeColor(pvGuide, color=None)

def reverseFoot(module, extraName, legMechGrp, footJnts, legIK):
    col = utils.getColors(module.side)
    footMechGrp = utils.newNode('group', name='{}footMech'.format(extraName),
                                side=module.side, parent=legMechGrp.name)
    ##- iks
    footBallIK = ikFn.ik(footJnts[0], footJnts[1], side=module.side,
                         name='{}footBallIK'.format(extraName))
    footBallIK.createIK(parent=footMechGrp.name)
    footToesIK = ikFn.ik(footJnts[1], footJnts[2], side=module.side,
                         name='{}footToesIK'.format(extraName))
    footToesIK.createIK(parent=footMechGrp.name)
    ##- rf joints
    rfMechGrp = utils.newNode('group', name='{}RFMech'.format(extraName),
                              side=module.side, parent=footMechGrp.name)
    rfJntGuides = [
        '{}footHeelGuide{}'.format(module.moduleName, suffix['locator']),
        '{}footToesGuide{}'.format(module.moduleName, suffix['locator']),
        footJnts[1],
        footJnts[0],
    ]
    rfJntNames = [
        'footHeel',
        'footToes',
        'footBall',
        'ankle',
    ]
    rfJnts = utils.createJntChainFromObjs(rfJntGuides, 'RF', side=module.side,
                                          extraName=extraName, jntNames=rfJntNames,
                                          parent=rfMechGrp.name)
    ##- rf iks
    rfToesIK = ikFn.ik(rfJnts[0], rfJnts[1], side=module.side,
                       name='{}RF_footToesIK'.format(extraName))
    rfToesIK.createIK(parent=rfMechGrp.name)
    rfBallIK = ikFn.ik(rfJnts[1], rfJnts[2], side=module.side,
                       name='{}RF_footBallIK'.format(extraName))
    rfBallIK.createIK(parent=rfMechGrp.name)
    rfAnkleIK = ikFn.ik(rfJnts[2], rfJnts[3], side=module.side,
                       name='{}RF_ankleIK'.format(extraName))
    rfAnkleIK.createIK(parent=rfMechGrp.name)
    ##- foot side pivots
    module.ikCtrl.addAttr('footRollsSep', nn='___   Foot Rolls', typ='enum',
                            enumOptions=['___'])
    innerPivGrp = utils.newNode('group', name='{}footInnerPivot'.format(extraName),
                                parent=module.ikCtrl.ctrlEnd, side=module.side,
                                skipNum=True)
    innerPivGrp.matchTransforms('{}footInnerGuide{}'.format(module.moduleName, suffix['locator']))
    outerPivGrp = utils.newNode('group', name='{}footOuterPivot'.format(extraName),
                                parent=innerPivGrp.name, side=module.side, skipNum=True)
    outerPivGrp.matchTransforms('{}footOuterGuide{}'.format(module.moduleName, suffix['locator']))
    module.ikCtrl.addAttr('sidePiv', nn='Side Pivot')
    sidePivNeg = utils.newNode('condition', name='{}footSidePivNeg'.format(extraName),
                                side=module.side, operation=3)
    sidePivNeg.connect('firstTerm', module.ikCtrl.ctrl.sidePiv, mode='to')
    if module.side == 'R':
        negFootPivAttr = utils.newNode('reverse',
                                       name='{}footSidePivNeg'.format(extraName),
                                       side=module.side)
        negFootPivAttr.connect('inputX', module.ikCtrl.ctrl.sidePiv, mode='to')
        negFootPivAttr = '{}.outputX'.format(negFootPivAttr.name)
    else:
        negFootPivAttr = module.ikCtrl.ctrl.sidePiv
    sidePivNeg.connect('colorIfTrueR', negFootPivAttr, mode='to')
    sidePivNeg.connect('outColorR', '{}.rz'.format(innerPivGrp.name), mode='from')

    sidePivPos = utils.newNode('condition', name='{}footSidePivPos'.format(extraName),
                                side=module.side, operation=4)
    sidePivPos.connect('firstTerm', module.ikCtrl.ctrl.sidePiv, mode='to')
    sidePivPos.connect('colorIfTrueR', module.ikCtrl.ctrl.sidePiv, mode='to')
    sidePivPos.connect('outColorR', '{}.rz'.format(outerPivGrp.name), mode='from')
    ##- controls
    module.footHeelIKCtrl = ctrlFn.ctrl(name='{}footHeelIK'.format(extraName),
                                      side=module.side, guide=rfJntGuides[0], skipNum=True,
                                      parent=outerPivGrp.name,
                                      scaleOffset=module.rig.scaleOffset,
                                      rig=module.rig, offsetGrpNum=2)
    module.footHeelIKCtrl.modifyShape(color=col['col2'], shape='pringle', mirror=True,
                                    scale=(0.7, 0.7, 0.7), rotation=(-45, 0, 0))
    module.footHeelIKCtrl.lockAttr(attr=['t', 's'])
    module.footHeelIKCtrl.constrain(rfJnts[0])
    module.footToesFKCtrl = ctrlFn.ctrl(name='{}footToesFK'.format(extraName),
                                      side=module.side, guide=footJnts[1], skipNum=True,
                                      parent=module.footHeelIKCtrl.ctrlEnd,
                                      scaleOffset=module.rig.scaleOffset,
                                      rig=module.rig)
    module.footToesFKCtrl.modifyShape(color=col['col3'], shape='arc', mirror=True,
                                    scale=(0.2, 0.2, 0.2),
                                    translation=(3, 1, 0),
                                    rotation=(90, 0, 0))
    module.footToesFKCtrl.constrain(footToesIK.grp)
    module.footToesFKCtrl.lockAttr(['t', 's'])
    module.footToesIKCtrl = ctrlFn.ctrl(name='{}footToesIK'.format(extraName),
                                      side=module.side, guide=rfJntGuides[1], skipNum=True,
                                      parent=module.footHeelIKCtrl.ctrlEnd,
                                      scaleOffset=module.rig.scaleOffset,
                                      rig=module.rig, offsetGrpNum=2)
    module.footToesIKCtrl.modifyShape(color=col['col2'], shape='pringle', mirror=True,
                                    scale=(0.7, 0.7, 0.7), rotation=(90, 0, 0),
                                    translation=(0, -1, 0))
    module.footToesIKCtrl.lockAttr(attr=['t', 's'])
    module.footToesIKCtrl.constrain(rfBallIK.grp)

    module.footBallIKCtrl = ctrlFn.ctrl(name='{}footBallIK'.format(extraName),
                                      side=module.side, guide=rfJntGuides[2], skipNum=True,
                                      parent=module.footToesIKCtrl.ctrlEnd,
                                      scaleOffset=module.rig.scaleOffset,
                                      rig=module.rig, offsetGrpNum=2)
    module.footBallIKCtrl.modifyShape(color=col['col2'], shape='pringle', mirror=True,
                                    scale=(0.7, 0.7, 0.7), translation=(0, 1.5, 0))
    module.footBallIKCtrl.lockAttr(attr=['t', 's'])
    cmds.xform(module.footBallIKCtrl.offsetGrps[0].name, ro=(-90, 0, 90))
    module.footBallIKCtrl.constrain(rfAnkleIK.grp)
    ##-- control attributes
    module.ikCtrl.addAttr('footCtrlTog', nn='Fine Foot Controls', typ='enum',
                            defaultVal=1, enumOptions=['Hide', 'Show'])
    cmds.connectAttr(module.ikCtrl.ctrl.footCtrlTog,
                     '{}.v'.format(module.footHeelIKCtrl.rootGrp.name))
    module.ikCtrl.addAttr('heelRoll', nn='Heel Roll')
    cmds.connectAttr(module.ikCtrl.ctrl.heelRoll,
                     '{}.rx'.format(module.footHeelIKCtrl.offsetGrps[1].name))
    module.ikCtrl.addAttr('heelTwist', nn='Heel Twist')
    cmds.connectAttr(module.ikCtrl.ctrl.heelTwist,
                     '{}.ry'.format(module.footHeelIKCtrl.offsetGrps[1].name))
    module.ikCtrl.addAttr('ballRoll', nn='Ball Roll')
    cmds.connectAttr(module.ikCtrl.ctrl.ballRoll,
                     '{}.rx'.format(module.footBallIKCtrl.offsetGrps[1].name))
    module.ikCtrl.addAttr('toeRoll', nn='Toe Roll')
    cmds.connectAttr(module.ikCtrl.ctrl.toeRoll,
                     '{}.rx'.format(module.footToesIKCtrl.offsetGrps[1].name))
    module.ikCtrl.addAttr('toeTwist', nn='Toe Twist')
    cmds.connectAttr(module.ikCtrl.ctrl.toeTwist,
                     '{}.ry'.format(module.footToesIKCtrl.offsetGrps[1].name))
    ##- constraints
    # cmds.parentConstraint(rfJnts[1], footToesIK.grp, mo=1)
    cmds.parentConstraint(module.footHeelIKCtrl.ctrlEnd, rfToesIK.grp, mo=1)
    cmds.parentConstraint(rfJnts[1], module.footToesFKCtrl.offsetGrps[0].name, mo=1)
    cmds.parentConstraint(rfJnts[2], footBallIK.grp, mo=1)
    cmds.parentConstraint(rfJnts[3], legIK.grp, mo=1)
    if cmds.objExists('{}footGuides{}'.format(module.moduleName, suffix['group'])):
        cmds.delete('{}footGuides{}'.format(module.moduleName, suffix['group']))

class strapModule:

    """ Create a strap rig. """

    def __init__(self, rig=None, name='strap', extraName='', side='C'):
        """ Setup the initial variables to use when creating the strap.
        [Args]:
        rig (class) - The rig class to use
        name (string) - The name of the strap
        extraName (string) - The extra name of the module
        side (string) - The side of the module ('C', 'R' or 'L')
        """
        self.name = name
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, jnts, nrb, parent=None, numOfJnts=10, skipSkinning=False):
        """ Create the strap.
        [Args]:
        jnts (list)(string) - The names of the joints to bind to the
                              nurbs plane
        nrb (string) - The name of the nurbs plane
        parent (string) - The name of the parent
        numOfJnts (int) - The amount of skinning joints to create
        """
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        col = utils.getColors(self.side)
        self.ctrls = []
        self.strapMechGrp = utils.newNode('group', name='{}{}Mech'.format(extraName, self.name),
                                          side=self.side, parent=self.rig.mechGrp.name,
                                          skipNum=True)
        cmds.setAttr('{}.it'.format(self.strapMechGrp.name), 0)
        cmds.parent(nrb, self.strapMechGrp.name)
        self.strapCtrlsGrp = utils.newNode('group', name='{}{}Ctrls'.format(extraName, self.name),
                                           side=self.side, parent=self.rig.ctrlsGrp.name,
                                           skipNum=True)
        cmds.parentConstraint(parent, self.strapCtrlsGrp.name, mo=1)
        prevJnt = None
        for each in jnts:
            if prevJnt:
                try:
                    cmds.parent(each, prevJnt)
                except RuntimeError:
                    pass
            prevJnt = each
        if not skipSkinning:
            utils.orientJoints(jnts, aimAxis=(1 if not self.side == 'R' else -1, 0, 0),
                               upAxis=(0, 1, 0))
        for each in jnts:
            cmds.parent(each, self.strapMechGrp.name)
            ## create control
            ctrl = ctrlFn.ctrl(name='{}{}'.format(extraName, self.name), side=self.side,
                               guide=each, rig=self.rig, parent=self.strapCtrlsGrp.name,
                               scaleOffset=self.rig.scaleOffset*0.4)
            ctrl.modifyShape(shape='sphere', color=col['col3'])
            self.ctrls.append(ctrl)
            ctrl.constrain(each)
            ctrl.constrain(each, typ='scale')
        if not skipSkinning:
            ## skin jnts to nrb / clusters
            skin = cmds.skinCluster(jnts, nrb, parent)[0]
        ## rivet locators + jnts
        if self.rig:
            rivJntPar = self.rig.skelGrp.name
        else:
            rivJntPar = None
        for i in range(numOfJnts):
            createRivet(self.name, extraName, self, nrb, parent=self.strapMechGrp.name,
                        pv=0.5, pu=(1.0/(numOfJnts-1.0))*i, rivJntPar=rivJntPar)


def ribbonJoints(sj, ej, bendyName, module, extraName='', moduleType=None, par=None,
                 endCtrl=False, basePar=None):
    """ Create a ribbon setup.
    [Args]:
    sj (string) -
    ej (string) -
    bendyName (string) - The name of the ribbon setup
    module (class) - The class of the body part module
    extraName (string) - The extra name of the ribbon setup
    moduleType (string) - The type of module
    par (string) - The name of the mechanics parent
    endCtrl (bool) - Toggles creating an end control
    basePar (string) - The name of the joints parent
    [Returns]:
    bendyEndCtrl (class) - The end control class or False
    """
    if not basePar:
        basePar = sj
    moduleName = utils.setupBodyPartName(module.extraName, module.side)
    bendyName = '{}{}'.format(moduleType, bendyName)
    col = utils.getColors(module.side)

    distance = cmds.getAttr('{}.tx'.format(ej))
    nPlane = cmds.nurbsPlane(p=(distance/2, 0, 0), lr=0.1, w=distance, axis=[0, 1, 0], u=3, d=3)
    nPlane = cmds.rename(nPlane[0], '{}{}Bendy{}'.format(moduleName, bendyName,
                                                         suffix['nurbsSurface']))
    if par:
        cmds.parent(nPlane, par)
    utils.matchTransforms(nPlane, sj)
    ## ctrl
    if not cmds.objExists('{}{}Ctrls{}'.format(moduleName, moduleType, suffix['group'])):
        ctrlGrp = cmds.group(n='{}{}Ctrls{}'.format(moduleName, moduleType, suffix['group']))
        cmds.parent(ctrlGrp, module.rig.ctrlsGrp.name)
    bendyCtrl = ctrlFn.ctrl(name='{}{}Bendy'.format(extraName, bendyName), side=module.side,
                            offsetGrpNum=2, skipNum=True, rig=module.rig,
                            scaleOffset=module.rig.scaleOffset,
                            parent='{}{}Ctrls{}'.format(moduleName, moduleType,
                                                        suffix['group']))
    bendyCtrl.modifyShape(color=col['col3'], shape='starFour', scale=(0.3, 0.3, 0.3))
    cmds.pointConstraint(sj, ej, bendyCtrl.offsetGrps[0].name)
    cmds.orientConstraint(sj, bendyCtrl.offsetGrps[0].name, sk='x')
    orientConstr = cmds.orientConstraint(basePar, ej, bendyCtrl.offsetGrps[1].name,
                                         sk=['y', 'z'], mo=1)
    cmds.setAttr('{}.interpType'.format(orientConstr[0]), 2)
    ## clusters
    cmds.select('{}.cv[0:1][0:3]'.format(nPlane))
    baseClu = utils.newNode('cluster', name='{}{}BendyBase'.format(extraName, bendyName),
                            side=module.side, parent=par)
    cmds.select('{}.cv[2:3][0:3]'.format(nPlane))
    midClu = utils.newNode('cluster', name='{}{}BendyMid'.format(extraName, bendyName),
                           side=module.side, parent=par)
    bendyCtrl.constrain(midClu.name)
    bendyCtrl.constrain(midClu.name, typ='scale')
    endCluGrpTrans = utils.newNode('group', name='{}{}BendyEndCluTrans'.format(extraName,
                                                                               bendyName),
                                   side=module.side, parent=par)
    utils.matchTransforms(endCluGrpTrans.name, ej)
    endCluGrpOrientYZ = utils.newNode('group', name='{}{}BendyEndCluOrient'.format(extraName,
                                                                                   bendyName),
                                      side=module.side, parent=endCluGrpTrans.name)
    utils.matchTransforms(endCluGrpOrientYZ.name, endCluGrpTrans.name)
    endCluGrpOrientX = utils.newNode('group', name='{}{}BendyEndCluOrientX'.format(extraName,
                                                                                   bendyName),
                                    side=module.side, parent=endCluGrpOrientYZ.name)
    utils.matchTransforms(endCluGrpOrientX.name, endCluGrpOrientYZ.name)
    cmds.select('{}.cv[4:5][0:3]'.format(nPlane))
    endClu = utils.newNode('cluster', name='{}{}BendyEnd'.format(extraName, bendyName),
                           side=module.side, parent=endCluGrpOrientX.name)
    cmds.parentConstraint(basePar, baseClu.name, mo=1)
    cmds.scaleConstraint(basePar, baseClu.name, mo=1)
    if not endCtrl:
        cmds.pointConstraint(ej, endCluGrpTrans.name, mo=1)
        cmds.orientConstraint(ej, endCluGrpOrientX.name, mo=1, sk=['y', 'z'])
        cmds.orientConstraint(sj, endCluGrpOrientYZ.name, mo=1, sk='x')
        bendyEndCtrl = False
    else:
        bendyEndCtrl = ctrlFn.ctrl(name='{}{}BendyEnd'.format(extraName, bendyName),
                                   side=module.side, skipNum=True, rig=module.rig,
                                   scaleOffset=module.rig.scaleOffset,
                                   parent='{}{}Ctrls{}'.format(moduleName, moduleType,
                                                               suffix['group']))
        bendyEndCtrl.modifyShape(color=col['col3'], shape='starFour', scale=(0.3, 0.3, 0.3))
        cmds.parentConstraint(ej, bendyEndCtrl.offsetGrps[0].name)
        bendyEndCtrl.constrain(endCluGrpTrans.name)
        bendyEndCtrl.constrain(endCluGrpTrans.name, typ='scale')
    ## rivets
    rivJntPar = sj
    for i in [0.1, 0.3, 0.5, 0.7, 0.9]:
        rivJnt = createRivet('{}Bendy'.format(bendyName), extraName, module, nPlane, pv=0.5, pu=i,
                             parent=par, rivJntPar=rivJntPar)
        rivJntPar = rivJnt
    return bendyEndCtrl


def bendyJoints(sj, mj, ej, moduleType, module):
    """ Create a bendy joints setup (mainly for arms & legs).
    [Args]:
    sj (string) - The name of the start joint
    mj (string) - The name of the middle joint
    ej (string) - The name of the end joint
    moduleType (string) - The type of body part ('arm', 'leg')
    module (class) - The class of the body part module
    """
    moduleName = utils.setupBodyPartName(module.extraName, module.side)
    extraName = module.extraName
    mechGrp = utils.newNode('group', name='{}BendyMech'.format(extraName),
                            side=module.side, skipNum=True,
                            parent='{}{}Mech{}'.format(moduleName, moduleType, suffix['group']))
    mechGrp.setAttr('it', 0)
    midBendCtrl = ribbonJoints(sj, mj, 'Upper', module, extraName=extraName,
                 moduleType=moduleType, par=mechGrp.name, endCtrl=True)
    ribbonJoints(mj, ej, 'Lower', module, extraName=extraName,
                 moduleType=moduleType, par=mechGrp.name, basePar=midBendCtrl.ctrlEnd)



def createLayeredSplineIK(jnts, name, rig=None, side='C', extraName='', parent=None, dyn=False):
    """ Create a layered spline IK.
    [Args]:
    jnts (list)(string) - The names of the joints to create the IK with
    name (string) - The name of the IK
    rig (class) - The rig class to use
    side (string) - The side of the IK
    extraName (string) - The extra name of the IK
    parent (string) - The name of the parent
    dyn (bool) - Toggles dynamics on the spline IK
    """
    moduleName = utils.setupBodyPartName(extraName, side)
    col = utils.getColors(side)
    ## create base layer jnts
    tmpCrv = utils.createCrvFromObjs(jnts, crvName='tmpCrv')
    ctrlGrp = utils.newNode('group', name='{}{}Ctrls'.format(extraName, name), side=side,
                            parent=rig.ctrlsGrp.name if rig else None, skipNum=True)
    mechGrp = utils.newNode('group', name='{}{}Mech'.format(extraName, name), side=side,
                            parent=rig.mechGrp.name if rig else None, skipNum=True)
    baseJnts = utils.createJntsFromCrv(tmpCrv, numOfJnts=4, side=side,
                                       name='{}{}_baseLayer'.format(extraName, name))
    if rig:
        cmds.parent(jnts[0], rig.skelGrp.name)
    cmds.parent(baseJnts[0], mechGrp.name)
    ## parent locs to base jnts
    ## base layer ctrls
    baseLayerLocs = []
    baseLayerCtrls = []
    baseCtrlParent = ctrlGrp.name
    for each in baseJnts:
        baseLoc = utils.newNode('locator', name='{}{}_baseLayer'.format(extraName, name),
                                side=side)
        baseLoc.parent(each, relative=True)
        utils.setShapeColor(baseLoc.name, color=None)
        baseLayerLocs.append(baseLoc)
        baseCtrl = ctrlFn.ctrl(name='{}{}_baseLayer'.format(extraName, name), guide=each,
                               side=side, parent=baseCtrlParent, rig=rig,
                               scaleOffset=rig.scaleOffset)
        baseCtrl.constrain(each)
        baseCtrl.modifyShape(shape='cube', color=col['col2'], scale=(1, 1, 1))
        baseLayerCtrls.append(baseCtrl)
        baseCtrlParent = baseCtrl.ctrlEnd
    baseSpaces = [rig.globalCtrl.ctrlEnd]
    if parent:
        baseSpaces.insert(0, parent)
    baseLayerCtrls[0].spaceSwitching(parents=baseSpaces, niceNames=None,
                                     constraint='parent', dv=0)

    ## mid layer crv FROM BASE JNTS
    midCrv = utils.createCrvFromObjs(baseJnts, crvName='{}_midLayer'.format(name),
                                     side=side, extraName=extraName)
    ## create mid jnts
    midJnts = utils.createJntsFromCrv(tmpCrv, numOfJnts=7, side=side,
                                      name='{}{}_midLayer'.format(extraName, name))
    cmds.parent(midJnts[0], mechGrp.name)
    cmds.delete(tmpCrv)
    ## parent locs to mid jnts
    ## create mid ctrls - parent constrain root grp to mid jnts
    midLayerLocs = []
    midLayerCtrls = []
    midCtrlParent = ctrlGrp.name
    for each in midJnts:
        midCtrl = ctrlFn.ctrl(name='{}{}_midLayer'.format(extraName, name), guide=each,
                               side=side, parent=midCtrlParent, rig=rig,
                               scaleOffset=rig.scaleOffset)
        cmds.parentConstraint(each, midCtrl.rootGrp.name, mo=1)
        midCtrl.modifyShape(shape='sphere', color=col['col1'], scale=(0.4, 0.4, 0.4))
        midLayerCtrls.append(midCtrl)
        midLoc = utils.newNode('locator', name='{}{}_midLayer'.format(extraName, name),
                               side=side)
        utils.setShapeColor(midLoc.name, color=None)
        midLoc.parent(midCtrl.ctrlEnd, relative=True)
        midLayerLocs.append(midLoc)
        midCtrlParent = midCtrl.ctrlEnd
    ## ik spline mid crv to mid jnts
    midIKSpline = ikFn.ik(sj=midJnts[0], ej=midJnts[-1],
                          name='{}{}_midLayerIK'.format(extraName, name), side=side)
    midIKSpline.createSplineIK(crv=midCrv, parent=mechGrp.name)
    midIKSpline.addStretch(operation='both', mode='length',
                           globalScaleAttr=rig.scaleAttr if rig else None)
    midIKSpline.advancedTwist(baseLayerCtrls[0].ctrlEnd, endObj=baseLayerCtrls[-1].ctrlEnd,
                              wuType=4)
    ## connect mid crv cvs to base locators
    for i, each in enumerate(baseLayerLocs):
        cmds.connectAttr('{}.wp'.format(each.name), '{}Shape.cv[{}]'.format(midCrv, i))
    ## create skin crv FROM MID JNTS
    skinCrvIn = utils.createCrvFromObjs(midJnts, side=side, extraName=extraName,
                                        crvName='{}_skinLayer{}'.format(name,
                                                                        'DynIn' if dyn else ''))
    skinCrvInShape = cmds.listRelatives(skinCrvIn, s=1)[0]
    if dyn:
        dynMechGrp = utils.newNode('group', name='{}Dynamics'.format(name), side=side,
                                   parent=mechGrp.name, skipNum=True)
        cmds.parent(skinCrvIn, dynMechGrp.name)
        skinCrv = utils.createCrvFromObjs(midJnts, crvName='{}_skinLayer'.format(name),
                                          side=side, extraName=extraName)
        ## create output curve
        dynOutCrv = utils.createCrvFromObjs(midJnts, side=side, extraName=extraName,
                                            crvName='{}_skinLayerDynOut'.format(name))
        cmds.parent(dynOutCrv, dynMechGrp.name)
        dynOutCrvShape = cmds.listRelatives(dynOutCrv, s=1)[0]
        ## create follicle
        fol = utils.newNode('follicle', name='{}_skinLayerDyn'.format(name), side=side,
                            parent=dynMechGrp.name)
        cmds.setAttr('{}.restPose'.format(fol.name),  1)
        cmds.setAttr('{}.startDirection'.format(fol.name),  1)
        cmds.setAttr('{}.degree'.format(fol.name),  3)
        ## create hair system
        hs = utils.newNode('hairSystem', name='{}_skinLayerDyn'.format(name), side=side,
                           parent=dynMechGrp.name)
        ## create nucleus
        nuc = utils.newNode('nucleus', name='{}_skinLayerDyn'.format(name), side=side,
                            parent=dynMechGrp.name)
        ## connect shit
        fol.connect('startPosition', '{}.local'.format(skinCrvInShape), mode='to')
        fol.connect('startPositionMatrix', '{}.wm'.format(skinCrvIn), mode='to')
        fol.connect('currentPosition', '{}.outputHair[0]'.format(hs.name), mode='to')
        fol.connect('outCurve', '{}.create'.format(dynOutCrvShape), mode='from')
        fol.connect('outHair', '{}.inputHair[0]'.format(hs.name), mode='from')
        hs.connect('currentState', '{}.inputActive[0]'.format(nuc.name), mode='from')
        hs.connect('startState', '{}.inputActiveStart[0]'.format(nuc.name), mode='from')
        hs.connect('nextState', '{}.outputObjects[0]'.format(nuc.name), mode='to')
        hs.connect('startFrame', '{}.startFrame'.format(nuc.name), mode='to')
        hs.connect('currentTime', 'time1.outTime', mode='to')
        nuc.connect('currentTime', 'time1.outTime', mode='to')
        ## blend shape curves
        blendNode = cmds.blendShape(skinCrvIn, dynOutCrv, skinCrv,
                                    n='{}_{}Dynamics{}'.format(side, name, suffix['blend']))[0]
        ## connect blend shape to attribute
        ##- create dyn control
        dynCtrl = ctrlFn.ctrl(name='{}Settings'.format(name),
                              guide='{}_{}SettingsGuide{}'.format(side, name, suffix['locator']),
                              rig=rig, deleteGuide=True, side=side, skipNum=True,
                              parent=rig.settingCtrlsGrp.name)
        dynCtrl.makeSettingCtrl(ikfk=False, parent=jnts[0])
        dynCtrl.addAttr('dynSwitch', nn='Dynamics Switch', minVal=0, maxVal=1, defaultVal=1)
        dynSwitchRev = utils.newNode('reverse',  name='{}DynamicsSwitch'.format(name), side=side)
        cmds.connectAttr(dynCtrl.ctrl.dynSwitch, '{}.{}'.format(blendNode, dynOutCrv))
        dynSwitchRev.connect('inputX', dynCtrl.ctrl.dynSwitch, mode='to')
        dynSwitchRev.connect('outputX', '{}.{}'.format(blendNode, skinCrvIn), mode='from')

    else:
        skinCrv = skinCrvIn


    ## ik spline skin crv to skin jnts
    skinIKSpline = ikFn.ik(sj=jnts[0], ej=jnts[-1],
                           name='{}{}_skinLayerIK'.format(extraName, name), side=side)
    skinIKSpline.createSplineIK(crv=skinCrv, parent=mechGrp.name)
    skinIKSpline.addStretch(operation='both', mode='length',
                            globalScaleAttr=rig.scaleAttr if rig else None)
    skinIKSpline.advancedTwist(midLayerCtrls[0].ctrlEnd, endObj=midLayerCtrls[-1].ctrlEnd,
                               wuType=4)
    ## connect skin crv cvs to mid locators
    for i, each in enumerate(midLayerLocs):
        cmds.connectAttr('{}.wp'.format(each.name), '{}Shape.cv[{}]'.format(skinCrvIn, i))

    ##


def createRivet(rivName, extraName='', module=None, nrb=None, side='C', loftComponents=None,
                pv=0.5, pu=0.5, parent=None, rivJntPar=None, jnt=True):
    """ Create a rivet.
    [Args]:
    rivName (string) - The name of the rivet
    extraName (string) - The extra name of the rivet
    module (class) - The class of the body part module
    nrb (string) - The nurbs plane to create the rivet on
    pv (float) - The V position for the rivet
    pu (float) - The U position for the rivet
    parent (string) - The name of the mechanics parent
    rivJntPar (string) - The name of the joint parent
    [Returns]:
    rivJnt.name (string) - The name of the rivet joint
    """
    if extraName:
        extraName += '_'
    if not nrb and loftComponents:
        nrb = cmds.loft(loftComponents, ch=1, u=1, d=3, ss=1, rn=0, po=0,
                        n='{}_{}{}Riv{}'.format(module.side if module else side, extraName,
                                               rivName, suffix['nurbsSurface']))[0]
        if parent:
            cmds.parent(nrb, parent)
    rivLoc = utils.newNode('locator', name='{}{}Riv'.format(extraName, rivName),
                           side=module.side if module else side, parent=parent)
    if jnt:
        rivJnt = utils.newNode('joint', name='{}{}Riv'.format(extraName, rivName),
                               side=module.side if module else side, parent=rivJntPar)
        if module:
            utils.addJntToSkinJnt(rivJnt.name, rig=module.rig)
        cmds.setAttr('{}.jointOrient'.format(rivJnt.name), 0, 0, 0)
        cmds.parentConstraint(rivLoc.name, rivJnt.name)
    rivNd = utils.newNode('mjRivet', name='{}{}Riv'.format(extraName, rivName),
                          side=module.side if module else side)
    rivNd.connect('is', '{}.ws'.format(nrb), 'to')
    rivNd.connect('ot', '{}.t'.format(rivLoc.name), 'from')
    rivNd.connect('or', '{}.r'.format(rivLoc.name), 'from')
    cmds.setAttr('{}.pv'.format(rivNd.name), pv)
    cmds.setAttr('{}.pu'.format(rivNd.name), pu)
    return rivJnt.name if jnt else rivLoc.name

def createRivetFromSelected(rivName, extraName='', module=None, side='C',
                            pv=1.5, pu=0.5, parent=None, rivJntPar=None, jnt=True):
    sel = cmds.ls(sl=1)
    if sel:
        createRivet(rivName=rivName, extraName=extraName, module=module, side=side,
                    loftComponents=sel, pv=pv, pu=pu, parent=parent, rivJntPar=rivJntPar,
                    jnt=jnt)