import maya.OpenMayaUI as omUi
import maya.cmds as cmds
from functools import partial
import re

from shapes import zGlobalControl as crv1
from shapes import zSettingsCog as crv2
from shapes import zCircle as crv3
from shapes import zTriCross as crv4
from shapes import zGlobe as crv5
from shapes import zCrossedCircle as crv6
from shapes import zEyes as crv7
from shapes import zFoot as crv8
from shapes import zPringle as crv9
from shapes import zArrow as crv10
from shapes import zCube as crv11
from shapes import zDualArrow as crv12
from shapes import zFatCross as crv13
from shapes import zFlatPringle as crv14
from shapes import zHand as crv15
from shapes import zLips as crv16
from shapes import zQuadArrow as crv17
from shapes import zThinCross as crv18
from shapes import zMattJenkins as crv19
from shapes import zPin as crv22
from shapes import zGlobe_single as crv23


def createGlobalCtrl(prefix):
    ctrlCrv=prefix+'_global'
    globalCtrlName=ctrlCrv+'_CTRL'
    if not cmds.objExists(prefix+'_geometry_GRP'):
        cmds.group(em=True,n=prefix+'_geometry_GRP')
    if not cmds.objExists(prefix+'_controls_GRP'):
        cmds.group(em=True,n=prefix+'_controls_GRP')
    if not cmds.objExists(prefix+'_skeleton_GRP'):
        cmds.group(em=True,n=prefix+'_skeleton_GRP')
    if not cmds.objExists(prefix+'_mechanics_GRP'):
        cmds.group(em=True,n=prefix+'_mechanics_GRP')
    if not cmds.objExists(ctrlCrv+'Ctrl_ROOT'):
        createCtrlShape(ctrlCrv,1,col=31)
        worldLoc=cmds.spaceLocator(n=prefix+'_world_LOC')
        createBuffer(ctrlCrv,1,1,worldLoc)

    existingAttr=cmds.listAttr(globalCtrlName)
    newAttr=["visSep","visGeo","visCtrls","visSkel","visMech","mdSep","mdGeo","mdSkel","sep1","credits"]

    ## create attributes
    if newAttr[0] not in existingAttr:
        cmds.addAttr(globalCtrlName, ln="visSep",nn="___   Visibilities", at="enum", en="___:", k=True)
    if newAttr[1] not in existingAttr:
        cmds.addAttr(globalCtrlName, ln="visGeo",nn="Geometry", at="enum", en="Hide:Show", k=True, dv=1)
    if newAttr[2] not in existingAttr:
        cmds.addAttr(globalCtrlName, ln="visCtrls",nn="Controls", at="enum", en="Hide:Show", k=True, dv=1)
    if newAttr[3] not in existingAttr:
        cmds.addAttr(globalCtrlName, ln="visSkel",nn="Skeleton", at="enum", en="Hide:Show", k=True, dv=1)
    if newAttr[4] not in existingAttr:
        cmds.addAttr(globalCtrlName, ln="visMech",nn="Mechanics", at="enum", en="Hide:Show", k=True)
    if newAttr[5] not in existingAttr:
        cmds.addAttr(globalCtrlName, ln="mdSep",nn="___   Display Mode", at="enum", en="___:", k=True)
    if newAttr[6] not in existingAttr:
        cmds.addAttr(globalCtrlName, ln="mdGeo",nn="Geometry", at="enum", en="Normal:Template:Reference", k=True, dv=2)
    if newAttr[7] not in existingAttr:
        cmds.addAttr(globalCtrlName, ln="mdSkel",nn="Skeleton", at="enum", en="Normal:Template:Reference", k=True)
    if newAttr[8] not in existingAttr:
        cmds.addAttr(globalCtrlName, ln="sep1",nn="___   ",at="enum",en="___", k=True)
    if newAttr[9] not in existingAttr:
        cmds.addAttr(globalCtrlName, ln="credits",nn="Rig by Matt Jenkins",at="enum",en="___", k=True)

    ## connect attributes
    if cmds.listConnections(globalCtrlName+".visGeo") is None:
        cmds.connectAttr(globalCtrlName+".visGeo",prefix+"_geometry_GRP.visibility")
    if cmds.listConnections(globalCtrlName+".visCtrls") is None:
        cmds.connectAttr(globalCtrlName+".visCtrls",prefix+"_controls_GRP.visibility")
    if cmds.listConnections(globalCtrlName+".visSkel") is None:
        cmds.connectAttr(globalCtrlName+".visSkel",prefix+"_skeleton_GRP.visibility")
    if cmds.listConnections(globalCtrlName+".visMech") is None:
        cmds.connectAttr(globalCtrlName+".visMech",prefix+"_mechanics_GRP.visibility")
    cmds.setAttr(prefix+"_geometry_GRP.overrideEnabled",1)
    if cmds.listConnections(globalCtrlName+".mdGeo") is None:
        cmds.connectAttr(globalCtrlName+".mdGeo",prefix+"_geometry_GRP.overrideDisplayType")
    cmds.setAttr(prefix+"_skeleton_GRP.overrideEnabled",1)
    if cmds.listConnections(globalCtrlName+".mdSkel") is None:
        cmds.connectAttr(globalCtrlName+".mdSkel",prefix+"_skeleton_GRP.overrideDisplayType")

    if not cmds.objExists(prefix+'__RIG_GRP'):
        cmds.group(em=True,n=prefix+'__RIG_GRP')
    cmds.parent(prefix+'_world_LOC',prefix+'_geometry_GRP',prefix+'_globalCtrl_ROOT',prefix+'__RIG_GRP')
    cmds.parent(prefix+'_controls_GRP',prefix+'_skeleton_GRP',prefix+'_mechanics_GRP',prefix+'_globalConst_GRP')


def createLegLocs(prefix,side,mirror=False,mirrorSide='R'):
    name=str(prefix)+'_'+str(side)+'_'
    suff='_posLOC'
    pvDist=1

    ## create Locs
    if side == 'L' or 'L_' in side or '_L' in side:
        legLocs={
            (0, 'hip'):(1, 6, 0),
            (1, 'knee'):(1, 3.5, 0.2),
            (2, 'ankle'):(1, 1, 0),
            (3, 'footHeel'):(1, 0, 0),
            (4, 'footBall'):(1, 0, 1),
            (5, 'footToes'):(1, 0, 2),
        }
    else:
        legLocs={
            (0, 'hip'):(-1, 6, 0),
            (1, 'knee'):(-1, 3.5, 0.2),
            (2, 'ankle'):(-1, 1, 0),
            (3, 'footHeel'):(-1, 0, 0),
            (4, 'footBall'):(-1, 0, 1),
            (5, 'footToes'):(-1, 0, 2),
        }
    if cmds.objExists(name+'wholeLeg'+suff) and not mirror:
        for key, val in legLocs.iteritems():
            pos=cmds.xform(name+key[1]+suff, q=True, t=True, ws=True)
            legLocs[key]=pos
        pvDist=cmds.getAttr(name+'legPvVis'+suff+'.pvDis')
        if cmds.objExists(name+'wholeFoot'+suff):
            cmds.parent(name+'wholeFoot'+suff, w=True)
        cmds.delete(name+'wholeLeg'+suff)
    elif not cmds.objExists(name+'wholeLeg'+suff):
        mirror=False

    ## mirror
    if mirror:
        name=str(prefix)+'_'+str(mirrorSide)+'_'
        if cmds.objExists(name+'wholeLeg'+suff):
            cmds.delete(name+'wholeLeg'+suff)
        legLocs=createLocs(legLocs,name, suff, prefix, side, mirror=True, mirSide=mirrorSide)
        side=mirrorSide
    else:
        legLocs=createLocs(legLocs,name,suff)
    hipLocPos=cmds.xform(name+'hip'+suff,q=True,t=True,ws=True)
    legName=createParCrv('wholeLeg',legLocs,name,suff,hipLocPos,[1,0,0])
    createPvVis('hip','knee','ankle','legPvVis',name,suff,legName, [3,0,0], pvDist)
    createIkfkVis('legIKFKVis','ankle',name,suff,side,[0.5,0.25,-0.5])

    ## final stuff before returning
    legLocs.pop((3, name+'footHeel'+suff))
    cmds.select(cl=True)
    sortedKeys=sorted(legLocs)
    returnKeys=[]
    for x in sortedKeys:
        returnKeys.append(x[1])
    return returnKeys


