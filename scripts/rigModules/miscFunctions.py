import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ikFunctions as ikFn
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules.suffixDictionary import suffix
from Jenks.scripts.rigModules import orientJoints

reload(utils)
reload(orientJoints)

def ikfkMechanics(module, extraName, jnts, mechSkelGrp, ctrlGrp, moduleType, rig):
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
        utils.addJntToSkinJnt(jnts[i], rig=rig)
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

class strapModule:
    def __init__(self, rig, name='strap', extraName='', side='C'):
        self.name = name
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def create(self, jnts, nrb, parent=None, numOfJnts=10):
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        self.ctrls = []
        self.strapMechGrp = utils.newNode('group', name='{}{}Mech'.format(extraName, self.name),
                                          side=self.side, parent=self.rig.mechGrp.name,
                                          skipNum=True)
        cmds.parent(nrb, self.strapMechGrp.name)
        self.strapCtrlsGrp = utils.newNode('group', name='{}{}Ctrls'.format(extraName, self.name),
                                           side=self.side, parent=self.rig.ctrlsGrp.name,
                                           skipNum=True)
        cmds.parentConstraint(parent, self.strapCtrlsGrp.name, mo=1)
        for each in jnts:
            cmds.parent(each, self.strapMechGrp.name)
            ## create control
            ctrl = ctrlFn.ctrl(name='{}{}'.format(extraName, self.name), side=self.side,
                               guide=each, rig=self.rig, parent=self.strapCtrlsGrp.name,
                               scaleOffset=self.rig.scaleOffset)
            ctrl.constrain(each)
            self.ctrls.append(ctrl)
        ## skin jnts to nrb / clusters
        skin = cmds.skinCluster(jnts, nrb, parent)[0]
        ## rivet locators + jnts
        for i in range(numOfJnts):
            createRivet(self.name, extraName, self, nrb, parent=self.strapMechGrp.name,
                        pv=0.5, pu=(1.0/(numOfJnts-1.0))*i, rivJntPar=parent)


def ribbonJoints(sj, ej, bendyName, module, extraName='', moduleType=None, par=None,
                 endCtrl=False, basePar=None):
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
    moduleName = utils.setupBodyPartName(module.extraName, module.side)
    extraName = '{}_'.format(module.extraName) if module.extraName else ''
    mechGrp = utils.newNode('group', name='{}BendyMech'.format(extraName),
                            side=module.side, skipNum=True,
                            parent='{}{}Mech{}'.format(moduleName, moduleType, suffix['group']))
    midBendCtrl = ribbonJoints(sj, mj, 'Upper', module, extraName=extraName,
                 moduleType=moduleType, par=mechGrp.name, endCtrl=True)
    ribbonJoints(mj, ej, 'Lower', module, extraName=extraName,
                 moduleType=moduleType, par=mechGrp.name, basePar=midBendCtrl.ctrlEnd)



def createLayeredSplineIK(jnts, name, rig=None, side='C', extraName='', ctrlLayers=2,
                          parent=None, dyn=False):
    moduleName = utils.setupBodyPartName(extraName, side)
    extraName = '{}_'.format(extraName) if extraName else ''
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


def createRivet(rivName, extraName, module, nrb, pv=0.5, pu=0.5, parent=None, rivJntPar=None):
    rivJnt = utils.newNode('joint', name='{}{}Riv'.format(extraName, rivName),
                           side=module.side, parent=rivJntPar)
    utils.addJntToSkinJnt(rivJnt.name, rig=module.rig)
    cmds.setAttr('{}.jointOrient'.format(rivJnt.name), 0, 0, 0)
    rivLoc = utils.newNode('locator', name='{}{}Riv'.format(extraName, rivName),
                           side=module.side, parent=parent)
    cmds.parentConstraint(rivLoc.name, rivJnt.name)
    rivNd = utils.newNode('mjRivet', name='{}{}Riv'.format(extraName, rivName),
                          side=module.side)
    rivNd.connect('is', '{}.ws'.format(nrb), 'to')
    rivNd.connect('ot', '{}.t'.format(rivLoc.name), 'from')
    rivNd.connect('or', '{}.r'.format(rivLoc.name), 'from')
    cmds.setAttr('{}.pv'.format(rivNd.name), pv)
    cmds.setAttr('{}.pu'.format(rivNd.name), pu)
    return rivJnt.name