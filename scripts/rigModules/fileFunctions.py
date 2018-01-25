import os
import json
import sys
import maya.cmds as cmds
import maya.mel as mel

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import apiFunctions as api
from Jenks.scripts.rigModules.suffixDictionary import suffix

reload(utils)

def getLatestVersion(assetName, path, location, new=False, name=None, suffix=None, prefix=None,
                     img=False, directory=False):
    if location == 'rig/Published':
        suffix = '.ma'
        name = assetName
    elif location == 'rig/WIP/guides':
        suffix = '.ma'
        name = 'guides'
    elif location == 'rig/WIP/skin':
        suffix = '.skin'
    elif location == 'rig/WIP/controlShapes':
        suffix = '.shape'
    elif location == 'model/Published':
        suffix = '.abc'
        name = assetName
    elif location == 'model/WIP':
        suffix = '.ma'
        name = assetName
    elif location == 'anim/Published':
        suffix = '.abc'
        name = assetName
    elif location == 'layout/Published':
        suffix = '.abc'
        name = assetName
    else:
        suffix = '.ma'
        name = assetName
    if img:
        suffix = '.jpg'
    if prefix:
        name = '{}_{}'.format(prefix, name)
    fileDirectory = '{}{}/{}/'.format(path, assetName, location)
    if not directory:
        ls = [f for f in os.listdir(fileDirectory) if os.path.isfile('{}/{}'.format(fileDirectory, f))]
        relevantFiles = []
        for each in sorted(ls):
            lsGeo = each.rsplit('_', 1 if not location == 'model/Published' else 2)[0]
            if lsGeo == name:
                relevantFiles.append(each)
    else:
        suffix = ''
        ls = [f for f in os.listdir(fileDirectory) if os.path.isdir('{}/{}'.format(fileDirectory, f))]
        relevantFiles = ls

    if new:
        if name:
            name += '_'
        if not relevantFiles:
            newFile = '{}{}v001{}'.format(fileDirectory, name, suffix)
        else:
            nameWithoutSuffix = relevantFiles[-1].rsplit('.')[0]
            latestNum = nameWithoutSuffix.rsplit('_', 1)[1].strip('v')
            newNum = str(int(latestNum)+1).zfill(3)

            newFile = '{}{}v{}{}'.format(fileDirectory, name, newNum, suffix)
    else:
        if not relevantFiles:
            return False
        else:
            newFile = '{}{}'.format(fileDirectory, relevantFiles[-1])
    return newFile

def newNameSpace(assetName):
    ns = '{}'.format(assetName)
    i = 1
    while cmds.namespace(ex=ns):
        i += 1
        ns = '{}{}'.format(assetName, str(i).zfill(2))
    return ns

def loadPlugin(nodeName, python=False):
    if python:
        fileType = '.py'
    else:
        if sys.platform == "linux" or sys.platform == "linux2":
           # linux
           fileType = '.so'
        elif sys.platform == "darwin":
           # MAC OS X
           fileType = '.bundle'
        elif sys.platform == "win32" or sys.platform == "win64":
           # Windows
           fileType = '.mll'
    loadedPlugins = cmds.pluginInfo(q=1, listPlugins=1)
    if nodeName in loadedPlugins:
        cmds.unloadPlugin('{}{}'.format(nodeName, fileType))
        cmds.flushUndo()
    pluginPath = '{}/Jenks/scripts/nodes'.format(getScriptDir())
    cmds.loadPlugin(r'{}/{}{}'.format(pluginPath, nodeName, fileType))
    mel.eval("refreshEditorTemplates; refreshAE;")

def loadAllPlugins():
    loadPlugin('mjStretchArray')
    loadPlugin('mjRivet')
    loadPlugin('mjSoftIK', True)


def getScriptDir():
    ## MIGHT NEED CHANGING - not sure if the path list will be
    ## consistant between pcs (or even restarts)
    homeDir = os.environ['HOME']
    if os.path.isfile('C:\\Docs\\readMe.txt'):
        ## on uni computers
        scriptPath = 'C:\\Docs\\maya\\scripts'
    elif os.path.isdir('{}\\maya'.format(homeDir)):
        ## on other computers
        scriptPath = '{}\\maya'.format(homeDir)
    else:
        scriptPath = sys.path[-1]
    return scriptPath

def getAssetDir():
    path = cmds.workspace(q=1, rd=1)
    return '{}assets/'.format(path)

def getSubAssetDir():
    assetNameSetup(None, False)
    assetName = getAssetName()
    path = cmds.workspace(q=1, rd=1)
    return '{}assets/{}/subAssets/'.format(path, assetName)

def getShotDir():
    path = cmds.workspace(q=1, rd=1)
    return '{}shots/'.format(path)

def getProjectName():
    path = cmds.workspace(q=1, rd=1)
    projName = path.rsplit('/', 2)[1]
    return projName

def newScene():
    if cmds.file(q=1, modified=1):
        t = 'Opening New Scene'
        m = 'This will override the current scene without saving. Save Now?'
        confirm = cmds.confirmDialog(t=t, m=m, b=['Yes', 'No', 'Cancel'], db='Yes',
                                     cb='Cancel', ds='Yes')
        if confirm == 'Yes':
            saveMayaFile()
        elif confirm == 'Cancel':
            return False
    f = cmds.file(new=1, force=1)
    return True

def abcExport(fileName, selection=True, frameRange=(1, 1), step=1.0):
    cmds.loadPlugin('AbcExport.so')
    if not frameRange == (1, 1):
        frameRange = (frameRange[0]-3, frameRange[1]+3)
    if selection:
        sel = cmds.ls(sl=True)
    else:
        a = cmds.ls(dag=1, v=1)
        b = cmds.ls(lights=1, cameras=1)
        sel = list(set(a)-set(b))
    args = '-f {0} -fr {1[0]} {1[1]} -uv -ws -wv -ef -wuvs -wc'.format(fileName, frameRange, sel)
    if not frameRange ==  (1, 1):
        args = '{} -s {}'.format(args, step)
    for each in sel:
        args = '{} -rt {}'.format(args, each)
    cmds.AbcExport(j=args)