def createLegSkelMech(locs,prefix,side,par=''):
    name=str(prefix)+'_'+str(side)+'_'
    if side == 'L' or 'L_' in side or '_L' in side:
        col=16
        altCol=29
        thirdCol=30
    else:
        col=13
        altCol=25
        thirdCol=22
    jnts=createJnts(locs,side=side)
    createFKIK(jnts,'leg',prefix,side,name+'ankle_JNT')

    ## create leg mech
    legIK=createIK(name+'legIK',name+'hip_IK_JNT',name+'ankle_IK_JNT')
    if cmds.objExists(name+'legPVCtrl_ROOT'):
        cmds.delete(name+'legPVCtrl_ROOT')
    ## create pv ctrl
    createCtrlShape(name+'legPV',4,scale=[0.3,0.3,0.3],col=col)
    createBuffer(name+'legPV',1,1,name+'legPvVis_posLOC')
    cmds.poleVectorConstraint(name+'legPVConst_GRP',legIK[1])

    ## create foot mech
    if cmds.objExists(name+'RF_mech_GRP'):
        cmds.delete(name+'RF_mech_GRP')
    createIK(name+'footBallIK',name+'ankle_IK_JNT',name+'footBall_IK_JNT')
    createIK(name+'footToesIK',name+'footBall_IK_JNT',name+'footToes_IK_JNT')
    rfJnts=createJnts([name+'footHeel_posLOC',name+'footToes_posLOC',name+'footBall_posLOC',name+'ankle_posLOC'],'_RF')
    rfToes=createIK(name+'RF_footToesIK',name+'RF_footHeel_JNT',name+'RF_footToes_JNT')
    rfBall=createIK(name+'RF_footBallIK',name+'RF_footToes_JNT',name+'RF_footBall_JNT')
    rfAnkle=createIK(name+'RF_ankleIK',name+'RF_footBall_JNT',name+'RF_ankle_JNT')
    cmds.parentConstraint(rfJnts[-1],name+'legIK_GRP',mo=True)
    cmds.parentConstraint(rfJnts[-2],name+'footBallIK_GRP',mo=True)
    cmds.parentConstraint(rfJnts[-3],name+'footToesIK_GRP',mo=True)
    cmds.group(rfJnts[0],rfToes[0],rfBall[0],rfAnkle[0],n=name+'RF_mech_GRP')
    footBallPos=cmds.xform(rfJnts[-2],q=True,t=True,ws=True)
    cmds.xform(name+'RF_mech_GRP', piv=footBallPos)
    cmds.group(name+'legIK_GRP',name+'footBallIK_GRP',name+'footToesIK_GRP',name+'RF_mech_GRP',n=name+'footMech_GRP')
    footBallJntPos=cmds.xform(name+'footBall_IK_JNT',q=True,t=True,ws=True)
    cmds.xform(name+'footMech_GRP',piv=footBallJntPos)

    ## create leg IK ctrls
    ##- foot Toes
    createCtrlShape(name+'footToesIK', 9,col=altCol,scale=[0.7,0.35,0.35],rotOffset=[75,15,0],transOffset=[0,0.35,0],side=side)
    createBuffer(name+'footToesIK', 1, 1, name+'footToes_posLOC')
    footBallLoc=cmds.xform(name+'footBall_posLOC',q=True,ws=True,t=True)
    cmds.xform(name+'footToesIK_CTRL',piv=footBallLoc)
    cmds.parentConstraint(name+'footToesIKConst_GRP',name+'RF_footToesIK_GRP',mo=True)
    ##- foot Ball
    createCtrlShape(name+'footBallIK', 9,col=altCol,scale=[0.7,0.5,0.5],transOffset=[0,1,0])
    createBuffer(name+'footBallIK', 1, 1, name+'footBall_posLOC')
    cmds.parentConstraint(name+'footBallIKConst_GRP',name+'RF_footBallIK_GRP',mo=True)
    cmds.parentConstraint(name+'footBallIKConst_GRP',name+'RF_ankleIK_GRP',mo=True)
    ##- foot Heel
    createCtrlShape(name+'footHeelIK', 9,col=altCol,scale=[0.5,0.5,0.5],rotOffset=[-120,0,0])
    createBuffer(name+'footHeelIK', 1, 1, name+'footHeel_posLOC')
    cmds.parentConstraint(name+'footHeelIKConst_GRP',name+'RF_footHeel_JNT',mo=True)
    cmds.parent(name+'footBallIKCtrl_ROOT',name+'footHeelIKConst_GRP')
    cmds.parent(name+'footToesIKCtrl_ROOT',name+'footHeelIKConst_GRP')
    ##- foot
    createCtrlShape(name+'footIK', 8,scale=[1.5,1.5,1.5],col=col,transOffset=[0,0,-0.25])
    createBuffer(name+'footIK', 1, 1, name+'footBall_posLOC')
    #cmds.parentConstraint(name+'footIKConst_GRP',name+'legIK_GRP',mo=True)
    cmds.parent(name+'footHeelIKCtrl_ROOT',name+'footIKConst_GRP')
    ## create leg FK ctrls
    createCtrlShape(name+'hipFK', 3,col=col,scale=[0.5,0.5,0.5],rotOffset=[0,0,90])
    createBuffer(name+'hipFK', 1, 1, name+'hip_FK_JNT')
    cmds.parentConstraint(name+'hipFKConst_GRP',name+'hip_FK_JNT',mo=True)
    createCtrlShape(name+'kneeFK', 3,col=altCol,scale=[0.5,0.5,0.5],rotOffset=[0,0,90],transOffset=[0,0,0.7])
    createBuffer(name+'kneeFK', 1, 1, name+'knee_FK_JNT')
    cmds.orientConstraint(name+'kneeFKConst_GRP',name+'knee_FK_JNT',mo=True)
    createCtrlShape(name+'ankleFK', 3,col=col,scale=[0.4,0.4,0.4],rotOffset=[0,0,90])
    createBuffer(name+'ankleFK', 1, 1, name+'ankle_FK_JNT')
    cmds.orientConstraint(name+'ankleFKConst_GRP',name+'ankle_FK_JNT',mo=True)
    createCtrlShape(name+'footBallFK', 3,col=altCol,scale=[0.3,0.3,0.3],rotOffset=[0,0,90])
    createBuffer(name+'footBallFK', 1, 1, name+'footBall_FK_JNT')
    cmds.orientConstraint(name+'footBallFKConst_GRP',name+'footBall_FK_JNT',mo=True)
    cmds.parent(name+'footBallFKCtrl_ROOT',name+'ankleFKConst_GRP')
    cmds.parent(name+'ankleFKCtrl_ROOT',name+'kneeFKConst_GRP')
    cmds.parent(name+'kneeFKCtrl_ROOT',name+'hipFKConst_GRP')
    ## legParent ctrl
    if not cmds.objExists(par):
        createCtrlShape(name+'legParent', 5, scale=[0.4,0.4,0.4])
        createBuffer(name+'legParent', 1, 1, name+'hip_posLOC')
        cmds.parentConstraint(name+'legParentConst_GRP', name+'hip_IK_JNT', mo=True)

    ## organise shit
    if cmds.objExists(name+'legMech_GRP'):
        cmds.delete(name+'legMech_GRP')
    cmds.group(name+'hip_IK_JNT',name+'hip_FK_JNT',n=name+'legFKIKSkel_GRP')
    cmds.group(name+'legFKIKSkel_GRP',name+'footMech_GRP',n=name+'legMech_GRP')
    hipJntPos=cmds.xform(name+'hip_IK_JNT',q=True,t=True,ws=True)
    cmds.xform(name+'legMech_GRP',piv=hipJntPos)
    cmds.group(name+'legPVCtrl_ROOT',name+'footIKCtrl_ROOT', n=name+'legIKCtrls_GRP')
    cmds.group(name+'hipFKCtrl_ROOT',n=name+'legFKCtrls_GRP')
    if cmds.objExists(par):
        cmds.parentConstraint(par, name+'hip_IK_JNT', mo=True)
        cmds.parentConstraint(par, name+'hipFKCtrl_ROOT', mo=True)
        createSpSwConstraint([prefix+'_world_LOC', par], name+'footIK_CTRL', 'World:Hip', niceNames=['World','Hip'])
        cmds.group(name+'legSettingsCtrl_ROOT', name+'legIKCtrls_GRP', name+'legFKCtrls_GRP', n=name+'legCtrls_GRP')
    else:
        cmds.parent(name+'legFKCtrls_GRP',name+'legIKCtrls_GRP',name+'legParentConst_GRP')
        cmds.group(name+'legSettingsCtrl_ROOT',name+'legParentCtrl_ROOT',n=name+'legCtrls_GRP')
    ## IKFK ctrl visibilities
    cmds.setDrivenKeyframe(name+'legFKCtrls_GRP', at='visibility',cd=name+'legSettings_CTRL.IKFKSwitch',dv=0.001,v=1)
    cmds.setDrivenKeyframe(name+'legFKCtrls_GRP', at='visibility',cd=name+'legSettings_CTRL.IKFKSwitch',dv=0,v=0)
    cmds.setDrivenKeyframe(name+'legIKCtrls_GRP', at='visibility',cd=name+'legSettings_CTRL.IKFKSwitch',dv=0.999,v=1)
    cmds.setDrivenKeyframe(name+'legIKCtrls_GRP', at='visibility',cd=name+'legSettings_CTRL.IKFKSwitch',dv=1,v=0)
    ## parent to overall rig stuffs
    if cmds.objExists(prefix+'_controls_GRP'):
        cmds.parent(name+'legCtrls_GRP',prefix+'_controls_GRP')
    if cmds.objExists(prefix+'_mechanics_GRP'):
        cmds.parent(name+'legMech_GRP',prefix+'_mechanics_GRP')
    if cmds.objExists(prefix+'_skeleton_GRP'):
        cmds.parent(name+'hip_result_JNT',prefix+'_skeleton_GRP')
    cmds.select(cl=True)


def createArmLocs(prefix,side,mirror=False,mirrorSide='R'):
    name=str(prefix)+'_'+str(side)+'_'
    suff='_posLOC'
    pvDist=1

    ## create Locs
    if side == 'L' or 'L_' in side or '_L' in side:
        armLocs={
            (0, 'clav'):(0.5,14,0),
            (1, 'shoulder'):(2,14,-0.5),
            (2, 'elbow'):(4.5,14,-0.7),
            (3, 'wrist'):(7,14,-0.5),
            (4, 'handPalm'):(8,14,-0.5),
        }
    else:
        armLocs={
            (0, 'clav'):(-0.5,14,0),
            (1, 'shoulder'):(-2,14,-0.5),
            (2, 'elbow'):(-4.5,14,-0.7),
            (3, 'wrist'):(-7,14,-0.5),
            (4, 'handPalm'):(-8,14,-0.5),
        }
    if cmds.objExists(name+'wholeArm'+suff) and not mirror:
        for key, val in armLocs.iteritems():
            pos=cmds.xform(name+key[1]+suff, q=True, t=True, ws=True)
            armLocs[key]=pos
        pvDist=cmds.getAttr(name+'armPvVis'+suff+'.pvDis')
        if cmds.objExists(name+'wholeHand'+suff):
            cmds.parent(name+'wholeHand'+suff, w=True)
        cmds.delete(name+'wholeArm'+suff)
    elif not cmds.objExists(name+'wholeArm'+suff):
        mirror=False

    if mirror:
        name=str(prefix)+'_'+str(mirrorSide)+'_'
        if cmds.objExists(name+'wholeArm'+suff):
            cmds.delete(name+'wholeArm'+suff)
        armLocs=createLocs(armLocs, name, suff, prefix, side, mirror=True, mirSide=mirrorSide)
    else:
        armLocs=createLocs(armLocs,name,suff)
    shoulderLocPos=cmds.xform(name+'shoulder'+suff,q=True,t=True,ws=True)
    armName=createParCrv('wholeArm',armLocs,name,suff,shoulderLocPos,[0,0,1])
    createPvVis('shoulder','elbow','wrist','armPvVis',name,suff,armName, [3,0,0], pvDist)
    createIkfkVis('armIKFKVis','wrist',name,suff,side,[0.5,0.25,-0.5])

    ## final stuff before returning
    cmds.select(cl=True)
    sortedKeys=sorted(armLocs)
    returnKeys=[]
    for x in sortedKeys:
        returnKeys.append(x[1])
    return returnKeys


