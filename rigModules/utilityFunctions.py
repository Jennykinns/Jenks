import maya.cmds as cmds

from Jenks.scripts.rigModules import suffixDictionary
from Jenks.scripts.rigModules import orientJoints

reload(suffixDictionary)

def setupName(name, obj='', suffix='', side='C', extraName='', skipNumber=False):
    if not suffix and obj:
        suffix = suffixDictionary.suffix[obj]
    freeName = False
    i = 1
    while not freeName:
        num = str(i).zfill(2)
        if not skipNumber or i > 1:
            newName = '{}_{}{}{}{}'.format(side, name, extraName, num, suffix)
        else:
            newName = '{}_{}{}{}'.format(side, name, extraName, suffix)
        if not cmds.objExists(newName):
            freeName = True
        else:
            i += 1
    return newName

def setupBodyPartName(extraName='', side='C'):
    freeName = False
    i = 1
    num = ''
    while not freeName:
        if extraName:
            extraName += '_'
        newName = '{}_{}{}'.format(side,extraName, num)
        if not cmds.objExists('{}_GRP'.format(newName)):
            freeName = True
        else:
            num = str(i).zfill(2)
            i += 1
    return newName

def getChildrenBetweenObjs(startObj, endObj, typ='joint'):
    sChilds = cmds.listRelatives(startObj, ad=1, type=typ)
    eChilds = cmds.listRelatives(endObj, ad=1, type=typ)
    if eChilds:
        objs = list(set(sChilds) - set(eChilds))
    else:
      objs = sChilds
      objs.reverse()
    objs.insert(0, startObj)
    return objs

def getColors(typ):
    colors = {}
    if typ == 'L':
        colors['col1'] = 15
        colors['col2'] = 28
        colors['col3'] = 29
        colors['settingCol'] = 26
    elif typ == 'R':
        colors['col1'] = 12
        colors['col2'] = 24
        colors['col3'] = 21
        colors['settingCol'] = 31
    elif typ == 'C':
        colors['col1'] = 10
        colors['col2'] = 22
        colors['col3'] = 23
        colors['settingCol'] = 7
    else:
        colors['col1'] = 30
        colors['col2'] = 0
        colors['col3'] = 0
        colors['settingCol'] = 7
    return colors

def setShapeColor(obj, color=None):
    shapes = cmds.listRelatives(obj, s=1)
    for each in shapes:
        setColor(each, color)

def setColor(obj, color=None):
    cmds.setAttr('{}.overrideEnabled'.format(obj), 1)
    cmds.setAttr('{}.overrideColor'.format(obj), color if color else 0)

def setOutlinerColor(obj, color=None):
    cmds.setAttr('{}.useOutlinerColor'.format(obj), 1 if color else 0)
    cmds.setAttr('{}.outlinerColor'.format(obj), color[0], color[1], color[2])

def matchTransforms(objs, targetObj, skipTrans=False, skipRot=False):
    if type(objs) is not type(list()):
        objs = [objs]
    for each in objs:
        if skipRot and skipTrans:
            continue
        if skipRot:
            cmds.delete(cmds.parentConstraint(targetObj, each, sr=['x', 'y', 'z']))
            continue
        if skipTrans:
            cmds.delete(cmds.parentConstraint(targetObj, each, st=['x', 'y', 'z']))
            continue
        cmds.delete(cmds.parentConstraint(targetObj, each))

def lockAttr(node, attr='', hide=True, unlock=False):
    if unlock:
        hide=False
    if not attr:
        attr = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
    for each in attr:
        if each == 't':
            cmds.setAttr('{}.{}'.format(node, 'tx'), l=not unlock, k=not hide)
            cmds.setAttr('{}.{}'.format(node, 'ty'), l=not unlock, k=not hide)
            cmds.setAttr('{}.{}'.format(node, 'tz'), l=not unlock, k=not hide)
        elif each == 'r':
            cmds.setAttr('{}.{}'.format(node, 'rx'), l=not unlock, k=not hide)
            cmds.setAttr('{}.{}'.format(node, 'ry'), l=not unlock, k=not hide)
            cmds.setAttr('{}.{}'.format(node, 'rz'), l=not unlock, k=not hide)
        elif each == 's':
            cmds.setAttr('{}.{}'.format(node, 'sx'), l=not unlock, k=not hide)
            cmds.setAttr('{}.{}'.format(node, 'sy'), l=not unlock, k=not hide)
            cmds.setAttr('{}.{}'.format(node, 'sz'), l=not unlock, k=not hide)
        else:
            cmds.setAttr('{}.{}'.format(node, each), l=not unlock, k=not hide)

