import maya.cmds as cmds

from Jenks.scripts.rigModules import suffixDictionary
from Jenks.scripts.rigModules import orientJoints
from Jenks.scripts.rigModules import apiFunctions as apiFn

import re

reload(suffixDictionary)
reload(apiFn)

def setupName(name, obj='', suffix='', side='C', extraName='', skipNumber=False):
    """ Set up a suitable name for a node to avoid naming conflicts.
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
    """ Set up a suitable name for a body part to avoid naming
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

def hashToNumber(name, suffix, startNum=1):
    """ Turn all the hashes in string to numbers. (also checks for
        naming conflicts)
        [Args]:
        name (string) - The base string with hashes
        suffix (string) - Suffix for the name
        startNum (int) - The number to start on
        [Returns]:
        newName (string) - The new name with hashes replaced
    """
    hashes = re.findall('#+', name)
    if hashes:
        i = 0
        for each in hashes:
            numFill = len(each)
            newName = '{}{}'.format(str(i+startNum).zfill(numFill).join(name.split(each)),
                                    suffix)
            while cmds.objExists(newName):
                i += 1
                newName = '{}{}'.format(str(i+startNum).zfill(numFill).join(name.split(each)),
                                        suffix)
    else:
        newName = '{}{}'.format(name, suffix)
        i = 0
        while cmds.objExists(newName):
            i += 1
            newName = '{}{}{}'.format(name, i, suffix)
    return newName

def getSuffixForObjType(obj):
    shapeNode = cmds.listRelatives(obj, s=1, f=1)
    objType = cmds.objectType(shapeNode[0] if shapeNode else obj)
    if objType in suffixDictionary.suffix.keys():
        suffix = suffixDictionary.suffix[objType]
    else:
        cmds.warning('{} {}'.format(objType,
                     'Node type not in suffixDictionary, contact the Pipeline TD to add it.'))
        suffix = ''
    return suffix

def rename(mObj, newName, side=None, startNum=1, skipSuff=False):
    """ Rename object with suffix to avoid conflicts.
        [Args]:
        mObj (mObj) - The mObj for the node to rename
        newName (string) - The new name for the node
        startNum (int) - The number to start on
        [Returns]:
        r (string) - renamed object name
    """
    if side:
        newName = '{}_{}'.format(side, newName)
    lN, sN = apiFn.getPath(mObj, returnString=True)
    try:
        cmds.rename(lN, 'TMPNAME_OOGIEOOGIE_POOP')
    except:
        return False
    lN, sN = apiFn.getPath(mObj, returnString=True)
    suffix = getSuffixForObjType(lN)
    if cmds.nodeType(lN) == 'aiImage':
        fileName = cmds.getAttr('{}.filename'.format(lN))
        fileName = fileName.rsplit('/', 1)[-1]
        newName = '{}_{}'.format(newName, fileName.rsplit('.', 1)[0])
    if newName.endswith(suffix) or skipSuff:
        nameNoDigits = newName
        while nameNoDigits[-1].isdigit():
            nameNoDigits = nameNoDigits[:-1]
        if '_{}'.format(newName.rsplit('_', 1)[-1]) in suffixDictionary.suffix.values():
            newName = newName.rsplit('_', 1)[0]
        else:
            suffix = ''
    newName = hashToNumber(newName, suffix, startNum)
    r = cmds.rename(lN, newName)
    return r

def findReplace(mObj, find, replace, startNum=1):
    """ Find a string and replaces it with another.
        (supports regex)
        [Args]:
        mObj (mObj) - The mObj for the node to rename
        find (string) - The string to find
        replace (string) - The string to replace with
        startNum (int) - The number to start with
        [Returns]:
        r (string) - The new string
    """
    lN, sN = apiFn.getPath(mObj, returnString=True)
    newName = re.sub(find, replace, sN)
    r = rename(mObj, newName, startNum=startNum, skipSuff=True)
    return r

def stripName(mObj, stripFromRight=False, startNum=1):
    """ Strip the left (or right) character from the name segment
        of an object.
        [Args]:
        mObj (mObj) - The mObj for the node to rename
        stripFromRight (bool) - Toggles stripping from the right
                                instead of left
        startNum (int) - The number to start with
        [Returns]:
        r (string) - The new string
    """
    lN, sN = apiFn.getPath(mObj, returnString=True)
    side, nameSegment = sN.split('_', 1)
    nameSegment = nameSegment.rsplit('_', 1)[0]
    if stripFromRight:
        newName = nameSegment[:-1]
    else:
        newName = nameSegment[1:]
    newName = '{}_{}'.format(side, newName)
    r = rename(mObj, newName, startNum=startNum)
    return r

