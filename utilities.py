import maya.cmds as cmds
import re

from Jenks.crvShapes import zGlobalControl as crv1
from Jenks.crvShapes import zSettingsCog as crv2
from Jenks.crvShapes import zCircle as crv3
from Jenks.crvShapes import zTriCross as crv4
from Jenks.crvShapes import zGlobe as crv5
from Jenks.crvShapes import zCrossedCircle as crv6
from Jenks.crvShapes import zEyes as crv7
from Jenks.crvShapes import zFoot as crv8
from Jenks.crvShapes import zPringle as crv9
from Jenks.crvShapes import zArrow as crv10
from Jenks.crvShapes import zCube as crv11
from Jenks.crvShapes import zDualArrow as crv12
from Jenks.crvShapes import zFatCross as crv13
from Jenks.crvShapes import zFlatPringle as crv14
from Jenks.crvShapes import zHand as crv15
from Jenks.crvShapes import zLips as crv16
from Jenks.crvShapes import zQuadArrow as crv17
from Jenks.crvShapes import zThinCross as crv18
from Jenks.crvShapes import zMattJenkins as crv19
from Jenks.crvShapes import zPin as crv22
from Jenks.crvShapes import zGlobe_single as crv23


def createLocs(locInfo, name, suff, rigName='', side='', limbName='',
               mirror=False, mirSide='', scale=1, importFile=False):
    if mirror:
        name = '{0}_{1}{2}'.format(rigName, side, limbName)
        mirName = '{0}_{1}_{2}'.format(rigName, mirSide, limbName)

    locKeys = sorted(locInfo)
    locNamesList = {}
    for key, val in locInfo.iteritems():
        locName = '{0}{1}{2}'.format(name, key[1], suff)
        if mirror:
            locData = getExistingLocData(locName)
            locData['translate'][0] *= -1
            locData['rotate'][1] *= -1
            locData['rotate'][2] *= -1
            locName = '{0}{1}{2}'.format(mirName, key[1], suff)
            cmds.delete(locName)
        else:
            if cmds.objExists(locName):
                locData = getExistingLocData(locName)
                cmds.delete(locName)
            else:
                locData = val
        locator = cmds.spaceLocator(n=locName)[0]
        cmds.xform(locator, t=locData['translate'], ro=locData['rotate'], s=locData['scale'])
        resizeLocs([locator], size=[locData['localScale'][0][0],
                                  locData['localScale'][0][1],
                                  locData['localScale'][0][2]])
        locNamesList[key[0]] = locName
        try:
            if locData['pvDist']:
                cmds.addAttr(locName, sn='pvDis', nn='Pole Vector Distance', dv=1.0, h=False, k=True)
                cmds.setAttr('{0}.pvDis'.format(locName), locData['pvDist'])
        except KeyError:
            continue
    for i, x in enumerate(locKeys):
        if not importFile:
            locInfo[i, locNamesList[i]] = locInfo.pop(x)
    return locInfo


def createSingleLoc(locName, name, suff, xyz, side=None, par=None, limbName='',
                    mirror=False, mirSide='', prefix='', scale=1):
    if mirror:
        name = '{0}_{1}_{2}'.format(prefix, side, limbName)
        mirName = '{0}_{1}_{2}'.format(prefix, mirSide, limbName)
    fullLocName = '{0}{1}{2}'.format(name, locName, suff)

    if mirror:
        locData = getExistingLocData(fullLocName)
        locData['translate'][0] *= -1
        locData['rotate'][1] *= -1
        locData['rotate'][2] *= -1
        fullLocName = '{0}{1}{2}'.format(mirName, locName, suff)
        cmds.delete(fullLocName)
    else:
        if cmds.objExists(fullLocName):
            locData = getExistingLocData(fullLocName)
            cmds.delete(fullLocName)
        else:
            locData = {
                'translate' : xyz,
                'rotate' : [0, 0, 0],
                'scale' : [1, 1, 1],
                'localScale' : [(scale, scale, scale)]
            }
    locator = cmds.spaceLocator(n=fullLocName)[0]
    cmds.xform(locator, t=locData['translate'], ro=locData['rotate'], s=locData['scale'])
    resizeLocs([locator], size=[locData['localScale'][0][0],
                              locData['localScale'][0][1],
                              locData['localScale'][0][2]])
    if par:
        cmds.parentConstraint(par, fullLocName, mo=True)
    return fullLocName


def getExistingLocData(loc):
    t = cmds.xform(loc, q=True, t=True, ws=True)
    r = cmds.xform(loc, q=True, ro=True, ws=True)
    s = cmds.xform(loc, q=True, s=True, ws=True)
    localS = cmds.getAttr('{0}.localScale'.format(loc))
    locAttrs = cmds.listAttr(loc)
    if 'pvDis' in locAttrs:
        pvDis = cmds.getAttr('{0}.pvDis'.format(loc))
    else:
        pvDis = None

    locData = {
        'translate' : t,
        'rotate' : r,
        'scale' : s,
        'localScale' : localS,
        'pvDist' : pvDis,
    }
    return locData


def resizeLocs(locs, size=[1, 1, 1], relative=True):
    """Resizes locators.

    Args:
    [string list] locs - List of locators
    [string] size - Size to set Locators
    """
    for x in locs:
        oldScale = [
            (cmds.getAttr('{0}.localScaleX'.format(x)) if relative else '1') ,
            (cmds.getAttr('{0}.localScaleY'.format(x)) if relative else '1'),
            (cmds.getAttr('{0}.localScaleZ'.format(x)) if relative else '1'),
        ]
        cmds.setAttr('{0}.localScaleX'.format(x), size[0]*oldScale[0])
        cmds.setAttr('{0}.localScaleY'.format(x), size[1]*oldScale[1])
        cmds.setAttr('{0}.localScaleZ'.format(x), size[2]*oldScale[2])


def createLocsOnCurve(name, jntNum, crv, crvName='spine', suff='_posLOC', attach=False, scale=1):
    ## disconnect existing locators
    cnncts = cmds.listConnections('{}.cp'.format(crv), c=True, p=True)
    if cnncts:
        pairedCnncts = []
        for i in range(len(cnncts)/2):
            i *= 2
            pairedCnncts.append((cnncts[i], cnncts[i+1]))
        for x in pairedCnncts:
            cmds.disconnectAttr(x[1], x[0])
    ## create locs on spine crv
    crvLocs = []
    crv = cmds.rebuildCurve(crv, s=jntNum-1, rpo=True, rt=0, end=1, kr=0, kt=False, d=1)
    if cmds.objExists('{0}_{1}_posGRP'.format(name, crvName)):
        cmds.parent(crv[0], w=True)
        cmds.delete('{0}_{1}_posGRP'.format(name, crvName))
    for i in range(jntNum):
        pos = cmds.xform('{0}.cp[{1}]'.format(crv[0], i), q=True, t=True, ws=True)
        if i==0:
            locNum = 'base'
        elif i==jntNum-1:
            locNum = 'end'
        elif jntNum <12:
            locNum = str(i).zfill(2)
        elif jntNum <102:
            locNum = str(i).zfill(3)
        else:
            locNum = str(i).zfill(4)
        if cmds.objExists('{0}_{1}_{2}{3}'.format(name, crvName, locNum, suff)):
            cmds.delete('{0}_{1}_{2}{3}'.format(name, crvName, locNum, suff))
        loc = cmds.spaceLocator(n='{0}_{1}_{2}{3}'.format(name, crvName, locNum, suff))
        cmds.xform(loc, t=pos)
        cmds.connectAttr('{0}.translate'.format(loc[0]), '{0}.cp[{1}]'.format(crv[0], i))
        crvLocs.append(loc[0])
    resizeLocs(crvLocs, size=[scale, scale, scale])
    cmds.group(crvLocs, n='{0}_{1}_posGRP'.format(name, crvName))
    cmds.parentConstraint(crv, '{0}_{1}_posGRP'.format(name, crvName), mo=True)
    return crvLocs