def getShapeNodes(obj):
    children = cmds.listRelatives(obj, s=1)
    return children

def createJntsFromCrv(crv, numOfJnts, chain=True, name='curveJoints', side='C'):
    tmpCrv = cmds.rebuildCurve(crv, rt=0, end=1, kr=0, kt=0, s=numOfJnts-1, d=3)[0]
    parent = None
    jntList = []
    for i in range(numOfJnts):
        jnt = newNode('joint', name=name, side=side, parent=parent)
        jntList.append(jnt.name)
        if chain:
            parent = jnt.name
        pos = cmds.getAttr('{}.ep[{}]'.format(tmpCrv, i))[0]
        cmds.xform(jnt.name, t=pos, ws=1)
    orientJoints.doOrientJoint(jointsToOrient=jntList, aimAxis=(1, 0, 0), upAxis=(0, 1, 0),
                                       worldUp=(0, 1, 0), guessUp=1)
    cmds.select(cl=1)
    if not tmpCrv == crv:
        cmds.delete(tmpCrv)
    return jntList

def duplicateJntChain(chainName, jnts, parent=None):
    newJnts = []
    dupeChain = cmds.duplicate(jnts[0], rc=1)
    for each in reversed(dupeChain):
        if (each.rstrip('1')) not in jnts or not cmds.objectType(each) == 'joint':
            cmds.delete(each)
            continue
        newName = '{}_{}{}'.format(each.rsplit('_', 1)[0], chainName,
                                   suffixDictionary.suffix['joint'])
        newJnts.insert(0, cmds.rename(each, newName))
    if parent:
        cmds.parent(newJnts[0], parent)
    return newJnts

def createJntChainFromObjs(objs, chainName, side='C', extraName='', jntNames=None, parent=None):
    newJnts = []
    for i, each in enumerate(objs):
        newJntName = '{}{}_{}'.format(extraName, chainName,
                                      jntNames[i] if jntNames else '')
        jnt = newNode('joint', name=newJntName, side=side, parent=parent,
                      skipNum=True if jntNames else False)
        jnt.matchTransforms(each)
        parent = jnt.name
        newJnts.append(jnt.name)
    orientJoints.doOrientJoint(jointsToOrient=newJnts, aimAxis=(1, 0, 0), upAxis=(0, 1, 0),
                               worldUp=(0, 1, 0), guessUp=1)
    return newJnts


class newNode:
    def __init__(self, node, name='', suffixOverride='', parent='', side='C',
                 operation=None, skipNum=False):
        self.node = node
        nodeName = setupName(name if name else node,
                             obj=node if not suffixOverride else suffixOverride,
                             side=side, skipNumber=skipNum)
        if node == 'locator':
            self.name = cmds.spaceLocator(n=nodeName)[0]
        elif node == 'group':
            self.name = cmds.group(n=nodeName, em=1)
        elif node == 'control':
            self.name = cmds.circle(n=nodeName, ch=0)[0]
        else:
            self.name = cmds.createNode(node, n=nodeName, ss=1)
        if parent:
            cmds.parent(self.name, parent)
        if operation and 'operation' in cmds.listAttr(self.name):
            cmds.setAttr('{}.operation'.format(self.name), operation)
        cmds.select(cl=1)

    def parent(self, parent, relative=False):
        if parent == 'world':
            cmds.parent(self.name, w=True, r=relative)
        cmds.parent(self.name, parent, r=relative)

    def lockAttr(self, attr='', hide=True, unlock=False):
        lockAttr(self.name, attr, hide, unlock)

    def connect(self, nodeAttr, dest, mode='from'):
        nodeAttrFull = '{}.{}'.format(self.name, nodeAttr)
        if mode == 'from':
            cmds.connectAttr(nodeAttrFull, dest)
        elif mode == 'to':
            existingConnections = cmds.listConnections(nodeAttrFull, p=1)
            if existingConnections:
                for plug in existingConnections:
                    cmds.disconnectAttr(plug, nodeAttrFull)
            cmds.connectAttr(dest, nodeAttrFull)

    def matchTransforms(self, obj, skipTrans=False, skipRot=False):
        matchTransforms(self.name, obj, skipTrans, skipRot)
        if self.node == 'joint':
            cmds.makeIdentity(self.name, a=1, r=1)



