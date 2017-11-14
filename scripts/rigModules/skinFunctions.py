import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

from Jenks.scripts.rigModules import fileFunctions as fileFn
from Jenks.scripts.rigModules import apiFunctions as apiFn

import xml.etree.cElementTree

def getAllSkinJnts(rigNode):
    jnts = cmds.listConnections('{}.rigSkinJnts'.format(rigNode), d=1, s=0)
    return jnts

def selectSkinJnts():
    sel = cmds.ls(sl=1)
    rigNodes = []
    for each in sel:
        if each.endswith('global_CTRL'):
            rigNodes.append(each)
        elif 'rigConnection' in cmds.listAttr(each):
            rigNodes.append(cmds.listConnections('{}.rigConnection'.format(each), d=0, s=1)[0])
    jnts = []
    if rigNodes == list():
        return False
    for rigNode in rigNodes:
        jnts.extend(getAllSkinJnts(rigNode))
    cmds.select(jnts)
    return True

def getSkinInfo(obj):
    ## skin cluster(s)
    shapes = cmds.listRelatives(obj, s=1)
    if not shapes:
        return False, False
    skinCls = []
    for each in shapes:
        cls = cmds.listConnections(each, type='skinCluster')
        if cls:
            skinCls.extend(cls)
    return skinCls

def loadSkin(geo, assetName=None, prompt=False, override=False):
    assetName = fileFn.assetNameSetup(assetName, prompt)
    path = fileFn.getAssetDir()
    fileName = fileFn.getLatestVersion(assetName, path, 'rig/WIP/skin', name=geo)
    if not fileName:
        return False
    skinCls = getSkinInfo(geo)
    if not skinCls:
        skinInfo = {}
        xmlRoot = xml.etree.cElementTree.parse(fileName).getroot()
        skinInfo['joints'] = [each.get('source') for each in xmlRoot.findall('weights')]
        skinCls = cmds.skinCluster(geo, skinInfo['joints'])[0]
        cmds.select(cl=1)
    cmds.deformerWeights(fileName, path='', deformer=skinCls, im=1, wp=5, wt=0.00001)
    cmds.skinCluster(skinCls, e=1, fnw=1)
    return True

def saveSkin(geo, assetName=None, prompt=False):
    assetName = fileFn.assetNameSetup(assetName, prompt)
    path = fileFn.getAssetDir()
    fileName = fileFn.getLatestVersion(assetName, path, 'rig/WIP/skin', new=True, name=geo)
    skinCls = getSkinInfo(geo)
    if skinCls:
        for each in skinCls:
            truncateWeights(each, geo)
            cmds.deformerWeights(fileName, path='', deformer=each, ex=1, wp=5, wt=0.00001)
    return True

def saveAllSkin(assetName=None, prompt=False):
    assetName = fileFn.assetNameSetup(assetName, prompt)
    geo = cmds.listRelatives('C_geometry_GRP', ad=1, type='transform')
    if geo:
        for each in geo:
            saveSkin(each, assetName)
        return True
    else:
        return False

def loadAllSkin(assetName=None, prompt=False):
    assetName = fileFn.assetNameSetup(assetName, prompt)
    print 'Starting Skinning From Saved Files.'
    geo = cmds.ls(type='transform')
    if geo:
        for each in geo:
            loadSkin(each, assetName)
        print 'Finished Skinning From Saved Files.'
        return True
    else:
        print 'Skinning From Saved Files FAILED.'
        return False

def truncateWeights(skinCls, geo):
    normVal = cmds.getAttr('{}.normalizeWeights'.format(skinCls))
    cmds.setAttr('{}.normalizeWeights'.format(skinCls), 0)
    cmds.skinPercent(skinCls, geo, prw=0.001, nrm=1)

    skinMObj = apiFn.getMObj(skinCls)
    skin = oma.MFnSkinCluster(skinMObj)
    inflObj = skin.influenceObjects()

    inflIdList = {}
    for x in range(len(inflObj)):
        inflId = int(skin.indexForInfluenceObject(inflObj[x]))
        inflIdList[inflId] = x

    weightListPlug = skin.findPlug('weightList', False)
    weightsPlug = skin.findPlug('weights', False)
    weightListAttr = weightListPlug.attribute()
    weightsAttr = weightsPlug.attribute()

    for vertId in range(weightListPlug.numElements()):
        vertWeights = {}
        weightsPlug.selectAncestorLogicalIndex(vertId, weightListAttr)
        weightInfluenceIds = weightsPlug.getExistingArrayAttributeIndices()

        remainder = 1
        largestIndex = None
        largestVal = 0

        inflPlug = om.MPlug(weightsPlug)
        for inflId in weightInfluenceIds:
            inflPlug.selectAncestorLogicalIndex(inflId, weightsAttr)
            try:
                vertWeights[inflIdList[inflId]] = val = round(inflPlug.asDouble(), 5)
                if val > largestVal:
                    largestVal = val
                    largestIndex = inflIdList[inflId]
                remainder -= val
            except KeyError:
                pass

        if largestVal <= 0:
            continue

        vertWeights[largestIndex] = round(vertWeights[largestIndex] + remainder, 5)
        for inflId in weightInfluenceIds:
            inflPlug.selectAncestorLogicalIndex(inflId, weightsAttr)
            cmds.setAttr('{}.weightList[{}].weights[{}]'.format(skinCls, vertId, inflId),
                         vertWeights[inflIdList[inflId]])

    cmds.setAttr('{}.normalizeWeights'.format(skinCls), normVal)



    ## get skincluster as MFnSkinCluster
    ## get skincluster influence objects
    ## for influence objects
    ##      append ids and influence object paths to lists
    ## get weightList plug (vertices)
    ## get weights plug (influence objects)

    ## for vertices
    ##      setup remainder and empty largeVal
    ##      for influence objects
    ##          round value
    ##          if largest set largest
    ##          minus from reminder
    ##      add remainder to largest weight
    ##      for influence objects
    ##          set attr value