def createJnts(locs, extraName='', side='L', par='', *args):
    """Creates joints at the location of locators and orients them
    correctly.

    Returns Joint Names.

    Args:
    [string list] locs - locators to create joints on
    [string] extraName - Extra name inserted before locator's name
    (e.g. for IK and FK chains)
    [string] side - Name of the side
    [string] par - Location of a dummy parent (used for orientating
    chains of two jnts)
    """
    jnts = []
    cmds.select(cl=True)
    if par is not '':
        locs.insert(0, par)
    for x in locs:
        jntName = x.rpartition('_')
        jntName = jntName[0].rpartition('_')
        jntName = '{0}{1}_{2}_JNT'.format(jntName[0], extraName, jntName[2])
        if not cmds.objExists(jntName):
            locPos = cmds.xform(x,q=True,t=True,ws=True)
            cmds.joint(n=jntName, p=locPos)
        jnts.append(jntName)
        cmds.setAttr('{0}.radius'.format(jntName), 0.2)
        cmds.select(jntName)
    if side is not 'L' and 'L_' not in side and '_L' not in side:
        doOrientJoint(jnts, [-1, 0, 0], [0, 1, 0], [0, 1, 0], 1)
    else:
        doOrientJoint(jnts, [1, 0, 0], [0, 1, 0], [0, 1, 0], 1)
    cmds.select(cl=True)
    return jnts


def createIK(ikName, start, end):
    """Creates a correctly named grouped IK handle (including the
    effector).

    Returns IK Group name, IK Handle Name, IK Effector name.

    Args:
    [string] ikName - The name of the IK
    [string] start - The starting joint of the IK
    [string] end - The end joint of the IK
    """
    hdlName = '{0}_HDL'.format(ikName)
    effName = '{0}_EFF'.format(ikName)
    grpName = '{0}_GRP'.format(ikName)
    if cmds.objExists(grpName):
        cmds.delete(grpName)
    ikH,ikE = cmds.ikHandle(n=hdlName, sj=start, ee=end)
    cmds.rename(ikE,effName)
    hdlPos = cmds.xform(ikH, q=True, t=True)
    cmds.group(hdlName, n=grpName, r=True)
    cmds.xform(grpName, piv=hdlPos)
    cmds.select(cl=True)
    return grpName, hdlName, effName


def createFKIK(joints, jntChainName, rigName, side, jntChainExtraName, parJnt, col,
               globalScale=1, suffixA='_IK_', suffixB='_FK_', curSuffix='_result_'):
    """Creates an IK, FK and result chain from an existing chain of
    joints and sets them up with an IK/FK switch.

    Args:
    [string list] joints - A list of existing joints to convert to an
    IK/FK chain
    [string] jntChainName - The name of the joint chain
    [string] rigName - The name of the rig
    [string] side - The side the chain is on
    [string] jntChainExtraName - The extra prefix before the joint
    chain's name
    [string] parJnt - The name of the joint chain's parent
    [int list] col - A list of three colour IDs to give the settings
    controls [Left colour, Right Colour, Misc Colour]
    [int] globalScale - The global scale to use for the settings
    controls
    """
    ## Set Suffix Values
    name = '{0}_{1}{2}'.format(rigName, side, jntChainExtraName)
    ctrlCrv = '{0}{1}Settings'.format(name, jntChainName)
    attrName = 'IKFKSwitch'

    createSettingCtrl(ctrlCrv, '{0}{1}IKFKVis_posLOC'.format(name, jntChainName),
                      parJnt, side, globalScale, col)

    for x in joints:
        if curSuffix not in x:
            if '_JNT' not in x:
                cmds.confirmDialog(
                    title='ERROR',
                    message='One or more incorrectly named Joints selected',
                    button=['Ok']
                )
                return
            ## Rename current Joint
            resultJointName = x.replace('_JNT', '{0}JNT'.format(curSuffix))
            if cmds.objExists(resultJointName):
                cmds.delete(resultJointName)

            cmds.rename(x,resultJointName)
            x = resultJointName

        ## Names from current Joint
        blendSuffix = '{0}{1}{2}'.format(suffixA[:-1], suffixB[1:2].upper(), suffixB[2:-1])
        ikJointName = x.replace(curSuffix, suffixA)
        fkJointName = x.replace(curSuffix, suffixB)
        blendRName = x.replace('{0}JNT'.format(curSuffix), '{0}Rot_BLND'.format(blendSuffix))
        blendTName = x.replace('{0}JNT'.format(curSuffix), '{0}Trans_BLND'.format(blendSuffix))
        blendSName = x.replace('{0}JNT'.format(curSuffix), '{0}Scale_BLND'.format(blendSuffix))

        ## Duplicate Joints
        if cmds.objExists(ikJointName):
            cmds.delete(ikJointName)
        if cmds.objExists(fkJointName):
            cmds.delete(fkJointName)
        ikJoints = cmds.duplicate(x, n=ikJointName, po=True)
        fkJoints = cmds.duplicate(x, n=fkJointName, po=True)

        ## Parent Duplicated Joints
        resultParent = cmds.listRelatives(x, p=True, c=False)
        if resultParent:
            for p in resultParent:
                if curSuffix in p:
                    ikParent = p.replace(curSuffix, suffixA)
                    fkParent = p.replace(curSuffix, suffixB)
                    cmds.parent(ikJointName, ikParent)
                    cmds.parent(fkJointName, fkParent)

        ## Create and attach Blends
        cmds.createNode('blendColors', n=blendRName)
        cmds.createNode('blendColors', n=blendTName)
        cmds.createNode('blendColors', n=blendSName)
        ##- Inputs
        ikAttrs = {
            (0, 'rotate') : ('', '', '', blendRName, 'color2'),
            (1, 'translate') : ('', '', '', blendTName, 'color2'),
            (2, 'scale') : ('', '', '', blendSName, 'color2'),
        }
        fkAttrs = {
            (0, 'rotate') : ('', '', '', blendRName, 'color1'),
            (1, 'translate') : ('', '', '', blendTName, 'color1'),
            (2, 'scale') : ('', '', '', blendSName, 'color1'),
        }
        ctrlAttrs = {
            (0, attrName) : ('', '', '', blendRName, 'blender'),
            (1, attrName) : ('', '', '', blendTName, 'blender'),
            (2, attrName) : ('', '', '', blendSName, 'blender'),
        }
        connectAttrs(ikJointName, ikAttrs)
        connectAttrs(fkJointName, fkAttrs)
        connectAttrs('{0}_CTRL'.format(ctrlCrv), ctrlAttrs)
        ##- Outputs
        cmds.connectAttr('{0}.output'.format(blendRName), '{0}.rotate'.format(x))
        cmds.connectAttr('{0}.output'.format(blendTName), '{0}.translate'.format(x))
        cmds.connectAttr('{0}.output'.format(blendSName), '{0}.scale'.format(x))


