import maya.cmds as cmds
import maya.api.OpenMaya as om

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import apiFunctions as api
from Jenks.scripts.rigModules import fileFunctions as fileFn
from Jenks.scripts.rigModules.suffixDictionary import suffix

reload(utils)
reload(fileFn)

def getAllControls(rigNode):
    """ Returns a list of controls that are part of the rig.
    [Args]:
    rigNode (string) - The name of the rig node
    [Returns]:
    ctrls (list) - A list of the control names
    """
    ctrls = cmds.listConnections('{}.rigCtrls'.format(rigNode), d=1, s=0)
    return ctrls

def selectRigControls():
    """ Selects the controls that are part of the currently selected
        rig.
    """
    sel = cmds.ls(sl=1)
    rigNodes = []
    for each in sel:
        if each.endswith('global_CTRL'):
            rigNodes.append(each)
        elif 'rigConnection' in cmds.listAttr(each):
            rigNodes.append(cmds.listConnections('{}.rigConnection'.format(each), d=0, s=1)[0])
    ctrls = []
    for rigNode in rigNodes:
        ctrls.extend(getAllControls(rigNode))
    cmds.select(ctrls)

def resetCtrlToBind(ctrl):
    """ Resets the control to bind position.
    [Args]:
    ctrl (string) - The name of the control to reset
    """
    attr = cmds.listAttr(ctrl, keyable=True)
    for each in attr:
        dv = cmds.attributeQuery(each, n=ctrl, ld=1)
        cmds.setAttr('{}.{}'.format(ctrl, each), dv[0])

def resetRigControlsToBind(selectedOnly=False):
    """ Resets controls of the rig to bind position.
    [Args]:
    selectedOnly (bool) - Toggles if the function will only effect the
                          selected controls or all the rig controls
    """
    if not selectedOnly:
        selectRigControls()
    sel = cmds.ls(sl=1)
    for each in sel:
        resetCtrlToBind(each)

def getShapeData(ctrlName, color=False):
    """ Gets the shape data of the control.
    [Args]:
    ctrlName (string) - The name of the control
    color (bool) - Toggles if the function will store the colour
                   information
    [Returns]:
    crvData (string) - The point data of the control shape
    """
    curveShapes = utils.getShapeNodes(ctrlName)
    crvData = {}
    for i, each in enumerate(curveShapes):
        crvData[i] = {}
        crvData[i]['CVs'] = []
        crvData[i]['knots'] = []

        nurbsCrv = api.getNurbsCurve(each)
        cvArray = om.MPointArray()
        knotArray = om.MDoubleArray()
        cvArray = nurbsCrv.cvPositions(om.MSpace.kObject)
        knotArray = nurbsCrv.knots()

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
    """ Applies the supplied curve data to the specified control.
    [Args]:
    ctrlName (string) - The name of the control to change
    crvData (string) - The point data to apply
    transOffset (int, int, int) - The translation offset to apply
                                  to the new crv data
    rotOffset (int, int, int) - The rotation offset to apply
                                to the new crv data
    scaleOffset (int, int, int) - The scale offset to apply
                                  to the new crv data
    """
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
    """ Saves control shape data to json file.
    [Args]:
    ctrlName (string) - The name of the control
    [Returns]:
    status (bool) - success
    """
    crvData = getShapeData(ctrlName)
    status = fileFn.saveJson(crvData,
                           defaultDir='/home/Jenks/maya/scripts/Jenks/scripts/controlShapes',
                           caption='Save Control Shape',
                           fileFormats=[('SHAPE', '*.shape')])
    return status

def loadShapeData(ctrlName, shape=False, path=None):
    """ Loads the shape data from a json file.
    [Args]:
    ctrlName (string) - The name of the control to apply the
                        shape data to
    shape (string) - The name of the json file
    path (string) - The path to the shape data directory
    [Returns]:
    (bool) - success
    """
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

def saveCtrls(assetName=None, prompt=False, selectedOnly=False):
    """ Saves the rig controls to the asset control shapes directory.
    [Args]:
    assetName (string) - The name of the asset
    prompt (bool) - Toggles a window prompt for asset name
    selectedOnly (bool) - Toggles saving of all the rig controls
                          or just the selected
    """
    if prompt:
        assetName = fileFn.assetNamePrompt()
    if not assetName:
        assetName = fileFn.getAssetName()
    if not assetName:
        assetName = fileFn.assetNamePrompt()
    if not assetName:
        print 'Asset Name not specified.'
        return False
    path = fileFn.getAssetDir()
    if not selectedOnly:
        ctrlsToSave = getAllControls()
    else:
        ctrlsToSave = cmds.ls(sl=1)
    for ctrl in ctrlsToSave:
        crvData = getShapeData(ctrl, color=True)
        fo = fileFn.getLatestVersion(assetName, path, 'rig/WIP/controlShapes', new=True, name=ctrl)
        fileFn.saveJson(crvData, fileOverride=fo)

