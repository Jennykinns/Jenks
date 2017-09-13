import maya.cmds as cmds

from Jenks.scripts.rigModules import suffixDictionary

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

def setShapeColor(obj, color=None):
    shapes = cmds.listRelatives(obj, s=1)
    for each in shapes:
        setColor(each, color)

def setColor(obj, color=None):
    cmds.setAttr('{}.overrideEnabled'.format(obj), 1)
    cmds.setAttr('{}.overrideColor'.format(obj), color if color else 0)

def matchTransforms(objs, targetObj):
    for each in objs:
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

class newNode:
    def __init__(self, node, name='', suffixOverride='', parent='', side='C',
                 operation=None, skipNum=False):
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