def createArmSkelMech(locs,prefix,side,par=''):
    name=str(prefix)+'_'+str(side)+'_'
    if side == 'L' or 'L_' in side or '_L' in side:
        col=16
        altCol=29
        thirdCol=30
    else:
        col=13
        altCol=25
        thirdCol=22
    jntLocs=locs
    jntLocs.remove(name+'clav_posLOC')
    jnts=createJnts(jntLocs,side=side)
    clavJnt=createJnts([name+'clav_posLOC'])
    cmds.parent(name+'shoulder_JNT',name+'clav_JNT')
    doOrientJoint(clavJnt, [1,0,0], [0,1,0], [0,1,0], 1)
    createFKIK(jnts,'arm',prefix,side,name+'wrist_JNT')
    ## create arm mech
    armIK=createIK(name+'armIK',name+'shoulder_IK_JNT',name+'wrist_IK_JNT')
    if cmds.objExists(name+'armPVCtrl_ROOT'):
        cmds.delete(name+'armPVCtrl_ROOT')
    createCtrlShape(name+'armPV',4,scale=[0.3,0.3,0.3],col=col)
    createBuffer(name+'armPV',1,1,name+'armPvVis_posLOC')
    cmds.poleVectorConstraint(name+'armPVConst_GRP',armIK[1])
    handPalmIK=createIK(name+'handPalmIK', name+'wrist_IK_JNT',name+'handPalm_IK_JNT')
    cmds.group(name+'handPalmIK_GRP',name+'armIK_GRP',n=name+'handMech_GRP')
    wristJntPos=cmds.xform(name+'wrist_IK_JNT',q=True,t=True,ws=True)
    cmds.xform(name+'handMech_GRP',piv=wristJntPos)
    cmds.duplicate(name+'shoulder_result_JNT',po=True,n=name+'shoulder_end_JNT')
    clavIK=createIK(name+'clavIK', name+'clav_JNT', name+'shoulder_end_JNT')
    ##- create forearm twist
    fArmTwist1=cmds.duplicate(name+'elbow_result_JNT',po=True,n=name+'foreArmTwist01_JNT')
    fArmTwist2=cmds.duplicate(name+'elbow_result_JNT',po=True,n=name+'foreArmTwist02_JNT')
    cmds.parent(fArmTwist1,name+'elbow_result_JNT')
    cmds.parent(fArmTwist2,fArmTwist1)
    cmds.pointConstraint(name+'elbow_result_JNT',fArmTwist1,w=0.666)
    cmds.pointConstraint(name+'wrist_result_JNT',fArmTwist1,w=0.333)
    cmds.pointConstraint(name+'elbow_result_JNT',fArmTwist2,w=0.333)
    cmds.pointConstraint(name+'wrist_result_JNT',fArmTwist2,w=0.666)
    cmds.orientConstraint(name+'elbow_result_JNT',fArmTwist1,w=0.666,sk=['y','z'])
    cmds.orientConstraint(name+'wrist_result_JNT',fArmTwist1,w=0.333,sk=['y','z'])
    cmds.orientConstraint(name+'elbow_result_JNT',fArmTwist2,w=0.333,sk=['y','z'])
    cmds.orientConstraint(name+'wrist_result_JNT',fArmTwist2,w=0.666,sk=['y','z'])
    ## create arm IK ctrls
    ##- hand Palm
    createCtrlShape(name+'handPalmIK', 9,col=altCol,scale=[0.7,0.7,0.7],rotOffset=[0,90,-45],side=side)
    createBuffer(name+'handPalmIK', 1, 1, name+'handPalm_posLOC')
    cmds.parentConstraint(name+'handPalmIKConst_GRP',name+'armIK_GRP',mo=True)
    cmds.parentConstraint(name+'handPalmIKConst_GRP',name+'handPalmIK_GRP',mo=True)
    ##- arm
    createCtrlShape(name+'handIK', 11,scale=[0.5,0.5,0.5],col=col)
    createBuffer(name+'handIK', 1, 1, name+'wrist_IK_JNT')
    if not side == 'L' and 'L_' not in side and '_L' not in side:
        armCtrlRot=cmds.xform(name+'handIKCtrl_PAR',q=True,ro=True)
        armCtrlRot[0]=armCtrlRot[0]-180
        cmds.xform(name+'handIKCtrl_PAR',ro=armCtrlRot)
    cmds.parent(name+'handPalmIKCtrl_ROOT',name+'handIKConst_GRP')
    ##- clav
    createCtrlShape(name+'clav', 9,col=altCol,rotOffset=[0,90,-15],transOffset=[0,0.3,0],side=side)
    createBuffer(name+'clav', 1, 1, clavIK[1])
    cmds.parentConstraint(name+'clavConst_GRP',clavIK[0],mo=True)
    ##- armParent
    if not cmds.objExists(par):
        createCtrlShape(name+'armParent', 5, scale=[0.4,0.4,0.4])
        createBuffer(name+'armParent', 1, 1, name+'clav_posLOC')
        cmds.parentConstraint(name+'armParentConst_GRP',name+'clav_JNT', mo=True)
        cmds.parent(name+'clavCtrl_ROOT',name+'armParentConst_GRP')
    ## create arm FK ctrls
    createCtrlShape(name+'shoulderFK', 3,col=col,scale=[0.4,0.4,0.4],rotOffset=[0,0,90])
    createBuffer(name+'shoulderFK', 1, 1, name+'shoulder_FK_JNT')
    cmds.parentConstraint(name+'shoulderFKConst_GRP',name+'shoulder_FK_JNT',mo=True)
    createCtrlShape(name+'elbowFK', 3,col=altCol,scale=[0.3,0.3,0.3],rotOffset=[0,0,90],transOffset=[0,0,0.6])
    createBuffer(name+'elbowFK', 1, 1, name+'elbow_FK_JNT')
    cmds.orientConstraint(name+'elbowFKConst_GRP',name+'elbow_FK_JNT',mo=True)
    createCtrlShape(name+'wristFK', 3,col=col,scale=[0.2,0.2,0.2],rotOffset=[0,0,90])
    createBuffer(name+'wristFK', 1, 1, name+'wrist_FK_JNT')
    cmds.orientConstraint(name+'wristFKConst_GRP',name+'wrist_FK_JNT',mo=True)
    cmds.parent(name+'wristFKCtrl_ROOT',name+'elbowFKConst_GRP')
    cmds.parent(name+'elbowFKCtrl_ROOT',name+'shoulderFKConst_GRP')
    ## organise shit
    if cmds.objExists(name+'armMech_GRP'):
        cmds.delete(name+'armMech_GRP')
    cmds.group(name+'shoulder_IK_JNT',name+'shoulder_FK_JNT',n=name+'armFKIKSkel_GRP')
    cmds.parentConstraint(name+'clav_JNT',name+'armFKIKSkel_GRP',mo=True)
    cmds.group(name+'armFKIKSkel_GRP',name+'handMech_GRP',name+'clavIK_GRP',n=name+'armMech_GRP')
    cmds.group(name+'armPVCtrl_ROOT',name+'handIKCtrl_ROOT', n=name+'armIKCtrls_GRP')
    cmds.group(name+'shoulderFKCtrl_ROOT',n=name+'armFKCtrls_GRP')
    cmds.parentConstraint(name+'clav_JNT',name+'armFKCtrls_GRP',mo=True)
    if cmds.objExists(par):
        cmds.parentConstraint(par, name+'clav_JNT', mo=True)
        cmds.parentConstraint(par,name+'clavCtrl_ROOT', mo=True)
        createSpSwConstraint([prefix+'_world_LOC',par], name+'handIK_CTRL', 'World:Chest', niceNames=['World', 'Chest'])
        cmds.group(name+'armSettingsCtrl_ROOT',name+'armIKCtrls_GRP', name+'armFKCtrls_GRP', name+'clavCtrl_ROOT',n=name+'armCtrls_GRP')
    else:
        cmds.parent(name+'armIKCtrls_GRP',name+'armFKCtrls_GRP',name+'armParentConst_GRP')
        cmds.group(name+'armSettingsCtrl_ROOT',name+'armParentCtrl_ROOT',n=name+'armCtrls_GRP')
    ## IKFK ctrl visibilities
    cmds.setDrivenKeyframe(name+'armFKCtrls_GRP', at='visibility',cd=name+'armSettings_CTRL.IKFKSwitch',dv=0.001,v=1)
    cmds.setDrivenKeyframe(name+'armFKCtrls_GRP', at='visibility',cd=name+'armSettings_CTRL.IKFKSwitch',dv=0,v=0)
    cmds.setDrivenKeyframe(name+'armIKCtrls_GRP', at='visibility',cd=name+'armSettings_CTRL.IKFKSwitch',dv=0.999,v=1)
    cmds.setDrivenKeyframe(name+'armIKCtrls_GRP', at='visibility',cd=name+'armSettings_CTRL.IKFKSwitch',dv=1,v=0)
    ## parent to overall rig stuffs
    if cmds.objExists(prefix+'_controls_GRP'):
        cmds.parent(name+'armCtrls_GRP',prefix+'_controls_GRP')
    if cmds.objExists(prefix+'_mechanics_GRP'):
        cmds.parent(name+'armMech_GRP',prefix+'_mechanics_GRP')
    if cmds.objExists(prefix+'_skeleton_GRP'):
        cmds.parent(name+'clav_JNT',prefix+'_skeleton_GRP')
    cmds.select(cl=True)