def createStretchyLimb(rigName, jnts, limbName, loc1Par, loc2Par, limbControl, prop1, prop2, pinAttr):
    """Creates a node network to add stretch to an IK joint chain.

    Args:
    [string] rigName - name of the rig
    [string list] jnts - the names of the joints in the chain
    [string] limbName - name of the limb
    """
    if not cmds.objExists('{0}_global_CTRL'.format(rigName)) or not cmds.objExists(limbControl):
        print 'you dun fucked it'
        return False
    else:
        ## create attributes on controller
        cmds.addAttr(limbControl, ln='stretchSep', nn='___   Stretchy',
                     at='enum', en='___', k=True)
        cmds.addAttr(limbControl, ln='stretchTog', nn='Toggle', min=0, max=1, k=True, dv=1)
        cmds.addAttr(limbControl, ln='prop1', nn=prop1, min=0, max=1, k=True, dv=0.5)
        cmds.addAttr(limbControl, ln='prop2', nn=prop2, min=0, max=1, k=True, dv=0.5)
        cmds.addAttr(limbControl, ln='midJntPinTog', nn=pinAttr, min=0, max=1, k=True, dv=0)

        ## create limb global scale
        globalScale = cmds.createNode('multDoubleLinear',
                                      n='{0}_globalScale_MULT'.format(limbName))
        cmds.connectAttr('{0}_global_CTRL.scaleX'.format(rigName),
                         '{0}.input1'.format(globalScale))
        ##- sum of limb joints
        jntLenList = []
        for i, x in enumerate(jnts):
            if i > 0:
                jntLen = cmds.getAttr('{0}.translateX'.format(x))
                jntLenList.append(jntLen)
        limbLen = sum(jntLenList)
        cmds.setAttr('{0}.input2'.format(globalScale), abs(limbLen))
        ## create distance node & locators
        loc1 = cmds.spaceLocator(n='{0}_stretchStart_LOC'.format(limbName))[0]
        loc2 = cmds.spaceLocator(n='{0}_stretchEnd_LOC'.format(limbName))[0]
        locGrp = cmds.group(loc1, loc2, n='{0}StretchyMech_GRP'.format(limbName))
        cmds.parent(locGrp, '{0}Mech_GRP'.format(limbName))
        cmds.delete(cmds.parentConstraint(jnts[0], loc1))
        cmds.delete(cmds.parentConstraint(jnts[-1], loc2))
        cmds.parentConstraint(loc1Par, loc1, mo=True)
        cmds.parentConstraint(loc2Par, loc2, mo=True)
        distNode = cmds.createNode('distanceBetween',
                                   n='{0}_stretch_DIST'.format(limbName))
        cmds.connectAttr('{0}.worldMatrix'.format(loc1),
                         '{0}.inMatrix1'.format(distNode))
        cmds.connectAttr('{0}.worldMatrix'.format(loc2),
                         '{0}.inMatrix2'.format(distNode))
        cmds.connectAttr('{0}.rotatePivotTranslate'.format(loc1),
                         '{0}.point1'.format(distNode))
        cmds.connectAttr('{0}.rotatePivotTranslate'.format(loc2),
                         '{0}.point2'.format(distNode))
        ## distance node / limb global scale
        sizeDiv = cmds.createNode('multiplyDivide',
                                  n='{0}_size_DIV'.format(limbName))
        cmds.setAttr('{0}.operation'.format(sizeDiv), 2)
        cmds.connectAttr('{0}.distance'.format(distNode),
                         '{0}.input1X'.format(sizeDiv))
        cmds.connectAttr('{0}.output'.format(globalScale),
                         '{0}.input2X'.format(sizeDiv))
        stretchPointCond = cmds.createNode('condition',
                                           n='{0}_stretchPoint_COND'.format(limbName))
        cmds.connectAttr('{0}.distance'.format(distNode),
                         '{0}.firstTerm'.format(stretchPointCond))
        cmds.connectAttr('{0}.output'.format(globalScale),
                         '{0}.secondTerm'.format(stretchPointCond))
        cmds.connectAttr('{0}.outputX'.format(sizeDiv),
                         '{0}.colorIfTrueR'.format(stretchPointCond))
        cmds.setAttr('{0}.operation'.format(stretchPointCond), 2)
        ## toggle multiplier (condition result [PWR] toggle)
        toggleMult = cmds.createNode('multiplyDivide',
                                     n='{0}_stretchTog_PWR'.format(limbName))
        cmds.setAttr('{0}.operation'.format(toggleMult), 3)
        cmds.connectAttr('{0}.outColorR'.format(stretchPointCond),
                         '{0}.input1X'.format(toggleMult))
        cmds.connectAttr('{0}.stretchTog'.format(limbControl),
                         '{0}.input2X'.format(toggleMult))
        ## proportion stuff
        ##- add proportions together
        propAdd = cmds.createNode('addDoubleLinear',
                                  n='{0}_proportion_ADD'.format(limbName))
        cmds.connectAttr('{0}.prop1'.format(limbControl), '{0}.input1'.format(propAdd))
        cmds.connectAttr('{0}.prop2'.format(limbControl), '{0}.input2'.format(propAdd))
        ##- 2 / added proportions
        propDiv = cmds.createNode('multiplyDivide',
                                  n='{0}_proportion_DIV'.format(limbName))
        cmds.setAttr('{0}.operation'.format(propDiv), 2)
        cmds.setAttr('{0}.input1X'.format(propDiv), 2)
        cmds.connectAttr('{0}.output'.format(propAdd),
                         '{0}.input2X'.format(propDiv))
        ##- proportion x result from divided (do for both sections of the limb)
        propMult = cmds.createNode('multiplyDivide',
                                   n='{0}_proportions_MULT'.format(limbName))
        cmds.connectAttr('{0}.outputX'.format(propDiv),
                         '{0}.input1X'.format(propMult))
        cmds.connectAttr('{0}.outputX'.format(propDiv),
                         '{0}.input1Y'.format(propMult))
        cmds.connectAttr('{0}.prop1'.format(limbControl),
                         '{0}.input2X'.format(propMult))
        cmds.connectAttr('{0}.prop2'.format(limbControl),
                         '{0}.input2Y'.format(propMult))
        ## scale factor multiply (result from condition x results from proportions)
        scaleFactorMult = cmds.createNode('multiplyDivide',
                                          n='{0}_scaleFactor_MULT'.format(limbName))
        cmds.connectAttr('{0}.output'.format(propMult),
                         '{0}.input1'.format(scaleFactorMult))
        cmds.connectAttr('{0}.outputX'.format(toggleMult),
                         '{0}.input2X'.format(scaleFactorMult))
        cmds.connectAttr('{0}.outputX'.format(toggleMult),
                         '{0}.input2Y'.format(scaleFactorMult))
        ## multiply original translate
        upperTransMult = cmds.createNode('multDoubleLinear',
                                         n='{0}_upperJntTrans_MULT'.format(limbName))
        lowerTransMult = cmds.createNode('multDoubleLinear',
                                         n='{0}_lowerJntTrans_MULT'.format(limbName))
        cmds.connectAttr('{0}.outputX'.format(scaleFactorMult),
                         '{0}.input2'.format(upperTransMult))
        cmds.connectAttr('{0}.outputY'.format(scaleFactorMult),
                         '{0}.input2'.format(lowerTransMult))
        upperTrans = cmds.getAttr('{0}.translateX'.format(jnts[1]))
        lowerTrans = cmds.getAttr('{0}.translateX'.format(jnts[-1]))
        cmds.setAttr('{0}.input1'.format(upperTransMult), upperTrans)
        cmds.setAttr('{0}.input1'.format(lowerTransMult), lowerTrans)
        ## mid joint pin
        ##- distance nodes
        pvLoc = cmds.spaceLocator(n='{0}_pinPV_LOC'.format(limbName))[0]
        cmds.parent(pvLoc, locGrp)
        cmds.parentConstraint('{0}PVConst_GRP'.format(limbName), pvLoc)
        upperPinDist = cmds.createNode('distanceBetween',
                                       n='{0}_upperJntPin_DIST'.format(limbName))
        lowerPinDist = cmds.createNode('distanceBetween',
                                       n='{0}_lowerJntPin_DIST'.format(limbName))
        cmds.connectAttr('{0}.worldMatrix'.format(loc1),
                         '{0}.inMatrix1'.format(upperPinDist))
        cmds.connectAttr('{0}.worldMatrix'.format(pvLoc),
                         '{0}.inMatrix2'.format(upperPinDist))
        cmds.connectAttr('{0}.rotatePivotTranslate'.format(loc1),
                         '{0}.point1'.format(upperPinDist))
        cmds.connectAttr('{0}.rotatePivotTranslate'.format(pvLoc),
                         '{0}.point2'.format(upperPinDist))
        cmds.connectAttr('{0}.worldMatrix'.format(loc2),
                         '{0}.inMatrix1'.format(lowerPinDist))
        cmds.connectAttr('{0}.worldMatrix'.format(pvLoc),
                         '{0}.inMatrix2'.format(lowerPinDist))
        cmds.connectAttr('{0}.rotatePivotTranslate'.format(loc2),
                         '{0}.point1'.format(lowerPinDist))
        cmds.connectAttr('{0}.rotatePivotTranslate'.format(pvLoc),
                         '{0}.point2'.format(lowerPinDist))
        ##- trans multiply nodes
        upperPinTransMult = cmds.createNode('multDoubleLinear',
                                            n='{0}_upperJntPinTrans_MULT'.format(limbName))
        lowerPinTransMult = cmds.createNode('multDoubleLinear',
                                            n='{0}_lowerJntPinTrans_MULT'.format(limbName))
        cmds.connectAttr('{0}.distance'.format(upperPinDist),
                         '{0}.input1'.format(upperPinTransMult))
        cmds.connectAttr('{0}_global_CTRL.scaleX'.format(rigName),
                         '{0}.input2'.format(upperPinTransMult))
        cmds.connectAttr('{0}.distance'.format(lowerPinDist),
                         '{0}.input1'.format(lowerPinTransMult))
        cmds.connectAttr('{0}_global_CTRL.scaleX'.format(rigName),
                         '{0}.input2'.format(lowerPinTransMult))
        ## blend between pin and stretch
        pinBlndNode = cmds.createNode('blendColors',
                                      n='{0}_midJntPin_BLND'.format(limbName))
        cmds.connectAttr('{0}.output'.format(upperPinTransMult),
                         '{0}.color1R'.format(pinBlndNode))
        cmds.connectAttr('{0}.output'.format(lowerPinTransMult),
                         '{0}.color1G'.format(pinBlndNode))
        cmds.connectAttr('{0}.output'.format(upperTransMult),
                         '{0}.color2R'.format(pinBlndNode))
        cmds.connectAttr('{0}.output'.format(lowerTransMult),
                         '{0}.color2G'.format(pinBlndNode))
        cmds.connectAttr('{0}.midJntPinTog'.format(limbControl),
                         '{0}.blender'.format(pinBlndNode))
        ## connect blend to joints
        cmds.connectAttr('{0}.outputR'.format(pinBlndNode), '{0}.translateX'.format(jnts[1]))
        cmds.connectAttr('{0}.outputG'.format(pinBlndNode), '{0}.translateX'.format(jnts[-1]))



