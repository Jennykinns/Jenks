import maya.cmds as cmds

from Jenks.scripts.rigModules import suffixDictionary
from Jenks.scripts.rigModules import orientJoints

reload(suffixDictionary)

def setupName(name, obj='', suffix='', side='C', extraName='', skipNumber=False):
    """ Sets up a suitable name for a node to avoid naming conflicts.
        [Args]:
        name (string) - The base name
        obj (string) - The object type of the node
                       (used for the suffix)
        suffix (string) - An override for the suffix
        side (string) - The side of the node
        extraName (string) - An extra name option
        skipNumber (bool) - Toggles whether or not to skip the number
                            if possible
        [Returns]:
        newName (string) - The new name for the node
    """
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
    """ Sets up a suitable name for a body part to avoid naming
        conflicts.
        [Args]:
        side (string) - The side of the node
        extraName (string) - An extra name option
        [Returns]:
        newName (string) - The new name for the body part
    """
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

def addJntToSkinJnt(jnt, rig):
    """ Adds the specified joint to the rig's skin joints category.
        [Args]:
        jnt (string) - The name of the joint node
        rig (class) - The rig Class of the destination rig
    """
    if 'rigConnection' not in cmds.listAttr(jnt):
        rigConnection = addAttr(jnt, name='rigConnection',
                                nn='Rig Connection', typ='message')
    else:
        rigConnection = '{}.rigConnection'.format(jnt)
    cmds.connectAttr(rig.skinJntsAttr, rigConnection)

def getChildrenBetweenObjs(startObj, endObj, typ='joint'):
    """ Gets the children DAGs between two objects.
        [Args]:
        startObj (string) - The name of the start DAG
        endObj (string) - The name of the end DAG
        typ (string) - The type of object to limit the function to
        [Returns]:
        objs (list) - A list of the names of the DAG nodes that are
                      between the specified nodes.
    """
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
    """ Gets the specified colours depending on the position
        on the rig.
        [Args]:
        typ (string) - The position on the rig
                       (usually 'L', 'R' or 'C')
        [Returns]:
        colors (dictionary) - a dictionary of the colour ID values.
    """
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
    """ Sets the specified objects shape node colour.
        [Args]:
        obj (string) - The name of the object to change colour
        color (int) - The colour ID value
                      (can also be None to remove colour)
    """
    shapes = cmds.listRelatives(obj, s=1)
    for each in shapes:
        setColor(each, color)

def setColor(obj, color=None):
    """ Sets the specified objects colour.
        [Args]:
        obj (string) - The name of the object to change colour
        color (int) - The colour ID value
                      (can also be None to remove colour)
    """
    cmds.setAttr('{}.overrideEnabled'.format(obj), 1)
    if color:
        cmds.setAttr('{}.overrideVisibility'.format(obj), 1)
        cmds.setAttr('{}.overrideColor'.format(obj), color)
    else:
        cmds.setAttr('{}.overrideVisibility'.format(obj), 0)

def setOutlinerColor(obj, color=None):
    """ Sets the outliner colour for the specified node.
        [Args]:
        obj (string) - the name of the node to change
        color (int) - The colour ID value
                      (can also be None to remove colour)
    """
    cmds.setAttr('{}.useOutlinerColor'.format(obj), 1 if color else 0)
    cmds.setAttr('{}.outlinerColor'.format(obj), color[0], color[1], color[2])

def matchTransforms(objs, targetObj, skipTrans=False, skipRot=False):
    """ Matches the transforms of one object to another.
        [Args]:
        obj (string) - The object to move
        targetObj (string) - The object to match to
        skipTrans (bool) - Toggles skipping translation
        skipRot (bool) - Toggles skipping rotation
    """
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

def addAttr(node, name, nn, typ, defaultVal=0, minVal=None, maxVal=None, enumOptions=None):
    """ Adds an attribute to a node.
        [Args]:
        node (string) - The name of the node to add the attribute to
        name (string) - The name of the attribute
        nn (string) - The nice name of the attribute
        typ (string) - The type of the attribute
        defaultVal (float) - The default Value for the attribute
                             (if applicable)
        minVal (float) - The minimum value of the attribute
                         (if applicable)
        maxVal (float) - The maximum value of the attribute
                         (if applicable)
        enumOptions (list) - A list of enum otions
        [Returns]:
        (string) the long name of the attribute
    """
    attrs = cmds.listAttr(node)
    if not name in attrs:
        if typ == 'enum':
            enumName = ':'.join(enumOptions)
            cmds.addAttr(node, sn=name, nn=nn, at=typ, en=enumName, dv=defaultVal, k=1)
        elif typ == 'message':
            cmds.addAttr(node, sn=name, nn=nn, at=typ)
        else:
            if minVal is not None and maxVal is not None:
                cmds.addAttr(node, sn=name, nn=nn, at=typ,
                             dv=defaultVal, min=minVal, max=maxVal, k=1)
            elif minVal is not None:
                cmds.addAttr(node, sn=name, nn=nn, at=typ,
                             dv=defaultVal, min=minVal, k=1)
            elif maxVal is not None:
                cmds.addAttr(node, sn=name, nn=nn, at=typ,
                             dv=defaultVal, max=maxVal, k=1)
            else:
                cmds.addAttr(node, sn=name, nn=nn, at=typ,
                             dv=defaultVal, k=1)
    else:
        cmds.warning('{} already exists on {}'.format(name, node))
    return '{}.{}'.format(node, name)

def lockAttr(node, attr='', hide=True, unlock=False):
    """ Locks attributes of specified node.
        [Args]:
        node (string) - name of the node
        attr (list) - A list of attributes to lock
        hide (bool) - Toggles hiding the attributes as well
        unlock (bool) - Unlocks the attributes instead
    """
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
    cmds.makeIdentity(crv, a=1, t=1, r=1)
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

def createCrvFromObjs(objs, crvName='curve', side='C', extraName='', parent=None):
    pointList = []
    for each in objs:
        pos = cmds.xform(each, q=1, t=1, ws=1)
        pointList.append(pos)
    crv = cmds.curve(p=pointList, d=3)
    crv = cmds.rename(crv, '{}_{}{}{}'.format(side, extraName, crvName,
                                              suffixDictionary.suffix['nurbsCrv']))
    return crv


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

    def addAttr(self, name, nn, typ='double', defaultVal=0, minVal=None, maxVal=None,
                enumOptions=None):
        attr = addAttr(self.name, name, nn, typ, defaultVal, minVal, maxVal, enumOptions)
        exec('self.{} = "{}"'.format(name, attr))
        return True

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



