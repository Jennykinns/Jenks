import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ikFunctions as ikFn
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules import mechFunctions as mechFn
from Jenks.scripts.rigModules.suffixDictionary import suffix
from Jenks.scripts.rigModules import defaultBodyOptions
from Jenks.scripts.rigModules import orientJoints

reload(orientJoints)
reload(utils)
reload(ikFn)
reload(ctrlFn)
reload(mechFn)
reload(defaultBodyOptions)


class face:
    def __init__(self, rig, extraName='', side='C'):
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def basicFace(self, jntPar=None, ctrlPar=None):
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        faceCtrlsGrp = utils.newNode('group', name='{}faceCtrls'.format(extraName), side=self.side,
                                    skipNum=True, parent=self.rig.ctrlsGrp.name)
        if ctrlPar:
            cmds.parentConstraint(ctrlPar, faceCtrlsGrp.name, mo=1)
        ## jaw
        jawJnt = 'C_{}jawLower{}'.format(extraName, suffix['joint'])
        utils.addJntToSkinJnt(jawJnt, self.rig)
        utils.addJntToSkinJnt('C_{}jawUpper{}'.format(extraName, suffix['joint']), self.rig)
        jawCtrl = ctrlFn.ctrl(name='{}lowerJaw'.format(extraName), side='C',
                              guide=jawJnt,
                              rig=self.rig, parent=faceCtrlsGrp.name,
                              scaleOffset=self.rig.scaleOffset)
        jawCtrl.constrain(jawJnt)
        if jntPar:
            cmds.parent(jawJnt, jntPar)
            cmds.parent('C_{}jawUpper{}'.format(extraName, suffix['joint']), jntPar)
        ## eyes
        for s in 'LR':
            eyeJnt = '{}_{}eye{}'.format(s, extraName, suffix['joint'])
            utils.addJntToSkinJnt(eyeJnt, self.rig)
            eyeCtrl = ctrlFn.ctrl(name='{}eye'.format(extraName), side=s,
                                  guide=eyeJnt,
                                  rig=self.rig, parent=faceCtrlsGrp.name,
                                  scaleOffset=self.rig.scaleOffset)
            eyeCtrl.constrain(eyeJnt)
            eyeCtrl.modifyShape(shape='sphere', scale=(0.1, 0.1, 0.1))
            if jntPar:
                cmds.parent(eyeJnt, jntPar)
            ## do aim controls
            ## eyelids
            upperEyelidJnt = '{}_{}eyelidUpper{}'.format(s, extraName, suffix['joint'])
            if jntPar:
                cmds.parent(upperEyelidJnt, jntPar)
            utils.addJntToSkinJnt(upperEyelidJnt, self.rig)
            upperEyelidCtrl = ctrlFn.ctrl(name='{}eyelidUpper'.format(extraName), side=s,
                                     guide=upperEyelidJnt,
                                     rig=self.rig, parent=faceCtrlsGrp.name,
                                     scaleOffset=self.rig.scaleOffset)
            upperEyelidCtrl.constrain(upperEyelidJnt)
            upperEyelidCtrl.constrain(upperEyelidJnt, typ='scale')
            upperEyelidCtrl.modifyShape(shape='arc', scale=(0.1, 0.1, 0.1), rotation=(0, 0, 90),
                                        mirror=True)

            lowerEyelidJnt = '{}_{}eyelidLower{}'.format(s, extraName, suffix['joint'])
            if jntPar:
                cmds.parent(lowerEyelidJnt, jntPar)
            utils.addJntToSkinJnt(lowerEyelidJnt, self.rig)
            lowerEyelidCtrl = ctrlFn.ctrl(name='{}eyelidLower'.format(extraName), side=s,
                                     guide=lowerEyelidJnt,
                                     rig=self.rig, parent=faceCtrlsGrp.name,
                                     scaleOffset=self.rig.scaleOffset)
            lowerEyelidCtrl.constrain(lowerEyelidJnt)
            lowerEyelidCtrl.constrain(lowerEyelidJnt, typ='scale')
            lowerEyelidCtrl.modifyShape(shape='arc', scale=(0.1, 0.1, 0.1), rotation=(0, 0, 90),
                                        mirror=True)

        ## tongue


        ## lips
        ## cheeks
        ## eyebrows
        ## nose
        jntList = [
            ('lipLower', 'C'),
            ('lipUpper', 'C'),
            ('mouthCorner', 'L'),
            ('mouthCorner', 'R'),
            ('noseCorner', 'L'),
            ('noseCorner', 'R'),
            ('eyebrowInner', 'L'),
            ('eyebrowMid', 'L'),
            ('eyebrowOuter', 'L'),
            ('eyebrowInner', 'R'),
            ('eyebrowMid', 'R'),
            ('eyebrowOuter', 'R'),
            ('cheek', 'L'),
            ('cheek', 'R'),
        ]
        for x in jntList:
            name = x[0]
            side = x[1]
            ## create control
            jnt = '{}_{}{}{}'.format(side, extraName, name, suffix['joint'])
            utils.addJntToSkinJnt(jnt, self.rig)
            if jntPar:
                cmds.parent(jnt, jntPar)
            childsOfJaw = ['lipLower', 'mouthCorner']
            if name in childsOfJaw:
                par = jawCtrl.ctrlEnd
            else:
                par = faceCtrlsGrp.name
            ctrl = ctrlFn.ctrl(name='{}{}'.format(extraName, name), guide=jnt, rig=self.rig,
                               side=side, parent=par,
                               scaleOffset=self.rig.scaleOffset)
            if name == 'mouthCorner':
                constr = cmds.parentConstraint(jawCtrl.ctrlEnd, faceCtrlsGrp.name,
                                               ctrl.offsetGrps[0].name, mo=1)[0]
                cmds.setAttr('{}.interpType'.format(constr), 2)
            ctrl.modifyShape(shape='pin', scale=(0.2, 0.2, 0.2), rotation=(-90, 0, 0), mirror=True)
            ## constrain
            ctrl.constrain(jnt)
            ctrl.constrain(jnt, typ='scale')
        cmds.delete('{}_{}faceJnts{}'.format(self.side, extraName, suffix['group']))

