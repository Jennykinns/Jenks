import maya.cmds as cmds
import maya.OpenMaya as om
from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import apiFuncitons as api
from Jenks.scripts.rigModules import fileFunctions as file

reload(utils)
reload(file)

def getShapeData(ctrlName):
    curveShapes = utils.getShapeNodes(ctrlName)
    crvData = {}
    for i, each in enumerate(curveShapes):
        crvData[i] = {}
        crvData[i]['CVs'] = []
        crvData[i]['knots'] = []

        nurbsCrv = api.getNurbsCurve(each)
        cvArray = om.MPointArray()
        knotArray = om.MDoubleArray()

        nurbsCrv.getCVs(cvArray, om.MSpace.kObject)
        nurbsCrv.getKnots(knotArray)

        for cvNum in range(cvArray.length()):
            cv = {'x' : cvArray[cvNum].x,
                  'y' : cvArray[cvNum].y,
                  'z' : cvArray[cvNum].z}
            crvData[i]['CVs'].append(cv)
        crvData[i]['knots'].extend(knotArray)
        crvData[i]['degree'] = nurbsCrv.degree()
        crvData[i]['form'] = nurbsCrv.form()

    return crvData


def applyShapeData(ctrlName, crvData):
    curveShapes = utils.getShapeNodes(ctrlName)
    ctrlMObj = api.getMObj(ctrlName)
    if curveShapes:
        for each in curveShapes:
            cmds.delete(each)
    for crvShape in crvData.keys():
        nurbsCrv = om.MFnNurbsCurve()
        cvArray = om.MPointArray()
        for x in crvData[crvShape]['CVs']:
            cvArray.append(x['x'], x['y'], x['z'])
        knotArray = om.MDoubleArray()
        for x in crvData[crvShape]['knots']:
            knotArray.append(x)
        degree = crvData[crvShape]['degree']
        form = crvData[crvShape]['form']
        nurbsCrv.create(cvArray, knotArray, degree, form, 0, 1, ctrlMObj)

    shapes = utils.getShapeNodes(ctrlName)
    for i, each in enumerate(shapes):
        cmds.rename(each, '{}Shape{}'.format(ctrlName, i+1))


def saveShapeData(ctrlName):
    crvData = getShapeData(ctrlName)
    status = file.saveJson(crvData,
                           defaultDir='/home/Jenks/maya/scripts/Jenks/scripts/controlShapes',
                           caption='Save Control Shape',
                           fileFormats=[('SHAPE', '*.shape')])
    return status

def loadShapeData(ctrlName, shape=False, path=None):
    fo = ['{}/{}.shape'.format(path, shape)] if shape and path else False
    crvData = file.loadJson(defaultDir='/home/Jenks/maya/scripts/Jenks/scripts/controlShapes',
                            caption='Save Control Shape',
                            fileFormats=[('SHAPE', '*.shape')],
                            fileOverride=fo)
    if crvData:
        applyShapeData(ctrlName, crvData)
        return True
    else:
        return False

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
            self.constGrp = utils.newNode('group', name=name,suffixOverride='controlConst',
                                          side=side, skipNum=skipNum, parent=self.ctrl.name)
            self.ctrlRoot = self.rootGrp.name
            self.ctrlEnd = self.constGrp.name
        else:
            self.ctrlRoot = self.ctrl
            self.ctrlEnd = self.ctrl
        if deleteGuide:
            cmds.delete(guide)
        if parent:
            cmds.parent(self.ctrlRoot, parent)

    def createCtrlOffsetGrps(self, num, name, guide=None, skipNum=False):
        self.rootGrp = utils.newNode('group', name=name, suffixOverride='controlRootGrp',
                                      side=self.side, skipNum=skipNum)
        if guide:
            utils.matchTransforms([self.rootGrp.name], guide)
        self.offsetGrps = []
        par = self.rootGrp.name
        for i in range(num):
            self.offsetGrps.append(utils.newNode('group', name=name,
                                                 suffixOverride='controlOffset', side=self.side,
                                                 skipNum=skipNum))
            self.offsetGrps[-1].parent(par, relative=True)
            par = self.offsetGrps[-1]

    def modifyShape(self, shape=None, color=None, rotation=(0, 0, 0), translation=(0, 0, 0)):
        if shape:
            path='/home/Jenks/maya/scripts/Jenks/scripts/controlShapes'
            loadShapeData(self.ctrl.name, shape, path)
        if color:
            utils.setShapeColor(self.ctrl.name, color=color)

    def constrain(self, target, typ='parent', mo=True, offset=[0, 0, 0],
                  aimVector=[1, 0, 0], aimUp=[0, 1, 0], aimWorldUpType=2, aimWorldUp=[0, 1, 0],
                  aimWorldUpObject='C_global_CTRL'):
        if typ == 'parent':
            cmds.parentConstraint(self.constGrp.name, target, mo=mo)
        elif typ == 'point':
            if mo:
                cmds.pointConstraint(self.constGrp.name, target, mo=mo)
            else:
                cmds.pointConstraint(self.constGrp.name, target, o=offset)
        elif typ == 'orient':
            if mo:
                cmds.orientConstraint(self.constGrp.name, target, mo=mo)
            else:
                cmds.orientConstraint(self.constGrp.name, target, o=offset)
        elif typ == 'aim':
            if mo:
                cmds.aimConstraint(self.constGrp.name, target, mo=mo, aim=aimVector, u=aimUp,
                                   wut=aimWorldUpType, wuo=aimWorldUpObject, wu=aimWorldUp)
            else:
                cmds.aimConstraint(self.constGrp.name, target, o=offset, aim=aimVector,
                                   u=aimUp, wut=aimWorldUpType, wuo=aimWorldUpObject,
                                   wu=aimWorldUp)
        elif typ == 'poleVector' or typ == 'pv':
            cmds.poleVectorConstraint(self.constGrp.name, target)
        else:
            cmds.warning('Parent Type Unsupported. Use: parent, point, orient, aim or poleVector.')