def createFingerLocs(prefix, side, mirror=False, mirrorSide='R'):
    name=str(prefix)+'_'+str(side)+'_'
    suff='_posLOC'
    ## create Locs
    if side == 'L' or 'L_' in side or '_L' in side:
        fngrIndexLocs={
            (0, 'fngrIndex_base',):(8.7, 14, -0.15),
            (1, 'fngrIndex_lowMid',):(9, 14.1, -0.15),
            (2, 'fngrIndex_highMid',):(9.3, 14.1, -0.15),
            (3, 'fngrIndex_tip',):(9.6, 14, -0.15),
        }
        fngrMiddleLocs={
            (0, 'fngrMiddle_base'):(8.7, 14, -0.45),
            (1, 'fngrMiddle_lowMid'):(9, 14.1, -0.45),
            (2, 'fngrMiddle_highMid'):(9.3, 14.1, -0.45),
            (3, 'fngrMiddle_tip'):(9.6, 14, -0.45),
        }
        fngrRingLocs={
            (0, 'fngrRing_base'):(8.7, 14, -0.75),
            (1, 'fngrRing_lowMid'):(9, 14.1, -0.75),
            (2, 'fngrRing_highMid'):(9.3, 14.1, -0.75),
            (3, 'fngrRing_tip'):(9.6, 14, -0.75),
        }
        fngrPinkyLocs={
            (0, 'fngrPinky_base'):(8.7, 14, -1.05),
            (1, 'fngrPinky_lowMid'):(9, 14.1, -1.05),
            (2, 'fngrPinky_highMid'):(9.3, 14.1, -1.05),
            (3, 'fngrPinky_tip'):(9.6, 14, -1.05),
        }
        fngrThumbLocs={
            (0, 'fngrThumb_base'):(8, 14, 0.3),
            (1, 'fngrThumb_lowMid'):(8.3, 14.1, 0.3),
            (2, 'fngrThumb_highMid'):(8.6, 14.1, 0.3),
            (3, 'fngrThumb_tip'):(8.9, 14, 0.3),
        }
    else:
        fngrIndexLocs={
            (0, 'fngrIndex_base'):(-8.7, 14, -0.15),
            (1, 'fngrIndex_lowMid'):(-9, 14.1, -0.15),
            (2, 'fngrIndex_highMid'):(-9.3, 14.1, -0.15),
            (3, 'fngrIndex_tip'):(-9.6, 14, -0.15),
        }
        fngrMiddleLocs={
            (0, 'fngrMiddle_base'):(-8.7, 14, -0.45),
            (1, 'fngrMiddle_lowMid'):(-9, 14.1, -0.45),
            (2, 'fngrMiddle_highMid'):(-9.3, 14.1, -0.45),
            (3, 'fngrMiddle_tip'):(-9.6, 14, -0.45),
        }
        fngrRingLocs={
            (0, 'fngrRing_base'):(-8.7, 14, -0.75),
            (1, 'fngrRing_lowMid'):(-9, 14.1, -0.75),
            (2, 'fngrRing_highMid'):(-9.3, 14.1, -0.75),
            (3, 'fngrRing_tip'):(-9.6, 14, -0.75),
        }
        fngrPinkyLocs={
            (0, 'fngrPinky_base'):(-8.7, 14, -1.05),
            (1, 'fngrPinky_lowMid'):(-9, 14.1, -1.05),
            (2, 'fngrPinky_highMid'):(-9.3, 14.1, -1.05),
            (3, 'fngrPinky_tip'):(-9.6, 14, -1.05),
        }
        fngrThumbLocs={
            (0, 'fngrThumb_base'):(-8, 14, 0.3),
            (1, 'fngrThumb_lowMid'):(-8.3, 14.1, 0.3),
            (2, 'fngrThumb_highMid'):(-8.6, 14.1, 0.3),
            (3, 'fngrThumb_tip'):(-8.9, 14, 0.3),
        }

    fngrLocs={
        (0, 'fngrIndexLocs', 'Index'):fngrIndexLocs,
        (1, 'fngrMiddleLocs', 'Middle'):fngrMiddleLocs,
        (2, 'fngrRingLocs', 'Ring'):fngrRingLocs,
        (3, 'fngrPinkyLocs', 'Pinky'):fngrPinkyLocs,
        (4, 'fngrThumbLocs', 'Thumb'):fngrThumbLocs,
    }

    if cmds.objExists(name+'wholeHand'+suff) and not mirror:
        for fngrKey, fngrVal in fngrLocs.iteritems():
            for sectKey, sectVal in fngrVal.iteritems():
                pos=cmds.xform(name+sectKey[1]+suff, q=True, t=True, ws=True)
                fngrLocs[fngrKey][sectKey]=(pos[0],pos[1],pos[2])
        cmds.delete(name+'wholeHand'+suff)
    elif not cmds.objExists(name+'wholeHand'+suff):
        mirror=False

    ## create
    if mirror:
        name=str(prefix)+'_'+str(mirrorSide)+'_'
        if cmds.objExists(name+'wholeHand'+suff):
            cmds.delete(name+'wholeHand'+suff)
        for k, v in fngrLocs.iteritems():
            fngrLocs[k]=createLocs(v, name, suff, prefix, side, mirror=True, mirSide=mirrorSide)
        side=mirrorSide
    else:
        for k, v in fngrLocs.iteritems():
            fngrLocs[k]=createLocs(v, name, suff)
    ## parent curves
    fngrsList=[
        'Index',
        'Middle',
        'Ring',
        'Pinky',
        'Thumb',
    ]
    handPos=cmds.xform(name+'fngrMiddle_base'+suff, q=True, t=True, ws=True)
    handName=createParCrv('wholeHand', '', name, suff, xyz=handPos)
    if cmds.objExists(name+'wholeArm'+suff):
        cmds.parent(name+'wholeHand'+suff, name+'wholeArm'+suff)
    for x in fngrsList:
        fngrBaseName=name+'fngr'+x+'_base'+suff
        pos=cmds.xform(fngrBaseName, q=True, t=True, ws=True)
        curFngrList=[]
        for k,v in fngrLocs.iteritems():
            for sectKey, sectVal in v.iteritems():
                if x in sectKey[1]:
                    curFngrList.append(sectKey)
        fngrName=createParCrv('wholeFngr'+x, curFngrList, name, suff, xyz=pos)
        cmds.parent(name+'wholeFngr'+x+suff, name+'wholeHand'+suff)
    for k, v in fngrLocs.iteritems():
        curFngr=k[2]
        createPvVis('fngr'+curFngr+'_base', 'fngr'+curFngr+'_lowMid', 'fngr'+curFngr+'_tip','fngr'+curFngr+'PvVis', name, suff, handName, [3,0,0], 0.2)

    ## final stuff before returning
    cmds.select(cl=True)
    for k, v in fngrLocs.iteritems():
        sortedKeys=sorted(v)
        newKeys=[]
        for x in sortedKeys:
            newKeys.append(x[1])
        fngrLocs[k]=newKeys
        resizeLocs(newKeys, [0.2, 0.2, 0.2])
    return fngrLocs


def createFingerSkelMech(locs, prefix, side, par=''):
    name=str(prefix)+'_'+str(side)+'_'
    if side == 'L' or 'L_' in side or '_L' in side:
        col = 16
        altCol = 29
        thirdCol = 30
    else:
        col = 13
        altCol = 25
        thirdCol = 22
    ## all finger ctrl
    createCtrlShape(name+'fingers', 14, col=altCol, scale=[0.5, 0.3, 0.5], rotOffset=[0, 0, -90], transOffset=[0, 3, 0], side=side)
    createBuffer(name+'fingers', 1, 1, name+'handPalm_posLOC')
    ## create jnts
    ikList=[]
    for k, v in locs.iteritems():
        curFngr=k[2]
        jnts = createJnts(v,side=side)
        if par is not '':
            for x in jnts:
                if '_base_' in x:
                    cmds.parent(x,par)

        ## create finger mech
        ikVarName='fngr'+curFngr+'IK'
        exec(ikVarName+ "= createIK(name+'fngr'+curFngr+'IK', name+'fngr'+curFngr+'_base_JNT', name+'fngr'+curFngr+'_tip_JNT')")
        exec("ikList.append("+ikVarName+"[0])")

        ## finger tips ctrls
        createCtrlShape(name+'fngr'+curFngr, 10, col=thirdCol, scale=[0.1,0.1,0.04], side=side)
        createBuffer(name+'fngr'+curFngr, 1, 1, name+'fngr'+curFngr+'_tip_posLOC')
        exec("cmds.parentConstraint(name+'fngr'+curFngr+'Const_GRP', "+ikVarName+"[1])")
        if not curFngr == 'Thumb':
            cmds.parent(name+'fngr'+curFngr+'Ctrl_ROOT', name+'fingersConst_GRP')
        else:
            cmds.parent(name+'fngr'+curFngr+'Ctrl_ROOT', name+'handPalmIKConst_GRP')
        ## create pv controls
        if cmds.objExists(name+'fngr'+curFngr+'PVCtrl_ROOT'):
            cmds.delete(name+'fngr'+curFngr+'PVCtrl_ROOT')
        createCtrlShape(name+'fngr'+curFngr+'PV', 4, scale=[0.2,0.2,0.2], col=thirdCol)
        createBuffer(name+'fngr'+curFngr+'PV', 1, 1, name+'fngr'+curFngr+'PvVis_posLOC')
        cmds.parent(name+'fngr'+curFngr+'PVCtrl_ROOT', name+'fngr'+curFngr+'Const_GRP')
        eval("cmds.poleVectorConstraint(name+'fngr'+curFngr+'PVConst_GRP', "+ikVarName+"[1])")

    ## organise shit
    cmds.group(ikList, n=name+'fingerIKs_GRP')
    cmds.parent(name+'fingerIKs_GRP', name+'handMech_GRP')
    cmds.parent(name+'fingersCtrl_ROOT', name+'handIKConst_GRP')