def swapSide(mObj, side='C', startNum=1):
    """ Swap the side prefix.
        [Args]:
        mObj (mObj) - The mObj for the node to rename
        side (string) - The side to swap to ('R', 'L' or 'C')
        startNum (int) - The number to start with
        [Returns]:
        r (string) - The new string
    """
    lN, sN = apiFn.getPath(mObj, returnString=True)
    if sN.startswith(('L_', 'R_', 'C_')):
        nameSegment = sN[2:]
    else:
        nameSegment = sN
    newName = '{}_{}'.format(side, nameSegment)
    # while newName.endswith(('1', '2', '3', '4', '5', '6', '7', '8', '9', '0')):
    while newName[-1].isdigit():
        newName = newName[:-1]
    r = rename(mObj, newName, startNum=startNum, skipSuff=True)
    return r


def renameSelection(newName, side):
    """ Rename the selected objects.
        [Args]:
        newName (string) - The new name for the objects
        [Returns]:
        True on success
    """
    sel = apiFn.getSelectionAsMObjs()
    for i, mObj in enumerate(sel, 1):
        rename(mObj, newName, side, i)
    return True

def findReplaceSelection(find, replace):
    """ Find and replace for the current selection.
        [Args]:
        find (string) - The string to find
        replace (string) - The string to replace with
        [Returns]:
        True on success
    """
    sel = apiFn.getSelectionAsMObjs()
    for i, mObj in enumerate(sel, 1):
        findReplace(mObj, find, replace, startNum=i)
    return True

def stripNameSelection(stripFromRight=False):
    """ Strip the name of the selected objects.
        [Args]:
        stripFromRight (bool) - Toggles stripping from the right
                                instead of the left
        [Returns]:
        True on success
    """
    sel = apiFn.getSelectionAsMObjs()
    for i, mObj in enumerate(sel, 1):
        stripName(mObj, stripFromRight=stripFromRight, startNum=i)
    return True

def swapSideSelection(side='C'):
    """ Swap the side prefix of the selected objects.
        [Args]:
        side (string) - The side to swap to ('R', 'L' or 'C')
        [Returns]:
        True on success
    """
    sel = apiFn.getSelectionAsMObjs()
    for i, mObj in enumerate(sel, 1):
        swapSide(mObj, side, startNum=i)
    return True

def addSuffixToSelection():
    """ Add suffix to selected objects."""
    sel = apiFn.getSelectionAsMObjs()
    for i, mObj in enumerate(sel, 1):
        lN, sN = apiFn.getPath(mObj, returnString=True)
        # suffix = getSuffixForObjType(lN)
        r = rename(mObj, sN, startNum=i, skipSuff=False)


def addJntToSkinJnt(jnt, rig):
    """ Add the specified joint to the rig's skin joints category.
        [Args]:
        jnt (string) - The name of the joint node
        rig (class) - The rig Class of the destination rig
    """
    if 'rigConnection' not in cmds.listAttr(jnt):
        rigConnection = addAttr(jnt, name='rigConnection',
                                nn='Rig Connection', typ='message')
    else:
        rigConnection = '{}.rigConnection'.format(jnt)
    existingConnections = cmds.listConnections(rigConnection, p=1)
    if not existingConnections or rig.skinJntsAttr not in existingConnections:
        cmds.connectAttr(rig.skinJntsAttr, rigConnection)


def getChildrenBetweenObjs(startObj, endObj, typ='joint'):
    """ Get the children DAGs between two objects.
        [Args]:
        startObj (string) - The name of the start DAG
        endObj (string) - The name of the end DAG
        typ (string) - The type of object to limit the function to
        [Returns]:
        objs (list)(string) - A list of the names of the DAG nodes
                              that are between the specified nodes.
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
    """ Get the specified colours depending on the position
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
    """ Set the specified objects shape node colour.
        [Args]:
        obj (string) - The name of the object to change colour
        color (int) - The colour ID value
                      (can also be None to remove colour)
    """
    shapes = cmds.listRelatives(obj, s=1)
    for each in shapes:
        setColor(each, color)