def createSettingCtrl(ctrlCrv, settingLoc, parJnt, side, globalScale, col):
    """Creates a settings control for an IK/FK Switch (probably should
    make this more broad at some point...).

    Args:
    [string] ctrlCrv - The name of the new control
    [string] settingLoc - The name of the object to use as a position
    guide
    [string] parJnt - The name of the joint that the control with
    follow
    [string] side - The side of the control
    [int] globalScale - The global scale of the control
    [int list] col - The colour ID to give the control [Left colour,
    Right Colour, Misc Colour]
    """
    attrName = 'IKFKSwitch'
    attrNiceName = 'IK / FK Switch'
    if side == 'L' or 'L_' in side or '_L' in side:
        col = col[0]
        rot = [-15, 30, 0]
    elif side == 'R' or 'R_' in side or '_R' in side:
        col = col[1]
        rot = [-15, -30, 0]
    else:
        col = col[2]
        rot = [-15, 0, 0]
    if cmds.objExists('{0}Ctrl_ROOT'.format(ctrlCrv)):
        cmds.delete('{0}Ctrl_ROOT'.format(ctrlCrv))
    createCtrlShape(ctrlCrv, 2, col=col, scale=[0.12, 0.12, 0.12], rotOffset=rot,
                    globalScale=globalScale)
    createBuffer(ctrlCrv, 1, 1, settingLoc)
    lockHideAttrs('{0}_CTRL'.format(ctrlCrv), 'translate, rotate, scale,')
    if not cmds.attributeQuery(attrName, node='{0}_CTRL'.format(ctrlCrv), exists=True):
        cmds.addAttr('{0}_CTRL'.format(ctrlCrv), ln=attrName, nn=attrNiceName, min=0, max=1,
                     at='float', dv=0, k=True)
    cmds.parentConstraint(parJnt, '{0}Ctrl_ROOT'.format(ctrlCrv), mo=True)


