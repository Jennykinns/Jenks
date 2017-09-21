import maya.cmds as cmds
import maya.api.OpenMaya as om

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import apiFuncitons as api
from Jenks.scripts.rigModules import fileFunctions as fileFn

reload(utils)

def getAllControls():
    ctrls = cmds.ls('*_CTRL')
    return ctrls

def getShapeData(ctrlName, color=False):
    curveShapes = utils.getShapeNodes(ctrlName)
    crvData = {}
    for i, each in enumerate(curveShapes):
        crvData[i] = {}
        crvData[i]['CVs'] = []
        crvData[i]['knots'] = []

        nurbsCrv = api.getNurbsCurve(each)
        cvArray = om.MPointArray()
        knotArray = om.MDoubleArray()

        #nurbsCrv.getCVs(cvArray, om.MSpace.kObject)
        cvArray = nurbsCrv.cvPositions(om.MSpace.kObject)
        #nurbsCrv.getKnots(knotArray)
        knotArray = nurbsCrv.knots()

        #for cvNum in range(cvArray.length()):
        for cvNum in range(len(cvArray)):
            cv = {'x' : cvArray[cvNum].x,
                  'y' : cvArray[cvNum].y,
                  'z' : cvArray[cvNum].z}
            crvData[i]['CVs'].append(cv)
        crvData[i]['knots'].extend(knotArray)
        crvData[i]['degree'] = nurbsCrv.degree
        crvData[i]['form'] = nurbsCrv.form
        if color:
            crvData[i]['color'] = cmds.getAttr('{}.overrideColor'.format(each))

    return crvData


def applyShapeData(ctrlName, crvData, transOffset=(0, 0, 0),
                   rotOffset=(0, 0, 0), scaleOffset=(1, 1, 1)):
    curveShapes = utils.getShapeNodes(ctrlName)
    ctrlMObj = api.getMObj(ctrlName)
    if curveShapes:
        for each in curveShapes:
            cmds.delete(each)
    for crvShape in crvData.keys():
        nurbsCrv = om.MFnNurbsCurve()
        cvArray = om.MPointArray()
        for i, x in enumerate(crvData[crvShape]['CVs']):
            cvArray.append((x['x'], x['y'], x['z']))
            cvArray[i] = (api.transformMPoint(cvArray[i], rot=rotOffset, trans=transOffset,
                                              scale=scaleOffset))
        knotArray = om.MDoubleArray()
        for x in crvData[crvShape]['knots']:
            knotArray.append(x)
        degree = crvData[crvShape]['degree']
        form = crvData[crvShape]['form']
        nurbsCrv.create(cvArray, knotArray, degree, form, 0, 1, ctrlMObj)
        if 'color' in crvData[crvShape].keys():
            utils.setColor(nurbsCrv.name(), color=crvData[crvShape]['color'])

    shapes = utils.getShapeNodes(ctrlName)
    for i, each in enumerate(shapes):
        cmds.rename(each, '{}Shape{}'.format(ctrlName, i+1))


def saveShapeData(ctrlName):
    crvData = getShapeData(ctrlName)
    status = fileFn.saveJson(crvData,
                           defaultDir='/home/Jenks/maya/scripts/Jenks/scripts/controlShapes',
                           caption='Save Control Shape',
                           fileFormats=[('SHAPE', '*.shape')])
    return status

def loadShapeData(ctrlName, shape=False, path=None):
    fo = '{}/{}.shape'.format(path, shape) if shape and path else False
    defDir = '{}/Jenks/scripts/controlShapes'.format(fileFn.getScriptDir())
    crvData = fileFn.loadJson(defaultDir=defDir,
                              caption='Save Control Shape',
                              fileFormats=[('SHAPE', '*.shape')],
                              fileOverride=fo)
    if crvData:
        applyShapeData(ctrlName, crvData)
        return True
    else:
        return False

def saveCtrls(rigName):
    path = fileFn.getAssetDir()
    for ctrl in getAllControls():
        crvData = getShapeData(ctrl, color=True)
        fo = fileFn.getLatestVersion(rigName, path, 'rig/WIP/controlShapes', new=True, name=ctrl)
        fileFn.saveJson(crvData, fileOverride=fo)

def loadCtrls(rigName):
    path = fileFn.getAssetDir()
    for ctrl in getAllControls():
        fo = fileFn.getLatestVersion(rigName, path, 'rig/WIP/controlShapes', name=ctrl)
        if fo:
            crvData = fileFn.loadJson(fileOverride=fo)
            if crvData:
                applyShapeData(ctrl, crvData)