def setColor(obj, color=None):
    """ Set the specified objects colour.
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
    """ Set the outliner colour for the specified node.
        [Args]:
        obj (string) - the name of the node to change
        color (int) - The colour ID value
                      (can also be None to remove colour)
    """
    cmds.setAttr('{}.useOutlinerColor'.format(obj), 1 if color else 0)
    cmds.setAttr('{}.outlinerColor'.format(obj), color[0], color[1], color[2])

def getRigInSelection():
    """ Return a list of rig global groups associated with the current
    selection.
    [Returns]:
    rigNodes (list)(string) - A list of the associated rigs.
    """
    sel = cmds.ls(sl=1)
    rigNodes = []
    for each in sel:
        if each.endswith('global_CTRL'):
            rigNodes.append(each)
        elif 'rigConnection' in cmds.listAttr(each):
            rigNodes.append(cmds.listConnections('{}.rigConnection'.format(each), d=0, s=1)[0])
    return rigNodes

def matchTransforms(objs, targetObj, skipTrans=False, skipRot=False):
    """ Match the transforms of one object to another.
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
    """ Add an attribute to a node.
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
        enumOptions (list)(string) - A list of enum otions
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
    """ Lock attributes of specified node.
        [Args]:
        node (string) - name of the node
        attr (list)(string) - A list of attributes to lock
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
    """ Get the shape nodes of the specified object.
        [Args]:
        obj (string) - The name of the object
        [Returns]:
        children (list)(string) - A list of children shapes
    """
    children = cmds.listRelatives(obj, s=1)
    return children

def orientJoints(jnts, aimAxis=(1, 0, 0), upAxis=(0, 1, 0)):
    """ Orient the joints correctly.
    [Args]:
    jnts (list)(string) - The joints to orient
    aimAxis (tuple) - The aim axis vector
    upAxis (tuple) - The up axis vector
    """
    tmpLoc = newNode('group', name='tmp')
    prevUpVector = apiFn.getVector(tmpLoc.name)
    cmds.delete(tmpLoc.name)
    for each in jnts:
        ## get vectors
        curVector = apiFn.getVector(each)
        # pos = cmds.xform(each, q=1, t=1, ws=1)
        # curVector = om.MVector(pos)
        child = cmds.listRelatives(each, typ='joint', c=1)
        if child:
            childVector = apiFn.getVector(child[0])
            # childPos = cmds.xform(child[0], q=1, t=1, ws=1)
            # childVector = om.MVector(childPos)
        else:
            cmds.setAttr('{}.jointOrient'.format(each), 0, 0, 0)
            cmds.setAttr('{}.r'.format(each), 0, 0, 0)
            continue
        parent = cmds.listRelatives(each, typ='joint', p=1)
        if parent:
            parentVector = apiFn.getVector(parent[0])
            # parentPos = cmds.xform(parent[0], q=1, t=1, ws=1)
            # parentVector = om.MVector(parentPos)
        else:
            parentVector = curVector
            curVector = childVector
            gChild = cmds.listRelatives(child[0], typ='joint', c=1)
            if gChild:
                childVector = apiFn.getVector(gChild[0])
                # gChildPos = cmds.xform(gChild[0], q=1, t=1, ws=1)
                # childVector = om.MVector(gChildPos)

        firstVector = curVector - parentVector
        secondVector = curVector - childVector
        crossProd = firstVector.normal() ^ secondVector.normal()

        child = cmds.parent(child, w=1)
        cmds.delete(cmds.aimConstraint(child[0], each, w=1, o=(0, 0, 0),
                                       upVector=upAxis, aim=aimAxis,
                                       worldUpVector=crossProd, worldUpType='vector'))

        dotProd = (float('{:3f}'.format(crossProd.x)) * prevUpVector.x
                   + float('{:3f}'.format(crossProd.y)) * prevUpVector.y
                   + float('{:3f}'.format(crossProd.z)) * prevUpVector.z)

        prevUpVector = crossProd

        if dotProd < 0.0:
            cmds.xform(each, r=1, os=1, ra=(aimAxis[0] * 180.0,
                                            aimAxis[1] * 180.0,
                                            aimAxis[2] * 180.0))
            prevUpVector *= -1

        cmds.joint(each, e=True, zeroScaleOrient=True)
        cmds.makeIdentity(each, a=1, t=0, r=1, s=0, n=0)
        cmds.parent(child, each)

        for t in 'xyz':
            tVal = cmds.getAttr('{}.t{}'.format(each, t))
            if tVal > -0.0001 and tVal < 0.0001:
                cmds.setAttr('{}.t{}'.format(each, t), 0)

