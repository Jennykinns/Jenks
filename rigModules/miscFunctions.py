import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ikFunctions as ikFn
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules.suffixDictionary import suffix
from Jenks.scripts.rigModules import orientJoints

reload(utils)
reload(orientJoints)

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
                               side=side, parent=baseCtrlParent, rig=rig)
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
                               side=side, parent=midCtrlParent, rig=rig)
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