class ctrl:
    def __init__(self, name='control', gimbal=False, offsetGrpNum=1, guide=None,
                 deleteGuide=False, side='C', skipNum=False, parent=None):
        self.side = side
        self.gimbal = False
        if not guide:
            deleteGuide = True
            guideLoc = utils.newNode('locator', name='controlGuide')
            guide = guideLoc.name

        self.guide = False if deleteGuide else guide
        self.ctrl = utils.newNode('control', name=name, side=self.side, skipNum=skipNum)
        if offsetGrpNum > 0:
            self.createCtrlOffsetGrps(offsetGrpNum, name, guide, skipNum)
            self.ctrl.parent(self.offsetGrps[-1].name, relative=True)
            self.constGrp = utils.newNode('group', name=name, suffixOverride='controlConst',
                                          side=side, skipNum=skipNum)
            utils.setOutlinerColor(self.constGrp.name, color=(0.6, 0.6, 0.58))
            self.constGrp.parent(parent=self.ctrl.name, relative=True)
            self.ctrlRoot = self.rootGrp.name
            self.ctrlEnd = self.constGrp.name
        else:
            self.ctrlRoot = self.ctrl
            self.ctrlEnd = self.ctrl
        if deleteGuide:
            cmds.delete(guide)
        if parent:
            cmds.parent(self.ctrlRoot, parent)
        cmds.select(cl=1)

    def createCtrlOffsetGrps(self, num, name, guide=None, skipNum=False):

        self.rootGrp = utils.newNode('group', name=name, suffixOverride='controlRootGrp',
                                      side=self.side, skipNum=skipNum)
        utils.setOutlinerColor(self.rootGrp.name, color=(0.48, 0.48, 0.44))
        if guide:
            utils.matchTransforms([self.rootGrp.name], guide)
        self.offsetGrps = []
        par = self.rootGrp.name
        for i in range(num):
            self.offsetGrps.append(utils.newNode('group', name=name,
                                                 suffixOverride='controlOffset', side=self.side,
                                                 skipNum=skipNum))
            utils.setOutlinerColor(self.offsetGrps[-1].name, color=(0.6, 0.6, 0.55))
            self.offsetGrps[-1].parent(par, relative=True)
            par = self.offsetGrps[-1]

    def modifyShape(self, shape=None, color=None, rotation=(0, 0, 0),
                    translation=(0, 0, 0), scale=(1, 1, 1)):
        if shape:
            scriptsPath = fileFn.getScriptDir()
            path = '{}/Jenks/scripts/controlShapes'.format(scriptsPath)
            loadShapeData(self.ctrl.name, shape, path)
        crvData = getShapeData(self.ctrl.name)
        applyShapeData(self.ctrl.name, crvData, transOffset=translation, rotOffset=rotation,
                       scaleOffset=scale)
        if color:
            utils.setShapeColor(self.ctrl.name, color=color)
        else:
            print '## get existing colour and apply (for if the shape changes)'

    def constrain(self, target, typ='parent', mo=True, offset=[0, 0, 0],
                  aimVector=[1, 0, 0], aimUp=[0, 1, 0], aimWorldUpType=2, aimWorldUp=[0, 1, 0],
                  aimWorldUpObject='C_global_CTRL', skipRot='none', skipTrans='none',
                  skipScale='none'):
        if typ == 'parent':
            cmds.parentConstraint(self.ctrlEnd, target, mo=mo, sr=skipRot, st=skipTrans)
        elif typ == 'point':
            if mo:
                cmds.pointConstraint(self.ctrlEnd, target, mo=mo, sk=skipTrans)
            else:
                cmds.pointConstraint(self.ctrlEnd, target, o=offset, sk=skipTrans)
        elif typ == 'orient':
            if mo:
                cmds.orientConstraint(self.ctrlEnd, target, mo=mo, sk=skipRot)
            else:
                cmds.orientConstraint(self.ctrlEnd, target, o=offset, sk=skipRot)
        elif typ == 'aim':
            if mo:
                cmds.aimConstraint(self.ctrlEnd, target, mo=mo, aim=aimVector, u=aimUp,
                                   wut=aimWorldUpType, wuo=aimWorldUpObject, wu=aimWorldUp,
                                   sk=skipRot)
            else:
                cmds.aimConstraint(self.ctrlEnd, target, o=offset, aim=aimVector,
                                   u=aimUp, wut=aimWorldUpType, wuo=aimWorldUpObject,
                                   wu=aimWorldUp, sk=skipRot)
        elif typ == 'scale':
            cmds.scaleConstraint(self.ctrlEnd, target, mo=mo, sk=skipScale)
        elif typ == 'poleVector' or typ == 'pv':
            cmds.poleVectorConstraint(self.ctrlEnd, target)
        else:
            cmds.warning('Parent Type Unsupported. Use: parent, point, orient, aim or poleVector.')

    def lockAttr(self, attr='', hide=True, unlock=False):
        utils.lockAttr(self.ctrl.name, attr, hide, unlock)

    def addAttr(self, name, nn, typ='double', defaultVal=0, minVal=None, maxVal=None, enumOptions=None):
        ctrlAttr = cmds.listAttr(self.ctrl.name)
        if not name in ctrlAttr:
            if typ == 'enum':
                enumName = ':'.join(enumOptions)
                cmds.addAttr(self.ctrl.name, sn=name, nn=nn, at=typ,
                             en=enumName, dv=defaultVal, k=1)
            else:
                if minVal is not None and maxVal is not None:
                    cmds.addAttr(self.ctrl.name, sn=name, nn=nn, at=typ,
                                 dv=defaultVal, min=minVal, max=maxVal, k=1)
                elif minVal is not None:
                    cmds.addAttr(self.ctrl.name, sn=name, nn=nn, at=typ,
                                 dv=defaultVal, min=minVal, k=1)
                elif maxVal is not None:
                    cmds.addAttr(self.ctrl.name, sn=name, nn=nn, at=typ,
                                 dv=defaultVal, max=maxVal, k=1)
                else:
                    cmds.addAttr(self.ctrl.name, sn=name, nn=nn, at=typ,
                                 dv=defaultVal, k=1)
            exec('self.ctrl.{0} = "{1}.{0}"'.format(name, self.ctrl.name))
        else:
            cmds.warning('{} already exists on {}.'.format(name, self.ctrl.name))

    def spaceSwitching(self, parents, niceNames=None, constraint='parent', dv=0):
        target = self.offsetGrps[0].name
        if not niceNames:
            niceNames=[]
            for each in parents:
                splitParent = each.partition('_')[-1].rpartition('_')[0]
                if splitParent == 'globalConst':
                    splitParent = 'World'
                niceNames.append(splitParent.capitalize())

        if niceNames <= 1:
            attrNiceName = niceNames[0]
        else:
            attrNiceName = ''
            for i, each in enumerate(niceNames):
                if i < len(niceNames)-1:
                    attrNiceName += '{} / '.format(each)
                else:
                    attrNiceName += '{}'.format(each)

        # add seperator
        self.addAttr('spSwSep', '___   Space Switching', typ='enum', enumOptions=['___'])
        # add attribute
        spSwAttr = self.addAttr('spaceSwitch', '{} Switch'.format(attrNiceName), typ='enum',
                                defaultVal=dv, enumOptions=niceNames)
        # constraint
        exec('constr = cmds.{}Constraint(parents, target, mo=1)[0]'.format(constraint))
        # connect attrs
        for i, each in enumerate(parents):
            # create condition node
            condNd = utils.newNode('condition', name='{}SpSwitch'.format(each), side=self.side, operation=0)
            # set cond vals
            cmds.setAttr('{}.secondTerm'.format(condNd.name), i)
            cmds.setAttr('{}.colorIfTrueR'.format(condNd.name), 1)
            cmds.setAttr('{}.colorIfFalseR'.format(condNd.name), 0)
            # connect
            condNd.connect('firstTerm', self.ctrl.spaceSwitch, mode='to')
            condNd.connect('outColorR', '{}.{}W{}'.format(constr, each, i) , mode='from')


    def makeSettingCtrl(self, ikfk=True, parent=''):
        self.modifyShape(shape='cog', color=utils.getColors(self.side)['settingCol'],
                         scale=(0.2, 0.2, 0.2))
        if parent:
            cmds.parentConstraint(parent, self.rootGrp.name, mo=1)
        self.lockAttr()
        if ikfk:
            self.addAttr('ikfkSwitch', nn='IK / FK Switch', minVal=0, maxVal=1)