def createSplineIK(start, end, ikName='splineIK', controlName='', squashCtrlName=''):
    """Creates an Spline IK with stretch (no weight preservation yet).

    Args:
    [string] start - The start joint
    [string] end - The end joint
    [string] ikName - The name of the spline IK
    [string] controlName - The name of the control to use for the
    rig's global scale
    [string] squasgCtrlName - The name of the control to add the squash
    attributes to
    """
    ## setup name variables
    hdlName = '{0}_HDL'.format(ikName)
    effName = '{0}_EFF'.format(ikName)
    crvName = '{0}_CRV'.format(ikName)
    grpName = '{0}_GRP'.format(ikName)
    crvInfoName = '{0}Crv_INFO'.format(ikName)

    if cmds.objExists(grpName):
        cmds.delete(grpName)
    ## get effected joints
    startJntParents = getParents(start)
    endJntParents = getParents(end)

    if startJntParents:
        eP = list(set(endJntParents)-set(startJntParents))
    else:
        eP = endJntParents
    effectedJnts = eP

    ## create IK
    ikH, ikE, ikC = cmds.ikHandle(n=hdlName, sj=start, ee=end, solver='ikSplineSolver',
                                  parentCurve=False, simplifyCurve=False)
    cmds.group(ikH, ikC, n=grpName)
    cmds.rename(ikE, effName)
    cmds.rename(ikC, crvName)

    ## create curve info node
    crvInf = cmds.arclen(crvName, ch=True)
    if not cmds.objExists(crvInfoName):
        cmds.rename(crvInf, crvInfoName)

    ## create global scale mult node
    crvGlobalScaleNode = cmds.createNode('multDoubleLinear',
                                         n='{0}CrvGlobalScale_MULT'.format(ikName), ss=True)
    if cmds.objExists(controlName):
        cmds.connectAttr('{0}.scaleY'.format(controlName),
                         '{0}.input1'.format(crvGlobalScaleNode))
    else:
        cmds.setAttr('{0}.input1'.format(crvGlobalScaleNode), 1)
    ikCrvLength = cmds.getAttr('{0}.arcLength'.format(crvInfoName))
    cmds.setAttr('{0}.input2'.format(crvGlobalScaleNode), ikCrvLength)

    ## create curve stretch divide node
    crvStretchNode = cmds.createNode('multiplyDivide', n='{0}CrvStretch_DIV'.format(ikName))
    cmds.setAttr('{0}.operation'.format(crvStretchNode), 2)  # 1=multiply 2=divide
    cmds.connectAttr('{0}.output'.format(crvGlobalScaleNode),
                     '{0}.input2X'.format(crvStretchNode))
    cmds.connectAttr('{0}.arcLength'.format(crvInfoName), '{0}.input1X'.format(crvStretchNode))

    ## create stretch mult node for each effected joint
    for sN,lN in effectedJnts:
        jntStretchName = '{0}{1}Stretch_MULT'.format(ikName, sN)
        jntStretchNode = cmds.createNode('multDoubleLinear', n=jntStretchName)
        jointTransX = cmds.getAttr('{0}.translateX'.format(lN))
        cmds.setAttr('{0}.input1'.format(jntStretchNode), jointTransX)
        cmds.connectAttr('{0}.outputX'.format(crvStretchNode),
                         '{0}.input2'.format(jntStretchNode))
        cmds.connectAttr('{0}.output'.format(jntStretchNode), '{0}.translateX'.format(lN))

    ## volume preservation (squash)
    ##- original length / current length
    squashDiv = cmds.createNode('multiplyDivide', n='{0}CrvSquash_DIV'.format(ikName))
    cmds.setAttr('{0}.operation'.format(squashDiv), 2)
    cmds.connectAttr('{0}.output'.format(crvGlobalScaleNode),
                     '{0}.input1X'.format(squashDiv))
    cmds.connectAttr('{0}.arcLength'.format(crvInfoName), '{0}.input2X'.format(squashDiv))
    ##- squashDiv [PWR] exponents
    squashExpPwr = cmds.createNode('multiplyDivide', n='{0}CrvSquashExps_PWR'.format(ikName))
    cmds.setAttr('{0}.operation'.format(squashExpPwr), 3)
    cmds.connectAttr('{0}.outputX'.format(squashDiv), '{0}.input1X'.format(squashExpPwr))
    cmds.connectAttr('{0}.outputX'.format(squashDiv), '{0}.input1Y'.format(squashExpPwr))
    cmds.connectAttr('{0}.outputX'.format(squashDiv), '{0}.input1Z'.format(squashExpPwr))
    ##-- create exponent attrs
    print squashCtrlName
    print cmds.objExists(squashCtrlName)
    if cmds.objExists(squashCtrlName):
        cmds.addAttr(squashCtrlName, ln='squashSep', nn='___   Squash',
                     at='enum', en='___', k=True)
        cmds.addAttr(squashCtrlName, ln='squashExpA', nn='Lower Exponent', k=True, dv=1.25)
        cmds.addAttr(squashCtrlName, ln='squashExpB', nn='Mid Exponent', k=True, dv=1.5)
        cmds.addAttr(squashCtrlName, ln='squashExpC', nn='Upper Exponent', k=True, dv=1.25)
        ##-- connect exponent attrs
        cmds.connectAttr('{0}.squashExpA'.format(squashCtrlName),
                         '{0}.input2X'.format(squashExpPwr))
        cmds.connectAttr('{0}.squashExpB'.format(squashCtrlName),
                         '{0}.input2Y'.format(squashExpPwr))
        cmds.connectAttr('{0}.squashExpC'.format(squashCtrlName),
                         '{0}.input2Z'.format(squashExpPwr))
    else:
        cmds.setAttr('{0}.input2X'.format(squashExpPwr), 1.25)
        cmds.setAttr('{0}.input2Y'.format(squashExpPwr), 1.5)
        cmds.setAttr('{0}.input2Z'.format(squashExpPwr), 1.25)
    ##-- connect to joints scale
    numSquashJnts = len(effectedJnts)-1
    perA = 0.2
    perB = 0.4
    perC = 0.6
    perD = 0.8

    lowAJnt = int(numSquashJnts * perA + (numSquashJnts % perA > 0)-1)
    lowBJnt = int(numSquashJnts * perB + (numSquashJnts % perB > 0)-1)
    lowCJnt = int(numSquashJnts * perC + (numSquashJnts % perC > 0)-1)
    upCJnt = int(numSquashJnts * perD + (numSquashJnts % perD > 0)-1)

    for i in xrange(numSquashJnts):
        i += 1
        if i < lowAJnt:
            continue
        elif i < lowBJnt:
            cmds.connectAttr('{0}.outputX'.format(squashExpPwr),
                             '{0}.scaleY'.format(effectedJnts[-(i+1)][1]))
        elif i < lowCJnt:
            cmds.connectAttr('{0}.outputY'.format(squashExpPwr),
                             '{0}.scaleY'.format(effectedJnts[-(i+1)][1]))
        elif i < upCJnt:
            cmds.connectAttr('{0}.outputZ'.format(squashExpPwr),
                             '{0}.scaleY'.format(effectedJnts[-(i+1)][1]))

    ## turn off inherit transforms
    cmds.setAttr('{0}.inheritsTransform'.format(grpName), 0)


def createPhalanges(locs, name, side, side_, globalScale, par, col, fingers=False):
    ikList = []
    if fingers:
        phalType = 'fngr'
        allPhalCtrl = '{0}fingersConst_GRP'.format(name)
    else:
        phalType = 'toe'
        allPhalCtrl = '{0}footToesIKConst_GRP'.format(name)
    for k, v in locs.iteritems():
        curPhal = k[2]
        jnts = createJnts(v, side=side_)
        if par is not '':
            for x in jnts:
                if '_base_' in x:
                    cmds.parent(x, par)

        ## create finger mech
        ik = createIK('{0}{1}{2}IK'.format(name, phalType, curPhal),
                      '{0}{1}{2}_base_JNT'.format(name, phalType, curPhal),
                      '{0}{1}{2}_tip_JNT'.format(name, phalType, curPhal))
        ikList.append(ik[0])

        ## finger tips ctrls
        phalCtrlPosLoc = cmds.spaceLocator(n='{0}{1}{2}_tip_LOC'.format(name, phalType, curPhal))
        cmds.delete(cmds.parentConstraint('{0}{1}{2}_tip_JNT'.format(name, phalType, curPhal),
                                          phalCtrlPosLoc))
        #cmds.setAttr('{0}.rotateX'.format(phalCtrlPosLoc[0]), 0)
        createCtrlShape('{0}{1}{2}'.format(name, phalType, curPhal), 10,
                                col=col, scale=[0.1, 0.1, 0.04], rotOffset=[-90, 0, 0],
                                side=side, globalScale=globalScale)
        createBuffer('{0}{1}{2}'.format(name, phalType, curPhal), 1, 1, phalCtrlPosLoc)
        lockHideAttrs('{0}{1}{2}_CTRL'.format(name, phalType, curPhal), 'rotateY')
        lockHideAttrs('{0}{1}{2}_CTRL'.format(name, phalType, curPhal), 'rotateZ')
        cmds.delete(phalCtrlPosLoc)
        if side is 'R' or 'R_' in side or '_R' in side:
            phalCtrlRot = cmds.xform('{0}{1}{2}Ctrl_PAR'.format(name, phalType, curPhal),
                                        q=True, ro=True)
            cmds.xform('{0}{1}{2}Ctrl_PAR'.format(name, phalType, curPhal),
                       ro=[phalCtrlRot[0]*-1, phalCtrlRot[1]+180, phalCtrlRot[2]])
        cmds.parentConstraint('{0}{1}{2}Const_GRP'.format(name, phalType, curPhal), ik[1])
        if not curPhal == 'Thumb' or not fingers:
            cmds.parent('{0}{1}{2}Ctrl_ROOT'.format(name, phalType, curPhal), allPhalCtrl)
        ## create pv controls
        pvPos = cmds.xform('{0}{1}{2}PvVis_posLOC'.format(name, phalType, curPhal),
                           q=True, t=True, ws=True)
        pvLoc = cmds.spaceLocator(n='{0}{1}{2}PV_LOC'.format(name, phalType, curPhal))
        cmds.xform(pvLoc[0], t=pvPos)
        cmds.makeIdentity(pvLoc[0], t=True)

        newPvPosLoc = cmds.spaceLocator()
        cmds.delete(cmds.parentConstraint('{0}{1}{2}_base_JNT'.format(name, phalType, curPhal),
                                          newPvPosLoc[0]))
        cmds.poleVectorConstraint(pvLoc[0], ik[1])
        # newPvPos = cmds.xform('{0}{1}{2}_base_JNT'.format(name, phalType, curPhal),
        #                       q=True, t=True, ws=True)
        # newPvPos[2] += 0.5
        # cmds.xform(pvLoc[0], t=newPvPos)
        cmds.delete(cmds.parentConstraint(newPvPosLoc[0], pvLoc[0]))
        cmds.delete(newPvPosLoc)
        cmds.xform(pvLoc[0], t=[0, 0.2, 0], r=True, os=True)
        cmds.setAttr('{0}.twist'.format(ik[1]), -90)
        #pvGrp = cmds.group(pvLoc, n='{0}{1}{2}PvLoc_GRP'.format(name, phalType, curPhal))
        pvPar = cmds.group(n='{0}{1}{2}PvLoc_PAR'.format(name, phalType, curPhal), em=True)
        cmds.delete(cmds.parentConstraint('{0}{1}{2}_base_JNT'.format(name, phalType, curPhal),
                                            pvPar))
        pvGrp = cmds.group(n='{0}{1}{2}PvLoc_GRP'.format(name, phalType, curPhal), em=True)
        cmds.delete(cmds.parentConstraint('{0}{1}{2}_base_JNT'.format(name, phalType, curPhal),
                                            pvGrp))
        cmds.parent(pvGrp, pvPar)
        cmds.parent(pvLoc, pvGrp)
        cmds.parentConstraint(par, pvPar, mo=True)
        # baseJntPos = cmds.xform('{0}{1}{2}_base_JNT'.format(name, phalType, curPhal),
        #                       q=True, t=True, ws=True)
        #cmds.xform(pvGrp, piv=baseJntPos)
        ikList.append(pvPar)
        ##- add finger roll
        # cmds.addAttr('{0}{1}{2}_CTRL'.format(name, phalType, curPhal), ln='fngrRoll',
        #              nn='Finger Roll', k=True)
        # cmds.connectAttr('{0}{1}{2}_CTRL.fngrRoll'.format(name, phalType, curPhal),
        #                  '{0}.rotateX'.format(pvGrp))
        cmds.connectAttr('{0}{1}{2}_CTRL.rotateX'.format(name, phalType, curPhal),
                         '{0}.rotateX'.format(pvGrp))
    return ikList