def loadGuides(assetName=None, prompt=False, new=False, latest=True):
    loadMayaFile(assetName, typ='rig/WIP/guides', prompt=prompt, new=new, latest=latest)
    return True

def saveGuides(assetName=None, autoName=False, prompt=False):
    saveMayaFile(assetName, typ='rig/WIP/guides', prompt=prompt, autoName=autoName,
                 removeRefs=True)
    return True

def publishRig(assetName=None, autoName=True, prompt=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    removeReferences()
    cmds.setAttr('C_global_CTRL.visGeo', 1)
    cmds.setAttr('C_global_CTRL.visCtrls', 1)
    cmds.setAttr('C_global_CTRL.visSkel', 0)
    cmds.setAttr('C_global_CTRL.visMech', 0)
    cmds.setAttr('C_global_CTRL.mdGeo', 2)
    cmds.setAttr('C_global_CTRL.mdSkel', 2)
    cmds.select('_RIG__GRP')
    publishSnapshot(asset=assetName, typ='rig')
    saveMayaFile(assetName, typ='rig/Published', prompt=prompt, autoName=autoName,
                 selectionOnly=True)
    return True

def referenceRig(assetName=None, prompt=False, replace=False, refNd=None):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    path = getAssetDir()
    fileName = getLatestVersion(assetName, path, 'rig/Published')
    if not replace:
        cmds.file(fileName, r=1, ns=newNameSpace(assetName))
    else:
        cmds.file(fileName, lr=refNd)
    # print 'Referenced Rig: {}'.format(fileName)
    printToMaya('Referenced Rig: {}'.format(fileName))
    return True

def loadWipRig(assetName=None, latest=False, prompt=False):
    loadMayaFile(assetName, typ='rig/WIP', prompt=prompt, latest=latest)
    return True

def saveWipRig(assetName=None, autoName=False, prompt=False):
    saveMayaFile(assetName, typ='rig/WIP', prompt=prompt, autoName=autoName)
    return True

def loadRigScript(assetName=None, prompt=False, build=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    path = getAssetDir()
    fileName = '{}rigScripts/{}.py'.format(path, assetName)
    # print 'Loading rig script: {}'.format(fileName)
    printToMaya('Loading Rig Script: {}'.format(fileName))
    f = open(fileName, 'r')
    rigScriptTxt = f.read()
    f.close()
    cmds.ScriptEditor()
    gCommandExecuterTabs = mel.eval('$v = $gCommandExecuterTabs')
    tabLabels = cmds.tabLayout(gCommandExecuterTabs, q=1, tl=1)
    tabIDs = cmds.tabLayout(gCommandExecuterTabs, q=1, ca=1)
    create = True
    for i, each in enumerate(tabLabels, start=1):
        if '{}_rig'.format(assetName) == each:
            create = False
            cmds.tabLayout(gCommandExecuterTabs, e=1, sti=i)
            rigTab = i
    if create:
        mel.eval('buildNewExecuterTab -1  "{}_rig"  "python" 1'.format(assetName))
        numOfTabs = cmds.tabLayout(gCommandExecuterTabs, q=1, nch=1)
        cmds.tabLayout(gCommandExecuterTabs, e=1,  selectTabIndex=numOfTabs)
        rigTab = numOfTabs
    executer = mel.eval('$a=$gCommandExecuter;')[rigTab-1]
    cmds.cmdScrollFieldExecuter(executer, e=1, t=rigScriptTxt, exc=build, sla=1)


def loadGeo(assetName=None, group=None, prompt=False, abc=True):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    path = getAssetDir()
    fileName = getLatestVersion(assetName, path, 'model/Published')
    if abc:
        if group:
            cmds.AbcImport(fileName, mode='import', rpr=group)
        else:
            cmds.AbcImport(fileName, mode='import')
    else:
        nodes = cmds.file(fileName, i=1, dns=1, type='mayaAscii', rnn=1)
        mNodes = []
        for each in nodes:
            mNodes.append(api.getMObj(each))
        if group:
            for each in mNodes:
                lN, sN = api.getPath(each)
                if cmds.nodeType(lN) == 'transform':
                    cmds.parent(lN, group)
    # print 'Loaded geometry: {}'.format(fileName)
    printToMaya('Loaded Geometry: {}'.format(fileName))
    return True

def publishGeo(assetName=None, autoName=True, prompt=False, abc=True):
    if cmds.ls(sl=1) == list():
        cmds.warning('{}{}{}'.format('Nothing Selected.', ' Cancelling publish',
                                     ' - Select the asset geometry and try again'))
        return False
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    path = getAssetDir()
    publishSnapshot(asset=assetName, typ='model')
    if abc:
        if not autoName:
            fileFilter = fileDialogFilter([('Alembic Cache', '*.abc')])
            fileName = cmds.fileDialog2(dialogStyle=2, caption='Publish Geometry',
                                        fileMode=0, fileFilter=fileFilter,
                                        dir='{}{}/model/Published'.format(path, assetName))
            if fileName:
                fileName = fileName[0]
            else:
                return False
        else:
            fileName = getLatestVersion(assetName, path, 'model/Published', new=True)
        # removeReferences()
        importReferences()
        abcExport(fileName, selection=True, frameRange=(1, 1))
        # print 'Published Geometry: {}'.format(fileName)
        printToMaya('Published Geometry: {}'.format(fileName))
    else:
        saveMayaFile(assetName, typ='model/Published', autoName=autoName, removeRefs=True,
                     selectionOnly=True)
        # print 'Saved as Maya File.'
        # printToMaya('Published Geometry as Maya File: {}'.format(fileName))
    return True

def referenceGeo(assetName=None, prompt=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    path = getAssetDir()
    fileName = getLatestVersion(assetName, path, 'model/Published')
    cmds.file(fileName, r=1, ns=newNameSpace(assetName))
    # print 'Referenced geometry: {}'.format(fileName)
    printToMaya('Referenced Geometry: {}'.format(fileName))
    return True

def saveWipGeo(assetName=None, autoName=False, prompt=False):
    saveMayaFile(assetName, typ='model/WIP', prompt=prompt, autoName=autoName,
                 removeRefs=False)
    return True

def loadWipGeo(assetName=None, latest=False, prompt=False):
    loadMayaFile(assetName, typ='model/WIP', prompt=prompt, latest=latest, new=True)
    return True

def loadSubAssetGeo(subAssetName=None, group=None, prompt=False, abc=True):
    subAssetName = assetNameSetup(subAssetName, prompt, typ='subAsset')
    if not subAssetName:
        return False
    path = getSubAssetDir()
    fileName = getLatestVersion(subAssetName, path, 'model/Published')
    if abc:
        if group:
            cmds.AbcImport(fileName, mode='import', rpr=group)
        else:
            cmds.AbcImport(fileName, mode='import')
    else:
        nodes = cmds.file(fileName, i=1, dns=1, type='mayaAscii', rnn=1)
        if group:
            mNodes = []
            for each in nodes:
                mNodes.append(api.getMObj(each))
            for each in mNodes:
                lN, sN = api.getPath(each)
                if cmds.nodeType(lN) == 'transform':
                    cmds.parent(lN, group)
    # print 'Loaded SubAsset geometry: {}'.format(fileName)
    printToMaya('Loaded SubAsset Geometry: {}'.format(fileName))
    return True

def publishSubAssetGeo(subAssetName=None, autoName=True, prompt=False, abc=True):
    subAssetName = assetNameSetup(subAssetName, prompt, typ='subAsset')
    if not subAssetName:
        return False
    publishSnapshot(subAsset=subAssetName, typ='model')
    path = getSubAssetDir()
    if abc:
        if not autoName:
            fileFilter = fileDialogFilter([('Alembic Cache', '*.abc')])
            fileName = cmds.fileDialog2(dialogStyle=2, caption='Publish SubAsset Geometry',
                                        fileMode=0, fileFilter=fileFilter,
                                        dir='{}{}/model/Published'.format(path, subAssetName))
            if fileName:
                fileName = fileName[0]
            else:
                return False
        else:
            fileName = getLatestVersion(subAssetName, path, 'model/Published', new=True)
        removeReferences()
        abcExport(fileName, selection=True, frameRange=(1, 1))
        # print 'Published Geometry: {}'.format(fileName)
        printToMaya('Published SubAsset Geometry: {}'.format(fileName))
    # else:
    #     saveMayaFile(subAssetName, typ='model/Published', autoName=autoName, removeRefs=True,
    #                  selectionOnly=True)
    #     print 'Saved as Maya File.'
    # publishSnapshot(asset=assetName, typ='model')
    return True

def referenceSubAssetGeo(subAssetName=None, prompt=False):
    subAssetName = assetNameSetup(subAssetName, prompt, typ='subAsset')
    if not subAssetName:
        return False
    fileName = referenceFile(subAssetName, typ='subAsset', location='model/Published')
    printToMaya('Referenced SubAsset Geometry: {}'.format(fileName))
    return True


    # subAssetName = assetNameSetup(subAssetName, prompt, typ='subAsset')
    # if not subAssetName:
    #     return False
    # path = getSubAssetDir()
    # fileName = getLatestVersion(subAssetName, path, 'model/Published')
    # cmds.file(fileName, r=1, ns=newNameSpace(subAssetName))
    # # print 'Referenced geometry: {}'.format(fileName)
    # printToMaya('Referenced SubAsset Geometry: {}'.format(fileName))
    # return True

def saveSubAssetWipGeo(subAssetName=None, autoName=False, prompt=False):
    saveMayaFile(subAssetName, typ='model/WIP', prompt=prompt, autoName=autoName,
                 removeRefs=True, subAsset=True)
    return True

def loadSubAssetWipGeo(subAssetName=None, latest=False, prompt=False):
    loadMayaFile(subAssetName, typ='model/WIP', prompt=prompt, latest=latest, new=True,
                 subAsset=True)
    return True

def setupLookDevScene(assetName=None, prompt=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    geoGrp = utils.newNode('group', name='geometry', skipNum=True)
    loadGeo(assetName, geoGrp.name)
    print '## ADD A QUICK FUNCTION TO AVOID NAMING CONFLICTS FOR LOOKDEV MESH SET NAMES'
    geoSetName = 'geoSet_{}'.format(assetName)
    i = 1
    while cmds.objExists(geoSetName):
        i += 1
        geoSetName = '{}{}'.format(geoSetName, str(i).zfill(2))
    geo = cmds.listRelatives(geoGrp.name, c=1)
    setName = cmds.sets(geo, n=geoSetName)
    geoSetAttrs = {
        'aiMatte' : ('bool', None),
        'primaryVisibility' : ('bool', None),
        'aiSubdivIterations' : ('enum', '0:1:2:3:4:5:6:7'),
        'aiSubdivType' : ('enum', 'None:Catclark:Linear'),
    }
    for k, v in geoSetAttrs.iteritems():
        if not v[1]:
            cmds.addAttr(setName, longName=k, attributeType=v[0])
        else:
            cmds.addAttr(setName, longName=k, attributeType=v[0], enumName=v[1])

    subAssets = cmds.listRelatives(geoGrp.name, c=1)
    saGrps = cmds.ls('*_sa_*', typ='transform')
    for each in saGrps:
        if each in subAssets:
            if cmds.objExists(each):
                subAssetNameWithSuff = each[5:]
                for suff in suffix.values():
                    subAssetName = subAssetNameWithSuff.rpartition(suff)[0]
                    if not subAssetName == '':
                        break
                refNds = referenceSubAssetLookDev(subAssetName)
                saGeo = cmds.listRelatives(refNds, c=1, ad=1, typ='transform')
                refGrp = cmds.listRelatives(saGeo, p=1)
                cmds.sets(saGeo, e=1, include=setName)
                cmds.parent(refGrp, geoGrp.name)
                cmds.delete(each)
                mergeSubAssetAlembic(assetName)
                cmds.select(refGrp)
                importReferences()
                cmds.namespace(rm=subAssetName, mnr=1)
    cmds.select(cl=1)
    printToMaya('LookDev Scene setup complete for {}.'.format(assetName))




def setupSubAssetLookDevScene(subAssetName=None, prompt=False):
    subAssetName = assetNameSetup(subAssetName, prompt, typ='subAsset')
    if not subAssetName:
        return False
    # geoGrp = utils.newNode('group', name=subAssetName, skipNum=True)
    loadSubAssetGeo(subAssetName)


def saveWipLookDev(assetName=None, autoName=False, prompt=False):
    saveMayaFile(assetName, typ='lookDev/WIP', prompt=prompt, autoName=autoName,
                 removeRefs=True)
    return True

def loadWipLookDev(assetName=None, latest=False, prompt=False):
    loadMayaFile(assetName, typ='lookDev/WIP', prompt=prompt, latest=latest, new=True)
    return True

def saveSubAssetWipLookDev(subAssetName=None, autoName=False, prompt=False):
    saveMayaFile(subAssetName, typ='lookDev/WIP', prompt=prompt, autoName=autoName,
                 removeRefs=True, subAsset=True)
    return True

def loadSubAssetWipLookDev(subAssetName=None, latest=False, prompt=False):
    loadMayaFile(subAssetName, typ='lookDev/WIP', prompt=prompt, latest=latest, new=True,
                 subAsset=True)
    return True

def publishLookDev(assetName=None, autoName=True, prompt=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    publishSnapshot(asset=assetName, typ='lookDev')
    setsToSave = []
    for each in cmds.listRelatives('C_geometry_GRP', c=1, ad=1):
        sets = cmds.listSets(o=each)
        if sets:
            setsToSave.extend(cmds.listSets(o=each))
    cmds.select(setsToSave, add=1, noExpand=1)
    saveMayaFile(assetName, typ='lookDev/Published', prompt=prompt, autoName=autoName,
                 removeRefs=True, selectionOnly=True)
    return True

def publishSubAssetLookDev(subAssetName=None, autoName=True, prompt=False):
    subAssetName = assetNameSetup(subAssetName, prompt, typ='subAsset')
    if not subAssetName:
        return False
    geo = cmds.listRelatives('C_sa_{}_GRP'.format(subAssetName), c=1)
    cmds.select(geo)
    saveMayaFile(subAssetName, typ='lookDev/Published', prompt=prompt, autoName=autoName,
                 removeRefs=True, selectionOnly=True, subAsset=True)
    return True

def referenceLookDev(assetName=None, prompt=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    path = getAssetDir()
    fileName = getLatestVersion(assetName, path, 'lookDev/Published')
    cmds.file(fileName, r=1, ns=newNameSpace(assetName))
    # print 'Referenced LookDev: {}'.format(fileName)
    printToMaya('Referenced LookDev: {}'.format(fileName))
    return True

def referenceSubAssetLookDev(subAssetName=None, prompt=False):
    subAssetName = assetNameSetup(subAssetName, prompt, typ='subAsset')
    if not subAssetName:
        return False
    path = getSubAssetDir()
    fileName = getLatestVersion(subAssetName, path, 'lookDev/Published')
    nds = cmds.file(fileName, r=1, ns=newNameSpace(subAssetName), rnn=1)
    # print 'Referenced SubAsset LookDev: {}'.format(fileName)
    printToMaya('Referenced SubAsset LookDev: {}'.format(fileName))
    return nds

def mergeSubAssetAlembic(assetName=None, latest=True, prompt=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    path = getAssetDir()
    if latest:
        fileName = getLatestVersion(assetName, path, 'model/Published')
    else:
        fileFilter = fileDialogFilter(['Alembic Cache', '*.abc'])
        fileName = cmds.fileDialog2(dialogStyle=2,
                                    caption='Merge SubAsset Alembic',
                                    fileMode=1,
                                    fileFilter=fileFilter,
                                    dir='{}{}/model/Published'.format(path, assetName))
        fileName = fileName[0] if fileName else False
    mel.eval('AbcImport -mode import -connect "/" "{}"'.format(fileName))

def saveWipLayout(shotName=None, autoName=False, prompt=False):
    saveMayaFile(shotName, typ='layout/WIP', prompt=prompt, autoName=autoName,
                 removeRefs=False, shot=True)
    return True

def loadWipLayout(shotName=None, latest=False, prompt=False):
    loadMayaFile(shotName, typ='layout/WIP', prompt=prompt, latest=latest, new=True, shot=True)
    return True

def publishLayout(shotName=None, autoName=True, prompt=False):
    if not cmds.objExists('renderCam'):
        cmds.warning('Cannot publish, no renderCam exists in the scene.')
        return False
    if not cmds.objExists('C_layout{}'.format(suffix['group'])):
        cmds.group(cmds.ls(sl=1), n='C_layout{}'.format(suffix['group']))
    shotName = assetNameSetup(shotName, prompt, typ='shot')
    if not shotName:
        return False
    path = getShotDir()
    if not autoName:
        fileFilter = fileDialogFilter([('Alembic Cache', '*.abc')])
        fileName = cmds.fileDialog2(dialogStyle=2, caption='Publish Shot Layout',
                                        fileMode=0, fileFilter=fileFilter,
                                        dir='{}{}/layout/Published'.format(path, shotName))
        if fileName:
            fileName = fileName[0]
        else:
            return False
    else:
        fileName = getLatestVersion(shotName, path, 'layout/Published', new=True)
    frameRange = (cmds.playbackOptions(q=1, min=1), cmds.playbackOptions(q=1, max=1))
    ## remove img plane
    plane = cmds.imagePlane('renderCam', q=1, n=1)
    cmds.delete(plane)
    ## duplicate cam
    oldCam = cmds.rename('renderCam', 'oldRenderCam')
    newCam = cmds.duplicate(oldCam, n='renderCam')[0]
    if cmds.listRelatives(newCam, p=1):
        cmds.parent(newCam, w=1)
    ## unlock attrs
    utils.lockAttr(newCam, attr=['t', 'r'], hide=False, unlock=True)
    ## parent constraint
    constr = cmds.parentConstraint(oldCam, newCam)
    scConstr = cmds.scaleConstraint(oldCam, newCam)
    ## bake camera
    cmds.bakeResults(newCam, at=['t', 'r'], dic=True, mr=True, pok=True, sm=False, t=frameRange)
    ## del constraints
    cmds.delete(constr, scConstr)

    cmds.select(['renderCam', 'C_layout{}'.format(suffix['group'])])
    abcExport(fileName, selection=True, frameRange=frameRange)
    printToMaya('Published Layout: {}'.format(fileName))

def referenceLayout(shotName=None, prompt=False, replace=False, refNd=None):
    shotName = assetNameSetup(shotName, prompt, typ='shot')
    fileName = referenceFile(shotName, typ='shot', location='layout/Published',
                             replace=replace, refNd=refNd)
    printToMaya('Referenced Shot Layout: {}'.format(fileName))

def createAnimationImagePlane(shotName=None, cam='renderCam'):
    shotName = assetNameSetup(shotName, False, typ='shot')
    if not shotName:
        return False
    path = getShotDir()
    versionFolder = getLatestVersion(shotName, path, 'plates/undistort/4608', directory=True)
    img = '{}/{}'.format(versionFolder, os.listdir(versionFolder)[0])
    if img:
        if cmds.objExists('{}:{}'.format(shotName, cam)):
            camName = '{}:{}'.format(shotName, cam)
        elif cmds.objExists(cam):
            camName = cam
        elif cmds.objExists('*{}'.format(cam)):
            camName = '*:{}'.format(cam)
        else:
            cmds.warning('Camera does not exist or is not valid.' )
            return False
        imgPlane = cmds.imagePlane(fileName=img, c=camName,
                                   name='footageImagePlane', sia=False)[0]
        cmds.setAttr('{}.useFrameExtension'.format(imgPlane), 1)
        printToMaya('Created Image Plane: {}'.format(img))
    else:
        return False

def saveWipAnimation(shotName=None, autoName=False, prompt=False):
    saveMayaFile(shotName, typ='anim/WIP', prompt=prompt, autoName=autoName,
                 removeRefs=False, shot=True)
    return True

def loadWipAnimation(shotName=None, latest=False, prompt=False):
    loadMayaFile(shotName, typ='anim/WIP', prompt=prompt, latest=latest, new=True, shot=True)
    return True

def publishAnimation(shotName=None, autoName=True, prompt=False):
    rigs = cmds.ls('*:_RIG__GRP')
    cmds.select(cl=True)
    for each in rigs:
        rigChilds = cmds.listRelatives(each, c=1, s=0)
        for child in rigChilds:
            if ':C_geometry_GRP' in child:
                cmds.select(child, add=1)
                continue
    shotName = assetNameSetup(shotName, prompt, typ='shot')
    if not shotName:
        return False
    path = getShotDir()
    if not autoName:
        fileFilter = fileDialogFilter([('Alembic Cache', '*.abc')])
        fileName = cmds.fileDialog2(dialogStyle=2, caption='Publish Animation',
                                    fileMode=0, fileFilter=fileFilter,
                                    dir='{}{}/anim/Published'.format(path, shotName))
        if fileName:
            fileName = fileName[0]
        else:
            return False
    else:
        fileName = getLatestVersion(shotName, path, 'anim/Published', new=True)
    # playBackSlider = mel.eval('$tmpVar=$gPlayBackSlider')
    # frameRange = cmds.timeControl(playBackSlider, q=1, ra=1)
    publishSnapshot(shot=shotName, typ='anim')
    frameRange = (cmds.playbackOptions(q=1, min=1), cmds.playbackOptions(q=1, max=1))
    abcExport(fileName, selection=True, frameRange=frameRange)
    # print 'Published Animation: {}'.format(fileName)
    printToMaya('Published Animation: {}'.format(fileName))

def mergeAnimationAlembic(shotName=None, latest=True, prompt=False):
    shotName = assetNameSetup(shotName, prompt, typ='shot')
    if not shotName:
        return False
    path = getShotDir()
    if latest:
        fileName = getLatestVersion(shotName, path, 'anim/Published')
    else:
        fileFilter = fileDialogFilter([('Alembic Cache', '*.abc')])
        fileName = cmds.fileDialog2(dialogStyle=2,
                                    caption='Merge Published Animation',
                                    fileMode=1,
                                    fileFilter=fileFilter,
                                    dir='{}{}/anim/Published'.format(path, shotName))
        fileName = fileName[0] if fileName else False
    mel.eval('AbcImport -mode import -connect "/" "{}"'.format(fileName))

def saveWipLighting(shotName=None, autoName=False, prompt=False):
    saveMayaFile(shotName, typ='lighting/WIP', prompt=prompt, autoName=autoName,
                 removeRefs=False, shot=True, prefix=getProjectName())
    return True

def loadWipLighting(shotName=None, latest=False, prompt=False):
    loadMayaFile(shotName, typ='lighting/WIP', prompt=prompt, latest=latest, new=True, shot=True,
                 prefix=getProjectName())
    return True

def publishLighting(shotName=None, autoName=True, prompt=False):
    publishSnapshot(shot=shotName, typ='lighting')
    saveMayaFile(shotName, typ='lighting/Published', prompt=prompt, autoName=autoName,
                 removeRefs=False, shot=True, prefix=getProjectName())
    return True

def setupSceneForRender(shotName=None, latest=True, prompt=False):
    newScene()
    shotName = assetNameSetup(shotName, prompt, typ='shot')
    if not shotName:
        return False
    path = getShotDir()
    fileName = getLatestVersion(shotName, path, 'lighting/Published')
    cmds.file(fileName, r=1, ns=newNameSpace(shotName))
    # print 'Referenced Lighting: {}'.format(fileName)
    printToMaya('Referenced Lighting: {}'.format(fileName))
    print '## DO OTHER STUFF FOR SETTING UP THE RENDER - aov\'s, render settings, etc.'


def publishSnapshot(asset=None, shot=None, subAsset=None, typ=''):
    if asset:
        path = getAssetDir()
        fileName = getLatestVersion(asset, path, typ, new=True, img=True)
    elif shot:
        path = getShotDir()
        fileName = getLatestVersion(shot, path, typ, new=True, img=True)
    elif subAsset:
        path = getSubAssetDir()
        fileName = getLatestVersion(subAsset, path, typ, new=True, img=True)
    else:
        return False

    oldSel = cmds.ls(sl=1, l=1)
    cmds.select(cl=True)
    ssao = cmds.getAttr('hardwareRenderingGlobals.ssaoEnable')
    multiSample = cmds.getAttr('hardwareRenderingGlobals.multiSampleEnable')
    cmds.setAttr('hardwareRenderingGlobals.ssaoEnable', 1)
    cmds.setAttr('hardwareRenderingGlobals.multiSampleEnable', 1)

    cmds.playblast(format='image', cf=fileName,
                   fr=1, percent=100, compression='jpg', quality=100, widthHeight=(1920, 1080),
                   fp=False, orn=False, v=False)

    print 'Snapshot image saved to: {}'.format(fileName)

    cmds.setAttr('hardwareRenderingGlobals.ssaoEnable', ssao)
    cmds.setAttr('hardwareRenderingGlobals.multiSampleEnable', multiSample)

    cmds.select(oldSel)

    return True


def removeReferences():
    refs = cmds.ls(typ='reference')
    if refs:
        for each in refs:
            cmds.file(rr=1, rfn=each)

def importReferences(sel=True):
    refs = []
    for each in cmds.ls(sl=sel):
        if cmds.referenceQuery(each, inr=1) and cmds.referenceQuery(each, rfn=1) not in refs:
            refs.append(cmds.referenceQuery(each, rfn=1))
    oldSel = cmds.ls(sl=1)
    if refs:
        for each in refs:
            if cmds.objExists(each):
                refFile = cmds.referenceQuery(each, f=True)
                cmds.file(refFile, importReference=True)
    if sel:
        cmds.select(oldSel)

def fileDialogFilter(fileFormats):
    fileFilter = ''
    fileFormats.append(('All', '*.*'))
    for i, x in enumerate(fileFormats):
        seperator = ';;' if i > 0 else ''
        fileFilter += '{0}{1[0]} Files ({1[1]})'.format(seperator, x)
    return fileFilter

def saveJson(data, defaultDir=None, caption='Save Json', fileFormats=[('JSON', '*.json')],
             fileOverride=False):
    if not fileOverride:
        fileFilter = fileDialogFilter(fileFormats)
        fileName = cmds.fileDialog2(dialogStyle=2,
                                    caption=caption,
                                    fileMode=0,
                                    fileFilter=fileFilter,
                                    dir=defaultDir)
        if fileName:
            fileName = fileName[0]
        else:
            return False
    else:
        if type(fileOverride) == list():
            fileName = fileOverride[0]
        else:
            fileName = fileOverride
    with open(fileName, 'w') as f:
        json.dump(data, f, indent=4)
    # print 'File Saved to: {}'.format(fileName)
    printToMaya('File Saved: {}'.format(fileName))
    return True

def loadJson(defaultDir=None, caption='Load Json', fileFormats=[('JSON', '*.json')],
             fileOverride=False):
    if not fileOverride:
        fileFilter = fileDialogFilter(fileFormats)
        fileName = cmds.fileDialog2(dialogStyle=1,
                                    caption=caption,
                                    fileMode=1,
                                    fileFilter=fileFilter,
                                    dir=defaultDir)
        if fileName:
            fileName = fileName[0]
        else:
            return False
    else:
        fileName = fileOverride
    with open(fileName, 'r') as f:
        data = json.load(f)
    return data

def createNewDirs(folder, directory, subFolder=None):
    if not os.path.isdir('{}/{}'.format(directory, folder)):
        os.mkdir('{}/{}'.format(directory, folder))
    if type(subFolder) == type(list()):
        for each in subFolder:
            createNewDirs(each, '{}/{}'.format(directory, folder))
    elif type(subFolder) == type(dict()):
        for f, sf in subFolder.iteritems():
            createNewDirs(f, '{}/{}'.format(directory, folder), sf)

def createNewPipelineAsset(assetName=None, prompt=False):
    assetName = assetNameSetup(assetName, prompt, textPrompt=True)
    if not assetName:
        return False
    setAssetName(assetName)
    assetDir = getAssetDir()
    newAssetDir = '{}{}'.format(assetDir, assetName)
    if os.path.isdir(newAssetDir):
        # print 'Asset directory already exists.'
        printToMaya('Asset directory already exists.')
        return False
    else:
        os.mkdir(newAssetDir)
        folderList = {
            'lookDev' : [
                'Published',
                'WIP',
            ],
            'model' : [
                'Published',
                'WIP',
            ],
            'subAssets' : [],
            'rig' : {
                'Published' : [],
                'WIP' : [
                    'controlShapes',
                    'guides',
                    'skin',
                ],
            },
            'texture' : {
                'Published' : [
                    'bump',
                    'diff',
                    'disp',
                    'masks',
                    'spc',
                    'spcRough',
                    'sss',
                ],
                'WIP' : [],
            },
        }

        for k, v in folderList.iteritems():
            createNewDirs(k, newAssetDir, v)
        # print 'Created Asset directories: {}'.format(newAssetDir)
        printToMaya('Created Asset Directories: {}'.format(newAssetDir))

def createNewPipelineSubAsset(subAssetName=None, prompt=False):
    subAssetName = assetNameSetup(subAssetName, prompt, textPrompt=True, typ='subAsset')
    if not subAssetName:
        return False
    setSubAssetName(subAssetName)
    subAssetDir = getSubAssetDir()
    newSubAssetDir = '{}{}'.format(subAssetDir, subAssetName)
    if os.path.isdir(newSubAssetDir):
        # print 'SubAsset directory already exists.'
        printToMaya('SubAsset directory already exists.')
        return False
    else:
        os.mkdir(newSubAssetDir)
        folderList = {
            'model' : [
                'Published',
                'WIP',
            ],
            'texture' : {
                'Published' : [
                    'bump',
                    'diff',
                    'disp',
                    'masks',
                    'spc',
                    'spcRough',
                    'sss',
                ],
                'WIP' : [],
            },
            'lookDev' : [
                'Published',
                'WIP',
            ],
        }

        for k, v in folderList.iteritems():
            createNewDirs(k, newSubAssetDir, v)
        # print 'Created SubAsset directories: {}'.format(newSubAssetDir)
        printToMaya('Created SubAsset Directories: {}'.format(newSubAssetDir))

def createNewPipelineShot(shotName=None, prompt=False):
    shotName = assetNameSetup(shotName, prompt, textPrompt=True, typ='shot')
    if not shotName:
        return False
    setShotName(shotName)
    shotDir = getShotDir()
    newShotDir = '{}{}'.format(shotDir, shotName)
    if os.path.isdir(newShotDir):
        # print 'Shot directory already exists.'
        printToMaya('Shot directory already exists.')
        return False
    else:
        os.mkdir(newShotDir)
        folderList = {
            'anim' : [
                'Published',
                'WIP',
                'Playblasts',
            ],
            'layout' : [
                'Published',
                'WIP',
            ],
            'lighting' : [
                'Published',
                'WIP',
            ],
            'nuke' : [],
            'plates' : {
                'misc' : [
                    '4608',
                    '1080',
                ],
                'prep' : [
                    '4608',
                    '1080',
                ],
                'raw' : [
                    '4608',
                    '1080',
                ],
                'retime' : [
                    '4608',
                    '1080',
                ],
                'roto' : [
                    '4608',
                    '1080',
                ],
                'undistort' : [
                    '4608',
                    '1080',
                ],
            },
            'renders' : [],
        }

        for k, v in folderList.iteritems():
            createNewDirs(k, newShotDir, v)
        # print 'Created Shot directories: {}'.format(newShotDir)
        printToMaya('Created Shot Directories: {}'.format(newShotDir))



def loadMayaFile(assetName='', typ='', prompt=False, new=False, latest=True,
                 shot=False, subAsset=False, prefix=None):
    if shot:
        directory = getShotDir()
        assetTyp = 'shot'
    elif subAsset:
        directory = getSubAssetDir()
        assetTyp = 'subAsset'
    else:
        directory = getAssetDir()
        assetTyp = 'asset'

    assetName = assetNameSetup(assetName, prompt, typ=assetTyp)
    if not assetName:
        return False
    subDir = '{}{}/{}/'.format(directory, assetName, typ)
    if not os.path.isdir(subDir):
        print '{} asset does not exist.'.format(assetName)
        return False
    if latest:
        fileName = getLatestVersion(assetName, directory, typ, prefix=prefix)
    else:
        fileFilter = fileDialogFilter([('Maya Ascii', '*.ma')])
        fileName = cmds.fileDialog2(dialogStyle=2,
                                    caption='Load {}'.format(typ),
                                    fileMode=1,
                                    fileFilter=fileFilter,
                                    dir=subDir)
        fileName = fileName[0] if fileName else False
    if fileName:
        if new:
            newScene()
            cmds.file(fileName, open=1, force=1)
        else:
            cmds.file(fileName, i=1, dns=1, type='mayaAscii')
        # print 'Opened File: {}'.format(fileName)
        printToMaya('Opened File: {}'.format(fileName))
        return True
    return False

def saveMayaFile(assetName='', typ='', prompt=False, autoName=False, removeRefs=False,
                 selectionOnly=False, shot=False, subAsset=False, prefix=None):
    if subAsset:
        directory = getSubAssetDir()
        assetTyp = 'subAsset'
    elif shot:
        directory = getShotDir()
        assetTyp = 'shot'
    else:
        directory = getAssetDir()
        assetTyp = 'asset'
    assetName = assetNameSetup(assetName, prompt, typ=assetTyp)
    if not assetName:
        return False

    subDir = '{}{}/{}/'.format(directory, assetName, typ)
    if autoName:
        fileName = getLatestVersion(assetName, directory, typ, new=1, prefix=prefix)
    else:
        fileFilter = fileDialogFilter([('Maya Ascii', '*.ma')])
        fileName = cmds.fileDialog2(dialogStyle=2,
                                    caption='Save {}'.format(typ.capitalize()),
                                    fileMode=0,
                                    fileFilter=fileFilter,
                                    dir=subDir)
        fileName = fileName[0] if fileName else False
    if fileName:
        if removeRefs:
            removeReferences()
        if selectionOnly:
            cmds.file(fileName, exportSelected=True, type='mayaAscii')
        else:
            cmds.file(rename=fileName)
            cmds.file(save=True, type='mayaAscii')
        # print 'Saved File: {}'.format(fileName)
        printToMaya('Saved File: {}'.format(fileName))

def referenceFile(assetName, typ='', location='', replace=False, refNd=None):
    if not assetName:
        return False
    if typ == 'subAsset':
        path = getSubAssetDir()
        # location = 'subAsset'
    elif typ == 'shot':
        path = getShotDir()
    else:
        path = getAssetDir()
    fileName = getLatestVersion(assetName, path, location)
    if not replace:
        cmds.file(fileName, r=1, ns=newNameSpace(assetName))
    else:
        cmds.file(fileName, lr=refNd)
    return fileName

def treeAssetNamePrompt(typ='asset'):
    if cmds.window('{}NamePrompt'.format(typ), exists=True):
        cmds.deleteUI('{}NamePrompt'.format(typ), window=True)
    window = cmds.window('{}NamePrompt'.format(typ), title='Set {} Name'.format(typ.capitalize()),
                         width=200)
    form = cmds.formLayout()
    treeLister = cmds.treeLister(rc='fileFn.treeAssetNamePrompt("{}")'.format(typ))
    btnCommand = 'fileFn.createNewPipeline{}{}(prompt=True) \nfileFn.treeAssetNamePrompt("{}")'.format(typ.capitalize()[0], typ[1:], typ)
    btn = cmds.button(label='Create New', command=btnCommand)
    cmds.formLayout(form, e=1, af=((treeLister, 'top', 0),
                                   (treeLister, 'left', 0),
                                   (treeLister, 'bottom', 30),
                                   (treeLister, 'right', 0),
                                   (btn, 'bottom', 10),
                                   (btn, 'left', 10)))
    cmds.showWindow(window)

    if typ == 'shot':
        directory = getShotDir()
        icon = 'Camera.png'
    elif typ == 'asset':
        directory = getAssetDir()
        icon = 'alignOnMin.png'
    elif typ == 'subAsset':
        directory = getSubAssetDir()
        icon = 'subdivSphere.png'
    if not os.path.isdir(directory):
        return False
    ls = [f for f in os.listdir(directory) if os.path.isdir('{}/{}'.format(directory, f))]
    if 'rigScripts' in ls:
        ls.remove('rigScripts')

    for each in ls:
        # command = 'fileFn.assetNamePromptCommand("{}", "{}")'.format(each, window)
        command = 'fileFn.set{}{}Name("{}") \ncmds.window("{}", e=1, vis=False)'.format(typ.capitalize()[0], typ[1:], each, window)
        cmds.treeLister(treeLister, e=1, add=[(each, icon, command)])

def textAssetNamePrompt(title='Asset'):
    result = cmds.promptDialog(title='{} Name'.format(title),
                               message='{} Name:'.format(title),
                               button=['OK', 'Cancel'],
                               defaultButton='OK',
                               cancelButton='Cancel',
                               dismissString='Cancel')
    if result == 'OK':
        assetName = cmds.promptDialog(query=True, text=True)
    else:
        assetName = None
    return assetName

def setAssetName(assetName=None):
    if not assetName:
        # assetName = assetNamePrompt()
        treeAssetNamePrompt()
    if assetName:
        mel.eval('putenv "assetName" {}'.format(assetName))
        printToMaya('Asset Set To: {}'.format(assetName))

def getAssetName(dialog=False):
    name = mel.eval('getenv "assetName"')
    if dialog:
        cmds.confirmDialog(m='Current Asset: {}'.format(name), button=['Ok'])
    return name

def setSubAssetName(subAssetName=None):
    assetName = assetNameSetup(None, False)
    if not assetName:
        return False
    setAssetName(assetName)
    if not subAssetName:
        treeAssetNamePrompt(typ='subAsset')
    if subAssetName:
        mel.eval('putenv "subAssetName" {}'.format(subAssetName))
        printToMaya('SubAsset Set To: {}'.format(subAssetName))

def getSubAssetName(dialog=False):
    assetName = assetNameSetup(None, False)
    if not assetName:
        return False
    setAssetName(assetName)
    name = mel.eval('getenv "subAssetName"')
    if dialog:
        cmds.confirmDialog(m='Current SubAsset: {}'.format(name), button=['Ok'])
    return name

def setShotName(shotName=None):
    if not shotName:
        treeAssetNamePrompt(typ='shot')
    if shotName:
        mel.eval('putenv "shotName" {}'.format(shotName))
        printToMaya('Shot Set To: {}'.format(shotName))

def getShotName(dialog=False):
    name = mel.eval('getenv "shotName"')
    if dialog:
        cmds.confirmDialog(m='Current Shot: {}'.format(name), button=['Ok'])
    return name

def assetNameSetup(assetName, prompt, textPrompt=False, typ='asset'):
    if prompt:
        if textPrompt:
            assetName = textAssetNamePrompt(typ.capitalize())
        else:
            treeAssetNamePrompt(typ)
    if not assetName:
        if typ == 'asset':
            assetName = getAssetName()
        elif typ == 'shot':
            assetName = getShotName()
        elif typ == 'subAsset':
            assetName = getSubAssetName()
    if not assetName:
        assetName = treeAssetNamePrompt(typ)
    if not assetName:
        # print 'Asset Name not specified.'
        printToMaya('Asset Name not specified.')
    return assetName

def reloadReferences():
    assets, refNd = utils.getAssetsInScene()
    for i, each in enumerate(assets):
        referenceRig(each, replace=True, refNd=refNd[i])
    layouts, refNd = utils.getAssetsInScene('layout/Published')
    for i, each in enumerate(layouts):
        referenceFile(each, typ='shot', location='layout/Published', replace=True, refNd=refNd[i])
    subAssets, refNd = utils.getAssetsInScene('subAssets')
    for i, each in enumerate(subAssets):
        referenceFile(each, typ='subAsset', location='model/Published', replace=True, refNd=refNd[i])

def printToMaya(msg):
    msg = '{}\n'.format(msg)
    sys.stdout.write(msg)