def orientSelectedJoints(hierarchy=False, aimAxis=(1, 0, 0), upAxis=(0, 1, 0)):
    sel = cmds.ls(sl=1, typ='joint', l=1)
    c = cmds.confirmDialog(m='Aim', button=['X', '-X'])
    if c == '-X':
        aimAxis = (-aimAxis[0], aimAxis[1], aimAxis[2])
    orientJoints(sel, aimAxis=aimAxis, upAxis=upAxis)
    cmds.select(sel)


def createJntsFromCrv(crv, numOfJnts, chain=True, name='curveJoints', side='C'):
    """ Create joints on a curve.
        [Args]:
        crv (string) - The name of the curve
        numOfJnts (int) - The amount of joints to create
        chain (bool) - A toggle for creating the joints as a chain
        name (string) - The name of the new joints
        side (string) - The side of the new joints
        [Returns]:
        jntList (list)(string) - A list of the new joint names
    """
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
    # orientJoints.doOrientJoint(jointsToOrient=jntList, aimAxis=(1, 0, 0), upAxis=(0, 1, 0),
    #                                    worldUp=(0, 1, 0), guessUp=1)
    orientJoints(jntList)
    cmds.select(cl=1)
    if not tmpCrv == crv:
        cmds.delete(tmpCrv)
    return jntList

def duplicateJntChain(chainName, jnts, parent=None):
    """ Duplicate a joint chain.
        [Args]:
        chainName (string) - The name of the new joint chain
        jnts (list)(string) - A list of the joints in the chain to
                              duplicate
        parent (string) - The name of the object to parent the
                          new joint chain
        [Returns]:
        newJnts (list)(string) - A list of the new joints created
    """
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
    """ Create a joint chain from a list of objects.
        [Args]:
        objs (list)(string) - A list of object names to create the
                              joints from
        chainName (string) - The name of the new joint chain
        side (string) - The side of the new chain
        extraName (string) - The optional extra name for the
                             new joint chain
        jntNames (list)(string) - A list of optional extra names for
                                  each joint
        parent (string) - The name of the object to parent the
                          new joint chain
        [Returns]:
        newJnts (list)(string) - A list of the new joints created
    """
    newJnts = []
    for i, each in enumerate(objs):
        newJntName = '{}{}_{}'.format(extraName, chainName,
                                      jntNames[i] if jntNames else '')
        jnt = newNode('joint', name=newJntName, side=side, parent=parent,
                      skipNum=True if jntNames else False)
        jnt.matchTransforms(each)
        parent = jnt.name
        newJnts.append(jnt.name)
    # orientJoints.doOrientJoint(jointsToOrient=newJnts, aimAxis=(1, 0, 0), upAxis=(0, 1, 0),
    #                            worldUp=(0, 1, 0), guessUp=1)
    orientJoints(newJnts)
    return newJnts

def createCrvFromObjs(objs, crvName='curve', side='C', extraName='', parent=None):
    """ Create a curve from a list of objects.
        [Args]:
        objs (list)(string) - Names of objects to create the curve from
        crvName (string) - The name of the new curve
        side (string) - The side of the new curve
        extraName (string) - The optional extra name for the new curve
        parent (string) - The name of the object to parent the
                          new curve to
        [Returns]:
        crv (string) - The name of the new curve
    """
    pointList = []
    for each in objs:
        pos = cmds.xform(each, q=1, t=1, ws=1)
        pointList.append(pos)
    crv = cmds.curve(p=pointList, d=3)
    crv = cmds.rename(crv, '{}_{}{}{}'.format(side, extraName, crvName,
                                              suffixDictionary.suffix['nurbsCrv']))
    return crv

def getAllChildren(obj):
    """ Return a list of children for the specified object.
        [Args]:
        obj (string) - Name of the object to list children
        [Returns]:
        jnts (list)(string) - Names of child objects
    """
    jnts = []
    a = cmds.listRelatives(obj, type='joint')
    if a:
        for each in a:
            jnts.append(each)
            jnts.extend(getAllChildren(each))
    return jnts

def getAssetsInScene(location='rig/Published'):
    """ Return current assets in the scene.
        [Returns]:
        assets (list)(string) - The names of the assets in the scene
        refNds (list)(string) - The reference nodes of the assets in
                                the scene
    """
    location = '/{}'.format(location)
    assets = []
    refNds = cmds.ls(type='reference')
    if 'sharedReferenceNode' in refNds:
        refNds.remove('sharedReferenceNode')
    for each in refNds:
        filePath = cmds.referenceQuery(each, f=True)
        if location in filePath:
            if filePath.endswith('}'):
                filePath = filePath[:-3]
            fileName = filePath.rpartition('/')[-1]
            assetName = fileName.rpartition('_')[0]
            assets.append(assetName)
        else:
            refNds.remove(each)
    return assets, refNds