def createCtrlShape(crvName, shapeNum, scale=[1, 1, 1], col=1, rotOffset=[0, 0, 0],
                    transOffset=[0, 0, 0], side=None, skipFreeze=False, globalScale=1):
    """Creates a control curve shape

    Args:
    [string] crvName - The name of the new control curve
    [int] shapeNum - The number ID of the shape
    [int list] scale - The scale in each axis
    [int] col - The colour ID of the curve
    [int list] rotOffset - The rotation offset of the curve
    [int list] transOffset - The translation offset of the curve
    [string] side - The side of the curve
    [bool] skipFreeze - DEBUG OPTION, skips freezing the curve (to
    help with finding the correct rotation and translation offsets)
    [int] globalScale - The global scale of the control
    """
    if not crvName:
        crvName = 'curve'
    ctrlName = '{0}_CTRL'.format(crvName)

    scale = [scale[0]*globalScale,
             scale[1]*globalScale,
             scale[2]*globalScale]

    for i in range(len(transOffset)):
        transOffset[i] = -transOffset[i]

    curveNum = eval('crv{0}'.format(shapeNum))
    crvs = curveNum.create(crvName, '_CTRL')
    combineCrv(crvs, col)
    mirScale = 1
    if not side is None and not side == 'L':
        mirScale = -1
    cmds.xform(ctrlName, scale=scale, ro=rotOffset, piv=transOffset)
    if not skipFreeze:
        cmds.makeIdentity(ctrlName, a=True, s=True, r=True)
        cmds.xform(ctrlName, scale=[mirScale, 1, 1])
        cmds.makeIdentity(ctrlName, a=True, s=True, r=True)


def createFKCtrl(limbName, ctrlName, gScale, scale, col, shp=3, rot=[0, 0, 0], trans=[0, 0, 0]):
    """Creates and constrains an FK control.

    Args:
    [string] limbName - the control's name prefix
    [string] ctrlName - the name of the control
    [float] gScale - the global scale of the control
    [float list] scale - the scale of each axis
    [int] col - the colour ID for the control shape
    [int] shp - the shape ID for the control shape
    [float list] rot - the rotation offset for the control shape
    [float list] trans - the translation offset for the control shape
    """
    createCtrlShape('{0}{1}FK'.format(limbName, ctrlName), shp, col=col, scale=scale,
                            rotOffset=rot, transOffset=trans, globalScale=gScale)
    createBuffer('{0}{1}FK'.format(limbName, ctrlName), 1, 1,
                         '{0}{1}_FK_JNT'.format(limbName, ctrlName))
    lockHideAttrs('{0}{1}FK_CTRL'.format(limbName, ctrlName), 'translate,')
    cmds.parentConstraint('{0}{1}FKConst_GRP'.format(limbName, ctrlName),
                          '{0}{1}_FK_JNT'.format(limbName, ctrlName), mo=True)
    #cmds.scaleConstraint('{0}{1}FKConst_GRP'.format(limbName, ctrlName),
    #                     '{0}{1}_FK_JNT'.format(limbName, ctrlName), mo=True)


def createSpSwConstraint(parents, target, enumNames=None, niceNames=None, constrType='parent',
                         constrTarget='', dv=0):
    """Creates a constraint and adds an attribute on the target to switch between the parents.

    Args:
    [string list] parents - of parent objects (limit to two... for now)
    [string] targets - constraint target
    [string] enumNames - names of the attribute's enum options (e.g. 'option1:option2')
    [string list] niceName - nice names of the parents
    [string] constrType - type of constraint (parent, orient, aim, point, scale)
    """
    if not niceNames:
        niceNames = []
        for x in parents:
            splitPar = x.partition('_')
            splitPar = splitPar[-1].rpartition('_')
            if splitPar[0] == 'globalConst':
                splitPar = ('World', splitPar[1], splitPar[2])
            niceNames.append(splitPar[0].capitalize())


    if constrTarget == '':
        if target.endswith('_CTRL'):
            stripName = target.rpartition('_')
            constrTarget = '{0}Ctrl_ROOT'.format(stripName[0])
        else:
            constrTarget = target

    if niceNames <= 1:
        niceName = niceNames
    else:
        niceName = ''
        enumName = ''
        for i, x in enumerate(niceNames):
            if i < len(niceNames)-1:
                niceName = '{0}{1} / '.format(niceName, x)
                enumName = '{0}{1}:'.format(enumName, x)
            else:
                niceName = '{0}{1}'.format(niceName, x)
                enumName = '{0}{1}'.format(enumName, x)

    if enumNames:
        enumName = enumNames

    existingAttr = cmds.listAttr(target)
    constr = eval('cmds.{0}Constraint(parents, constrTarget, mo=True)'.format(constrType))
    if 'spSwSep' not in existingAttr:
        cmds.addAttr(target, ln='spSwSep', nn='___   Space Switching',
                     at='enum', en='___', k=True)
    cmds.addAttr(target, ln='spaceSwitch', nn='{0} Switch'.format(niceName),
                 at='enum', en=enumName, k=True, dv=dv)
    for i, x in enumerate(parents):
        if not i == 1:
            rev = cmds.createNode('reverse', n='{0}spaceSwitch_REV'.format(target))
            cmds.connectAttr('{0}.spaceSwitch'.format(target), '{0}.inputX'.format(rev))
            cmds.connectAttr('{0}.outputX'.format(rev), '{0}.{1}W{2}'.format(constr[0], x, i))
        else:
            cmds.connectAttr('{0}.spaceSwitch'.format(target), '{0}.{1}W{2}'.format(constr[0], x, i))