def createToeLocs(prefix, side, mirror=False, mirrorSide='R'):
    name=str(prefix)+'_'+str(side)+'_'
    suff='_posLOC'
    ## create locs
    if side == 'L' or 'L_' in side or '_L' in side:
        toeIndexLocs={
            (0, 'toeIndex_base'):(0.8, 0, 1.45),
            (1, 'toeIndex_lowMid'):(0.8, 0.07, 1.6),
            (2, 'toeIndex_highMid'):(0.8, 0.06, 1.75),
            (3, 'toeIndex_tip'):(0.8, 0, 1.9),
        }
        toeMiddleLocs={
            (0, 'toeMiddle_base'):(1, 0, 1.45),
            (1, 'toeMiddle_lowMid'):(1, 0.07, 1.6),
            (2, 'toeMiddle_highMid'):(1, 0.06, 1.75),
            (3, 'toeMiddle_tip'):(1, 0, 1.9),
        }
        toeRingLocs={
            (0, 'toeRing_base'):(1.2, 0, 1.45),
            (1, 'toeRing_lowMid'):(1.2, 0.07, 1.6),
            (2, 'toeRing_highMid'):(1.2, 0.06, 1.75),
            (3, 'toeRing_tip'):(1.2, 0, 1.9),
        }
        toePinkyLocs={
            (0, 'toePinky_base'):(1.4, 0, 1.45),
            (1, 'toePinky_lowMid'):(1.4, 0.07, 1.6),
            (2, 'toePinky_highMid'):(1.4, 0.06, 1.75),
            (3, 'toePinky_tip'):(1.4, 0, 1.9),
        }
        toeThumbLocs={
            (0, 'toeThumb_base'):(0.6, 0, 1.45),
            (1, 'toeThumb_lowMid'):(0.6, 0.07, 1.6),
            (2, 'toeThumb_highMid'):(0.6, 0.06, 1.75),
            (3, 'toeThumb_tip'):(0.6, 0, 1.9),
        }
    else:
        toeIndexLocs={
            (0, 'toeIndex_base'):(-0.8, 0, 1.45),
            (1, 'toeIndex_lowMid'):(-0.8, 0.07, 1.6),
            (2, 'toeIndex_highMid'):(-0.8, 0.06, 1.75),
            (3, 'toeIndex_tip'):(-0.8, 0, 1.9),
        }
        toeMiddleLocs={
            (0, 'toeMiddle_base'):(-1, 0, 1.45),
            (1, 'toeMiddle_lowMid'):(-1, 0.07, 1.6),
            (2, 'toeMiddle_highMid'):(-1, 0.06, 1.75),
            (3, 'toeMiddle_tip'):(-1, 0, 1.9),
        }
        toeRingLocs={
            (0, 'toeRing_base'):(-1.2, 0, 1.45),
            (1, 'toeRing_lowMid'):(-1.2, 0.07, 1.6),
            (2, 'toeRing_highMid'):(-1.2, 0.06, 1.75),
            (3, 'toeRing_tip'):(-1.2, 0, 1.9),
        }
        toePinkyLocs={
            (0, 'toePinky_base'):(-1.4, 0, 1.45),
            (1, 'toePinky_lowMid'):(-1.4, 0.07, 1.6),
            (2, 'toePinky_highMid'):(-1.4, 0.06, 1.75),
            (3, 'toePinky_tip'):(-1.4, 0, 1.9),
        }
        toeThumbLocs={
            (0, 'toeThumb_base'):(-0.6, 0, 1.45),
            (1, 'toeThumb_lowMid'):(-0.6, 0.07, 1.6),
            (2, 'toeThumb_highMid'):(-0.6, 0.06, 1.75),
            (3, 'toeThumb_tip'):(-0.6, 0, 1.9),
        }

    toeLocs={
        (0, 'toeIndexLocs', 'Index'):toeIndexLocs,
        (1, 'toeMiddleLocs', 'Middle'):toeMiddleLocs,
        (2, 'toeRingLocs', 'Ring'):toeRingLocs,
        (3, 'toePinkyLocs', 'Pinky'):toePinkyLocs,
        (4, 'toeThumbLocs', 'Thumb'):toeThumbLocs,
    }

    if cmds.objExists(name+'wholeFoot'+suff) and not mirror:
        for toeKey, toeVal in toeLocs.iteritems():
            for sectKey, sectVal in toeVal.iteritems():
                #pos=cmds.xform(name+toeKey+'_'+sectKey+suff)
                pos=cmds.xform(name+sectKey[1]+suff, q=True, t=True, ws=True)
                toeLocs[toeKey][sectKey]=(pos[0],pos[1],pos[2])
        cmds.delete(name+'wholeFoot'+suff)
    elif not cmds.objExists(name+'wholeFoot'+suff):
        mirror=False

    ## create
    if mirror:
        name=str(prefix)+'_'+str(mirrorSide)+'_'
        if cmds.objExists(name+'wholeFoot'+suff):
            cmds.delete(name+'wholeFoot'+suff)
        for k, v in toeLocs.iteritems():
            toeLocs[k]=createLocs(v, name, suff, prefix, side, mirror=True, mirSide=mirrorSide)
        side=mirrorSide
    else:
        for k, v in toeLocs.iteritems():
            toeLocs[k]=createLocs(v, name, suff)
    ## parent curves
    toesList=[
        'Index',
        'Middle',
        'Ring',
        'Pinky',
        'Thumb',
    ]
    footPos=cmds.xform(name+'toeMiddle_base'+suff, q=True, t=True, ws=True)
    footName=createParCrv('wholeFoot', '', name, suff, xyz=footPos)
    if cmds.objExists(name+'wholeLeg'+suff):
        cmds.parent(name+'wholeFoot'+suff, name+'wholeLeg'+suff)
    for x in toesList:
        toeBaseName=name+'toe'+x+'_base'+suff
        pos=cmds.xform(toeBaseName, q=True, t=True, ws=True)
        curToeList=[]
        for k,v in toeLocs.iteritems():
            for sectKey, sectVal in v.iteritems():
                if x in sectKey[1]:
                    curToeList.append(sectKey)
        toeName=createParCrv('wholeToe'+x, curToeList, name, suff, xyz=pos)
        cmds.parent(name+'wholeToe'+x+suff, name+'wholeFoot'+suff)
    for k, v in toeLocs.iteritems():
        curToe=k[2]
        createPvVis('toe'+curToe+'_base', 'toe'+curToe+'_lowMid', 'toe'+curToe+'_tip','toe'+curToe+'PvVis', name, suff, footName, [3,0,0], 0.2)
    ## final stuff before returning
    cmds.select(cl=True)
    for k, v in toeLocs.iteritems():
        sortedKeys=sorted(v)
        newKeys=[]
        for x in sortedKeys:
            newKeys.append(x[1])
        toeLocs[k]=newKeys
        resizeLocs(newKeys, [0.2,0.2,0.2])
    return toeLocs


def createToeSkelMech(locs, prefix, side, par=''):
    name=str(prefix)+'_'+str(side)+'_'
    if side == 'L' or 'L_' in side or '_L' in side:
        col = 16
        altCol = 29
        thirdCol = 30
    else:
        col = 13
        altCol = 25
        thirdCol = 22

    ## all toes ctrl - created in leg instead {might need changing}
    if not cmds.objExists(name+'footToesIK_CTRL'):
        createCtrlShape(name+'footToesIK', 9,col=altCol,scale=[0.7,0.35,0.35],rotOffset=[75,15,0],transOffset=[0,0.35,0],side=side)
        createBuffer(name+'footToesIK', 1, 1, name+'footToes_posLOC')
        footBallLoc=cmds.xform(name+'footBall_posLOC',q=True,ws=True,t=True)
        cmds.xform(name+'footToesIK_CTRL',piv=footBallLoc)
    ## create jnts
    ikList = []
    for k, v in locs.iteritems():
        curToe = k[2]
        jnts = createJnts(v, side=side)
        if par is not '':
            for x in jnts:
                if '_base_' in x:
                    cmds.parent(x, par)

        ## create toe mech
        ikVarName = 'toe'+curToe+'IK'
        exec(ikVarName + "= createIK(name+'toe'+curToe+'IK', name+'toe'+curToe+'_base_JNT', name+'toe'+curToe+'_tip_JNT')")
        exec("ikList.append("+ikVarName+"[0])")

        ## create toe tip ctrls
        createCtrlShape(name+'toe'+curToe, 10, col=thirdCol, scale=[0.04, 0.04, 0.016], side=side, rotOffset=[90,-60,-90], transOffset=[0,1.5,0])
        createBuffer(name+'toe'+curToe, 1, 1, name+'toe'+curToe+'_tip_posLOC')
        exec("cmds.parentConstraint(name+'toe'+curToe+'Const_GRP', "+ikVarName+"[1])")
        cmds.parent(name+'toe'+curToe+'Ctrl_ROOT', name+'footToesIKConst_GRP')
        ## create pv ctrls
        if cmds.objExists(name+'toe'+curToe+'PVCtrl_ROOT'):
            cmds.delete(name+'toe'+curToe+'PVCtrl_ROOT')
        createCtrlShape(name+'toe'+curToe+'PV', 4, scale=[0.05,0.05,0.05], col=thirdCol)
        createBuffer(name+'toe'+curToe+'PV', 1, 1, name+'toe'+curToe+'PvVis_posLOC')
        cmds.parent(name+'toe'+curToe+'PVCtrl_ROOT', name+'toe'+curToe+'Const_GRP')
        eval("cmds.poleVectorConstraint(name+'toe'+curToe+'PVConst_GRP', "+ikVarName+"[1])")

    ## organise shit
    cmds.group(ikList, n=name+'toeIKs_GRP')
    cmds.parent(name+'toeIKs_GRP', name+'footMech_GRP')


def createSpineLocs(prefix):
    name=str(prefix)+'_'
    suff='_posLOC'
    if cmds.objExists(name+'spine_posCRV'):
        spineCrv=cmds.rebuildCurve(name+'spine_posCRV', rpo=True,rt=True)
    else:
        spineCrv=cmds.curve(n=name+'spine_posCRV',degree = 3,\
                knot = [\
                        0, 0, 0, 1, 2, 3, 4, 5, 5, 5\
                ],\
                point = [\
                            (0.0, 9.70, -0.70),\
                            (0.0, 10.00, -0.60),\
                            (0.0, 10.80, -0.50),\
                            (0.0, 11.60, -0.50),\
                            (0.0, 12.30, -0.60),\
                            (0.0, 13.50, -1.00),\
                            (0.0, 14.30, -1.00),\
                            (0.0, 14.70, -0.90)\
                ]\
        )
    headLocs={
        (0, 'head'):(0, 15.5, -0.6),
        (1, 'headEnd'):(0, 17, -0.4),
    }
    headAimPos=[0,16.25,10]
    if cmds.objExists(name+'wholeHead'+suff):
        headAimPos=cmds.xform(name+'headAim'+suff,q=True,ws=True,t=True)
        for key, val in headLocs.iteritems():
            pos=cmds.xform(name+key[1]+suff, q=True, t=True, ws=True)
            headLocs[key]=pos
        cmds.delete(name+'wholeHead'+suff)
    headLocs=createLocs(headLocs, name, suff)
    headLocPos=cmds.xform(name+'head'+suff,q=True,t=True,ws=True)
    ## head aim
    createSingleLoc('headAim', name, suff, headAimPos,par=(name+'head'+suff,name+'headEnd'+suff))
    cmds.parent(name+'headAim'+suff,name+'head'+suff)
    headName=createParCrv('wholeHead', headLocs, name, suff, headLocPos)
    cmds.select(cl=True)
    sortedKeys=sorted(headLocs)
    returnKeys=[]
    for x in sortedKeys:
        returnKeys.append(x[1])
    return spineCrv,returnKeys