class newNode:
    """ Create new nodes."""
    def __init__(self, node, name='', suffixOverride='', parent='', side='C',
                 operation=None, skipNum=False, shaderNode=False):
        """ The creation function to create new nodes.
        [Args]:
        node (string) - The type of node to create
        name (string) - The name of the new node
        suffixOverride (string) - The optional override for the suffix
                                  (Uses object type not custom string
                                   e.g 'locator' or 'group')
        parent (string) - The name of the object to parent the
                          new node to
        side (string) - The side of the new node
        operation (int) - The value of the new node's operation
                          attribute (if applicable)
        skipNumber (bool) - Toggles whether or not to skip the number
                            if possible
        """
        self.node = node
        nodeName = setupName(name if name else node,
                             obj=node if not suffixOverride else suffixOverride,
                             side=side, skipNumber=skipNum)
        if shaderNode:
            if shaderNode == 'shader':
                self.name = cmds.shadingNode(node, n=nodeName, ss=1, asShader=1)
            if shaderNode == 'texture':
                self.name = cmds.shadingNode(node, n=nodeName, ss=1, asTexture=1)
            if shaderNode == 'utility':
                self.name = cmds.shadingNode(node, n=nodeName, ss=1, asUtility=1)
        else:
            if node == 'locator':
                self.name = cmds.spaceLocator(n=nodeName)[0]
            elif node == 'group':
                self.name = cmds.group(n=nodeName, em=1)
            elif node == 'control' or node == 'gimbalCtrl':
                self.name = cmds.circle(n=nodeName, ch=0)[0]
            elif node == 'follicle':
                fol = cmds.createNode(node, ss=1)
                folTransform = cmds.listRelatives(fol, p=1)
                self.name = cmds.rename(folTransform, nodeName)
            elif node == 'hairSystem':
                hs = cmds.createNode(node, ss=1)
                hsTransform = cmds.listRelatives(hs, p=1)
                self.name = cmds.rename(hsTransform, nodeName)
            elif node == 'cluster':
                clu, cluHdl = cmds.cluster(n=nodeName)
                self.name = cmds.rename(cluHdl, '{}H'.format(nodeName))
            elif node == 'shadingEngine':
                self.name = cmds.sets(renderable=True, noSurfaceShader=True,
                                      empty=True, name=nodeName)
            else:
                self.name = cmds.createNode(node, n=nodeName, ss=1)
            if parent:
                cmds.parent(self.name, parent)
            if operation and 'operation' in cmds.listAttr(self.name):
                cmds.setAttr('{}.operation'.format(self.name), operation)
        cmds.select(cl=1)

    def parent(self, parent, relative=False):
        """ Parent the node.
        [Args]:
        parent (string) - The name of the parent
        relative (bool) - Toggles if the parent should be relative
        """
        if parent == 'world':
            cmds.parent(self.name, w=True, r=relative)
        cmds.parent(self.name, parent, r=relative)

    def addAttr(self, name, nn, typ='double', defaultVal=0, minVal=None, maxVal=None,
                enumOptions=None):
        """ Add an attribute to the node.
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
        enumOptions (list)(string) - A list of enum otions
        [Returns]:
        (bool) If sucessful
        """
        attr = addAttr(self.name, name, nn, typ, defaultVal, minVal, maxVal, enumOptions)
        exec('self.{} = "{}"'.format(name, attr))
        return True

    def lockAttr(self, attr='', hide=True, unlock=False):
        """ Lock attrubutes on node.
        [Args]:
        attr (list)(string) - A list of attributes to lock
        hide (bool) - Toggles hiding the attributes as well
        unlock (bool) - Unlocks the attributes instead
        """
        lockAttr(self.name, attr, hide, unlock)

    def connect(self, nodeAttr, dest, mode='from'):
        """ Connect an attribute to the node.
        [Args]:
        nodeAttr (string) - The name of the node's attribute
        dest (string) - The long name of the another node's attribute
        mode (string) - Changes the mode of the function
                        ('from' the node's attribute,
                         'to' the node's attribute)
        """
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
        """ Match the transforms of one object to another.
        [Args]:
        obj (string) - The object to match to
        skipTrans (bool) - Toggles skipping translation
        skipRot (bool) - Toggles skipping rotation
        """
        matchTransforms(self.name, obj, skipTrans, skipRot)
        if self.node == 'joint':
            cmds.makeIdentity(self.name, a=1, r=1)



