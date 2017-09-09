import maya.cmds as cmds
import uiTest1_UI as customUI
import maya.OpenMayaUI as omUi
from functools import partial
import json


try:
    from PySide import QtGui, QtCore
    import PySide.QtGui as QtWidgets
    from shiboken import wrapInstance
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets
    from shiboken2 import wrapInstance

from Jenks.scripts import utilities as j_utils
import defaultLocData

reload(j_utils)
reload(defaultLocData)
reload(customUI)

## remove global variables from previous runs
deleteVars = []
var = None
val = None

for var, val in globals().iteritems():
    if 'j_wwiar' in var:
        deleteVars.append(var)
for x in deleteVars:
    del globals()[x]

## declare global variables
j_wwiar_limbBoxNum = 0
j_wwiar_currentLimbBoxes = []
j_wwiar_rigMode = False
j_wwiar_spineJntsNum = 7
j_wwiar_locScaleSpnBoxVal = 1
j_wwiar_ctrlScaleSpnBoxVal = 1
j_wwiar_rigNameTxt = None
j_wwiar_spine = 2

iconDir = '{0}scripts/Jenks/icons/'.format(cmds.internalVar(uad=True))

def createGlobalCtrl(rigName):
    """Creates a global control and basic group structure for the rig.

    Args:
    [string] rigName - The rig's name
    """

    miscCol = j_wwiar_misc1SpnBoxVal
    globalCtrlName = '{0}_global'.format(rigName)
    fullGlobalCtrlName = '{0}_CTRL'.format(globalCtrlName)

    ## create group structure
    grps = [
        '{0}_geometry_GRP'.format(rigName),
        '{0}_controls_GRP'.format(rigName),
        '{0}_skeleton_GRP'.format(rigName),
        '{0}_mechanics_GRP'.format(rigName),
    ]
    for x in grps:
        if not cmds.objExists('{0}{1}'.format(rigName, x)):
            cmds.group(em=True, n=x)
    ## create global control
    if not cmds.objExists('{0}Ctrl_ROOT'.format(globalCtrlName)):
        ##- world locator
        worldLoc=cmds.spaceLocator(n='{0}_world_LOC'.format(rigName))
        lockWorldLocAttr = [
            'translateX',
            'translateY',
            'translateZ',
            'rotateX',
            'rotateY',
            'rotateZ',
            'scaleX',
            'scaleY',
            'scaleZ',
        ]
        for attr in lockWorldLocAttr:
            cmds.setAttr('{0}_world_LOC.{1}'.format(rigName, attr), lock=True)
        cmds.setAttr('{0}_world_LOC.visibility'.format(rigName), 0, lock=True)
        ##- global ctrl
        j_utils.createCtrlShape(globalCtrlName, 1, col=miscCol,
                                globalScale=j_wwiar_ctrlScaleSpnBoxVal)
        j_utils.createBuffer(globalCtrlName, 1, 1, worldLoc)

    ##- create & connect attributes
    newAttr = {
        (0, 'visSep') : (
            '___   Visibilities',
             '___',
             0,
             '',
             ''
        ),
        (1, 'visGeo') : (
            'Geometry',
            'Hide:Show',
             1,
             '{0}_geometry_GRP'.format(rigName),
             'visibility'
        ),
        (2, 'visCtrls') : (
            'Controls',
            'Hide:Show',
            1,
            '{0}_controls_GRP'.format(rigName),
            'visibility'
        ),
        (3, 'visSkel') : (
            'Skeleton',
            'Hide:Show',
            1,
            '{0}_skeleton_GRP'.format(rigName),
            'visibility'
        ),
        (4, 'visMech') : (
            'Mechanics',
            'Hide:Show',
            0,
            '{0}_mechanics_GRP'.format(rigName),
            'visibility'
        ),
        (5, 'mdSep') : (
            '___   Display Mode',
            '___',
            0,
            '',
            ''
        ),
        (6, 'mdGeo') : (
            'Geometry',
            'Normal:Template:Reference',
            2,
            '{0}_geometry_GRP'.format(rigName),
            'overrideDisplayType'
        ),
        (7, 'mdSkel') : (
            'Skeleton',
            'Normal:Template:Reference',
            0,
            '{0}_skeleton_GRP'.format(rigName),
            'overrideDisplayType'
        ),
        (8, 'sep1') : (
            '___   ',
            '___',
            0,
            '',
            ''
        ),
        (9, 'credits') : (
            'Rig by Matt Jenkins',
            '___',
            0,
            '',
            ''
        ),
    }

    j_utils.createAttr(fullGlobalCtrlName, newAttr)
    j_utils.connectAttrs(fullGlobalCtrlName, newAttr)

    ## parent grps to global ctrl
    if not cmds.objExists('{0}__RIG_GRP'.format(rigName)):
        cmds.group(em=True, n='{0}__RIG_GRP'.format(rigName))
    cmds.parent('{0}_world_LOC'.format(rigName), grps[0], '{0}_globalCtrl_ROOT'.format(rigName),
                '{0}__RIG_GRP'.format(rigName))
    cmds.parent(grps[1:], '{0}_globalConst_GRP'.format(rigName))


def createLegLocs(rigName, side, limbName, mirror=False, mirrorSide='R'):
    """Creates the locators for a leg limb, can optionally mirror the
    limb too.

    Args:
    [string] rigName - The rig's name
    [string] side - The limb's side
    [string] limbName - The limb's name
    [bool] mirror - Will the limb be mirrored?
    [string] mirrorSide - The mirrored limb's side
    """

    limbName, side_, name = nameStuff(rigName, limbName, side)
    suff = '_posLOC'
    pvDist = 1

    ## create Locs
    legLocs = defaultLocData.getLegLocData(j_wwiar_locScaleSpnBoxVal)
    if side.lower() == 'r' or 'right' in side.lower():
        j_utils.reverseLocPosValues(legLocs)

    ## create locs
    if not cmds.objExists('{0}wholeLeg{1}'.format(name, suff)):
        mirror = False

    legLocs = j_utils.createLocs(legLocs, name, suff, rigName=rigName, side=side_,
                                 limbName=limbName, mirror=mirror, mirSide=mirrorSide,
                                 scale=j_wwiar_locScaleSpnBoxVal)
    ## create leg parent curve
    legName, name = createParCrv(rigName, name, suff, mirrorSide, limbName, legLocs, mirror,
                                 'Leg', 'hip')
    ## create pole vector locator
    createPvVis('hip', 'knee', 'ankle', 'legPvVis', name, suff, legName, [3, 0 ,0], pvDist)
    ikfkVisPos = [0.5, 0.25, -0.5]
    if mirror:
        ikfkVisPos[0] *= -1
    createIkfkVis('legIKFKVis', 'ankle', name, suff, side_, ikfkVisPos)

    ## final stuff before returning
    legLocs.pop((3, name+'footHeel'+suff))
    cmds.select(cl=True)
    sortedKeys = sorted(legLocs)
    returnKeys = []
    for key in sortedKeys:
        returnKeys.append(key[1])
    return returnKeys, legName


