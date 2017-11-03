import maya.cmds as cmds

from Jenks.scripts.rigModules import fileFunctions as fileFn

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
        cmds.deformerWeights(fileName, path='', deformer=skinCls, ex=1, wp=5, wt=0.00001)
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