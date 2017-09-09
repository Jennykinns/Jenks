import maya.cmds as cmds
from Jenks.scripts.rigModules import suffixDictionary

reload(suffixDictionary)

def setupName(name, obj='', suffix='', side='C', extraName=''):
    if not suffix and obj:
        suffix = suffixDictionary.suffix[obj]
    freeName = False
    i = 1
    while not freeName:
        num = str(i).zfill(2)
        newName = '{}_{}{}{}{}'.format(side, name, extraName, num, suffix)
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
    print 'Color Set'

def matchTransforms(objs, targetObj):
    for each in objs:
        cmds.delete(cmds.parentConstraint(targetObj, each))

class newNode:
    def __init__(self, node, name='', suffix='', parent='', operation=None):
        nodeName = setupName(name if name else node, suffix=suffix, obj=node)
        if node == 'locator':
            self.name = cmds.spaceLocator(n=nodeName)[0]
        elif node == 'group':
            self.name = cmds.group(n=nodeName, em=1)
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