def combineCrv(crvs, col):
    """Combines curves into one transform node

    Args:
    [string list] parents - of parent objects (limit to two... for now)
    [int] targets - constraint target
    """
    for i, x in enumerate(crvs):
        shape = cmds.listRelatives(x, s=True)
        if col:
            cmds.setAttr('{0}.overrideEnabled'.format(x), True)
            cmds.setAttr('{0}.overrideColor'.format(x), col-1)
        if not i > 0:
            parent = x
        else:
            cmds.parent(shape, parent, s=True, r=True)
            cmds.delete(x)


def createBuffer(name, locNum, grpNum, obj, *args):
    """Creates The buffer groups for a control curve.

    Args:
    [string] name - Name of control
    [int] locNum - Number of locator buffers
    [int] grpNum - Number of group buffers
    [string] obj - The name of the object the curve will match
    orientation and translate to
    """
    if not name:
        name = 'curve'

    rootCtrlName = '{0}Ctrl_ROOT'.format(name)
    ctrlParentName = '{0}Ctrl_PAR'.format(name)
    spareCtrlParentName = '{0}CtrlPar#_PAR'.format(name)
    ctrlName = '{0}_CTRL'.format(name)
    constGrpName = '{0}Const_GRP'.format(name)

    buffers = []
    prevBuff = None
    if grpNum == 0 and locNum == 0:
        cmds.parentConstraint(obj,ctrlName,mo=False)
        cmds.delete('{0}_parentConstraint1'.format(ctrlName))
        cmds.makeIdentity(ctrlName, a=True, t=True, s=True, r=True)
    else:
        for y in range(grpNum+locNum):
            if y == 0:
                buffName = rootCtrlName
            elif y == 1:
                buffName = ctrlParentName
            else:
                buffName = spareCtrlParentName
            buffName = swapDigits(buffName, y-2)
            if y < grpNum:
                cmds.group(em=True, n=buffName)
            else:
                cmds.spaceLocator(n=buffName)
                cmds.setAttr('{0}Shape.overrideEnabled'.format(buffName), True)
                cmds.setAttr('{0}Shape.overrideVisibility'.format(buffName), 0)
                locPath = zip(cmds.ls(buffName, l=True), buffName)


            cmds.parentConstraint(obj, buffName, mo=False)
            cmds.delete('{0}_parentConstraint1'.format(buffName))
            if y == 0:
                cmds.makeIdentity(buffName, a=True, t=True, s=True, r=True)
            else:
                cmds.makeIdentity(buffName, a=True, t=True, s=True)
            buffers.append(buffName)

        for y in range(len(buffers)):
            if y > 0:
                cmds.parent(buffers[y], buffers[y-1])

        cmds.parentConstraint(buffers[-1], ctrlName, mo=False)
        cmds.delete('{0}_parentConstraint1'.format(ctrlName))
        cmds.parent(ctrlName, buffers[-1])
        cmds.makeIdentity(ctrlName, a=True, t=True, s=True, r=True)

        constGrpPar = ctrlName

        cmds.group(em=True, n=constGrpName)
        cmds.parentConstraint(constGrpPar, constGrpName, mo=False)
        cmds.delete('{0}_parentConstraint1'.format(constGrpName))
        cmds.parent(constGrpName, constGrpPar)
        cmds.makeIdentity(a=True, t=True, s=True, r=True)


def lockHideAttrs(obj, attr, lock=True, show=False):
    """Locks and/or hides specified attributes from an object.

    Args:
    [string] obj - the name of the object to modify attributes on
    [string] attr - the attribute to lock or hide (can also use
    translate, rotate, and scale, NOTE: the comma is required even when
    only one is specified)
    [bool] lock - whether the attribute will be locked
    [bool] show - whether the attribute will be shown
    """
    if 'translate,' in attr:
        cmds.setAttr('{0}.translateX'.format(obj), lock=lock, k=show)
        cmds.setAttr('{0}.translateY'.format(obj), lock=lock, k=show)
        cmds.setAttr('{0}.translateZ'.format(obj), lock=lock, k=show)
    if 'rotate,' in attr:
        cmds.setAttr('{0}.rotateX'.format(obj), lock=lock, k=show)
        cmds.setAttr('{0}.rotateY'.format(obj), lock=lock, k=show)
        cmds.setAttr('{0}.rotateZ'.format(obj), lock=lock, k=show)
    if 'scale,' in attr:
        cmds.setAttr('{0}.scaleX'.format(obj), lock=lock, k=show)
        cmds.setAttr('{0}.scaleY'.format(obj), lock=lock, k=show)
        cmds.setAttr('{0}.scaleZ'.format(obj), lock=lock, k=show)
    if 'translate,' not in attr and 'rotate,' not in attr and 'scale,' not in attr:
        cmds.setAttr('{0}.{1}'.format(obj, attr), lock=lock, k=show)


def swapDigits(name, i=0, *args):
    """Swaps hashes in a string to numbers

    Args:
    [string] name - String to process
    [int] i - Starting number
    """
    minDigitLength = 0
    bufferChar = ''
    findHashes = re.findall("(#+)", name)
    newName = name
    if findHashes:
        minDigitLength = len(findHashes[0])
        bufferChar = findHashes[0]
        newName = str(i+1).zfill(minDigitLength).join(name.split(bufferChar))
        while cmds.objExists(newName):
            i += 1
            newName=str(i+1).zfill(minDigitLength).join(name.split(bufferChar))
    return newName


def getParents(joint, *args):
    """Gets parent, grandparent, etc joints of a joint (up to 1000
    parents).
    Returns parents & grandparents

    Args:
    [string] joint - Name of the joint to process
    """
    parents = []
    sNParents = []
    curPar = joint
    for i in range(1000):
        curPar = cmds.listRelatives(curPar, typ='joint', f=True, p=True)
        if not curPar:
            break
        sN = curPar[0].split('|')
        sNParents.append(sN[-1])
        parents.append(curPar[0])
    parents = zip(sNParents, parents)

    return parents


def getCrv(inCrv):
    """Gets the knot, and cv points of a curve (I should look into
    using openMaya for this instead).
    Returns Knots and cv Points

    Args:
    [string] inCrv - The name of the curve to process
    """
    crvShapeNodes = cmds.listRelatives(inCrv, c=True)
    for pathCurve in crvShapeNodes:
        cmds.select('{0}.cv[*]'.format(pathCurve))
        pathCvs = cmds.ls(sl=True, fl=True)

        knotNum = 0
        cvPoints = []
        knots = []

        for cv in pathCvs:
            coords = cmds.xform(cv, q=True, t=True)
            coords = (coords[0], coords[1], coords[2])
            cvPoints.append(coords)


        noOfPoints = len(cvPoints)
        noOfKnots = noOfPoints+2
        noOfSpans = noOfPoints-3

        knotValue = 1
        for x in range(noOfKnots):
            knots.append(None)
            if x < 3:
                knots[x] = 0
            else:
                knots[x] = knotValue
                knotValue = knotValue+1

            if x >= (noOfKnots-3):
                knots[x] = noOfSpans

    return knots,cvPoints


def createAttr(obj, newAttrs, typ='enum'):
    """Creates attributes on an object.

    Args:
    [string] obj - Name of the object to add atributes to
    [string tuple list] newAttrs - The information of the attributes
    (nice name, enum values, default value, connection object,
    connection Attribute)
    [string] typ - The type of attribute
    """
    existingAttr = cmds.listAttr(obj)
    for key in sorted(newAttrs):
        num, attr = key
        nn, en, dv, connObj, connAttr = newAttrs[key]
        if attr not in existingAttr:
            cmds.addAttr(obj, ln=attr, nn=nn, at=typ, en=en, k=True, dv=dv)