def loadCtrls(assetName=None, prompt=False):
    """ Loads all the saved rig control shapes.
    [Args]:
    assetName (string) - The name of the asset
    prompt (bool) - Toggles a window prompt for asset name
    """
    if prompt:
        assetName = fileFn.assetNamePrompt()
    if not assetName:
        assetName = fileFn.getAssetName()
    if not assetName:
        assetName = fileFn.assetNamePrompt()
    if not assetName:
        print 'Asset Name not specified.'
        return False
    path = fileFn.getAssetDir()
    allCtrls = getAllControls('C_global_CTRL')
    allCtrls.append('C_global_CTRL')
    for ctrl in allCtrls:
        fo = fileFn.getLatestVersion(assetName, path, 'rig/WIP/controlShapes', name=ctrl)
        if fo:
            crvData = fileFn.loadJson(fileOverride=fo)
            if crvData:
                applyShapeData(ctrl, crvData)

class ctrl:

    """ Create and manipulate a control. """

    def __init__(self, name='control', gimbal=False, offsetGrpNum=1, guide=None, rig=None,
                 deleteGuide=False, side='C', skipNum=False, parent=None, scaleOffset=1.0,
                 constrainGuide=False):
        """ Create the control, offset groups, root group and const group.
        [Args]:
        name (string) - The name of the control
        gimbal (bool) - Toggles creating a gimbal control
        offsetGrpNum (int) - The amount of offset groups to create
        guide (string) - The guide to match transforms to
        rig (class) - The rig class to link the control to
        deleteGuide (bool) - Toggles deleting the guide
        side (string) - The side of the control
        skipNum (bool) - Toggles skipping the number in the control name
                         if possible
        parent (string) - The parent of the control
        scaleOffset (float) - The scale offset of the control shape
        """
        self.side = side
        self.gimbal = gimbal
        self.scaleOffset = scaleOffset
        if not guide:
            deleteGuide = True
            guideLoc = utils.newNode('locator', name='controlGuide')
            guide = guideLoc.name

        self.guide = False if deleteGuide else guide
        self.ctrl = utils.newNode('control', name=name, side=self.side, skipNum=skipNum)
        if self.gimbal:
            self.gimbalCtrl = utils.newNode('gimbalCtrl', name=name, side=self.side,
                                            skipNum=skipNum, parent=self.ctrl.name)
            scriptsPath = fileFn.getScriptDir()
            path = '{}/Jenks/scripts/controlShapes'.format(scriptsPath)
            loadShapeData(self.gimbalCtrl.name, 'sphere', path)
            self.gimbalCtrl.lockAttr(['t', 's'])
            self.ctrl.addAttr(name='gimbal', nn='Gimbal Visibility', typ='enum',
                enumOptions=['Hide', 'Show'])
            for each in cmds.listRelatives(self.gimbalCtrl.name, s=1):
                self.ctrl.connect('gimbal', '{}.v'.format(each), 'from')
            constGrpPar = self.gimbalCtrl.name
        else:
            constGrpPar = self.ctrl.name
        if offsetGrpNum > 0:
            self.createCtrlOffsetGrps(offsetGrpNum, name, guide, skipNum)
            self.ctrl.parent(self.offsetGrps[-1].name, relative=True)
            self.constGrp = utils.newNode('group', name=name, suffixOverride='controlConst',
                                          side=side, skipNum=skipNum)
            utils.setOutlinerColor(self.constGrp.name, color=(0.6, 0.6, 0.58))
            self.constGrp.parent(parent=constGrpPar, relative=True)
            self.ctrlRoot = self.rootGrp.name
            self.ctrlEnd = self.constGrp.name
        else:
            self.ctrlRoot = self.ctrl
            self.ctrlEnd = self.ctrl
        if deleteGuide:
            cmds.delete(guide)
        if parent:
            cmds.parent(self.ctrlRoot, parent)
        self.ctrl.rigConnection = utils.addAttr(self.ctrl.name, name='rigConnection',
                                                nn='Rig Connection', typ='message')

        if constrainGuide and guide:
            self.constrain(guide, typ=constrainGuide)
            if rig:
                utils.addJntToSkinJnt(guide, rig)

        if rig:
            cmds.connectAttr(rig.ctrlsAttr, self.ctrl.rigConnection)
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
            par = self.offsetGrps[-1].name

    def modifyShape(self, shape=None, color=False, rotation=(0, 0, 0),
                    translation=(0, 0, 0), scale=(1, 1, 1), mirror=False):
        if color == False:
            # color = cmds.getAttr('{}Shape1.overrideColor'.format(self.ctrl.name))
            shapes = cmds.listRelatives(self.ctrl.name, s=1)
            color = cmds.getAttr('{}.overrideColor'.format(shapes[0]))
        scale = (scale[0]*self.scaleOffset,
                 scale[1]*self.scaleOffset,
                 scale[2]*self.scaleOffset)
        if shape:
            scriptsPath = fileFn.getScriptDir()
            path = '{}/Jenks/scripts/controlShapes'.format(scriptsPath)
            loadShapeData(self.ctrl.name, shape, path)
        crvData = getShapeData(self.ctrl.name)
        if self.side == 'R' and mirror:
            rotation = (rotation[0]+180, rotation[1], rotation[2])
            translation = (-translation[0], translation[1], translation[2])
        applyShapeData(self.ctrl.name, crvData, transOffset=translation, rotOffset=rotation,
                       scaleOffset=scale)
        utils.setShapeColor(self.ctrl.name, color=color)
        if self.gimbal:
            utils.setShapeColor(self.gimbalCtrl.name, color=color)

    def constrain(self, target, typ='parent', mo=True, offset=[0, 0, 0],
                  aimVector=[1, 0, 0], aimUp=[0, 1, 0], aimWorldUpType=2, aimWorldUp=[0, 1, 0],
                  aimWorldUpObject='C_global_CTRL', skipRot='none', skipTrans='none',
                  skipScale='none', weight=1):
        if typ == 'parent':
            c = cmds.parentConstraint(self.ctrlEnd, target, mo=mo, sr=skipRot,
                                      st=skipTrans, w=weight)
        elif typ == 'point':
            if mo:
                c = cmds.pointConstraint(self.ctrlEnd, target, mo=mo, sk=skipTrans, w=weight)
            else:
                c = cmds.pointConstraint(self.ctrlEnd, target, o=offset, sk=skipTrans, w=weight)
        elif typ == 'orient':
            if mo:
                c = cmds.orientConstraint(self.ctrlEnd, target, mo=mo, sk=skipRot, w=weight)
            else:
                c = cmds.orientConstraint(self.ctrlEnd, target, o=offset, sk=skipRot, w=weight)
        elif typ == 'aim':
            if mo:
                c = cmds.aimConstraint(self.ctrlEnd, target, mo=mo, aim=aimVector, u=aimUp,
                                       wut=aimWorldUpType, wuo=aimWorldUpObject, wu=aimWorldUp,
                                       sk=skipRot, w=weight)
            else:
                c = cmds.aimConstraint(self.ctrlEnd, target, o=offset, aim=aimVector,
                                       u=aimUp, wut=aimWorldUpType, wuo=aimWorldUpObject,
                                       wu=aimWorldUp, sk=skipRot, w=weight)
        elif typ == 'scale':
            c = cmds.scaleConstraint(self.ctrlEnd, target, mo=mo, sk=skipScale, w=weight)
        elif typ == 'poleVector' or typ == 'pv':
            c = cmds.poleVectorConstraint(self.ctrlEnd, target, w=weight)
        else:
            cmds.warning('Parent Type Unsupported. Use: parent, point, orient, aim or poleVector.')
        return c[0]

    def lockAttr(self, attr='', hide=True, unlock=False):
        utils.lockAttr(self.ctrl.name, attr, hide, unlock)

    def addAttr(self, name, nn, typ='double', defaultVal=0, minVal=None, maxVal=None,
                enumOptions=None):
        attr = utils.addAttr(self.ctrl.name, name, nn, typ, defaultVal,
                             minVal, maxVal, enumOptions)
        exec('self.ctrl.{} = "{}"'.format(name, attr))
        return True

    def spaceSwitching(self, parents, niceNames=None, constraint='parent', dv=0):
        target = self.offsetGrps[0].name
        if not niceNames:
            niceNames=[]
            for each in parents:
                splitParent = each.partition('_')[-1].rpartition('_')[0]
                if splitParent == 'global':
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
            condNd = utils.newNode('condition', name='{}SpSwitch'.format(each),
                                   side=self.side, operation=0)
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