def createLegSkelMech(locs, rigName, side, limbName, par='', fkik=None, stretchy=None):
    """Creates the skeleton and mechanics for a leg built upon
    locators as guides.

    Args:
    [string list] locs - List of the names of locators to use as guides
    for the joints
    [string] rigName - Name of the rig
    [string] side - The side the leg is on
    [string] limbName - The extra name of the limb
    [string] par - Name of the leg's parent joint
    [boot] fkik - Toggles the creation of an IK/FK switch for the leg
    """

    limbName, side_, name = nameStuff(rigName, limbName, side)
    suff = '_JNT'

    ## sets the colours from the UI
    col, altCol, thirdCol = getLeftRightColour(side)

    ## create joints
    jnts = j_utils.createJnts(locs, side=side_)

    suff, ikSuff, fkSuff, IK = createBaseMech(fkik, jnts, rigName, name, side_, limbName, suff,
                                              col, 'hip', 'ankle', 'leg')

    ## create foot mech
    if cmds.objExists('{0}RF_mech_GRP'.format(name)):
        cmds.delete('{0}RF_mech_GRP'.format(name))
    j_utils.createIK('{0}footBallIK'.format(name), '{0}ankle{1}'.format(name, ikSuff),
                     '{0}footBall{1}'.format(name, ikSuff))
    j_utils.createIK('{0}footToesIK'.format(name), '{0}footBall{1}'.format(name, ikSuff),
                     '{0}footToes{1}'.format(name, ikSuff))
    rfJnts=j_utils.createJnts(['{0}footHeel_posLOC'.format(name),
                               '{0}footToes_posLOC'.format(name),
                               '{0}footBall_posLOC'.format(name),
                               '{0}ankle_posLOC'.format(name)],
                              '_RF')
    rfToes=j_utils.createIK('{0}RF_footToesIK'.format(name), '{0}RF_footHeel_JNT'.format(name),
                            '{0}RF_footToes_JNT'.format(name))
    rfBall=j_utils.createIK('{0}RF_footBallIK'.format(name), '{0}RF_footToes_JNT'.format(name),
                            '{0}RF_footBall_JNT'.format(name))
    rfAnkle=j_utils.createIK('{0}RF_ankleIK'.format(name), '{0}RF_footBall_JNT'.format(name),
                            '{0}RF_ankle_JNT'.format(name))
    cmds.parentConstraint(rfJnts[-1], '{0}legIK_GRP'.format(name), mo=True)
    cmds.parentConstraint(rfJnts[-2], '{0}footBallIK_GRP'.format(name), mo=True)
    cmds.parentConstraint(rfJnts[-3], '{0}footToesIK_GRP'.format(name), mo=True)
    cmds.group(rfJnts[0], rfToes[0], rfBall[0], rfAnkle[0], n='{0}RF_mech_GRP'.format(name))
    footBallPos = cmds.xform(rfJnts[-2], q=True, t=True, ws=True)
    cmds.xform('{0}RF_mech_GRP'.format(name), piv=footBallPos)
    cmds.group('{0}legIK_GRP'.format(name), '{0}footBallIK_GRP'.format(name),
               '{0}footToesIK_GRP'.format(name), '{0}RF_mech_GRP'.format(name),
               n='{0}footMech_GRP'.format(name))
    footBallJntPos = cmds.xform('{0}footBall{1}'.format(name, ikSuff), q=True, t=True, ws=True)
    cmds.xform('{0}footMech_GRP'.format(name), piv=footBallJntPos)

    ## create leg IK ctrls
    ##- foot Toes
    j_utils.createCtrlShape('{0}footToesIK'.format(name), 9, col=altCol,
                            scale=[0.7, 0.35, 0.35], rotOffset=[75, 15, 0],
                            transOffset=[0, 0.35, 0], side=side,
                            globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer('{0}footToesIK'.format(name), 1, 1, '{0}footToes_posLOC'.format(name))
    j_utils.lockHideAttrs('{0}footToesIK_CTRL'.format(name), 'scale,')
    footBallLoc=cmds.xform('{0}footBall_posLOC'.format(name), q=True, ws=True, t=True)
    cmds.xform('{0}footToesIK_CTRL'.format(name), piv=footBallLoc)
    cmds.parentConstraint('{0}footToesIKConst_GRP'.format(name),
                          '{0}RF_footToesIK_GRP'.format(name), mo=True)
    ##- foot Ball
    j_utils.createCtrlShape('{0}footBallIK'.format(name), 9, col=altCol, scale=[0.7, 0.5, 0.5],
                            transOffset=[0, 1, 0], globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer('{0}footBallIK'.format(name), 1, 1, '{0}footBall_posLOC'.format(name))
    j_utils.lockHideAttrs('{0}footBallIK_CTRL'.format(name), 'scale,')
    cmds.parentConstraint('{0}footBallIKConst_GRP'.format(name),
                          '{0}RF_footBallIK_GRP'.format(name), mo=True)
    cmds.parentConstraint('{0}footBallIKConst_GRP'.format(name),
                          '{0}RF_ankleIK_GRP'.format(name), mo=True)
    ##- foot Heel
    j_utils.createCtrlShape('{0}footHeelIK'.format(name), 9, col=altCol, scale=[0.5, 0.5, 0.5],
                            rotOffset=[-120, 0, 0], globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer('{0}footHeelIK'.format(name), 1, 1, '{0}footHeel_posLOC'.format(name))
    j_utils.lockHideAttrs('{0}footHeelIK_CTRL'.format(name), 'scale,')
    cmds.parentConstraint('{0}footHeelIKConst_GRP'.format(name),
                          '{0}RF_footHeel_JNT'.format(name), mo=True)
    cmds.parent('{0}footBallIKCtrl_ROOT'.format(name), '{0}footHeelIKConst_GRP'.format(name))
    cmds.parent('{0}footToesIKCtrl_ROOT'.format(name), '{0}footHeelIKConst_GRP'.format(name))
    ##- foot
    j_utils.createCtrlShape('{0}footIK'.format(name), 8, scale=[1.5,1.5,1.5], col=col,
                            transOffset=[0, 0, -0.25], globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer('{0}footIK'.format(name), 1, 1, '{0}footBall_posLOC'.format(name))
    cmds.parent('{0}footHeelIKCtrl_ROOT'.format(name),'{0}footIKConst_GRP'.format(name))
    if fkik:
    ## create leg FK ctrls
        j_utils.createFKCtrl(name, 'hip', j_wwiar_ctrlScaleSpnBoxVal, [0.5, 0.5, 0.5],
                             col, rot=[0, 0, 90])
        j_utils.createFKCtrl(name, 'knee', j_wwiar_ctrlScaleSpnBoxVal, [0.5, 0.5, 0.5],
                             altCol, rot=[0, 0, 90], trans=[0, 0, 0.7])
        j_utils.createFKCtrl(name, 'ankle', j_wwiar_ctrlScaleSpnBoxVal, [0.4, 0.4, 0.4],
                             col, rot=[0, 0, 90])
        j_utils.createFKCtrl(name, 'footBall', j_wwiar_ctrlScaleSpnBoxVal, [0.3, 0.3, 0.3],
                             altCol, rot=[0, 0, 90])
        cmds.parent('{0}footBallFKCtrl_ROOT'.format(name), '{0}ankleFKConst_GRP'.format(name))
        cmds.parent('{0}ankleFKCtrl_ROOT'.format(name), '{0}kneeFKConst_GRP'.format(name))
        cmds.parent('{0}kneeFKCtrl_ROOT'.format(name), '{0}hipFKConst_GRP'.format(name))
        cmds.group('{0}hipFKCtrl_ROOT'.format(name), n='{0}legFKCtrls_GRP'.format(name))
    ## legParent ctrl
    if not cmds.objExists(par):
        j_utils.createCtrlShape('{0}legParent'.format(name), 5, scale=[0.4, 0.4, 0.4],
                                globalScale=j_wwiar_ctrlScaleSpnBoxVal)
        j_utils.createBuffer('{0}legParent'.format(name), 1, 1, '{0}hip_posLOC'.format(name))
        cmds.parentConstraint('{0}legParentConst_GRP'.format(name),
                              '{0}hip{1}'.format(name, ikSuff), mo=True)

    ## organise shit
    if cmds.objExists('{0}legMech_GRP'.format(name)):
        cmds.delete('{0}legMech_GRP'.format(name))
    if fkik:
        cmds.group('{0}hip{1}'.format(name, ikSuff), '{0}hip_FK_JNT'.format(name),
                   n='{0}legFKIKSkel_GRP'.format(name))
        cmds.group('{0}legFKIKSkel_GRP'.format(name), '{0}footMech_GRP'.format(name),
                   n='{0}legMech_GRP'.format(name))
    else:
        cmds.group('{0}footMech_GRP'.format(name), n='{0}legMech_GRP'.format(name))
    hipJntPos = cmds.xform('{0}hip{1}'.format(name, ikSuff), q=True, t=True, ws=True)
    cmds.xform('{0}legMech_GRP'.format(name), piv=hipJntPos)
    cmds.group('{0}legPVCtrl_ROOT'.format(name), '{0}footIKCtrl_ROOT'.format(name),
               n='{0}legIKCtrls_GRP'.format(name))
    j_utils.createSpSwConstraint(['{0}_globalConst_GRP'.format(rigName),
                                  '{0}footIKConst_GRP'.format(name)],
                                  '{0}legPV_CTRL'.format(name),
                                  enumNames='World:Foot',
                                  niceNames=['World', 'Foot'])
    if cmds.objExists(par):
        hipParLoc = cmds.spaceLocator(n='{0}hipParent_LOC'.format(name))[0]
        cmds.parent(hipParLoc, par)
        cmds.delete(cmds.parentConstraint('{0}hip{1}'.format(name, ikSuff), hipParLoc))
        cmds.setAttr('{0}.overrideEnabled'.format(hipParLoc), True)
        cmds.setAttr('{0}.overrideVisibility'.format(hipParLoc), 0)
        cmds.parentConstraint(hipParLoc, '{0}hip{1}'.format(name, ikSuff), mo=True)
        if fkik:
            cmds.parentConstraint(par, '{0}hipFKCtrl_ROOT'.format(name), mo=True)
            cmds.group('{0}legSettingsCtrl_ROOT'.format(name), '{0}legIKCtrls_GRP'.format(name),
                       '{0}legFKCtrls_GRP'.format(name), n='{0}legCtrls_GRP'.format(name))
        else:
            cmds.group('{0}legIKCtrls_GRP'.format(name), n='{0}legCtrls_GRP'.format(name))
        j_utils.createSpSwConstraint(['{0}_globalConst_GRP'.format(rigName), par],
                                      '{0}footIK_CTRL'.format(name))
    else:
        if fkik:
            cmds.parent('{0}legFKCtrls_GRP'.format(name), '{0}legIKCtrls_GRP'.format(name),
                        '{0}legParentConst_GRP'.format(name))
        else:
            cmds.parent('{0}legIKCtrls_GRP'.format(name), '{0}legParentConst_GRP'.format(name))
        cmds.group('{0}legSettingsCtrl_ROOT'.format(name), '{0}legParentCtrl_ROOT'.format(name),
                   n='{0}legCtrls_GRP'.format(name))
    ## IKFK ctrl visibilities
    if fkik:
        cmds.setDrivenKeyframe('{0}legFKCtrls_GRP'.format(name), at='visibility',
                               cd='{0}legSettings_CTRL.IKFKSwitch'.format(name), dv=0.001, v=1)
        cmds.setDrivenKeyframe('{0}legFKCtrls_GRP'.format(name), at='visibility',
                               cd='{0}legSettings_CTRL.IKFKSwitch'.format(name), dv=0, v=0)
        cmds.setDrivenKeyframe('{0}legIKCtrls_GRP'.format(name), at='visibility',
                               cd='{0}legSettings_CTRL.IKFKSwitch'.format(name), dv=0.999, v=1)
        cmds.setDrivenKeyframe('{0}legIKCtrls_GRP'.format(name), at='visibility',
                               cd='{0}legSettings_CTRL.IKFKSwitch'.format(name), dv=1, v=0)
    ## parent to overall rig stuffs
    if cmds.objExists('{0}_controls_GRP'.format(rigName)):
        cmds.parent('{0}legCtrls_GRP'.format(name), '{0}_controls_GRP'.format(rigName))
    if cmds.objExists('{0}_mechanics_GRP'.format(rigName)):
        cmds.parent('{0}legMech_GRP'.format(name), '{0}_mechanics_GRP'.format(rigName))
    if cmds.objExists('{0}_skeleton_GRP'.format(rigName)):
        cmds.parent('{0}hip{1}'.format(name, suff), '{0}_skeleton_GRP'.format(rigName))
    ## extra limb mechanics
    if stretchy:
        j_utils.createStretchyLimb(rigName, ['{0}hip{1}'.format(name, ikSuff),
                                             '{0}knee{1}'.format(name, ikSuff),
                                             '{0}ankle{1}'.format(name, ikSuff)],
                                   '{0}leg'.format(name),
                                   par if par else '{0}_world_LOC'.format(rigName),
                                   #'{0}_spine_base_JNT'.format(rigName),
                                   # par,
                                   '{0}footIKConst_GRP'.format(name),
                                   '{0}footIK_CTRL'.format(name), 'Upper Leg', 'Lower Leg',
                                   'Knee Pin Toggle')
    cmds.select(cl=True)


def createArmLocs(rigName, side, limbName, mirror=False, mirrorSide='R'):
    limbName, side_, name = nameStuff(rigName, limbName, side)
    suff = '_posLOC'
    pvDist = 1

    ## create Locs
    armLocs = defaultLocData.getArmLocData(j_wwiar_locScaleSpnBoxVal)
    if side.lower() == 'r' or 'right' in side.lower():
        j_utils.reverseLocPosValues(armLocs)

    ## create locs
    if not cmds.objExists('{0}wholeArm{1}'.format(name, suff)):
        mirror = False

    armLocs = j_utils.createLocs(armLocs, name, suff, rigName=rigName, side=side_,
                                 limbName=limbName, mirror=mirror, mirSide=mirrorSide,
                                 scale=j_wwiar_locScaleSpnBoxVal)
    ## create arm parent curve
    armName, name = createParCrv(rigName, name, suff, mirrorSide, limbName, armLocs, mirror,
                                 'Arm', 'shoulder')
    ## create pole vector locator
    createPvVis('shoulder', 'elbow', 'wrist', 'armPvVis', name, suff, armName, [3, 0, 0], pvDist)
    ikfkVisPos = [0.5, 0.25, -0.5]
    if mirror:
        ikfkVisPos[0] *= -1
    createIkfkVis('armIKFKVis', 'wrist', name, suff, side_, ikfkVisPos)

    ## final stuff before returning
    cmds.select(cl=True)
    sortedKeys = sorted(armLocs)
    returnKeys = []
    for x in sortedKeys:
        returnKeys.append(x[1])
    return returnKeys, armName


def createArmSkelMech(locs, rigName, side, limbName, par='', fkik=None, stretchy=None):
    """Creates the skeleton and mechanics for an arm built upon
    locators as guides.

    Args:
    [string list] locs - List of the names of locators to use as guides
    for the joints
    [string] rigName - Name of the rig
    [string] side - The side the arm is on
    [string] limbName - The extra name of the limb
    [string] par - Name of the arm's parent joint
    [boot] fkik - Toggles the creation of an IK/FK switch for the arm
    """
    limbName, side_, name = nameStuff(rigName, limbName, side)
    suff = '_JNT'

    col, altCol, thirdCol = getLeftRightColour(side)

    jntLocs = locs
    jntLocs.remove(name+'clav_posLOC')
    jnts = j_utils.createJnts(jntLocs, side=side_)
    clavJnt = j_utils.createJnts([name+'clav_posLOC'])
    cmds.parent(name+'shoulder'+suff, name+'clav'+suff)
    j_utils.doOrientJoint(clavJnt, [1, 0, 0], [0, 1, 0], [0, 1, 0], 1)

    suff, ikSuff, fkSuff, IK = createBaseMech(fkik, jnts, rigName, name, side_, limbName, suff,
                                              col, 'shoulder', 'wrist', 'arm')

    handPalmIK = j_utils.createIK(name+'handPalmIK', name+'wrist'+ikSuff, name+'handPalm'+ikSuff)
    cmds.group(name+'handPalmIK_GRP', name+'armIK_GRP', n=name+'handMech_GRP')
    wristJntPos = cmds.xform(name+'wrist'+ikSuff, q=True, t=True, ws=True)
    cmds.xform(name+'handMech_GRP', piv=wristJntPos)
    cmds.duplicate(name+'shoulder'+suff, po=True, n=name+'shoulder_end_JNT')
    clavIK = j_utils.createIK(name+'clavIK', name+'clav_JNT', name+'shoulder_end_JNT')
    ##- create forearm twist
    fArmTwist1 = cmds.duplicate(name+'elbow'+suff, po=True, n=name+'foreArmTwist01_JNT')
    fArmTwist2 = cmds.duplicate(name+'elbow'+suff, po=True, n=name+'foreArmTwist02_JNT')
    cmds.parent(fArmTwist1, name+'elbow'+suff)
    cmds.parent(fArmTwist2, fArmTwist1)
    cmds.pointConstraint(name+'elbow'+suff, fArmTwist1, w=0.666)
    cmds.pointConstraint(name+'wrist'+suff, fArmTwist1, w=0.333)
    cmds.pointConstraint(name+'elbow'+suff, fArmTwist2, w=0.333)
    cmds.pointConstraint(name+'wrist'+suff, fArmTwist2, w=0.666)
    cmds.orientConstraint(name+'elbow'+suff, fArmTwist1, w=0.666, sk=['y', 'z'])
    cmds.orientConstraint(name+'wrist'+suff, fArmTwist1, w=0.333, sk=['y', 'z'])
    cmds.orientConstraint(name+'elbow'+suff, fArmTwist2, w=0.333, sk=['y', 'z'])
    cmds.orientConstraint(name+'wrist'+suff, fArmTwist2, w=0.666, sk=['y', 'z'])
    ## create arm IK ctrls
    ##- hand Palm
    j_utils.createCtrlShape(name+'handPalmIK', 9, col=altCol, scale=[0.7, 0.7, 0.7],
                            rotOffset=[0, 90, -45], side=side,
                            globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer(name+'handPalmIK', 1, 1, name+'handPalm_posLOC')
    j_utils.lockHideAttrs('{0}handPalmIK_CTRL'.format(name), 'scale,')
    cmds.parentConstraint(name+'handPalmIKConst_GRP', name+'armIK_GRP', mo=True)
    cmds.parentConstraint(name+'handPalmIKConst_GRP', name+'handPalmIK_GRP', mo=True)
    ##- arm
    j_utils.createCtrlShape(name+'handIK', 11, scale=[0.5, 0.5, 0.5], col=col,
                            globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer(name+'handIK', 1, 1, name+'wrist'+ikSuff)
    if side == 'R' or 'R_' in side or '_R' in side:
        armCtrlRot = cmds.xform(name+'handIKCtrl_PAR', q=True, ro=True)
        armCtrlRot[0] = armCtrlRot[0]-180
        cmds.xform(name+'handIKCtrl_PAR', ro=armCtrlRot)
    cmds.parent(name+'handPalmIKCtrl_ROOT', name+'handIKConst_GRP')
    ##- clav
    j_utils.createCtrlShape(name+'clav', 9, col=altCol, rotOffset=[0, 90, -15],
                            transOffset=[0, 0.3, 0], side=side,
                            globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer(name+'clav', 1, 1, clavIK[1])
    j_utils.lockHideAttrs('{0}clav_CTRL'.format(name), 'rotate,')
    cmds.parentConstraint(name+'clavConst_GRP', clavIK[0], mo=True)
    ##- armParent
    if not cmds.objExists(par):
        j_utils.createCtrlShape(name+'armParent', 5, scale=[0.4, 0.4, 0.4],
                                globalScale=j_wwiar_ctrlScaleSpnBoxVal)
        j_utils.createBuffer(name+'armParent', 1, 1, name+'clav_posLOC')
        cmds.parentConstraint(name+'armParentConst_GRP', name+'clav_JNT', mo=True)
        cmds.parent(name+'clavCtrl_ROOT', name+'armParentConst_GRP')
    if fkik:
        ## create arm FK ctrls
        j_utils.createFKCtrl(name, 'shoulder', j_wwiar_ctrlScaleSpnBoxVal, [0.4, 0.4, 0.4],
                             col, rot=[0, 0, 90])
        j_utils.createFKCtrl(name, 'elbow', j_wwiar_ctrlScaleSpnBoxVal, [0.3, 0.3, 0.3],
                             altCol, rot=[0, 0, 90], trans=[0, 0, 0.6])
        j_utils.createFKCtrl(name, 'wrist', j_wwiar_ctrlScaleSpnBoxVal,
                             [0.2, 0.2, 0.2], col, rot=[0, 0, 90])
        cmds.parent(name+'wristFKCtrl_ROOT', name+'elbowFKConst_GRP')
        cmds.parent(name+'elbowFKCtrl_ROOT', name+'shoulderFKConst_GRP')

        cmds.group(name+'shoulder_IK_JNT', name+'shoulder_FK_JNT', n=name+'armFKIKSkel_GRP')
        cmds.parentConstraint(name+'clav_JNT', name+'armFKIKSkel_GRP', mo=True)
        if cmds.objExists(name+'armMech_GRP'):
            cmds.delete(name+'armMech_GRP')
        cmds.group(name+'armFKIKSkel_GRP', name+'handMech_GRP', name+'clavIK_GRP',
                   n=name+'armMech_GRP')
        cmds.group(name+'shoulderFKCtrl_ROOT', n=name+'armFKCtrls_GRP')
        cmds.parentConstraint(name+'clav_JNT', name+'armFKCtrls_GRP', mo=True)
    else:
        cmds.parentConstraint(name+'clav_JNT', name+'shoulder'+suff, mo=True)
        if cmds.objExists(name+'armMech_GRP'):
            cmds.delete(name+'armMech_GRP')
        cmds.group(name+'handMech_GRP', name+'clavIK_GRP', n=name+'armMech_GRP')
    cmds.group(name+'armPVCtrl_ROOT', name+'handIKCtrl_ROOT', n=name+'armIKCtrls_GRP')
    j_utils.createSpSwConstraint(['{0}_globalConst_GRP'.format(rigName),
                                  '{0}handIKConst_GRP'.format(name)],
                                  '{0}armPV_CTRL'.format(name),
                                  enumNames='World:Hand',
                                  niceNames=['World', 'Hand'])
    if cmds.objExists(par):
        clavParLoc = cmds.spaceLocator(n='{0}clavParent_LOC'.format(name))[0]
        cmds.parent(clavParLoc, par)
        cmds.delete(cmds.parentConstraint('{0}clav_JNT'.format(name), clavParLoc))
        cmds.setAttr('{0}.overrideEnabled'.format(clavParLoc), True)
        cmds.setAttr('{0}.overrideVisibility'.format(clavParLoc), 0)
        cmds.parentConstraint(clavParLoc, name+'clav_JNT', mo=True)
        cmds.parentConstraint(clavParLoc, name+'clavCtrl_ROOT', mo=True)
        j_utils.createSpSwConstraint([rigName+'_globalConst_GRP', par], name+'handIK_CTRL')
        if fkik:
            cmds.group(name+'armSettingsCtrl_ROOT', name+'armIKCtrls_GRP',
                       name+'armFKCtrls_GRP', name+'clavCtrl_ROOT', n=name+'armCtrls_GRP')
        else:
            cmds.group(name+'armIKCtrls_GRP', name+'clavCtrl_ROOT', n=name+'armCtrls_GRP')
    else:
        if fkik:
            cmds.parent(name+'armIKCtrls_GRP', name+'armFKCtrls_GRP', name+'armParentConst_GRP')
        else:
            cmds.parent(name+'armIKCtrls_GRP', name+'armParentConst_GRP')
        cmds.group(name+'armSettingsCtrl_ROOT', name+'armParentCtrl_ROOT', n=name+'armCtrls_GRP')
    ## IKFK ctrl visibilities
    if fkik:
        cmds.setDrivenKeyframe(name+'armFKCtrls_GRP', at='visibility',
                               cd=name+'armSettings_CTRL.IKFKSwitch', dv=0.001, v=1)
        cmds.setDrivenKeyframe(name+'armFKCtrls_GRP', at='visibility',
                               cd=name+'armSettings_CTRL.IKFKSwitch', dv=0, v=0)
        cmds.setDrivenKeyframe(name+'armIKCtrls_GRP', at='visibility',
                               cd=name+'armSettings_CTRL.IKFKSwitch', dv=0.999, v=1)
        cmds.setDrivenKeyframe(name+'armIKCtrls_GRP', at='visibility',
                               cd=name+'armSettings_CTRL.IKFKSwitch', dv=1, v=0)
    ## parent to overall rig stuffs
    if cmds.objExists(rigName+'_controls_GRP'):
        cmds.parent(name+'armCtrls_GRP', rigName+'_controls_GRP')
    if cmds.objExists(rigName+'_mechanics_GRP'):
        cmds.parent(name+'armMech_GRP', rigName+'_mechanics_GRP')
    if cmds.objExists(rigName+'_skeleton_GRP'):
        cmds.parent(name+'clav_JNT', rigName+'_skeleton_GRP')
    ## extra limb mechanics
    if stretchy:
        j_utils.createStretchyLimb(rigName, ['{0}shoulder{1}'.format(name, ikSuff),
                                             '{0}elbow{1}'.format(name, ikSuff),
                                             '{0}wrist{1}'.format(name, ikSuff)],
                                   '{0}arm'.format(name), '{0}clav_JNT'.format(name),
                                   '{0}handIKConst_GRP'.format(name),
                                   '{0}handIK_CTRL'.format(name), 'Upper Arm', 'Lower Arm',
                                   'Elbow Pin Toggle')
    cmds.select(cl=True)


def createFingerLocs(rigName, side, limbName, mirror=False, mirrorSide='R'):
    limbName, side_, name = nameStuff(rigName, limbName, side)
    suff = '_posLOC'
    ## create Locs
    (fngrIndexLocs,
     fngrMiddleLocs,
     fngrRingLocs,
     fngrPinkyLocs,
     fngrThumbLocs) = defaultLocData.getFngrLocData(j_wwiar_locScaleSpnBoxVal)
    if side.lower() == 'r' or 'right' in side.lower():
        j_utils.reverseLocPosValues(fngrIndexLocs)
        j_utils.reverseLocPosValues(fngrMiddleLocs)
        j_utils.reverseLocPosValues(fngrRingLocs)
        j_utils.reverseLocPosValues(fngrPinkyLocs)
        j_utils.reverseLocPosValues(fngrThumbLocs)

    fngrLocs = {
        (0, 'fngrIndexLocs', 'Index') : fngrIndexLocs,
        (1, 'fngrMiddleLocs', 'Middle') : fngrMiddleLocs,
        (2, 'fngrRingLocs', 'Ring') : fngrRingLocs,
        (3, 'fngrPinkyLocs', 'Pinky') : fngrPinkyLocs,
        (4, 'fngrThumbLocs', 'Thumb') : fngrThumbLocs,
    }

    ## create locs
    if not cmds.objExists('{0}wholeHand{1}'.format(name, suff)):
        mirror = False

    for k, v in fngrLocs.iteritems():
        fngrLocs[k] = j_utils.createLocs(v, name, suff, rigName=rigName, side=side_,
                                         limbName=limbName, mirror=mirror, mirSide=mirrorSide,
                                         scale=j_wwiar_locScaleSpnBoxVal)
    ## create parent curves
    fngrsList = [
        'Index',
        'Middle',
        'Ring',
        'Pinky',
        'Thumb',
    ]
    ##- hand parent curve
    origName = name
    handName, name = createParCrv(rigName, origName, suff, mirrorSide, limbName, '',
                                  mirror, 'Hand', 'wrist')
    if cmds.objExists('{0}wholeArm{1}'.format(name, suff)):
        cmds.parent('{0}wholeHand{1}'.format(name, suff), '{0}wholeArm{1}'.format(name, suff))
    ##- fingers parent curves
    for x in fngrsList:
        curFngrList = []
        for k, v in fngrLocs.iteritems():
            for sectKey, sectVal in v.iteritems():
                if x in sectKey[1]:
                    curFngrList.append(sectKey)
        fngrName, name = createParCrv(rigName, origName, suff, mirrorSide, limbName, curFngrList,
                                      mirror, 'Fngr{0}'.format(x), 'fngr{0}_base'.format(x))
        cmds.parent('{0}wholeFngr{1}{2}'.format(name, x, suff),
                    '{0}wholeHand{1}'.format(name, suff))
    for k, v in fngrLocs.iteritems():
        curFngr = k[2]
        createPvVis('fngr{0}_base'.format(curFngr), 'fngr{0}_lowMid'.format(curFngr),
                    'fngr{0}_tip'.format(curFngr), 'fngr{0}PvVis'.format(curFngr),
                    name, suff, handName, [3, 0, 0], 0.2)
    ## final stuff before returning
    cmds.select(cl=True)
    for k, v in fngrLocs.iteritems():
        sortedKeys = sorted(v)
        newKeys = []
        for x in sortedKeys:
            newKeys.append(x[1])
        fngrLocs[k] = newKeys
        j_utils.resizeLocs(newKeys, [0.2, 0.2, 0.2])
    return fngrLocs


def createFingerSkelMech(locs, rigName, side, limbName, par='wrist', fkik=None):
    limbName, side_, name = nameStuff(rigName, limbName, side)
    suff = '_JNT'
    if fkik:
        suff = '_result_JNT'
        ikSuff = '_IK_JNT'
        fkSuff = '_FK_JNT'
    else:
        ikSuff = '_JNT'
    par = name+par+suff

    col, altCol, thirdCol = getLeftRightColour(side)

    ## all finger ctrl
    j_utils.createCtrlShape(name+'fingers', 14, col=altCol, scale=[0.5, 0.3, 0.5],
                            rotOffset=[0, 0, -90], transOffset=[0, 3, 0], side=side,
                            globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer(name+'fingers', 1, 1, name+'handPalm_posLOC')
    j_utils.lockHideAttrs('{0}fingers_CTRL'.format(name), 'scale,')
    ## create jnts
    ikList = j_utils.createPhalanges(locs, name, side, side_, j_wwiar_ctrlScaleSpnBoxVal,
                                     par, thirdCol, fingers=True)
    # ikList = []
    # for k, v in locs.iteritems():
    #     curFngr = k[2]
    #     jnts = j_utils.createJnts(v, side=side_)
    #     if par is not '':
    #         for x in jnts:
    #             if '_base_' in x:
    #                 cmds.parent(x, par)

    #     ## create finger mech
    #     ik = j_utils.createIK(name+'fngr'+curFngr+'IK', name+'fngr'+curFngr+'_base_JNT',
    #                           name+'fngr'+curFngr+'_tip_JNT')
    #     ikList.append(ik[0])

    #     ## finger tips ctrls
    #     fngrCtrlPosLoc = cmds.spaceLocator(n='{0}fngr{1}_tip_LOC'.format(name, curFngr))
    #     tmpFngrCtrlConstr = cmds.parentConstraint('{0}fngr{1}_tip_JNT'.format(name, curFngr),
    #                                               fngrCtrlPosLoc)
    #     cmds.delete(tmpFngrCtrlConstr)
    #     cmds.setAttr('{0}.rotateX'.format(fngrCtrlPosLoc[0]), 0)
    #     j_utils.createCtrlShape(name+'fngr'+curFngr, 10, col=thirdCol, scale=[0.1, 0.1, 0.04],
    #                             side=side, globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    #     j_utils.createBuffer(name+'fngr'+curFngr, 1, 1, fngrCtrlPosLoc)
    #     j_utils.lockHideAttrs('{0}fngr{1}_CTRL'.format(name, curFngr), 'rotateY')
    #     j_utils.lockHideAttrs('{0}fngr{1}_CTRL'.format(name, curFngr), 'rotateZ')
    #     cmds.delete(fngrCtrlPosLoc)
    #     cmds.parentConstraint(name+'fngr'+curFngr+'Const_GRP', ik[1])
    #     if not curFngr == 'Thumb':
    #         cmds.parent(name+'fngr'+curFngr+'Ctrl_ROOT', name+'fingersConst_GRP')
    #     ## create pv controls
    #     pvPos = cmds.xform('{0}fngr{1}PvVis_posLOC'.format(name, curFngr),
    #                        q=True, t=True, ws=True)
    #     pvLoc = cmds.spaceLocator(n='{0}fngr{1}PV_LOC'.format(name, curFngr))
    #     cmds.xform(pvLoc[0], t=pvPos)
    #     cmds.makeIdentity(pvLoc[0], t=True)
    #     cmds.poleVectorConstraint(pvLoc[0], ik[1])
    #     newPvPos = cmds.xform('{0}fngr{1}_base_JNT'.format(name, curFngr),
    #                           q=True, t=True, ws=True)
    #     newPvPos[2] += 0.5
    #     cmds.xform(pvLoc[0], t=newPvPos)
    #     cmds.setAttr('{0}.twist'.format(ik[1]), -90)
    #     pvGrp = cmds.group(pvLoc, n='{0}fngr{1}PvLoc_GRP'.format(name, curFngr))
    #     baseJntPos = cmds.xform('{0}fngr{1}_base_JNT'.format(name, curFngr),
    #                           q=True, t=True, ws=True)
    #     cmds.xform(pvGrp, piv=baseJntPos)
    #     ikList.append(pvGrp)
    #     ##- add finger roll
    #     # cmds.addAttr('{0}fngr{1}_CTRL'.format(name, curFngr), ln='fngrRoll', nn='Finger Roll', k=True)
    #     # cmds.connectAttr('{0}fngr{1}_CTRL.fngrRoll'.format(name, curFngr),
    #     #                  '{0}.rotateX'.format(pvGrp))
    #     cmds.connectAttr('{0}fngr{1}_CTRL.rotateX'.format(name, curFngr),
    #                      '{0}.rotateX'.format(pvGrp))

    ## fkik hand parenting
    cmds.group(name+'fingersCtrl_ROOT', name+'fngrThumbCtrl_ROOT', n=name+'fingerCtrls_GRP')
    if fkik:
        fngrsConstr = cmds.parentConstraint(name+'wristFKConst_GRP', name+'handIKConst_GRP',
                                            name+'fingersCtrl_ROOT', mo=True)
        thumbConstr = cmds.parentConstraint(name+'wristFKConst_GRP', name+'handPalmIKConst_GRP',
                                            name+'fngrThumbCtrl_ROOT', mo=True)
        if not cmds.objExists(name+'armSettings_CTRLfkik_REV'):
            rev = cmds.createNode('reverse', n=name+'armSettings_CTRLfkik_REV')
            cmds.connectAttr(name+'armSettings_CTRL.IKFKSwitch',
                             name+'armSettings_CTRLfkik_REV.inputX')
        cmds.connectAttr(name+'armSettings_CTRL.IKFKSwitch',
                         fngrsConstr[0]+'.'+name+'wristFKConst_GRPW0')
        cmds.connectAttr(name+'armSettings_CTRLfkik_REV.outputX',
                         fngrsConstr[0]+'.'+name+'handIKConst_GRPW1')
        cmds.connectAttr(name+'armSettings_CTRL.IKFKSwitch',
                         thumbConstr[0]+'.'+name+'wristFKConst_GRPW0')
        cmds.connectAttr(name+'armSettings_CTRLfkik_REV.outputX',
                         thumbConstr[0]+'.'+name+'handPalmIKConst_GRPW1')

    ## organise shit
    cmds.group(ikList, n=name+'fingerIKs_GRP')
    cmds.parent(name+'fingerIKs_GRP', name+'handMech_GRP')
    cmds.parent(name+'fingerCtrls_GRP', name+'armCtrls_GRP')


def createToeLocs(rigName, side, limbName, mirror=False, mirrorSide='R'):
    limbName, side_, name = nameStuff(rigName, limbName, side)
    suff = '_posLOC'
    ## create locs
    (toeIndexLocs,
    toeMiddleLocs,
    toeRingLocs,
    toePinkyLocs,
    toeThumbLocs) = defaultLocData.getToeLocData(j_wwiar_locScaleSpnBoxVal)
    if side.lower() == 'r' or 'right' in side.lower():
        j_utils.reverseLocPosValues(toeIndexLocs)
        j_utils.reverseLocPosValues(toeMiddleLocs)
        j_utils.reverseLocPosValues(toeRingLocs)
        j_utils.reverseLocPosValues(toePinkyLocs)
        j_utils.reverseLocPosValues(toeThumbLocs)

    toeLocs = {
        (0, 'toeIndexLocs', 'Index') : toeIndexLocs,
        (1, 'toeMiddleLocs', 'Middle') : toeMiddleLocs,
        (2, 'toeRingLocs', 'Ring') : toeRingLocs,
        (3, 'toePinkyLocs', 'Pinky') : toePinkyLocs,
        (4, 'toeThumbLocs', 'Thumb') : toeThumbLocs,
    }

    ## create locs
    if not cmds.objExists('{0}wholeFoot{1}'.format(name, suff)):
        mirror = False

    for k, v in toeLocs.iteritems():
        toeLocs[k] = j_utils.createLocs(v, name, suff, rigName=rigName, side=side_,
                                        limbName=limbName, mirror=mirror, mirSide=mirrorSide,
                                        scale=j_wwiar_locScaleSpnBoxVal)
    ## create parent curves
    toesList = [
        'Index',
        'Middle',
        'Ring',
        'Pinky',
        'Thumb',
    ]
    ##- foot parent curve
    origName = name
    footName, name = createParCrv(rigName, origName, suff, mirrorSide, limbName, '',
                                  mirror, 'Foot', 'ankle')
    if cmds.objExists('{0}wholeLeg{1}'.format(name, suff)):
        cmds.parent('{0}wholeFoot{1}'.format(name, suff), '{0}wholeLeg{1}'.format(name, suff))
    ##- toe parent curves
    for x in toesList:
        curToeList = []
        for k, v in toeLocs.iteritems():
            for sectKey, sectVal in v.iteritems():
                if x in sectKey[1]:
                    curToeList.append(sectKey)
        toeName, name = createParCrv(rigName, origName, suff, mirrorSide, limbName, curToeList,
                                     mirror, 'Toe{0}'.format(x), 'toe{0}_base'.format(x))
        cmds.parent('{0}wholeToe{1}{2}'.format(name, x, suff),
                    '{0}wholeFoot{1}'.format(name, suff))
    for k, v in toeLocs.iteritems():
        curToe = k[2]
        createPvVis('toe{0}_base'.format(curToe), 'toe{0}_lowMid'.format(curToe),
                    'toe{0}_tip'.format(curToe), 'toe{0}PvVis'.format(curToe),
                    name, suff, footName, [3, 0, 0], 0.2)

    cmds.select(cl=True)
    for k, v in toeLocs.iteritems():
        sortedKeys = sorted(v)
        newKeys = []
        for x in sortedKeys:
            newKeys.append(x[1])
        toeLocs[k] = newKeys
        j_utils.resizeLocs(newKeys, [0.2, 0.2, 0.2])
    return toeLocs


def createToeSkelMech(locs, rigName, side, limbName, par='ankle', fkik=None):
    limbName, side_, name = nameStuff(rigName, limbName, side)
    suff = '_JNT'
    if fkik:
        suff = '_result_JNT'
        ikSuff = '_IK_JNT'
        fkSuff = '_FK_JNT'
    else:
        ikSuff = '_JNT'
    par = name+par+suff

    col, altCol, thirdCol = getLeftRightColour(side)

    ## all toes ctrl - created in leg instead {might need changing}
    if not cmds.objExists(name+'footToesIK_CTRL'):
        j_utils.createCtrlShape(name+'footToesIK', 9, col=altCol, scale=[0.7, 0.35, 0.35],
                                rotOffset=[75, 15, 0], transOffset=[0, 0.35, 0], side=side,
                                globalScale=j_wwiar_ctrlScaleSpnBoxVal)
        j_utils.createBuffer(name+'footToesIK', 1, 1, name+'footToes_posLOC')
        footBallLoc = cmds.xform(name+'footBall_posLOC', q=True, ws=True, t=True)
        cmds.xform(name+'footToesIK_CTRL', piv=footBallLoc)
    ## create jnts
    ikList = j_utils.createPhalanges(locs, name, side, side_, j_wwiar_ctrlScaleSpnBoxVal,
                                     par, thirdCol)
    # ikList = []
    # for k, v in locs.iteritems():
    #     curToe = k[2]
    #     jnts = j_utils.createJnts(v, side=side_)
    #     if par is not '':
    #         for x in jnts:
    #             if '_base_' in x:
    #                 cmds.parent(x, par)

    #     ## create toe mech
    #     ik = j_utils.createIK(name+'toe'+curToe+'IK', name+'toe'+curToe+'_base_JNT',
    #                           name+'toe'+curToe+'_tip_JNT')
    #     ikList.append(ik[0])

    #     ## create toe tip ctrls
    #     j_utils.createCtrlShape(name+'toe'+curToe, 10, col=thirdCol, scale=[0.04, 0.04, 0.016],
    #                             side=side, rotOffset=[90, -60, -90], transOffset=[0, 1.5, 0],
    #                             globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    #     j_utils.createBuffer(name+'toe'+curToe, 1, 1, name+'toe'+curToe+'_tip_posLOC')
    #     cmds.parentConstraint(name+'toe'+curToe+'Const_GRP', ik[1])
    #     cmds.parent(name+'toe'+curToe+'Ctrl_ROOT', name+'footToesIKConst_GRP')
    #     ## create pv ctrls
    #     if cmds.objExists(name+'toe'+curToe+'PVCtrl_ROOT'):
    #         cmds.delete(name+'toe'+curToe+'PVCtrl_ROOT')
    #     j_utils.createCtrlShape(name+'toe'+curToe+'PV', 4, col=thirdCol, scale=[0.05, 0.05, 0.05],
    #                             globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    #     j_utils.createBuffer(name+'toe'+curToe+'PV', 1, 1, name+'toe'+curToe+'PvVis_posLOC')
    #     cmds.parent(name+'toe'+curToe+'PVCtrl_ROOT', name+'toe'+curToe+'Const_GRP')
    #     cmds.poleVectorConstraint(name+'toe'+curToe+'PVConst_GRP', ik[1])

    ## organise shit
    cmds.group(ikList, n=name+'toeIKs_GRP')
    cmds.parent(name+'toeIKs_GRP', name+'footMech_GRP')


def createSpineLocs(rigName):
    name = str(rigName)+'_'
    suff = '_posLOC'
    if cmds.objExists('{0}spine_posCRV'.format(name)):
        spineCrv = cmds.rebuildCurve('{0}spine_posCRV'.format(name), rpo=True, rt=True)
    else:
        spineCrv = cmds.curve(n='{0}spine_posCRV'.format(name), degree = 3,
                knot = [
                        0, 0, 0, 1, 2, 3, 4, 5, 5, 5\
                ],
                point = [
                            (0.0, 9.70, -0.70),\
                            (0.0, 10.00, -0.60),\
                            (0.0, 10.80, -0.50),\
                            (0.0, 11.60, -0.50),\
                            (0.0, 12.30, -0.60),\
                            (0.0, 13.50, -1.00),\
                            (0.0, 14.30, -1.00),\
                            (0.0, 14.70, -0.90)\
                ]
        )
        cmds.xform(spineCrv, cp=True)
        cmds.xform(spineCrv, s=[j_wwiar_locScaleSpnBoxVal,
                                j_wwiar_locScaleSpnBoxVal,
                                j_wwiar_locScaleSpnBoxVal])
    return spineCrv


def createSpineSkelMech(rigName, jntNum, spineCrv):
    name = str(rigName)+'_'
    suff = '_posLOC'

    col = j_wwiar_main1SpnBoxVal
    altCol = j_wwiar_main2SpnBoxVal
    thirdCol = j_wwiar_main3SpnBoxVal

    spineLocs = j_utils.createLocsOnCurve(rigName, jntNum, spineCrv,
                                          scale=j_wwiar_locScaleSpnBoxVal)
    j_utils.createJnts(spineLocs)
    if cmds.objExists(name+'spineIK_hips_BIND') or cmds.objExists(name+'spineIK_chest_BIND'):
        cmds.delete(name+'spineIK_hips_BIND')
        cmds.delete(name+'spineIK_chest_BIND')
    if jntNum < 12:
        chestJnt = str(jntNum/2).zfill(2)
        spineArmJnt = str(jntNum-2).zfill(2)
    elif jntNum < 102:
        chestJnt = str(jntNum/2).zfill(3)
        spineArmJnt = str(jntNum-2).zfill(3)
    else:
        chestJnt = str(jntNum/2).zfill(4)
        spineArmJnt = str(jntNum-2).zfill(4)
    ##- create bind jnts
    cmds.duplicate(name+'spine_base_JNT', n=name+'spineIK_hips_BIND', po=True)
    cmds.duplicate(name+'spine_'+chestJnt+'_JNT', n=name+'spineIK_chest_BIND', po=True)
    cmds.parent(name+'spineIK_chest_BIND', w=True)
    cmds.group(name+'spineIK_hips_BIND', n=name+'spineIK_hipsMech_GRP')
    cmds.group(name+'spineIK_chest_BIND', n=name+'spineIK_chestMech_GRP')
    ##- create spine IK end locators
    cmds.spaceLocator(n=name+'spineIK_base_LOC')
    constr = cmds.parentConstraint(name+'spine_base_JNT', name+'spineIK_base_LOC')
    cmds.delete(constr)
    cmds.parent(name+'spineIK_base_LOC', name+'spineIK_hips_BIND')
    cmds.spaceLocator(n=name+'spineIK_end_LOC')
    constr = cmds.parentConstraint(name+'spine_end_JNT', name+'spineIK_end_LOC')
    cmds.delete(constr)
    cmds.parent(name+'spineIK_end_LOC', name+'spineIK_chest_BIND')
    ## create ctrls
    ##- hips
    j_utils.createCtrlShape(name+'hips', 5, col=col, globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer(name+'hips', 1, 1, name+'spineIK_hipsMech_GRP')
    cmds.parentConstraint(name+'hipsConst_GRP',name+'spineIK_hipsMech_GRP',mo=True)
    cmds.addAttr(name+'hips_CTRL', ln='twist', at='float', k=True)
    cmds.connectAttr(name+'hips_CTRL.twist', name+'spineIK_base_LOC.rotateX')
    ##- chest
    j_utils.createCtrlShape(name+'chest', 5, col=altCol, globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer(name+'chest', 1, 1, name+'spineIK_chestMech_GRP')
    cmds.parentConstraint(name+'chestConst_GRP', name+'spineIK_chestMech_GRP', mo=True)
    cmds.addAttr(name+'chest_CTRL', ln='twist', at='float', k=True)
    cmds.connectAttr(name+'chest_CTRL.twist', name+'spineIK_end_LOC.rotateX')
    ##- body
    j_utils.createCtrlShape(name+'body', 13, col=altCol, globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer(name+'body', 1, 1, name+'spineIK_hipsMech_GRP')
    cmds.parent(name+'hipsCtrl_ROOT', name+'chestCtrl_ROOT', name+'bodyConst_GRP')
    ## create spine IK
    j_utils.createSplineIK(name+'spine_base_JNT', name+'spine_end_JNT',
                           name+'spineIK', name+'global_CTRL', '{0}chest_CTRL'.format(name))
    cmds.group(name+'spineIK_hipsMech_GRP', name+'spineIK_chestMech_GRP', name+'spineIK_GRP',
               n=name+'spineIKMech_GRP')
    ##- skin bind jnts to crv
    cmds.skinCluster(name+'spineIK_hips_BIND', name+'spineIK_chest_BIND', name+'spineIK_CRV')
    ##- spine IK adv twist
    cmds.setAttr(name+'spineIK_HDL.dTwistControlEnable', 1)
    cmds.setAttr(name+'spineIK_HDL.dWorldUpType', 4)
    cmds.connectAttr(name+'spineIK_base_LOC.worldMatrix[0]', name+'spineIK_HDL.dWorldUpMatrix')
    cmds.connectAttr(name+'spineIK_end_LOC.worldMatrix[0]', name+'spineIK_HDL.dWorldUpMatrixEnd')
    ##- dynamic pivot
    j_utils.createCtrlShape('{0}bodyPivot'.format(name), 18, scale=[0.3, 0.3, 0.3],
                            col=thirdCol, rotOffset=[0, 0, 90],
                            globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer('{0}bodyPivot'.format(name), 1, 1,
                         '{0}spineIK_hipsMech_GRP'.format(name))
    j_utils.lockHideAttrs('{0}bodyPivot_CTRL'.format(name), 'scale,')
    cmds.connectAttr('{0}bodyPivot_CTRL.translate'.format(name),
                     '{0}bodyCtrl_ROOT.translate'.format(name))
    cmds.connectAttr('{0}bodyPivot_CTRL.rotate'.format(name),
                     '{0}bodyCtrl_ROOT.rotate'.format(name))
    pivTransDiv = cmds.createNode('multiplyDivide', n='{0}bodyPivTrans_DIV'.format(name))
    cmds.connectAttr('{0}bodyPivot_CTRL.translate'.format(name),
                     '{0}.input1'.format(pivTransDiv))
    cmds.setAttr('{0}.input2'.format(pivTransDiv), -1, -1, -1)
    cmds.connectAttr('{0}.output'.format(pivTransDiv), '{0}bodyCtrl_PAR.translate'.format(name))
    cmds.parent('{0}bodyPivotCtrl_ROOT'.format(name), '{0}controls_GRP'.format(name))
    ## clean shit up
    if cmds.objExists(rigName+'_controls_GRP'):
        cmds.parent(name+'bodyCtrl_ROOT', rigName+'_controls_GRP')
    if cmds.objExists(rigName+'_mechanics_GRP'):
        cmds.parent(name+'spineIKMech_GRP', rigName+'_mechanics_GRP')
    if cmds.objExists(rigName+'_skeleton_GRP'):
        cmds.parent(name+'spine_base_JNT', rigName+'_skeleton_GRP')
    cmds.select(cl=True)
    return spineArmJnt


def createHeadLocs(rigName, side, limbName, mirror=False, mirrorSide='R'):
    limbName, side_, name = nameStuff(rigName, limbName, side)
    suff = '_posLOC'

    ## get loc positions
    headLocs, headAimPos = defaultLocData.getHeadLocData(j_wwiar_locScaleSpnBoxVal, side)
    # if ((side is not 'L' and 'L_' not in side and '_L' not in side)
    #         and (side is 'R' or 'R_' in side or '_R' in side)):
    if side.lower() == 'r' or 'right' in side.lower():
        j_utils.reverseLocPosValues(headLocs)
        headAimPos[0] = -1

    ## create locs
    if not cmds.objExists('{0}wholeHead{1}'.format(name, suff)):
        mirror = False
    if cmds.objExists('{0}headAim{1}_parentConstraint1'.format(name, suff)):
        cmds.delete('{0}headAim{1}_parentConstraint1'.format(name, suff))
    j_utils.createLocs(headLocs, name, suff, rigName=rigName, side=side_,
                       limbName=limbName, mirror=mirror, mirSide=mirrorSide,
                       scale=j_wwiar_locScaleSpnBoxVal)
    headName, name = createParCrv(rigName, name, suff, mirrorSide, limbName, headLocs, mirror,
                                  'Head', 'head')
    j_utils.createSingleLoc('headAim', name, suff, headAimPos, side=side,
                            par=('{0}head{1}'.format(name, suff),
                                 '{0}headEnd{1}'.format(name, suff)),
                            limbName=limbName, mirror=mirror, mirSide=mirrorSide,
                            prefix=rigName, scale=j_wwiar_locScaleSpnBoxVal)
    cmds.parent('{0}headAim{1}'.format(name, suff), '{0}wholeHead{1}'.format(name, suff))
    cmds.select(cl=True)
    sortedKeys = sorted(headLocs)
    returnKeys = []
    for x in sortedKeys:
        returnKeys.append(x[1])
    return returnKeys, headName


def createHeadSkelMech(locs, rigName, side, limbName, par='', suff='_posLOC', ik=None):
    limbName, side_, name = nameStuff(rigName, limbName, side)

    if side.lower() == 'l' or 'left' in side.lower():
        col = j_wwiar_left1SpnBoxVal
    elif side.lower() == 'r' or 'right' in side.lower():
        col = j_wwiar_right1SpnBoxVal
    else:
        col = j_wwiar_main3SpnBoxVal

    ## mechanics
    if par is not '' and ik:
        ## controls
        ##- head
        j_utils.createCtrlShape(name+'head', 5, col=col, scale=[0.7, 0.7, 0.7],
                                transOffset=[0, 1, 0.5], globalScale=j_wwiar_ctrlScaleSpnBoxVal)
        ##- head aim ctrl
        j_utils.createCtrlShape(name+'headAim', 6, col=col, scale=[0.65, 0.65, 0.65],
                                rotOffset=[90, 0, 0], globalScale=j_wwiar_ctrlScaleSpnBoxVal)
        j_utils.createBuffer(name+'headAim', 1, 1, name+'headAim_posLOC')
        j_utils.lockHideAttrs('{0}headAim_CTRL'.format(name), 'rotate,')
        jnts = j_utils.createJnts(locs, side=side, par=par)
        neckIK = j_utils.createIK(name+'neckIK', par, name+'head_JNT')
        headIK = j_utils.createIK(name+'headIK', name+'head_JNT', name+'headEnd_JNT')
        cmds.group(neckIK[0], headIK[0], n=name+'headIKs_GRP')
        cmds.group('{0}headIKs_GRP'.format(name), n='{0}headMech_GRP'.format(name))
        ## head control buffer
        j_utils.createBuffer(name+'head', 1, 1, neckIK[1])
        cmds.parentConstraint(name+'headConst_GRP', name+'headIKs_GRP', mo=True)
        ## remove neck ik if one already exists
        childEff = cmds.listRelatives(par, typ='ikEffector')
        if not childEff == [neckIK[-1]]:
            cmds.delete(neckIK)
        cmds.group(name+'headCtrl_ROOT', name+'headAimCtrl_ROOT', n=name+'headCtrls_GRP')
        aimConstr = cmds.aimConstraint(name+'headAimConst_GRP', name+'headCtrl_ROOT', mo=True)
        ##- headAim up locator
        headUpAimPos = cmds.xform(headIK[1], q=True, t=True, ws=True)
        headUpAimPos[1] += 1
        cmds.spaceLocator(n='{0}headAimUp_LOC'.format(name))
        cmds.xform('{0}headAimUp_LOC'.format(name), t=headUpAimPos)
        cmds.setAttr('{0}.worldUpType'.format(aimConstr[0]), 2)
        cmds.connectAttr('{0}headAimUp_LOC.worldMatrix'.format(name),
                         '{0}.worldUpMatrix'.format(aimConstr[0]))
        cmds.parent('{0}headAimUp_LOC'.format(name), '{0}headMech_GRP'.format(name))
        cmds.parentConstraint('{0}headCtrls_GRP'.format(name),
                              '{0}headAimUp_LOC'.format(name), mo=True)
    else:
        neckIK = None
        if par is '':
            ##- head ctrl
            j_utils.createCtrlShape(name+'head', 5, col=col,
                                    scale=[0.7, 0.7, 0.7], transOffset=[0, 1, 0.5],
                                    globalScale=j_wwiar_ctrlScaleSpnBoxVal)
            endLocTrans = cmds.xform(locs[-1], q=True, t=True, ws=True)
            headTmpName = j_utils.createSingleLoc('headTmp', name, suff, endLocTrans,
                                                  scale=j_wwiar_locScaleSpnBoxVal)
            locs.append(headTmpName)
            jnts = j_utils.createJnts(locs, side=side)
            cmds.parent(name+'head_JNT', rigName+'_skeleton_GRP')
            cmds.delete(jnts[-1], headTmpName)
            baseLocTrans = cmds.xform(locs[0], q=True, t=True, ws=True)
            headBaseTmpName = j_utils.createSingleLoc('headBaseTmp', name, suff, baseLocTrans,
                                                      scale=j_wwiar_locScaleSpnBoxVal)
            j_utils.createBuffer(name+'head', 1, 1, name+'headBaseTmp_posLOC')
            cmds.delete(headBaseTmpName)
            cmds.group(name+'headCtrl_ROOT', n=name+'headCtrls_GRP')
        else:
            jnts = j_utils.createJnts(locs, side=side, par=par)
            ##- head ctrl
            j_utils.createCtrlShape(name+'head', 5, col=col, scale=[0.7, 0.7, 0.7],
                                    transOffset=[0, 1, 0.5], rotOffset=[0, 180, 90],
                                    globalScale=j_wwiar_ctrlScaleSpnBoxVal)
            j_utils.createBuffer(name+'head', 1, 1, name+'head_JNT')
            j_utils.createCtrlShape(name+'neck', 3, col=col, scale=[0.7, 0.7, 0.7],
                                    rotOffset=[0,0,90],
                                    globalScale=j_wwiar_ctrlScaleSpnBoxVal)
            j_utils.createBuffer(name+'neck', 1, 1, par)
            j_utils.lockHideAttrs('{0}neck_CTRL'.format(name), 'translate,')
            cmds.orientConstraint(name+'neckConst_GRP', par, mo=True)
            cmds.parent(name+'headCtrl_ROOT', name+'neckConst_GRP')
            cmds.group(name+'neckCtrl_ROOT', n=name+'headCtrls_GRP')
        cmds.parentConstraint(name+'headConst_GRP', name+'head_JNT', mo=True)
    if par is not '':
        grndPar = cmds.listRelatives(par, p=True)
        j_utils.createSpSwConstraint([rigName+'_globalConst_GRP', grndPar[0]], name+'head_CTRL',
                                     constrTarget=name+'headCtrls_GRP', dv=1)
    ## clean shit up
    if cmds.objExists(rigName+'_controls_GRP'):
        cmds.parent(name+'headCtrls_GRP', rigName+'_controls_GRP')
    if cmds.objExists(rigName+'_mechanics_GRP') and neckIK:
        cmds.parent(name+'headMech_GRP', rigName+'_mechanics_GRP')


def createParCrv(rigName, name, suff, mirrorSide, limbName, locs, mirror, limb, base):
    origName = name
    wholeLimb = '{0}whole{1}{2}'.format(name, limb, suff)
    if cmds.objExists(wholeLimb):
        baseLocPos = cmds.xform('{0}whole{1}{2}'.format(origName, limb, suff),
                                q=True, t=True, ws=True)
        baseLocRot = cmds.xform('{0}whole{1}{2}'.format(origName, limb, suff),
                                q=True, ro=True, ws=True)
        if mirror:
            name = '{0}_{1}_{2}'.format(rigName, mirrorSide, limbName)
            wholeLimb = '{0}whole{1}{2}'.format(name, limb, suff)
            baseLocPos[0] *= -1
            baseLocRot[1] *= -1
            baseLocRot[2] *= -1
        limbChildren = cmds.listRelatives(wholeLimb, c=True, typ='transform')
        if limbChildren:
            cmds.parent(limbChildren, w=True)
        cmds.delete(wholeLimb)
    else:
        baseLocPos = cmds.xform('{0}{1}{2}'.format(name, base, suff),
                                    q=True, t=True, ws=True)
        baseLocRot = cmds.xform('{0}{1}{2}'.format(name, base, suff),
                                    q=True, ro=True, ws=True)
    parCrv = createParCrvShape('whole{0}'.format(limb), locs, name, suff,
                           xyz=baseLocPos, rotXyz=baseLocRot, freeze=False)
    return parCrv, name


def createParCrvShape(crvName, locs, name, suff, xyz=[0, 0, 0], rotXyz=[0, 0, 0], freeze=True):
    parCrvName = name+crvName+suff
    if not cmds.objExists(parCrvName):
        parCrv = cmds.circle(n=parCrvName)
        cmds.delete(parCrv, ch=True)
        cmds.xform(parCrvName, t=(xyz[0], xyz[1], xyz[2]), ro=(rotXyz[0], rotXyz[1], rotXyz[2]),
                   s=[j_wwiar_locScaleSpnBoxVal,
                      j_wwiar_locScaleSpnBoxVal,
                      j_wwiar_locScaleSpnBoxVal])
        if freeze:
            cmds.makeIdentity(parCrvName, a=True, t=True)
        for x in locs:
            cmds.parent(x[1],parCrvName)
    return parCrvName


def createPvVis(strtJnt, aimJnt, endJnt, locName, name, suff, parName, xyz=[0, 0, 0], dist=1):
    dist *= j_wwiar_locScaleSpnBoxVal
    pvParName = '{0}{1}Par{2}'.format(name, locName, suff)
    if cmds.objExists(pvParName):
        pvParData = j_utils.getExistingLocData(pvParName)
        cmds.delete(pvParName)
    else:
        pvParData = {
            'localScale' : [(3, 0, 0)],
        }
    cmds.spaceLocator(n=pvParName)
    cmds.parent(pvParName, parName)
    cmds.pointConstraint('{0}{1}{2}'.format(name, strtJnt, suff),
                         '{0}{1}{2}'.format(name, endJnt, suff),
                         pvParName)
    cmds.aimConstraint('{0}{1}{2}'.format(name, aimJnt, suff), pvParName)
    j_utils.resizeLocs([pvParName], size=[pvParData['localScale'][0][0],
                                          pvParData['localScale'][0][1],
                                          pvParData['localScale'][0][2]])
    cmds.setAttr('{0}.overrideEnabled'.format(pvParName), 1)
    cmds.setAttr('{0}.overrideDisplayType'.format(pvParName), 1)
    ## create moveable PV control loc
    pvName = '{0}{1}{2}'.format(name, locName, suff)
    if cmds.objExists(pvName):
        pvData = j_utils.getExistingLocData(pvName)
        cmds.delete(pvName)
    else:
        pvData = {
            'localScale' : [(j_wwiar_locScaleSpnBoxVal*0.5,
                             j_wwiar_locScaleSpnBoxVal*0.5,
                             j_wwiar_locScaleSpnBoxVal*0.5)],
            'pvDist' : dist,
        }
    cmds.spaceLocator(n=pvName)
    cmds.parent(pvName, parName)
    cmds.delete(cmds.parentConstraint(pvParName, pvName))
    cmds.xform(pvName, t=xyz, r=True, os=True)
    cmds.parentConstraint(pvParName, pvName, mo=True)
    j_utils.lockHideAttrs(pvName, 'translate, rotate,')
    cmds.addAttr(pvName, sn='pvDis', nn='Pole Vector Distance', dv=1.0, h=False, k=True)
    cmds.connectAttr('{0}.pvDis'.format(pvName), '{0}.scaleX'.format(pvParName))
    cmds.setAttr('{0}.pvDis'.format(pvName), pvData['pvDist'])
    j_utils.resizeLocs([pvName], size=[pvData['localScale'][0][0],
                                       pvData['localScale'][0][1],
                                       pvData['localScale'][0][2]])


def createIkfkVis(crvName, jntPar, name, suff, side, xyz=[0.5, 0.25, -0.5]):
    ikfkName = '{0}{1}{2}'.format(name, crvName, suff)
    if cmds.objExists(ikfkName):
        ikfkData = j_utils.getExistingLocData(ikfkName)
        cmds.delete(ikfkName)
    else:
        ikfkData = {
            'translate' : xyz,
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(0.5, 0.5, 0.5)],
        }
    if side is 'R' or '_R' in side or 'R_' in side:
        ikfkData['translate'][0] *= -1
    locator = cmds.spaceLocator(n=ikfkName)
    cmds.xform(ikfkName, t=ikfkData['translate'])
    cmds.parent(ikfkName, '{0}{1}{2}'.format(name, jntPar, suff), r=True)
    j_utils.resizeLocs([ikfkName], size=[ikfkData['localScale'][0][0],
                                         ikfkData['localScale'][0][1],
                                         ikfkData['localScale'][0][2]])


def nameStuff(rigName, limbName, side):
    if limbName is not '':
        limbName = '{0}_'.format(limbName)
    if side is not '':
        side_ = '{0}_'.format(side)
    else:
        side_ = side
    name = '{0}_{1}{2}'.format(rigName, side_, limbName)
    return limbName, side_, name


def getLeftRightColour(side):
    if side.lower() == 'l' or 'left' in side.lower():
        col = j_wwiar_left1SpnBoxVal
        altCol = j_wwiar_left2SpnBoxVal
        thirdCol = j_wwiar_left3SpnBoxVal
    elif side.lower() == 'r' or 'right' in side.lower():
        col = j_wwiar_right1SpnBoxVal
        altCol = j_wwiar_right2SpnBoxVal
        thirdCol = j_wwiar_right3SpnBoxVal
    else:
        col = j_wwiar_main2SpnBoxVal
        altCol = j_wwiar_main1SpnBoxVal
        thirdCol = j_wwiar_main3SpnBoxVal
    return col, altCol, thirdCol


def createBaseMech(fkik, jnts, rigName, name, side_, limbName, suff, col, start, end, chain):
    parJnt = '{0}{1}{2}'.format(name, end, suff)

    if fkik:
        j_utils.createFKIK(
            jnts, chain, rigName, side_, limbName, parJnt,
            [j_wwiar_settings1SpnBoxVal, j_wwiar_settings2SpnBoxVal, j_wwiar_settings3SpnBoxVal],
            globalScale=j_wwiar_ctrlScaleSpnBoxVal)
        suff = '_result_JNT'
        ikSuff = '_IK_JNT'
        fkSuff = '_FK_JNT'
    else:
        ikSuff = '_JNT'
        fkSuff = '_JNT'
    ## create mech
    ##- IK mechanics
    IK = j_utils.createIK('{0}{1}IK'.format(name, chain),
                             '{0}{1}{2}'.format(name, start, ikSuff),
                             '{0}{1}{2}'.format(name, end, ikSuff))
    if cmds.objExists('{0}{1}PVCtrl_ROOT'.format(name, chain)):
        cmds.delete('{0}{1}PVCtrl_ROOT'.format(name, chain))
    ##- pv ctrl
    j_utils.createCtrlShape('{0}{1}PV'.format(name, chain), 4, scale=[0.3, 0.3, 0.3],
                            col=col, globalScale=j_wwiar_ctrlScaleSpnBoxVal)
    j_utils.createBuffer('{0}{1}PV'.format(name, chain), 1, 1,
                         '{0}{1}PvVis_posLOC'.format(name, chain))
    j_utils.lockHideAttrs('{0}{1}PV_CTRL'.format(name, chain), 'rotate, scale,')
    cmds.poleVectorConstraint('{0}{1}PVConst_GRP'.format(name, chain), IK[1])

    return suff, ikSuff, fkSuff, IK


def updateRigName():
    global j_wwiar_rigName
    if not j_wwiar_rigNameTxt:
        if j_wwiar_rigMode:
            j_wwiar_rigName = 'Quadruped'
        else:
            j_wwiar_rigName = 'Biped'
    else:
        j_wwiar_rigName = j_wwiar_rigNameTxt


def getNewLocData(rigName):
    locData = {
        'locators' : {}
    }
    hierarchy = cmds.listRelatives('{0}_rigPreviewLocs_GRP'.format(rigName), ad=True, typ='transform')
    for obj in hierarchy:
        if obj.endswith('_posLOC') and 'whole' not in obj:
            locData['locators'][str(obj)] = j_utils.getExistingLocData(obj)
    return locData


def saveLocsToJson(fileName, rigName, uiData):
    locs = getNewLocData(rigName)
    locs['rigName'] = rigName
    locs['ui'] = uiData
    with open(fileName, 'w') as f:
        json.dump(locs, f, indent=4)


def loadLocsFromJson(fileName):
    with open(fileName, 'r') as f:
        fileContents = json.load(f)
    rigName = fileContents['rigName']
    locs = fileContents['locators']
    ui = fileContents['ui']
    for x in locs.keys():
        locs[0, x] = locs.pop(x)
    j_utils.createLocs(locs, '', '', importFile=True)
    return rigName, locs, ui


def groupPreviewLocs(rigName, limbLocLists, spineCrv=None):
    parCrvsList = []
    prevGrpName = '{0}_rigPreviewLocs_GRP'.format(rigName)
    for x in limbLocLists:
        parCrvsList.append(x[8])
    if cmds.objExists(prevGrpName):
        childs = cmds.listRelatives(prevGrpName, c=True, typ='transform')
        if childs:
            cmds.parent(childs, w=True)
        cmds.delete(prevGrpName)
    #cmds.group(n=prevGrpName, em=True)
    prevCrv = cmds.circle(n=prevGrpName, nr=[0, 1, 0], r=j_wwiar_locScaleSpnBoxVal*4)
    cmds.delete(prevCrv, ch=True)
    if spineCrv:
        cmds.parent(spineCrv, '{0}_spine_posGRP'.format(rigName), prevGrpName)
    for x in parCrvsList:
        cmds.parent(x, prevGrpName)
    cmds.select(cl=True)


def mirrorSingleLimb(rigName, limb):
    limbLocLists = []
    for x in limb:
        extraLocsList = None
        mirExtraLocsList = None
        fkik = False
        ik = False
        parCrv = None
        ## arm
        if eval('j_wwiar_limbType_'+x+'Val') == 0:
            locsList, parCrv = eval('createArmLocs( \
                rigName, j_wwiar_limbSide_'+x+'Val, j_wwiar_limbName_'+x+'Val, \
                True, j_wwiar_limbMirName_'+x+'Val)')
            if eval('j_wwiar_limbOpt1_'+x+'Val') == 2:
                extraLocsList = eval('createFingerLocs( \
                    rigName, j_wwiar_limbSide_'+x+'Val, j_wwiar_limbName_'+x+'Val, \
                    True, j_wwiar_limbMirName_'+x+'Val)')

        ## leg
        elif eval('j_wwiar_limbType_'+x+'Val') == 1:
            locsList, parCrv = eval('createLegLocs( \
                rigName, j_wwiar_limbSide_'+x+'Val, j_wwiar_limbName_'+x+'Val, \
                True, j_wwiar_limbMirName_'+x+'Val)')
            if eval('j_wwiar_limbOpt1_'+x+'Val') == 2:
                extraLocsList = eval('createToeLocs( \
                    rigName, j_wwiar_limbSide_'+x+'Val, j_wwiar_limbName_'+x+'Val, \
                    True, j_wwiar_limbMirName_'+x+'Val)')

        ## tail
        elif eval('j_wwiar_limbType_'+x+'Val') == 2:
            continue

        ## head
        else:
            locsList, parCrv = eval('createHeadLocs( \
                rigName, j_wwiar_limbSide_'+x+'Val, j_wwiar_limbName_'+x+'Val, \
                True, j_wwiar_limbMirName_'+x+'Val)')

        ## populate locator list
        limbLocLists.append((locsList, eval('j_wwiar_limbType_'+x+'Val'),
                             eval('j_wwiar_limbSide_'+x+'Val'),
                             eval('j_wwiar_limbParent_'+x+'Val'),
                             eval('j_wwiar_limbName_'+x+'Val'),
                             extraLocsList, fkik, ik, parCrv))

    return limbLocLists


def createAllLocs(rigName):
    if j_wwiar_spine:
        spineCrv = createSpineLocs(rigName)
        if type(spineCrv) is list:
            spineCrv = spineCrv[0]
        j_utils.createLocsOnCurve(rigName, j_wwiar_spineJntsNum, spineCrv,
                                  scale=j_wwiar_locScaleSpnBoxVal)
    limbLocLists = []
    for x in j_wwiar_currentLimbBoxes:
        extraLocsList = None
        mirExtraLocsList = None
        fkik = False
        ik = False
        parCrv = None
        stretchy = False
        ## arm
        if eval('j_wwiar_limbType_'+x+'Val') == 0:
            locsList, parCrv = eval('createArmLocs( \
                rigName, j_wwiar_limbSide_'+x+'Val, j_wwiar_limbName_'+x+'Val)')
            ##- fingers
            if eval('j_wwiar_limbOpt1_'+x+'Val') == 2:
                extraLocsList = eval('createFingerLocs( \
                    rigName, j_wwiar_limbSide_'+x+'Val, j_wwiar_limbName_'+x+'Val)')
            ##- mirrored
            if eval('j_wwiar_limbMirTog_'+x+'Val') == 2:
                mirLocsList, mirParCrv = eval('createArmLocs( \
                    rigName, j_wwiar_limbMirName_'+x+'Val, j_wwiar_limbName_'+x+'Val)')
                ##-- mirrored fingers
                if eval('j_wwiar_limbOpt1_'+x+'Val') == 2:
                    mirExtraLocsList = eval('createFingerLocs( \
                        rigName, j_wwiar_limbMirName_'+x+'Val, j_wwiar_limbName_'+x+'Val)')
            else:
                mirLocsList = None
            ##- fk/ik
            if eval('j_wwiar_limbOpt2_'+x+'Val') == 2:
                fkik = True
            ##- stretchy
            if eval('j_wwiar_limbOpt3_{0}Val'.format(x)) == 2:
                stretchy = True

        ## leg
        elif eval('j_wwiar_limbType_'+x+'Val') == 1:
            locsList, parCrv = eval('createLegLocs( \
                rigName, j_wwiar_limbSide_'+x+'Val, j_wwiar_limbName_'+x+'Val)')
            ##- toes
            if eval('j_wwiar_limbOpt1_'+x+'Val') == 2:
                extraLocsList = eval('createToeLocs( \
                    rigName, j_wwiar_limbSide_'+x+'Val, j_wwiar_limbName_'+x+'Val)')
            ##- mirrored
            if eval('j_wwiar_limbMirTog_'+x+'Val') == 2:
                mirLocsList, mirParCrv = eval('createLegLocs( \
                    rigName, j_wwiar_limbMirName_'+x+'Val, j_wwiar_limbName_'+x+'Val)')
                ##-- toes
                if eval('j_wwiar_limbOpt1_'+x+'Val') == 2:
                    mirExtraLocsList = eval('createToeLocs( \
                        rigName, j_wwiar_limbMirName_'+x+'Val, j_wwiar_limbName_'+x+'Val)')
            else:
                mirLocsList = None
            ##- fk/ik
            if eval('j_wwiar_limbOpt2_'+x+'Val') == 2:
                fkik = True
            ##- stretchy
            if eval('j_wwiar_limbOpt3_{0}Val'.format(x)) == 2:
                stretchy = True

        ## tail
        elif eval('j_wwiar_limbType_'+x+'Val') == 2:
            continue

        ## head
        else:
            locsList, parCrv = eval('createHeadLocs( \
                rigName, j_wwiar_limbSide_'+x+'Val, j_wwiar_limbName_'+x+'Val)')
            ##- mirror
            if eval('j_wwiar_limbMirTog_'+x+'Val') == 2:
                mirLocsList, mirParCrv = eval('createHeadLocs( \
                    rigName, j_wwiar_limbMirName_'+x+'Val, j_wwiar_limbName_'+x+'Val)')
            else:
                mirLocsList = None
            ##- ik
            if eval('j_wwiar_limbOpt1_'+x+'Val') == 2:
                ik = True

        ## populate locator list
        limbLocLists.append((locsList, eval('j_wwiar_limbType_'+x+'Val'),
                             eval('j_wwiar_limbSide_'+x+'Val'),
                             eval('j_wwiar_limbParent_'+x+'Val'),
                             eval('j_wwiar_limbName_'+x+'Val'),
                             extraLocsList, fkik, ik, parCrv, stretchy))
        if mirLocsList:
            limbLocLists.append((mirLocsList, eval('j_wwiar_limbType_'+x+'Val'),
                                 eval('j_wwiar_limbMirName_'+x+'Val'),
                                 eval('j_wwiar_limbParent_'+x+'Val'),
                                 eval('j_wwiar_limbName_'+x+'Val'),
                                 mirExtraLocsList, fkik, ik, mirParCrv, stretchy))
    if not j_wwiar_spine:
        spineCrv = None
    groupPreviewLocs(rigName, limbLocLists, spineCrv)

    return spineCrv, limbLocLists


def mirrorAllLocs(rigName):
    ## get limb boxes to be mirrored
    currentMirLimbBoxes = []
    for x in j_wwiar_currentLimbBoxes:
        if eval('j_wwiar_limbMirTog_{0}Val'.format(x)) == 2:
            currentMirLimbBoxes.append(x)
    ## mirror locators
    limbLocLists = mirrorSingleLimb(rigName, currentMirLimbBoxes)
    groupPreviewLocs(rigName, limbLocLists)


def createAllRig(rigName):
    createGlobalCtrl(rigName)
    spineCrv, allLocs = createAllLocs(rigName)
    if j_wwiar_spine:
        createSpineSkelMech(rigName, j_wwiar_spineJntsNum, spineCrv)
        groupPreviewLocs(rigName, allLocs, spineCrv)
    for locs, typ, side, par, limbName, extraLocs, fkik, ik, parCrv, stretchy in allLocs:
        if par is not '':
            par = '{0}_{1}_JNT'.format(rigName, par)
        if typ == 0:    # arm
            createArmSkelMech(locs, rigName, side, limbName, par, fkik=fkik, stretchy=stretchy)
            if extraLocs:
                createFingerSkelMech(extraLocs, rigName, side, limbName, fkik=fkik)
        elif typ == 1:  # leg
            createLegSkelMech(locs, rigName, side, limbName, par, fkik=fkik, stretchy=stretchy)
            if extraLocs:
                createToeSkelMech(extraLocs, rigName, side, limbName, fkik=fkik)
        elif typ == 2:  # tail
            continue
        else:   # head
            createHeadSkelMech(locs, rigName, side, limbName, par, ik=ik)


##

## UI STUFF

def maya_main_window():
    main_window_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def main():
    global myWindow

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
        self.ui = customUI.Ui_Form()

        self.ui.setupUi(self)

        ## connect inputs to functions
        self.ui.newEntry.clicked.connect(self.add)
        self.ui.clearEntries.clicked.connect(self.clear)
        self.ui.biRad.clicked.connect(partial(self.updateModeRad, False))
        self.ui.quadRad.clicked.connect(partial(self.updateModeRad, True))
        self.ui.nameEdit.textChanged.connect(self.updateName)
        self.ui.spineChkBox.stateChanged.connect(self.updateSpineChkBox)
        self.ui.spineSpnBox.valueChanged.connect(self.updateSpineSpnBox)
        self.ui.saveLocsBtn.clicked.connect(self.updateSaveLocsBtn)
        self.ui.loadLocsBtn.clicked.connect(self.updateLoadLocsBtn)
        self.ui.delLocsBtn.clicked.connect(self.updateDelLocsBtn)
        self.ui.main1SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'main1'))
        self.ui.main2SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'main2'))
        self.ui.main3SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'main3'))
        self.ui.left1SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'left1'))
        self.ui.left2SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'left2'))
        self.ui.left3SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'left3'))
        self.ui.right1SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'right1'))
        self.ui.right2SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'right2'))
        self.ui.right3SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'right3'))
        self.ui.settings1SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'settings1'))
        self.ui.settings2SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'settings2'))
        self.ui.settings3SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'settings3'))
        self.ui.misc1SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'misc1'))
        self.ui.misc2SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'misc2'))
        self.ui.misc3SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'misc3'))
        self.ui.locScaleSpnBox.valueChanged.connect(self.updateLocScaleSpnBox)
        self.ui.ctrlScaleSpnBox.valueChanged.connect(self.updateCtrlScaleSpnBox)
        self.ui.locsBtn.pressed.connect(self.updateLocsBtn)
        self.ui.mirrorBtn.pressed.connect(self.updateMirrorBtn)
        self.ui.createBtn.pressed.connect(self.updateCreateBtn)

        self.updateColSpnBox('main1', '11')
        self.updateColSpnBox('main2', '23')
        self.updateColSpnBox('main3', '24')
        self.updateColSpnBox('left1', '16')
        self.updateColSpnBox('left2', '29')
        self.updateColSpnBox('left3', '30')
        self.updateColSpnBox('right1', '13')
        self.updateColSpnBox('right2', '25')
        self.updateColSpnBox('right3', '22')
        self.updateColSpnBox('settings1', '27')
        self.updateColSpnBox('settings2', '32')
        self.updateColSpnBox('settings3', '8')
        self.updateColSpnBox('misc1', '31')
        self.updateColSpnBox('misc2', '1')
        self.updateColSpnBox('misc3', '1')

        for i in range(3):
            if i > 1:
                self.add(typ=1)
            elif i > 0:
                self.add(typ=0)
            else:
                self.add(typ=3)

    def add(self, typ=0, loadVal=None, *args):
        global j_wwiar_limbBoxNum
        global j_wwiar_currentLimbBoxes
        j_wwiar_limbBoxNum += 1
        num = str(j_wwiar_limbBoxNum)
        j_wwiar_currentLimbBoxes.append(num)
        ## set default mirror
        if typ == 0 or typ == 1:    ## arms or legs
            mir = True
        else:   ## tail or head
            mir = False
        ## create limb entry
        exec('self.limbBox_{0} = QtWidgets.QWidget(self.ui.scrollAreaWidgetContents)'.format(num))
        exec('self.limbBox_{0}.setMinimumSize(QtCore.QSize(400, 60))'.format(num))
        exec('self.limbBox_{0}.setMaximumSize(QtCore.QSize(400, 60))'.format(num))
        exec('self.limbBox_{0}.setObjectName("limbBox_{0}")'.format(num))
        exec('self.limbBoxGrid = QtWidgets.QGridLayout(self.limbBox_{0})'.format(num))
        self.limbBoxGrid.setContentsMargins(0, 0, 0, 0)
        self.limbBoxGrid.setSpacing(0)
        self.limbBoxGrid.setContentsMargins(0, 0, 0, 0)
        self.limbBoxGrid.setObjectName("limbBoxGrid")
        exec('self.limbBoxInside = QtWidgets.QGroupBox(self.limbBox_{0})'.format(num))
        self.limbBoxInside.setTitle("")
        self.limbBoxInside.setObjectName("limbBoxInside")
        self.limbBoxInsideGrid = QtWidgets.QGridLayout(self.limbBoxInside)
        self.limbBoxInsideGrid.setContentsMargins(0, 0, 0, 0)
        self.limbBoxInsideGrid.setHorizontalSpacing(2)
        self.limbBoxInsideGrid.setVerticalSpacing(0)
        self.limbBoxInsideGrid.setObjectName("limbBoxInsideGrid")
        exec('self.limbMinus_{0} = QtWidgets.QPushButton(self.limbBoxInside)'.format(num))
        exec('self.limbMinus_{0}.setMaximumSize(QtCore.QSize(10, 10))'.format(num))
        exec('self.limbMinus_{0}.setObjectName("limbMinus_{0}")'.format(num))
        exec('self.limbBoxInsideGrid.addWidget(self.limbMinus_{0}, 0, 0, 1, 1)'.format(num))
        exec('self.limbType_{0} = QtWidgets.QComboBox(self.limbBoxInside)'.format(num))
        exec('self.limbType_{0}.setMaximumSize(QtCore.QSize(60, 50))'.format(num))
        exec('self.limbType_{0}.setObjectName("limbType_{0}")'.format(num))
        exec('self.limbType_{0}.addItem("")'.format(num))
        exec('self.limbType_{0}.addItem("")'.format(num))
        exec('self.limbType_{0}.addItem("")'.format(num))
        exec('self.limbType_{0}.addItem("")'.format(num))
        exec('self.limbBoxInsideGrid.addWidget(self.limbType_{0}, 0, 1, 1, 1)'.format(num))
        exec('self.limbSide_{0} = QtWidgets.QLineEdit(self.limbBoxInside)'.format(num))
        exec('self.limbSide_{0}.setObjectName("limbSide_{0}")'.format(num))
        exec('self.limbBoxInsideGrid.addWidget(self.limbSide_{0}, 0, 2, 1, 1)'.format(num))
        exec('self.limbMir_{0} = QtWidgets.QLineEdit(self.limbBoxInside)'.format(num))
        exec('self.limbMir_{0}.setObjectName("limbMir_{0}")'.format(num))
        exec('self.limbBoxInsideGrid.addWidget(self.limbMir_{0}, 0, 3, 1, 1)'.format(num))
        exec('self.limbName_{0} = QtWidgets.QLineEdit(self.limbBoxInside)'.format(num))
        exec('self.limbName_{0}.setObjectName("limbName_{0}")'.format(num))
        exec('self.limbBoxInsideGrid.addWidget(self.limbName_{0}, 0, 4, 1, 1)'.format(num))
        exec('self.limbParent_{0} = QtWidgets.QLineEdit(self.limbBoxInside)'.format(num))
        exec('self.limbParent_{0}.setObjectName("limbParent_{0}")'.format(num))
        exec('self.limbBoxInsideGrid.addWidget(self.limbParent_{0}, 0, 5, 1, 1)'.format(num))
        self.limbOptions = QtWidgets.QGridLayout()
        self.limbOptions.setSpacing(0)
        self.limbOptions.setObjectName("limbOptions")
        exec('self.limbOpt1_{0} = QtWidgets.QCheckBox(self.limbBoxInside)'.format(num))
        exec('self.limbOpt1_{0}.setObjectName("limbOpt1_{0}")'.format(num))
        exec('self.limbOptions.addWidget(self.limbOpt1_{0}, 0, 0, 1, 1)'.format(num))
        exec('self.limbOpt2_{0} = QtWidgets.QCheckBox(self.limbBoxInside)'.format(num))
        exec('self.limbOpt2_{0}.setObjectName("limbOpt2_{0}")'.format(num))
        exec('self.limbOptions.addWidget(self.limbOpt2_{0}, 0, 1, 1, 1)'.format(num))
        exec('self.limbOpt3_{0} = QtWidgets.QCheckBox(self.limbBoxInside)'.format(num))
        exec('self.limbOpt3_{0}.setObjectName("limbOpt3_{0}")'.format(num))
        exec('self.limbOptions.addWidget(self.limbOpt3_{0}, 0, 2, 1, 1)'.format(num))
        exec('self.limbOpt4_{0} = QtWidgets.QCheckBox(self.limbBoxInside)'.format(num))
        exec('self.limbOpt4_{0}.setObjectName("limbOpt4_{0}")'.format(num))
        exec('self.limbOptions.addWidget(self.limbOpt4_{0}, 1, 0, 1, 1)'.format(num))
        exec('self.limbOpt5_{0} = QtWidgets.QCheckBox(self.limbBoxInside)'.format(num))
        exec('self.limbOpt5_{0}.setObjectName("limbOpt5_{0}")'.format(num))
        exec('self.limbOptions.addWidget(self.limbOpt5_{0}, 1, 1, 1, 1)'.format(num))
        exec('self.limbOpt6_{0} = QtWidgets.QCheckBox(self.limbBoxInside)'.format(num))
        exec('self.limbOpt6_{0}.setObjectName("limbOpt6_{0}")'.format(num))
        exec('self.limbOptions.addWidget(self.limbOpt6_{0}, 1, 2, 1, 1)'.format(num))
        exec('self.limbMirTog_{0} = QtWidgets.QCheckBox(self.limbBoxInside)'.format(num))
        exec('self.limbMirTog_{0}.setMaximumSize(QtCore.QSize(15, 15))'.format(num))
        exec('self.limbMirTog_{0}.setText("")'.format(num))
        exec('self.limbMirTog_{0}.setObjectName("limbMirTog_{0}")'.format(num))
        exec('self.limbOptions.addWidget(self.limbMirTog_{0}, 0, 3, 2, 1)'.format(num))
        exec('self.limbMirBtn_{0} = QtWidgets.QPushButton(self.limbBoxInside)'.format(num))
        exec('self.limbMirBtn_{0}.setMinimumSize(QtCore.QSize(40, 25))'.format(num))
        exec('self.limbMirBtn_{0}.setMaximumSize(QtCore.QSize(40, 25))'.format(num))
        exec('self.limbMirBtn_{0}.setObjectName("limbMirBtn_{0}")'.format(num))
        exec('self.limbOptions.addWidget(self.limbMirBtn_{0}, 0, 5, 2, 1)'.format(num))
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Minimum)
        self.limbOptions.addItem(spacerItem, 0, 6, 2, 1)
        spacerItem1 = QtWidgets.QSpacerItem(7, 20, QtWidgets.QSizePolicy.Fixed,
                                            QtWidgets.QSizePolicy.Minimum)
        self.limbOptions.addItem(spacerItem1, 0, 4, 2, 1)
        self.limbBoxInsideGrid.addLayout(self.limbOptions, 2, 0, 1, 6)
        self.limbSep = QtWidgets.QFrame(self.limbBoxInside)
        self.limbSep.setFrameShape(QtWidgets.QFrame.HLine)
        self.limbSep.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.limbSep.setObjectName("limbSep")
        self.limbBoxInsideGrid.addWidget(self.limbSep, 1, 0, 1, 6)
        self.limbBoxGrid.addWidget(self.limbBoxInside, 0, 0, 1, 1)
        # exec('self.ui.formLayout.setWidget('+str(j_wwiar_limbBoxNum-1)+
        #      ', QtWidgets.QFormLayout.LabelRole, self.limbBox_'+num+')')
        exec('self.ui.formLayout.setWidget({0}, QtWidgets.QFormLayout.LabelRole, \
             self.limbBox_{1})'.format(j_wwiar_limbBoxNum-1, num))

        ##- limb type click down index
        exec('self.limbType_{0}.setCurrentIndex({1})'.format(num, typ))

        ##- labels
        exec('self.limbType_{0}.setItemText(0, \
             QtWidgets.QApplication.translate("Form", "Arm", None, -1))'.format(num))
        exec('self.limbType_{0}.setItemText(1, \
             QtWidgets.QApplication.translate("Form", "Leg", None, -1))'.format(num))
        exec('self.limbType_{0}.setItemText(2, \
             QtWidgets.QApplication.translate("Form", "Tail [NI]", None, -1))'.format(num))
        exec('self.limbType_{0}.setItemText(3, \
             QtWidgets.QApplication.translate("Form", "Head", None, -1))'.format(num))
        exec('self.limbMinus_{0}.setText( \
             QtWidgets.QApplication.translate("Form", "-", None, -1))'.format(num))
        exec('self.limbSide_{0}.setPlaceholderText( \
             QtWidgets.QApplication.translate("Form", "Side (Opt)", None, -1))'.format(num))
        exec('self.limbMir_{0}.setPlaceholderText( \
             QtWidgets.QApplication.translate("Form", "Mirror Side", None, -1))'.format(num))
        exec('self.limbName_{0}.setPlaceholderText( \
             QtWidgets.QApplication.translate("Form", "Name (Opt)", None, -1))'.format(num))
        exec('self.limbParent_{0}.setPlaceholderText( \
             QtWidgets.QApplication.translate("Form", "Parent Joint", None, -1))'.format(num))
        exec('self.limbMirBtn_{0}.setText( \
             QtWidgets.QApplication.translate("Form", "Mirror", None, -1))'.format(num))

        ## force initial updates
        self.updateLimbType(num, typ, loadVal)
        if loadVal:
            mir = loadVal['mirror']
        if mir:
            self.updateLimbMirTog(num, 2, loadVal=loadVal)
        else:
            self.updateLimbMirTog(num, 0, loadVal=loadVal)

        ## connect limb inputs to functions
        inputWidgetConns = {
            'limbMinus' : ('clicked', 'updateLimbMinus', ''),
            'limbSide' : ('textChanged', 'updateLimbSide', ''),
            'limbName' : ('textChanged', 'updateLimbName', ''),
            'limbParent' : ('textChanged', 'updateLimbParent', ''),
            'limbType' : ('currentIndexChanged', 'updateLimbType', ''),
            'limbOpt1' : ('stateChanged', 'updateLimbOpt', '"1"'),
            'limbOpt2' : ('stateChanged', 'updateLimbOpt', '"2"'),
            'limbOpt3' : ('stateChanged', 'updateLimbOpt', '"3"'),
            'limbOpt4' : ('stateChanged', 'updateLimbOpt', '"4"'),
            'limbOpt5' : ('stateChanged', 'updateLimbOpt', '"5"'),
            'limbOpt6' : ('stateChanged', 'updateLimbOpt', '"6"'),
            'limbMir' : ('textChanged', 'updateLimbMirName', ''),
            'limbMirTog' : ('stateChanged', 'updateLimbMirTog', ''),
            'limbMirBtn' : ('clicked', 'updateLimbMirBtn', ''),
        }
        for key, val in inputWidgetConns.iteritems():
            # listener, function, arg = val
            # exec('self.'+key+'_'+num+'.'+listener+'.connect( \
            #      partial(self.'+function+', num, '+arg+'))')
            exec('self.{0}_{1}.{2[0]}.connect(partial(self.{2[1]}, num, {2[2]}))'.format(key, num,
                                                                                         val))

        ## set text edit vars to Blank
        self.updateLimbName(num, '', loadVal=loadVal)

    def clear(self, *args):
        global j_wwiar_limbBoxNum
        global j_wwiar_currentLimbBoxes
        for i in j_wwiar_currentLimbBoxes:
            try:
                exec('self.ui.formLayout.removeWidget(self.limbBox_{0})'.format(i))
                exec('self.limbBox_{0}.deleteLater()'.format(i))
                exec('self.limbBox_{0} = None'.format(i))
            except AttributeError:
                continue
        j_wwiar_currentLimbBoxes = []

    def updateModeRad(self, val, *args):
        global j_wwiar_rigMode
        j_wwiar_rigMode = val

    def updateName(self, val, *args):
        global j_wwiar_rigNameTxt
        j_wwiar_rigNameTxt = val

    def updateSpineChkBox(self, val, *args):
        global j_wwiar_spine
        j_wwiar_spine = val
        self.ui.spineSpnBox.setEnabled(bool(val))
        if val == 0:
            for i in range(j_wwiar_limbBoxNum):
                i = str(i+1)
                curParTxt = eval('self.limbParent_{0}.text()'.format(i))
                exec('j_wwiar_limbStoredParent_{0}Val = "{1}"'.format(i, curParTxt), globals())
                exec('self.limbParent_{0}.setText("")'.format(i))
                self.updateLimbParent(i, '')
        else:
            for i in range(j_wwiar_limbBoxNum):
                i = str(i+1)
                exec('self.limbParent_{0}.setText(j_wwiar_limbStoredParent_{0}Val)'.format(i))
                self.updateLimbParent(i, '')

    def updateSpineSpnBox(self, val, *args):
        global j_wwiar_spineJntsNum
        j_wwiar_spineJntsNum = val
        for x in j_wwiar_currentLimbBoxes:
            if eval('j_wwiar_limbType_{0}Val'.format(x)) == 0:
                self.setParentText(x, 0)

    def updateSaveLocsBtn(self, *args):
        updateRigName()
        if cmds.objExists(j_wwiar_rigName+'_rigPreviewLocs_GRP'):
            fileFilter = 'JSON Files(*.json);;All Files (*.*)'
            fileName = cmds.fileDialog2(
                                dialogStyle=1,
                                caption='Save Locators as JSON',
                                fileMode=0,
                                fileFilter=fileFilter,
                                )
            uiData = {}
            for x in j_wwiar_currentLimbBoxes:
                uiData[x] = self.getLimbOptions(x)
            saveLocsToJson(fileName[0], j_wwiar_rigName, uiData)

    def updateLoadLocsBtn(self, *args):
        updateRigName()
        fileFilter = 'JSON Files(*.json);;All Files (*.*)'
        fileName = cmds.fileDialog2(
                            dialogStyle=1,
                            caption='Load Locators from JSON',
                            fileMode=1,
                            fileFilter=fileFilter,
                            )
        rigName, locs, ui = loadLocsFromJson(fileName[0])
        self.clear()
        self.ui.nameEdit.setText(rigName)
        self.updateName(rigName)
        for x in sorted(ui):
            self.add(typ=ui[x]['limbType'], loadVal=ui[x])
        createAllLocs(rigName)

    def updateDelLocsBtn(self, *args):
        updateRigName()
        if cmds.objExists('{0}_rigPreviewLocs_GRP'.format(j_wwiar_rigName)):
            confirm=cmds.confirmDialog(
                            title='Delete Locators?',
                            message='{0}{1}{2}'.format('Are you sure you want to delete ',
                                                       j_wwiar_rigName, ' rig\'s locators?'),
                            button=['Yes', 'Cancel'],
                            defaultButton='Yes',
                            cancelButton='Cancel',
                            )
            if 'Yes' in confirm:
                cmds.delete('{0}_rigPreviewLocs_GRP'.format(j_wwiar_rigName))

    def updateColSpnBox(self, box, val, *args):
        exec('j_wwiar_{0}SpnBoxVal = {1}'.format(box, val), globals())
        exec('self.ui.{0}ImgBtn.setIcon(QtGui.QIcon("{1}Colour{2:0>2}.png"))'.format(box, iconDir,
                                                                                     val))

    def updateLocScaleSpnBox(self, val, *args):
        global j_wwiar_locScaleSpnBoxVal
        j_wwiar_locScaleSpnBoxVal = val

    def updateCtrlScaleSpnBox(self, val, *args):
        global j_wwiar_ctrlScaleSpnBoxVal
        j_wwiar_ctrlScaleSpnBoxVal = val

    def updateLocsBtn(self, *args):
        updateRigName()
        createAllLocs(j_wwiar_rigName)

    def updateMirrorBtn(self, *args):
        ## add a check to make sure locators exist before mirroring them
        updateRigName()
        mirrorAllLocs(j_wwiar_rigName)

    def updateCreateBtn(self, *args):
        updateRigName()
        createAllRig(j_wwiar_rigName)

    def updateLimbName(self, num, val, loadVal=None, *args):
        if loadVal:
            val = loadVal['limbName']
            exec('self.limbName_{0}.setText("{1}")'.format(num, val))
        exec('j_wwiar_limbName_{0}Val = "{1}"'.format(num, val), globals())

    def updateLimbSide(self, num, val, *args):
        exec('j_wwiar_limbSide_{0}Val = "{1}"'.format(num, val), globals())

    def updateLimbMirName(self, num, val, *args):
        exec('j_wwiar_limbMirName_{0}Val = "{1}"'.format(num, val), globals())

    def updateLimbParent(self, num, val, *args):
        exec('j_wwiar_limbParent_{0}Val = "{1}"'.format(num, val), globals())

    def updateLimbMinus(self, num, *args):
        global j_wwiar_currentLimbBoxes
        exec('self.ui.formLayout.removeWidget(self.limbBox_{0})'.format(num))
        exec('self.limbBox_{0}.deleteLater()'.format(num))
        exec('self.limbBox_{0} = None'.format(num))
        j_wwiar_currentLimbBoxes.remove(num)

    def setLimbOptBoxDefault(self, optionValues, num, loadVal=None):
        ## get current check box states
        limbOpt1Checked = eval('self.limbOpt1_{0}.isChecked()'.format(num))
        limbOpt2Checked = eval('self.limbOpt2_{0}.isChecked()'.format(num))
        limbOpt3Checked = eval('self.limbOpt3_{0}.isChecked()'.format(num))
        limbOpt4Checked = eval('self.limbOpt4_{0}.isChecked()'.format(num))
        limbOpt5Checked = eval('self.limbOpt5_{0}.isChecked()'.format(num))
        limbOpt6Checked = eval('self.limbOpt6_{0}.isChecked()'.format(num))
        limbMirTogChecked = eval('self.limbMirTog_{0}.isChecked()'.format(num))
        opt1_chked = not limbOpt1Checked if optionValues['opt1']['value'] else limbOpt1Checked
        opt2_chked = not limbOpt2Checked if optionValues['opt2']['value'] else limbOpt2Checked
        opt3_chked = not limbOpt3Checked if optionValues['opt3']['value'] else limbOpt3Checked
        opt4_chked = not limbOpt4Checked if optionValues['opt4']['value'] else limbOpt4Checked
        opt5_chked = not limbOpt5Checked if optionValues['opt5']['value'] else limbOpt5Checked
        opt6_chked = not limbOpt6Checked if optionValues['opt6']['value'] else limbOpt6Checked
        mirTog_chked = not limbMirTogChecked if optionValues['mirror']['value'] else limbMirTogChecked
        ## option 1
        exec('self.limbOpt1_{0}.setText("{1}")'.format(num, optionValues['opt1']['label']))
        exec('self.limbOpt1_{0}.setEnabled({1})'.format(num, optionValues['opt1']['enabled']))
        if opt1_chked:
            exec('self.limbOpt1_{0}.toggle()'.format(num))
        self.updateLimbOpt(num, '1', optionValues['opt1']['value'])
        ## option 2
        exec('self.limbOpt2_{0}.setText("{1}")'.format(num, optionValues['opt2']['label']))
        exec('self.limbOpt2_{0}.setEnabled({1})'.format(num, optionValues['opt2']['enabled']))
        if opt2_chked:
            exec('self.limbOpt2_{0}.toggle()'.format(num))
        self.updateLimbOpt(num, '2', optionValues['opt2']['value'])
        ## option 3
        exec('self.limbOpt3_{0}.setText("{1}")'.format(num, optionValues['opt3']['label']))
        exec('self.limbOpt3_{0}.setEnabled({1})'.format(num, optionValues['opt3']['enabled']))
        if opt3_chked:
            exec('self.limbOpt3_{0}.toggle()'.format(num))
        self.updateLimbOpt(num, '3', optionValues['opt3']['value'])
        ## option 4
        exec('self.limbOpt4_{0}.setText("{1}")'.format(num, optionValues['opt4']['label']))
        exec('self.limbOpt4_{0}.setEnabled({1})'.format(num, optionValues['opt4']['enabled']))
        if opt4_chked:
            exec('self.limbOpt4_{0}.toggle()'.format(num))
        self.updateLimbOpt(num, '4', optionValues['opt4']['value'])
        ## option 5
        exec('self.limbOpt5_{0}.setText("{1}")'.format(num, optionValues['opt5']['label']))
        exec('self.limbOpt5_{0}.setEnabled({1})'.format(num, optionValues['opt5']['enabled']))
        if opt5_chked:
            exec('self.limbOpt5_{0}.toggle()'.format(num))
        self.updateLimbOpt(num, '5', optionValues['opt5']['value'])
        ## option 6
        exec('self.limbOpt6_{0}.setText("{1}")'.format(num, optionValues['opt6']['label']))
        exec('self.limbOpt6_{0}.setEnabled({1})'.format(num, optionValues['opt6']['enabled']))
        if opt6_chked:
            exec('self.limbOpt6_{0}.toggle()'.format(num))
        self.updateLimbOpt(num, '6', optionValues['opt6']['value'])
        ## mirror option
        if mirTog_chked:
            exec('self.limbMirTog_{0}.toggle()'.format(num))
        self.updateLimbMirTog(num, optionValues['mirror']['value'])

    def updateLimbType(self, num, val, loadVal=None, *args):
        exec('j_wwiar_limbType_{0}Val = {1}'.format(num, val), globals())
        ## set parent text
        if loadVal:
            self.setParentText(num, val, loadVal)
        else:
            self.setParentText(num, val)
        ## set options
        optionValues = {
            'arm' : {
                'opt1' : {
                    'label' : 'Fingers',
                    'enabled' : 'True',
                    'value' : 2 if not loadVal else loadVal['opt1']
                },
                'opt2' : {
                    'label' : 'IK/FK Switch',
                    'enabled' : 'True',
                    'value' : 2 if not loadVal else loadVal['opt2']
                },
                'opt3' : {
                    'label' : 'Stretchy',
                    'enabled' : 'True',
                    'value' : 2 if not loadVal else loadVal['opt3']
                },
                'opt4' : {
                    'label' : 'Soft IK [NI]',
                    'enabled' : 'True',
                    'value' : 2 if not loadVal else loadVal['opt4']
                },
                'opt5' : {
                    'label' : 'Ribbon [NI]',
                    'enabled' : 'True',
                    'value' : 0 if not loadVal else loadVal['opt5']
                },
                'opt6' : {
                    'label' : 'Auto Clav [NI]',
                    'enabled' : 'True',
                    'value' : 2 if not loadVal else loadVal['opt6']
                },
                'mirror' : {
                    'label' : 'Mirror Toggle',
                    'value' : 2 if not loadVal else loadVal['mirror']
                },
            },
            'leg' : {
                'opt1' : {
                    'label' : 'Toes',
                    'enabled' : 'True',
                    'value' : 0 if not loadVal else loadVal['opt1']
                },
                'opt2' : {
                    'label' : 'IK/FK Switch',
                    'enabled' : 'True',
                    'value' : 2 if not loadVal else loadVal['opt2']
                },
                'opt3' : {
                    'label' : 'Stretchy',
                    'enabled' : 'True',
                    'value' : 2 if not loadVal else loadVal['opt3']
                },
                'opt4' : {
                    'label' : 'Soft IK [NI]',
                    'enabled' : 'True',
                    'value' : 2 if not loadVal else loadVal['opt4']
                },
                'opt5' : {
                    'label' : 'Ribbon [NI]',
                    'enabled' : 'True',
                    'value' : 0 if not loadVal else loadVal['opt5']
                },
                'opt6' : {
                    'label' : '-',
                    'enabled' : 'False',
                    'value' : 0 if not loadVal else loadVal['opt6']
                },
                'mirror' : {
                    'label' : 'Mirror Toggle',
                    'value' : 2 if not loadVal else loadVal['mirror']
                },
            },
            'tail' : {
                'opt1' : {
                    'label' : 'IK Spline',
                    'enabled' : 'True',
                    'value' : 2 if not loadVal else loadVal['opt1']
                },
                'opt2' : {
                    'label' : 'Dynamics [NI]',
                    'enabled' : 'True',
                    'value' : 0 if not loadVal else loadVal['opt2']
                },
                'opt3' : {
                    'label' : '-',
                    'enabled' : 'False',
                    'value' : 0 if not loadVal else loadVal['opt3']
                },
                'opt4' : {
                    'label' : '-',
                    'enabled' : 'False',
                    'value' : 0 if not loadVal else loadVal['opt4']
                },
                'opt5' : {
                    'label' : '-',
                    'enabled' : 'False',
                    'value' : 0 if not loadVal else loadVal['opt5']
                },
                'opt6' : {
                    'label' : '-',
                    'enabled' : 'False',
                    'value' : 0 if not loadVal else loadVal['opt6']
                },
                'mirror' : {
                    'label' : 'Mirror Toggle',
                    'value' : 0 if not loadVal else loadVal['mirror']
                },
            },
            'head' : {
                'opt1' : {
                    'label' : 'IK',
                    'enabled' : 'True',
                    'value' : 2 if not loadVal else loadVal['opt1']
                },
                'opt2' : {
                    'label' : '-',
                    'enabled' : 'False',
                    'value' : 0 if not loadVal else loadVal['opt2']
                },
                'opt3' : {
                    'label' : '-',
                    'enabled' : 'False',
                    'value' : 0 if not loadVal else loadVal['opt3']
                },
                'opt4' : {
                    'label' : '-',
                    'enabled' : 'False',
                    'value' : 0 if not loadVal else loadVal['opt4']
                },
                'opt5' : {
                    'label' : '-',
                    'enabled' : 'False',
                    'value' : 0 if not loadVal else loadVal['opt5']
                },
                'opt6' : {
                    'label' : '-',
                    'enabled' : 'False',
                    'value' : 0 if not loadVal else loadVal['opt6']
                },
                'mirror' : {
                    'label' : 'Mirror Toggle',
                    'value' : 0 if not loadVal else loadVal['mirror']
                },
            },
        }
        if val == 0:
            ## arm
            self.setLimbOptBoxDefault(optionValues['arm'], num, loadVal)
        elif val == 1:
            ## leg
            self.setLimbOptBoxDefault(optionValues['leg'], num, loadVal)
        elif val == 2:
            ## tail
            self.setLimbOptBoxDefault(optionValues['tail'], num, loadVal)
        else:
            ## head
            self.setLimbOptBoxDefault(optionValues['head'], num, loadVal)

    def updateLimbOpt(self, num, optNum, val, *args):
        exec('j_wwiar_limbOpt{0}_{1}Val = {2}'.format(optNum, num, val), globals())

    def updateLimbMirTog(self, num, val, loadVal=None, *args):
        exec('j_wwiar_limbMirTog_{0}Val = {1}'.format(num, val), globals())

        if loadVal:
            val = loadVal['mirror']
            side = loadVal['limbSide']
            mirSide = loadVal['limbMirSide']
        elif val:
            side = 'L'
            mirSide = 'R'
        else:
            side = ''

        exec('self.limbMirBtn_{0}.setEnabled({1})'.format(num, val))
        exec('self.limbMir_{0}.setEnabled({1})'.format(num, val))
        exec('self.limbSide_{0}.setPlaceholderText( \
            QtWidgets.QApplication.translate("Form", "Side", None, -1))'.format(num))
        exec('self.limbSide_{0}.setText("{1}")'.format(num, side))
        self.updateLimbSide(num, side)
        if val:
            exec('self.limbMir_{0}.setText("{1}")'.format(num, mirSide))
            self.updateLimbMirName(num, mirSide)
        else:
            # exec('self.limbSide_{0}.setPlaceholderText( \
            #     QtWidgets.QApplication.translate("Form", "Side (Opt)", None, -1))'.format(num))
            # exec('self.limbSide_{0}.setText("")'.format(num))
            # self.updateLimbSide(num, '')
            exec('self.limbMir_{0}.setText("")'.format(num))
            self.updateLimbMirName(num, '')

    def updateLimbMirBtn(self, num, *args):
        mirrorSingleLimb(j_wwiar_rigName, num)

    def setParentText(self, num, type, loadVal=None, *args):
        if loadVal:
            parentTxt = loadVal['limbPar']
        else:
            if j_wwiar_spine:
                if type == 0:   ## arm
                    parName = int(j_wwiar_spineJntsNum / 1.5 + (j_wwiar_spineJntsNum % 1.5 > 0)-1)
                    if j_wwiar_spineJntsNum < 12:
                        parentTxt = 'spine_'+str(parName).zfill(2)
                    elif j_wwiar_spineJntsNum < 102:
                        parentTxt = 'spine_'+str(parName).zfill(3)
                    else:
                        parentTxt = 'spine_'+str(parName).zfill(4)
                elif type == 1 or type == 2: ## leg or tail
                    parentTxt = 'spine_base'
                else:   ## head
                    parentTxt = 'spine_end'
            else:
                parentTxt = ''

        exec('self.limbParent_{0}.setText(parentTxt)'.format(num))
        self.updateLimbParent(num, parentTxt)

    def getLimbOptions(self, num, *args):
        limbBoxData = {
            'limbName' : eval('j_wwiar_limbName_{0}Val'.format(num)),
            'limbSide' : eval('j_wwiar_limbSide_{0}Val'.format(num)),
            'limbMirSide' : eval('j_wwiar_limbMirName_{0}Val'.format(num)),
            'limbPar' : eval('j_wwiar_limbParent_{0}Val'.format(num)),
            'mirror' : eval('j_wwiar_limbMirTog_{0}Val'.format(num)),
            'limbType' : eval('j_wwiar_limbType_{0}Val'.format(num)),
            'opt1' : eval('j_wwiar_limbOpt1_{0}Val'.format(num)),
            'opt2' : eval('j_wwiar_limbOpt2_{0}Val'.format(num)),
            'opt3' : eval('j_wwiar_limbOpt3_{0}Val'.format(num)),
            'opt4' : eval('j_wwiar_limbOpt4_{0}Val'.format(num)),
            'opt5' : eval('j_wwiar_limbOpt5_{0}Val'.format(num)),
            'opt6' : eval('j_wwiar_limbOpt6_{0}Val'.format(num)),
        }
        return limbBoxData



main()