def createSpineSkelMech(prefix,jntNum,spineCrv,headLocs):
    name=str(prefix)+'_'
    suff='_posLOC'
    spineLocs=[]
    ## create jnts on spine crv
    reCrv=cmds.duplicate(spineCrv,n=name+'reCrv')
    cmds.rebuildCurve(reCrv,s=jntNum-1,rpo=True,rt=0,end=1,kr=0,kt=False)
    for i in range(jntNum):
        pos=cmds.xform(reCrv[0]+'.ep['+str(i)+']',q=True,t=True,ws=True)
        if i==0:
            spineNum='base'
        elif i==jntNum-1:
            spineNum='end'
        elif jntNum <12:
            spineNum=str(i).zfill(2)
        elif jntNum <102:
            spineNum=str(i).zfill(3)
        loc=cmds.spaceLocator(n=name+'spine_'+spineNum+suff)
        cmds.xform(loc,t=pos)
        spineLocs.append(loc[0])
    cmds.delete(reCrv)
    allLocs=spineLocs+headLocs
    createJnts(allLocs)
    cmds.delete(spineLocs)
    ## create spine IK
    createSplineIK(name+'spine_base_JNT',name+'spine_end_JNT',name+'spineIK',name+'global_CTRL')
    if cmds.objExists(name+'spineIK_hips_BIND') or cmds.objExists(name+'spineIK_chest_BIND'):
        cmds.delete(name+'spineIK_hips_BIND')
        cmds.delete(name+'spineIK_chest_BIND')
    if jntNum < 12:
        chestJnt=str(jntNum/2).zfill(2)
        spineArmJnt=str(jntNum-2).zfill(2)
    elif jntNum < 102:
        chestJnt=str(jntNum/2).zfill(3)
        spineArmJnt=str(jntNum-2).zfill(3)
    ##- create bind jnts
    cmds.duplicate(name+'spine_base_JNT',n=name+'spineIK_hips_BIND',po=True)
    cmds.duplicate(name+'spine_'+chestJnt+'_JNT',n=name+'spineIK_chest_BIND',po=True)
    cmds.parent(name+'spineIK_chest_BIND',w=True)
    cmds.group(name+'spineIK_hips_BIND',n=name+'spineIK_hipsMech_GRP')
    cmds.group(name+'spineIK_chest_BIND',n=name+'spineIK_chestMech_GRP')
    cmds.group(name+'spineIK_hipsMech_GRP',name+'spineIK_chestMech_GRP',name+'spineIK_GRP',n=name+'spineIKMech_GRP')
    ##- create spine IK end locators
    cmds.spaceLocator(n=name+'spineIK_base_LOC')
    constr=cmds.parentConstraint(name+'spine_base_JNT',name+'spineIK_base_LOC')
    cmds.delete(constr)
    cmds.parent(name+'spineIK_base_LOC',name+'spineIK_hips_BIND')
    cmds.spaceLocator(n=name+'spineIK_end_LOC')
    constr=cmds.parentConstraint(name+'spine_end_JNT',name+'spineIK_end_LOC')
    cmds.delete(constr)
    cmds.parent(name+'spineIK_end_LOC',name+'spineIK_chest_BIND')
    ##- skin bind jnts to crv
    cmds.skinCluster(name+'spineIK_hips_BIND',name+'spineIK_chest_BIND',name+'spineIK_CRV')
    ##- spine IK adv twist
    cmds.setAttr(name+'spineIK_HDL.dTwistControlEnable',1)
    cmds.setAttr(name+'spineIK_HDL.dWorldUpType', 4)
    cmds.connectAttr(name+'spineIK_base_LOC.worldMatrix[0]',name+'spineIK_HDL.dWorldUpMatrix')
    cmds.connectAttr(name+'spineIK_end_LOC.worldMatrix[0]',name+'spineIK_HDL.dWorldUpMatrixEnd')
    ## create head mech
    neckIK=createIK('neckIK', name+'spine_end_JNT', name+'head_JNT')
    headIK=createIK('headIK', name+'head_JNT', name+'headEnd_JNT')
    cmds.group(neckIK[0],headIK[0],n=name+'headMech_GRP')
    ## create ctrls
    ##- hips
    createCtrlShape(name+'hips', 5,col=11)
    createBuffer(name+'hips', 1, 1, name+'spineIK_hipsMech_GRP')
    cmds.parentConstraint(name+'hipsConst_GRP',name+'spineIK_hipsMech_GRP',mo=True)
    cmds.addAttr(name+'hips_CTRL',ln='twist',at='float',k=True)
    cmds.connectAttr(name+'hips_CTRL.twist',name+'spineIK_base_LOC.rotateX')
    ##- chest
    createCtrlShape(name+'chest', 5,col=23)
    createBuffer(name+'chest', 1, 1, name+'spineIK_chestMech_GRP')
    cmds.parentConstraint(name+'chestConst_GRP',name+'spineIK_chestMech_GRP',mo=True)
    cmds.addAttr(name+'chest_CTRL',ln='twist',at='float',k=True)
    cmds.connectAttr(name+'chest_CTRL.twist',name+'spineIK_end_LOC.rotateX')
    ##- body
    createCtrlShape(name+'body', 13,col=23)
    createBuffer(name+'body', 1, 1, name+'spineIK_hipsMech_GRP')
    cmds.parent(name+'hipsCtrl_ROOT',name+'chestCtrl_ROOT',name+'bodyConst_GRP')
    ##- head aim
    createCtrlShape(name+'headAim', 6,col=24,scale=[0.65,0.65,0.65],rotOffset=[90,0,0])
    createBuffer(name+'headAim', 1, 1, name+'headAim_posLOC')
    ##- head
    createCtrlShape(name+'head', 5,col=24,scale=[0.7,0.7,0.7],transOffset=[0,1,0.5])
    createBuffer(name+'head', 1, 1, neckIK[1])
    cmds.group(name+'headCtrl_ROOT',name+'headAimCtrl_ROOT',n=name+'headCtrls_GRP')
    cmds.parentConstraint(name+'headConst_GRP',name+'headMech_GRP',mo=True)
    cmds.aimConstraint(name+'headAimConst_GRP',name+'headCtrl_ROOT',mo=True)
    cmds.parent(name+'headCtrls_GRP',name+'chestConst_GRP')
    createSpSwConstraint([prefix+'_world_LOC',name+'spineIK_end_LOC'], name+'head_CTRL', 'World:Chest', niceNames=['World','Chest'], constrTarget=name+'headAimCtrl_ROOT')
    ## clean shit up
    if cmds.objExists(prefix+'_controls_GRP'):
        cmds.parent(name+'bodyCtrl_ROOT',prefix+'_controls_GRP')
    if cmds.objExists(prefix+'_mechanics_GRP'):
        cmds.parent(name+'spineIKMech_GRP',name+'headMech_GRP',prefix+'_mechanics_GRP')
    if cmds.objExists(prefix+'_skeleton_GRP'):
        cmds.parent(name+'spine_base_JNT',prefix+'_skeleton_GRP')
    cmds.select(cl=True)
    return spineArmJnt


def createLocs(locInfo, name, suff, prefix='', side='', mirror=False, mirSide=''):
    if mirror:
        name=str(prefix)+'_'+str(side)+'_'
        mirName=str(prefix)+'_'+str(mirSide)+'_'
    locKeys=sorted(locInfo)

    locNamesList={}
    for key, val in locInfo.iteritems():
        locName=name+key[1]+suff
        if mirror:
            val=cmds.xform(locName, q=True, t=True, ws=True)
            locName=mirName+key[1]+suff
            val[0]=-val[0]
        if not cmds.objExists(locName):
            cmds.spaceLocator(n=locName)
            cmds.xform(locName,t=(val[0], val[1], val[2]))
        locNamesList[key[0]] = locName
    for i, x in enumerate(locKeys):
        locInfo[i, locNamesList[i]]=locInfo.pop(x)
    return locInfo


def resizeLocs(locs, size=[1,1,1]):
    for x in locs:
        cmds.setAttr(x+'.localScaleX', size[0])
        cmds.setAttr(x+'.localScaleY', size[1])
        cmds.setAttr(x+'.localScaleZ', size[2])


def createParCrv(crvName,locs,name,suff,xyz=[0,0,0],rotXyz=[0,0,0]):
    parCrvName=name+crvName+suff
    if not cmds.objExists(parCrvName):
        cmds.circle(n=parCrvName,nr=(rotXyz[0],rotXyz[1],rotXyz[2]))
        cmds.xform(parCrvName,t=(xyz[0],xyz[1],xyz[2]))
        cmds.makeIdentity(parCrvName,a=True,t=True)
        for x in locs:
            cmds.parent(x[1],parCrvName)
    return parCrvName


def createPvVis(strtJnt,aimJnt,endJnt,locName,name,suff,parName,xyz=[0,0,0],dist=1):
    pvParName=name+locName+'Par'+suff
    if not cmds.objExists(pvParName):
        cmds.spaceLocator(n=pvParName)
        cmds.parent(pvParName,parName)
        cmds.pointConstraint(name+strtJnt+suff,name+endJnt+suff,pvParName)
        cmds.aimConstraint(name+aimJnt+suff,pvParName)
        cmds.setAttr(pvParName+'Shape.localScale',3,0,0)
        cmds.setAttr(pvParName+'.overrideEnabled',1)
        cmds.setAttr(pvParName+'.overrideDisplayType',1)
        ## create moveable PV control loc
    pvName=name+locName+suff
    if not cmds.objExists(pvName):
        cmds.spaceLocator(n=pvName)
        cmds.parent(pvName,parName)

        cmds.parentConstraint(pvParName,pvName)
        cmds.delete(pvName,cn=True)
        cmds.xform(pvName,t=xyz,r=True,os=True)
        cmds.parentConstraint(pvParName,pvName,mo=True)

        cmds.setAttr(pvName+'Shape.localScale',0.5,0.5,0.5)
        pvLckAttr=[
            'translateX',
            'translateY',
            'translateZ',
            'rotateX',
            'rotateY',
            'rotateZ'
        ]
        for x in pvLckAttr:
            cmds.setAttr(pvName+'.'+x,l=True,k=False)
        cmds.select(pvName)
        cmds.addAttr(sn='pvDis',nn='Pole Vector Distance', dv=1.0, h=False,k=True)
        cmds.connectAttr(pvName+'.pvDis',pvParName+'.scaleX')
        cmds.setAttr(pvName+'.pvDis', dist)


def createIkfkVis(crvName,jntPar,name,suff,side,xyz=[0.5,0.25,-0.5]):
    ikfkName=name+crvName+suff
    if not cmds.objExists(ikfkName):
        cmds.spaceLocator(n=ikfkName)
        if side=='L' or 'L_' in side or '_L' in side:
            ikfkXPos=xyz[0]
        else:
            ikfkXPos=-xyz[0]
        cmds.xform(ikfkName,t=(ikfkXPos,xyz[1],xyz[2]))
        cmds.parent(ikfkName,name+jntPar+suff, r=True)
        cmds.setAttr(ikfkName+'Shape.localScale',0.5,0.5,0.5)