def connectAttrs(obj, newAttrs):
    """Connects attributes.

    Args:
    [string] obj - Name of the object to connect attibutes from
    [string tuple list] newAttrs - The information of the attributes
    (nice name, enum values, default value, connection object,
    connection Attribute)
    """
    for key in sorted(newAttrs):
        num, attr = key
        nn, en, dv, connObj, connAttr = newAttrs[key]
        try:
            cmds.connectAttr('{0}.{1}'.format(obj, attr), '{0}.{1}'.format(connObj, connAttr))
            if 'override' in connAttr:
                cmds.setAttr('{0}.overrideEnabled'.format(connObj), 1)
        except RuntimeError:
            continue


def reverseLocPosValues(locs, axis=[True, False, False]):
    """Reverses the position of locators in choses axes.

    Args:
    [string dict] locs - dictionary of locators to process
    [bool list] axis - reverse axis booleans
    """
    for k, v in locs.iteritems():
        locs[k]['translate'] = (-locs[k]['translate'][0], locs[k]['translate'][1],
                                locs[k]['translate'][2])
    return locs


# ======================================================================
#
#   doOrientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp)
#   crossProduct(firstObj, secondObj, thirdObj)
#   freezeJointOrientation(jointToOrient)
#
# AUTHOR:
#   Jose Antonio Martin Martin - JoseAntonioMartinMartin@gmail.com
#                    contact@joseantoniomartinmartin.com
#   http://www.joseantoniomartinmartin.com
#   Copyright 2010 Jose Antonio Martin Martin - All Rights Reserved.
#
# ======================================================================


def doOrientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp):
    firstPass = 0
    prevUpVector = [0,0,0]
    for eachJoint in jointsToOrient:
        childJoint = cmds.listRelatives(eachJoint, type="joint", c=True)
        if childJoint != None:
            if len(childJoint) > 0:
                #Store the name in case when unparented it changes it's name.
                childNewName = cmds.parent(childJoint, w=True)
                if guessUp == 0:
                    #Not guess Up direction
                    cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0, 0, 0),
                        aim=aimAxis, upVector=upAxis, worldUpVector=worldUp, worldUpType="vector"))
                    freezeJointOrientation(eachJoint)
                    cmds.parent(childNewName, eachJoint)
                else:
                    if guessUp == 1:
                        #Guess Up direction
                        parentJoint = cmds.listRelatives(eachJoint, type="joint", p=True)
                        if parentJoint != None :
                            if len(parentJoint) > 0:
                                posCurrentJoint = cmds.xform(eachJoint, q=True, ws=True, rp=True)
                                posParentJoint = cmds.xform(parentJoint, q=True, ws=True, rp=True)
                                tol = 0.0001

                                if (abs(posCurrentJoint[0] - posParentJoint[0]) <= tol
                                      and abs(posCurrentJoint[1] - posParentJoint[1]) <= tol
                                      and abs(posCurrentJoint[2] - posParentJoint[2]) <= tol):
                                    aimChild = cmds.listRelatives(childNewName[0],
                                                                  type="joint", c=True)
                                    upDirRecalculated = crossProduct(eachJoint, childNewName[0],
                                                                     aimChild[0])
                                    cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint,
                                                                   w=1, o=(0, 0, 0), aim=aimAxis,
                                                                   upVector=upAxis,
                                                                   worldUpVector=upDirRecalculated,
                                                                   worldUpType="vector"))
                                else:
                                    upDirRecalculated = crossProduct(parentJoint, eachJoint,
                                                                     childNewName[0])
                                    cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint,
                                                                   w=1, o=(0, 0, 0), aim=aimAxis,
                                                                   upVector=upAxis,
                                                                   worldUpVector=upDirRecalculated,
                                                                   worldUpType="vector"))
                            else:
                                aimChild = cmds.listRelatives(childNewName[0], type="joint",
                                                              c=True)
                                upDirRecalculated = crossProduct(eachJoint, childNewName[0],
                                                                 aimChild[0])
                        else:
                            aimChild = cmds.listRelatives(childNewName[0], type="joint", c=True)
                            upDirRecalculated = crossProduct(eachJoint, childNewName[0],
                                                             aimChild[0])
                            cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1,
                                                           o=(0, 0, 0), aim=aimAxis,
                                                           upVector=upAxis,
                                                           worldUpVector=upDirRecalculated,
                                                           worldUpType="vector"))





                    dotProduct = (upDirRecalculated[0] * prevUpVector[0]
                                 + upDirRecalculated[1] * prevUpVector[1]
                                 + upDirRecalculated[2] * prevUpVector[2])

                    #For the next iteration
                    prevUpVector = upDirRecalculated

                    if firstPass > 0 and  dotProduct <= 0.0:
                        #dotProduct
                        cmds.xform(eachJoint, r=1, os=1,
                                   ra=(aimAxis[0] * 180.0, aimAxis[1] * 180.0, aimAxis[2] * 180.0))
                        prevUpVector[0] *= -1
                        prevUpVector[1] *= -1
                        prevUpVector[2] *= -1

                    freezeJointOrientation(eachJoint)
                    cmds.parent(childNewName, eachJoint)




            else:
                #Child joint. Use the same rotation as the parent.
                if len(childJoint) == 0:
                    parentJoint = cmds.listRelatives(eachJoint, type="joint", p=True)
                    if parentJoint != None :
                        if len(parentJoint) > 0:
                            cmds.delete(cmds.orientConstraint(parentJoint[0], eachJoint,
                                        w=1, o=(0,0,0)))
                            freezeJointOrientation(eachJoint)
        else:
            #Child joint. Use the same rotation as the parent.
            parentJoint = cmds.listRelatives(eachJoint, type="joint", p=True)
            if parentJoint != None :
                if len(parentJoint) > 0:
                    cmds.delete(cmds.orientConstraint(parentJoint[0], eachJoint, w=1, o=(0,0,0)))
                    freezeJointOrientation(eachJoint)



        firstPass += 1


def crossProduct(firstObj, secondObj, thirdObj):
    #We have 3 points in space so we have to calculate the vectors from
    #the secondObject (generally the middle joint and the one to orient)
    #to the firstObject and from the secondObject to the thirdObject.

    xformFirstObj = cmds.xform(firstObj, q=True, ws=True, rp=True)
    xformSecondObj = cmds.xform(secondObj, q=True, ws=True, rp=True)
    xformThirdObj = cmds.xform(thirdObj, q=True, ws=True, rp=True)

    #B->A so A-B.
    firstVector = [0,0,0]
    firstVector[0] = xformFirstObj[0] - xformSecondObj[0];
    firstVector[1] = xformFirstObj[1] - xformSecondObj[1];
    firstVector[2] = xformFirstObj[2] - xformSecondObj[2];

    #B->C so C-B.
    secondVector = [0,0,0]
    secondVector[0] = xformThirdObj[0] - xformSecondObj[0];
    secondVector[1] = xformThirdObj[1] - xformSecondObj[1];
    secondVector[2] = xformThirdObj[2] - xformSecondObj[2];

    #THE MORE YOU KNOW - 3D MATH
    #========================================
    #Cross Product u x v:
    #(u2v3-u3v2, u3v1-u1v3, u1v2-u2v1)
    crossProductResult = [0,0,0]
    crossProductResult[0] = firstVector[1]*secondVector[2] - firstVector[2]*secondVector[1]
    crossProductResult[1] = firstVector[2]*secondVector[0] - firstVector[0]*secondVector[2]
    crossProductResult[2] = firstVector[0]*secondVector[1] - firstVector[1]*secondVector[0]

    return crossProductResult


def freezeJointOrientation(jointToOrient):
    cmds.joint(jointToOrient, e=True, zeroScaleOrient=True)
    cmds.makeIdentity(jointToOrient, apply=True, t=0, r=1, s=0, n=0)