def createSingleLoc(locName,name,suff,xyz,side=None,par=None):
    locName=name+locName+suff
    if not cmds.objExists(locName):
        cmds.spaceLocator(n=locName)
        if side is not None:
            if not side == 'L' and 'L_' not in side and '_L' not in side:
                xyz[0]=-xyz[0]
        cmds.xform(locName,t=xyz)
        if par:
            cmds.parentConstraint(par,locName,mo=True)


def createJnts(locs,extraName='',side='L',*args):
    jnts=[]
    cmds.select(cl=True)
    for x in locs:
        jntName=x.rpartition('_')
        jntName=jntName[0].rpartition('_')
        jntName=jntName[0]+extraName+'_'+jntName[2]+'_JNT'
        if cmds.objExists(jntName):
            cmds.delete(jntName)
        locPos=cmds.xform(x,q=True,t=True,ws=True)
        cmds.joint(n=jntName,p=locPos)
        jnts.append(jntName)
        cmds.setAttr(jntName+'.radius', 0.2)
    if side == 'L' or 'L_' in side or '_L' in side:
        doOrientJoint(jnts, [1,0,0], [0,1,0], [0,1,0], 1)
    else:
        doOrientJoint(jnts, [-1,0,0], [0,1,0], [0,1,0], 1)
    cmds.select(cl=True)
    return jnts


def createIK(ikName,start,end):
    hdlName=ikName+'_HDL'
    effName=ikName+'_EFF'
    grpName=ikName+'_GRP'
    if cmds.objExists(grpName):
        cmds.delete(grpName)
    ikH,ikE=cmds.ikHandle(n=hdlName,sj=start,ee=end)
    cmds.rename(ikE,effName)
    hdlPos=cmds.xform(ikH,q=True,t=True)
    cmds.group(hdlName,n=grpName,r=True)
    cmds.xform(grpName,piv=hdlPos)
    cmds.select(cl=True)
    return grpName,hdlName


def createFKIK(joints,limb,prefix,side,parJnt):
    ## Set Suffix Values
    suffixA = '_IK_'
    suffixB = '_FK_'
    curSuffix = '_result_'
    name=str(prefix)+'_'+str(side)+'_'
    ctrlCrv = name+limb+'Settings'
    attrName = 'IKFKSwitch'

    createSettingCtrl(ctrlCrv, name+limb+'IKFKVis_posLOC',parJnt,side)

    ## Main Code

    for x in joints:
        if curSuffix not in x:
            if '_JNT' not in x:
                cmds.confirmDialog(title='ERROR', message='One or more incorrectly named Joints selected', button=['Ok'])
                return

            ## Rename current Joint
            resultJointName = x.replace('_JNT', curSuffix+'JNT')
            if cmds.objExists(resultJointName):
                cmds.delete(resultJointName)

            cmds.rename(x,resultJointName)
            x=resultJointName

        ## Names from current Joint
        blendSuffix = '_'+'IK'+'FK'[:1].upper() + 'FK'[1:]
        ikJointName = x.replace(curSuffix, suffixA)
        fkJointName = x.replace(curSuffix, suffixB)
        blendRName = x.replace(curSuffix+'JNT', blendSuffix+'Rot_BLND')
        blendTName = x.replace(curSuffix+'JNT', blendSuffix+'Trans_BLND')
        blendSName = x.replace(curSuffix+'JNT', blendSuffix+'Scale_BLND')

        ## Duplicate Joints
        if cmds.objExists(ikJointName):
            cmds.delete(ikJointName)
        if cmds.objExists(fkJointName):
            cmds.delete(fkJointName)
        ikJoints = cmds.duplicate(x, n=ikJointName, po=True)
        fkJoints = cmds.duplicate(x, n=fkJointName, po=True)

        ## Parent Duplicated Joints
        resultParent=cmds.listRelatives(x, p=True, c=False)
        if resultParent:
            for p in resultParent:
                if curSuffix in p:
                    ikParent=p.replace(curSuffix, suffixA)
                    fkParent=p.replace(curSuffix, suffixB)
                    cmds.parent(ikJointName, ikParent)
                    cmds.parent(fkJointName, fkParent)

        ## Create and attach Blends
        cmds.createNode('blendColors', n=blendRName)
        cmds.createNode('blendColors', n=blendTName)
        cmds.createNode('blendColors', n=blendSName)
        ##- Inputs
        cmds.connectAttr(ikJointName + '.rotate', blendRName + '.color2')
        cmds.connectAttr(fkJointName + '.rotate', blendRName + '.color1')
        cmds.connectAttr(ikJointName + '.translate', blendTName + '.color2')
        cmds.connectAttr(fkJointName + '.translate', blendTName + '.color1')
        cmds.connectAttr(ikJointName + '.scale', blendSName + '.color2')
        cmds.connectAttr(fkJointName + '.scale', blendSName + '.color1')
        cmds.connectAttr(ctrlCrv+'_CTRL' + '.' + attrName, blendRName + '.blender')
        cmds.connectAttr(ctrlCrv+'_CTRL' + '.' + attrName, blendTName + '.blender')
        cmds.connectAttr(ctrlCrv+'_CTRL' + '.' + attrName, blendSName + '.blender')
        ##- Outputs
        cmds.connectAttr(blendRName + '.output', x + '.rotate')
        cmds.connectAttr(blendTName + '.output', x + '.translate')
        cmds.connectAttr(blendSName + '.output', x + '.scale')


def createSplineIK(start,end,ikName='splineIK',controlName=''):
        ## setup name variables
        hdlName=ikName+'_HDL'
        effName=ikName+'_EFF'
        crvName=ikName+'_CRV'
        grpName=ikName+'_GRP'
        crvInfoName=ikName+'Crv_INFO'
        crvGlobalScaleName=ikName+'CrvGlobalScale_MULT'
        crvStretchName=ikName+'CrvStretch_DIV'

        if cmds.objExists(grpName):
            cmds.delete(grpName)
        ## get effected joints
        startJntParents=getParents(start)
        endJntParents=getParents(end)

        if startJntParents:
            eP = list(set(endJntParents)-set(startJntParents))
        else:
            eP=endJntParents
        effectedJnts=eP

        ## create IK
        ikH,ikE,ikC=cmds.ikHandle(n=hdlName, sj=start, ee=end, solver='ikSplineSolver', parentCurve=False, simplifyCurve=False)
        cmds.group(ikH,ikC,n=grpName)
        cmds.rename(ikE,effName)
        cmds.rename(ikC,crvName)

        ## create curve info node
        crvInf=cmds.arclen(crvName, ch=True)
        if not cmds.objExists(crvInfoName):
            cmds.rename(crvInf,crvInfoName)

        ## create global scale mult node
        crvGlobalScaleNode=cmds.createNode('multDoubleLinear', n=crvGlobalScaleName, ss=True)
        if cmds.objExists(controlName):
            cmds.connectAttr(controlName+'.scaleY',crvGlobalScaleNode+'.input1')
        else:
            cmds.setAttr(crvGlobalScaleNode+'.input1', 1)
        ikCrvLength=cmds.getAttr(crvInfoName+'.arcLength')
        cmds.setAttr(crvGlobalScaleNode+'.input2',ikCrvLength)

        ## create curve stretch divide node
        crvStretchNode=cmds.createNode('multiplyDivide', n=crvStretchName)
        cmds.setAttr(crvStretchNode+'.operation', 2) # 1=multiply 2=divide
        cmds.connectAttr(crvGlobalScaleNode+'.output', crvStretchNode+'.input2X')
        cmds.connectAttr(crvInfoName+'.arcLength', crvStretchNode+'.input1X')

        ## create stretch mult node for each effected joint
        for sN,lN in effectedJnts:
            jntStretchName=ikName+sN+'Stretch_MULT'
            jntStretchNode=cmds.createNode('multDoubleLinear', n=jntStretchName)
            jointTransX=cmds.getAttr(lN+'.translateX')
            cmds.setAttr(jntStretchNode+'.input1', jointTransX)
            cmds.connectAttr(crvStretchNode+'.outputX', jntStretchNode+'.input2')
            cmds.connectAttr(jntStretchNode+'.output', lN+'.translateX')

        ## turn off inherit transforms
        cmds.setAttr(grpName+'.inheritsTransform',0)


def createSettingCtrl(ctrlCrv, settingLoc, parJnt,side):
    attrName = 'IKFKSwitch'
    attrNiceName = 'IK / FK Switch'
    if side == 'L' or 'L_' in side or '_L' in side:
        col=27
        rot=[-15,30,0]
    else:
        col=32
        rot=[-15,-30,0]
    if cmds.objExists(ctrlCrv+'Ctrl_ROOT'):
        cmds.delete(ctrlCrv+'Ctrl_ROOT')
    createCtrlShape(ctrlCrv,2,col=col,scale=[0.12,0.12,0.12],rotOffset=rot)
    createBuffer(ctrlCrv,1,1,settingLoc)
    if not cmds.attributeQuery(attrName, node=ctrlCrv+'_CTRL', exists=True):
        cmds.addAttr(ctrlCrv+'_CTRL', ln=attrName, nn=attrNiceName, min=0, max=1, at='float', dv=0, k=True)

    cmds.parentConstraint(parJnt,ctrlCrv+'Ctrl_ROOT',mo=True)


def createCtrlShape(n,s,scale=[1,1,1],col=1,rotOffset=[0,0,0],transOffset=[0,0,0],side=None,skipFreeze=False):
    if not n:
        n='curve'
    ctrlName = n+"_CTRL"

    for i in range(len(transOffset)):
        transOffset[i]=-transOffset[i]

    curveNum=eval('crv'+str(s))
    crvs=curveNum.create(n,'_CTRL')
    combineCrv(crvs,col)
    mirScale=1
    if not side is None and not side == 'L':
        # rotOffset[1]=-rotOffset[1]
        # rotOffset[2]=-rotOffset[2]
        mirScale=-1
    cmds.xform(ctrlName,scale=scale,ro=rotOffset,piv=transOffset)
    if not skipFreeze:
        cmds.makeIdentity(ctrlName,a=True,s=True,r=True)
        cmds.xform(ctrlName, scale=[mirScale,1,1])
        cmds.makeIdentity(ctrlName,a=True,s=True,r=True)


def createSpSwConstraint(parents, target, enumNames, niceNames=['Space'],constrType='parent',constrTarget=''):
    """Creates a constraint and adds an attribute on the target to switch between the parents.

    Args:
    [string list] parents - of parent objects (limit to two... for now)
    [string] targets - constraint target
    [string] enumName - names of the attribute's enum options (e.g. 'option1:option2')
    [string list] niceName - nice names of the parents
    [string] constrType - type of constraint (parent, orient, aim, point, scale)
    """
    if constrTarget == '':
        if target.endswith('_CTRL'):
            stripName=target.rpartition('_')
            constrTarget=stripName[0]+'Ctrl_ROOT'
        else:
            constrTarget=target

    if niceNames <= 1:
        niceName=niceNames
    else:
        niceName=''
        for i,x in enumerate(niceNames):
            if i < len(niceNames)-1:
                niceName=niceName+x+' / '
            else:
                niceName=niceName+x

    existingAttr=cmds.listAttr(target)
    constr=eval('cmds.'+constrType+'Constraint(parents,constrTarget,mo=True)')
    if 'spSwSep' not in existingAttr:
        cmds.addAttr(target, ln='spSwSep', nn='___   Space Switching', at='enum', en='___', k=True)
    cmds.addAttr(target, ln='spaceSwitch', nn=niceName+' Switch', at='enum', en=enumNames, k=True)
    for i,x in enumerate(parents):
        if not i == 1:
            rev=cmds.createNode('reverse', n=target+'spaceSwitch_REV')
            cmds.connectAttr(target+'.spaceSwitch',rev+'.inputX')
            cmds.connectAttr(rev+'.outputX', constr[0]+'.'+x+'W'+str(i))
        else:
            cmds.connectAttr(target+'.spaceSwitch', constr[0]+'.'+x+'W'+str(i))


def combineCrv(crvs,col):
    for i,x in enumerate(crvs):
        shape=cmds.listRelatives(x,s=True)
        if col:
            cmds.setAttr(x+'.overrideEnabled',True)
            cmds.setAttr(x+'.overrideColor',col-1)
        if not i > 0:
            parent=x
        else:
            cmds.parent(shape,parent,s=True,r=True)
            cmds.delete(x)


def createBuffer(n,loc,grp,obj,*args):
    if not n:
        n='curve'

    rootCtrlName = str(n)+"Ctrl_ROOT"
    ctrlParentName = str(n)+"Ctrl_PAR"
    spareCtrlParentName = str(n)+"CtrlPar#_PAR"
    ctrlName = str(n)+"_CTRL"
    constGrpName = str(n)+"Const_GRP"

    sel = cmds.ls(sl=True)

    buffers = []
    prevBuff=None
    if grp == 0 and loc == 0:
        cmds.parentConstraint(obj,ctrlName,mo=False)
        cmds.delete(ctrlName+'_parentConstraint1')
        cmds.makeIdentity(ctrlName,a=True,t=True,s=True,r=True)
    else:
        for y in range(grp+loc):
            if y == 0:
                buffName = rootCtrlName
            elif y ==1:
                buffName = ctrlParentName
            else:
                buffName = spareCtrlParentName
            buffName = swapDigits(buffName,y-2)
            if y < grp:
                cmds.group(em=True,n=buffName)
            else:
                cmds.spaceLocator(n=buffName)
                cmds.setAttr(buffName+'Shape'+'.overrideEnabled', True)
                cmds.setAttr(buffName+'Shape'+'.overrideVisibility', 0)
                locPath=zip(cmds.ls(buffName,l=True),buffName)


            cmds.parentConstraint(obj,buffName,mo=False)
            cmds.delete(buffName+'_parentConstraint1')
            if y == 0:
                cmds.makeIdentity(buffName,a=True,t=True,s=True,r=True)
            else:
                cmds.makeIdentity(buffName,a=True,t=True,s=True)
            buffers.append(buffName)

        for y in range(len(buffers)):
            if y > 0:
                cmds.parent(buffers[y],buffers[y-1])

        cmds.parentConstraint(buffers[-1],ctrlName,mo=False)
        cmds.delete(ctrlName+'_parentConstraint1')
        cmds.parent(ctrlName,buffers[-1])
        cmds.makeIdentity(ctrlName,a=True,t=True,s=True,r=True)

        constGrpPar = ctrlName

        cmds.group(em=True,n=constGrpName)
        cmds.parentConstraint(constGrpPar,constGrpName,mo=False)
        cmds.delete(constGrpName+'_parentConstraint1')
        cmds.parent(constGrpName,constGrpPar)
        cmds.makeIdentity(a=True,t=True,s=True,r=True)


def swapDigits(n,i=0,*args):
    minDigitLength=0
    bufferChar=''
    findHashes = re.findall("(#+)", n)
    newN=n
    if findHashes:
        minDigitLength=len(findHashes[0])
        bufferChar=findHashes[0]
        newN=str(i+1).zfill(minDigitLength).join(n.split(bufferChar))
        while cmds.objExists(newN):
            i=i+1
            newN=str(i+1).zfill(minDigitLength).join(n.split(bufferChar))
    return newN


def getParents(joint,*args):
    parents=[]
    sNParents=[]
    curPar=joint
    for i in range(500):
        curPar=cmds.listRelatives(curPar,typ='joint',f=True, p=True)
        if not curPar:
            break
        sN=curPar[0].split('|')
        sNParents.append(sN[-1])
        parents.append(curPar[0])
    parents=zip(sNParents,parents)
    return parents


def getCrv(inCrv):
    crvShapeNodes=cmds.listRelatives(inCrv, c=True)
    for pathCurve in crvShapeNodes:
        cmds.select(pathCurve+'.cv[*]')
        pathCvs=cmds.ls(sl=True,fl=True)

        knotNum=0
        cvPoints=[]
        knots=[]

        for cv in pathCvs:
            coords=cmds.xform(cv,q=True,t=True)
            coords=(coords[0],coords[1],coords[2])
            cvPoints.append(coords)

        3
        noOfPoints=len(cvPoints)
        noOfKnots=noOfPoints + 2
        noOfSpans=noOfPoints - 3

        knotValue=1
        for x in range(noOfKnots):
            knots.append(None)
            if x < 3:
                knots[x]=0
            else:
                knots[x]=knotValue
                knotValue=knotValue+1

            if x >= (noOfKnots-3):
                knots[x]=noOfSpans


    return knots,cvPoints


# ====================================================================================================================
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
# ====================================================================================================================


def doOrientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp):
    firstPass = 0
    prevUpVector = [0,0,0]
    for eachJoint in jointsToOrient:
        childJoint = cmds.listRelatives(eachJoint, type="joint", c=True)
        if childJoint != None:
            if len(childJoint) > 0:

                childNewName = cmds.parent(childJoint, w=True)  #Store the name in case when unparented it changes it's name.

                if guessUp == 0:
                    #Not guess Up direction

                    cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=worldUp, worldUpType="vector"))
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
                                tolerance = 0.0001

                                if (abs(posCurrentJoint[0] - posParentJoint[0]) <= tolerance and abs(posCurrentJoint[1] - posParentJoint[1]) <= tolerance and abs(posCurrentJoint[2] - posParentJoint[2]) <= tolerance):
                                    aimChild = cmds.listRelatives(childNewName[0], type="joint", c=True)
                                    upDirRecalculated = crossProduct(eachJoint, childNewName[0], aimChild[0])
                                    cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))
                                else:
                                    upDirRecalculated = crossProduct(parentJoint, eachJoint, childNewName[0])
                                    cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))
                            else:
                                aimChild = cmds.listRelatives(childNewName[0], type="joint", c=True)
                                upDirRecalculated = crossProduct(eachJoint, childNewName[0], aimChild[0])
                        else:
                            aimChild = cmds.listRelatives(childNewName[0], type="joint", c=True)
                            upDirRecalculated = crossProduct(eachJoint, childNewName[0], aimChild[0])
                            cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))





                    dotProduct = upDirRecalculated[0] * prevUpVector[0] + upDirRecalculated[1] * prevUpVector[1] + upDirRecalculated[2] * prevUpVector[2]

                    #For the next iteration
                    prevUpVector = upDirRecalculated

                    if firstPass > 0 and  dotProduct <= 0.0:
                        #dotProduct
                        cmds.xform(eachJoint, r=1, os=1, ra=(aimAxis[0] * 180.0, aimAxis[1] * 180.0, aimAxis[2] * 180.0))
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
                            cmds.delete(cmds.orientConstraint(parentJoint[0], eachJoint, w=1, o=(0,0,0)))
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


##

def bipedLocs():
    spineCrv,headLocs=createSpineLocs('biped')
    LlegLocs=createLegLocs('biped', 'L')
    LtoeLocs=createToeLocs('biped', 'L')
    LarmLocs=createArmLocs('biped', 'L')
    LfingerLocs=createFingerLocs('biped', 'L')


def bipedMirror():
    RlegLocs=createLegLocs('biped','L', True, 'R')
    RtoeLocs=createToeLocs('biped', 'L', True, 'R')
    RarmLocs=createArmLocs('biped', 'L', True, 'R')
    RfingerLocs=createFingerLocs('biped', 'L', True, 'R')


def bipedSkel():
    createGlobalCtrl('biped')

    spineCrv,headLocs=createSpineLocs('biped')
    LlegLocs=createLegLocs('biped','L')
    LtoeLocs=createToeLocs('biped', 'L')
    LarmLocs=createArmLocs('biped', 'L')
    LfingerLocs=createFingerLocs('biped', 'L')

    RlegLocs=createLegLocs('biped','R')
    RtoeLocs=createToeLocs('biped', 'R')
    RarmLocs=createArmLocs('biped', 'R')
    RfingerLocs=createFingerLocs('biped', 'R')

    ## with spine
    spineArmJnt=createSpineSkelMech('biped',10,spineCrv,headLocs)
    createLegSkelMech(LlegLocs,'biped','L','biped_spine_base_JNT')
    createArmSkelMech(LarmLocs,'biped', 'L','biped_spine_'+spineArmJnt+'_JNT')
    createFingerSkelMech(LfingerLocs, 'biped', 'L', 'biped_L_wrist_result_JNT')
    createToeSkelMech(LtoeLocs, 'biped', 'L', 'biped_L_footBall_result_JNT')
    createLegSkelMech(RlegLocs,'biped','R','biped_spine_base_JNT')
    createArmSkelMech(RarmLocs,'biped', 'R','biped_spine_'+spineArmJnt+'_JNT')
    createFingerSkelMech(RfingerLocs, 'biped', 'R', 'biped_R_wrist_result_JNT')
    createToeSkelMech(RtoeLocs, 'biped', 'R', 'biped_R_footBall_result_JNT')

    ## no spine (aka seperated limbs)
    # createLegSkelMech(LlegLocs,'biped','L')
    # createArmSkelMech(LarmLocs,'biped', 'L')
    # createLegSkelMech(RlegLocs,'biped','R')
    # createArmSkelMech(RarmLocs,'biped', 'R')

