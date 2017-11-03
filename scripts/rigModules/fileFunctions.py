import os
import json
import sys
import maya.cmds as cmds
import maya.mel as mel

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import apiFunctions as api
from Jenks.scripts.rigModules.suffixDictionary import suffix

def getLatestVersion(assetName, path, location, new=False, name=None, suffix=None):
    if location == 'rig/Published':
        suffix = 'ma'
        name = assetName
    elif location == 'rig/WIP/guides':
        suffix = 'ma'
        name = 'guides'
    elif location == 'rig/WIP/skin':
        suffix = 'skin'
    elif location == 'rig/WIP/controlShapes':
        suffix = 'shape'
    elif location == 'model/Published':
        suffix = 'abc'
        name = assetName
    elif location == 'model/WIP':
        suffix = 'ma'
        name = assetName
    elif location == 'anim/Published':
        suffix = 'abc'
        name = assetName
    else:
        suffix = 'ma'
        name = assetName
    fileDirectory = '{}{}/{}/'.format(path, assetName, location)
    # ls = os.listdir(fileDirectory)
    ls = [f for f in os.listdir(fileDirectory) if os.path.isfile('{}/{}'.format(fileDirectory, f))]
    relevantFiles = []
    for each in sorted(ls):
        lsGeo = each.rsplit('_', 1 if not location == 'model/Published' else 2)[0]
        if lsGeo == name:
            relevantFiles.append(each)
    if new:
        if not relevantFiles:
            newFile = '{}{}_v001.{}'.format(fileDirectory, name, suffix)
        else:
            nameWithoutSuffix = relevantFiles[-1].rsplit('.')[0]
            latestNum = nameWithoutSuffix.rsplit('_', 1)[1].strip('v')
            newNum = str(int(latestNum)+1).zfill(3)

            newFile = '{}{}_v{}.{}'.format(fileDirectory, name, newNum, suffix)
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
    if os.path.isfile('C:\\Docs\\readMe.txt'):
        ## on uni computers
        scriptPath = 'C:\\Docs\\maya\\scripts'
    else:
        scriptPath = sys.path[-1]
    return scriptPath

def getAssetDir():
    path = cmds.workspace(q=1, rd=1)
    return '{}assets/'.format(path)

def getShotDir():
    path = cmds.workspace(q=1, rd=1)
    return '{}shots/'.format(path)

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
    removeReferences()
    cmds.select('_RIG__GRP')
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
    print 'Referenced Rig: {}'.format(fileName)
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
    print 'Loading rig script: {}'.format(fileName)
    f = open(fileName, 'r')
    rigScriptTxt = f.read()
    f.close()
    cmds.ScriptEditor()
    gCommandExecuterTabs = mel.eval('$v = $gCommandExecuterTabs')
    tabLabels = cmds.tabLayout(gCommandExecuterTabs, q=1, tl=1)
    tabIDs = cmds.tabLayout(gCommandExecuterTabs, q=1, ca=1)
    create = True
    for i, each in enumerate(tabLabels):
        if '{}_rig'.format(assetName) == each:
            create = False
            cmds.tabLayout(gCommandExecuterTabs, e=1, sti=i+1)
    if create:
        mel.eval('buildNewExecuterTab -1  "{}_rig"  "python" 1'.format(assetName))
    executer = mel.eval('$a=$gCommandExecuter;')[-1]
    cmds.cmdScrollFieldExecuter(executer, e=1, t=rigScriptTxt, exc=build, sla=1)
    numOfTabs = cmds.tabLayout(gCommandExecuterTabs, q=1, nch=1)
    cmds.tabLayout(gCommandExecuterTabs, e=1, selectTabIndex=numOfTabs)


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
    print 'Loaded geometry: {}'.format(fileName)
    return True

def publishGeo(assetName=None, autoName=True, prompt=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    path = getAssetDir()
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
    removeReferences()
    abcExport(fileName, selection=True, frameRange=(1, 1))
    print 'Published Geometry: {}'.format(fileName)
    return True

def referenceGeo(assetName=None, prompt=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    path = getAssetDir()
    fileName = getLatestVersion(assetName, path, 'model/Published')
    cmds.file(fileName, r=1, ns=newNameSpace(assetName))
    print 'Referenced geometry: {}'.format(fileName)
    return True

def saveWipGeo(assetName=None, autoName=False, prompt=False):
    saveMayaFile(assetName, typ='model/WIP', prompt=prompt, autoName=autoName,
                 removeRefs=True)
    return True

def loadWipGeo(assetName=None, latest=False, prompt=False):
    loadMayaFile(assetName, typ='model/WIP', prompt=prompt, latest=latest, new=True)
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


    # cmds.addAttr('geoSet_Name_of_Asset', longName = 'aiMatte', attributeType = "bool", )
    # cmds.addAttr('geoSet_Name_of_Asset', longName = 'primaryVisibility', attributeType = "bool" )
#     cmds.addAttr('geoSet_Name_of_Asset', longName = 'aiSubdivType', attributeType = "enum", enumName = "0 :1 ")
# cmds.addAttr('geoSet_Name_of_Asset', longName = 'aiSubdivIterations', attributeType = "enum", enumName = "0 :1 : 2 : 3")


def saveWipLookDev(assetName=None, autoName=False, prompt=False):
    saveMayaFile(assetName, typ='lookDev/WIP', prompt=prompt, autoName=autoName,
                 removeRefs=True)
    return True

def loadWipLookDev(assetName=None, latest=False, prompt=False):
    loadMayaFile(assetName, typ='lookDev/WIP', prompt=prompt, latest=latest, new=True)
    return True

def publishLookDev(assetName=None, autoName=True, prompt=False):
    setsToSave = []
    for each in cmds.listRelatives('C_geometry_GRP', c=1):
        setsToSave.extend(cmds.listSets(o=each))
    cmds.select(setsToSave, add=1, noExpand=1)
    saveMayaFile(assetName, typ='lookDev/Published', prompt=prompt, autoName=autoName,
                 removeRefs=True, selectionOnly=True)
    return True

def referenceLookDev(assetName=None, prompt=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    path = getAssetDir()
    fileName = getLatestVersion(assetName, path, 'lookDev/Published')
    cmds.file(fileName, r=1, ns=newNameSpace(assetName))
    print 'Referenced LookDev: {}'.format(fileName)
    return True

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
    frameRange = (cmds.playbackOptions(q=1, min=1), cmds.playbackOptions(q=1, max=1))
    abcExport(fileName, selection=True, frameRange=frameRange)
    print 'Published Animation: {}'.format(fileName)

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
                 removeRefs=False, shot=True)
    return True

def loadWipLighting(shotName=None, latest=False, prompt=False):
    loadMayaFile(shotName, typ='lighting/WIP', prompt=prompt, latest=latest, new=True, shot=True)
    return True

def publishLighting(shotName=None, autoName=True, prompt=False):
    saveMayaFile(shotName, typ='lighting/Published', prompt=prompt, autoName=autoName,
                 removeRefs=False, shot=True)
    return True

def setupSceneForRender(shotName=None, latest=True, prompt=False):
    newScene()
    shotName = assetNameSetup(shotName, prompt, typ='shot')
    if not shotName:
        return False
    path = getShotDir()
    fileName = getLatestVersion(shotName, path, 'lighting/Published')
    cmds.file(fileName, r=1, ns=newNameSpace(shotName))
    print 'Referenced Lighting: {}'.format(fileName)
    print '## DO OTHER STUFF FOR SETTING UP THE RENDER - aov\'s, render settings, etc.'


def removeReferences():
    sel = cmds.ls()
    for each in sel:
        if cmds.objExists(each):
            if cmds.nodeType(each) == 'reference':
                cmds.file(rr=1, rfn=each)

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
    print 'File Saved to: {}'.format(fileName)
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


def createNewPipelineAsset(assetName=None, prompt=False):
    assetName = assetNameSetup(assetName, prompt, textPrompt=True)
    if not assetName:
        return False
    setAssetName(assetName)
    assetDir = getAssetDir()
    newAssetDir = '{}{}'.format(assetDir, assetName)
    if os.path.isdir(newAssetDir):
        print 'Asset directory already exists.'
        return False
    else:
        os.mkdir(newAssetDir)
        folderList = {
            'lookDev' : {'Published' : None, 'WIP': None},
            'model' : {'Published' : None, 'WIP': None},
            'rig' : {'Published' : None, 'WIP': {'controlShapes' : None, 'guides' : None, 'skin' : None}},
            'texture' : {'Published' : None, 'WIP': None},
        }
        for k, v in folderList.iteritems():
            os.mkdir('{}/{}'.format(newAssetDir, k))
            if v is None:
                continue
            for k2, v2 in v.iteritems():
                os.mkdir('{}/{}/{}'.format(newAssetDir, k, k2))
                if v2 is None:
                    continue
                for k3, v3 in v2.iteritems():
                    os.mkdir('{}/{}/{}/{}'.format(newAssetDir, k, k2, k3))
        print 'Created asset directories: {}'.format(newAssetDir)

def createNewPipelineShot(shotName=None, prompt=False):
    shotName = assetNameSetup(shotName, prompt, textPrompt=True, typ='shot')
    if not shotName:
        return False
    setShotName(shotName)
    shotDir = getShotDir()
    newShotDir = '{}{}'.format(shotDir, shotName)
    if os.path.isdir(newShotDir):
        print 'Shot directory already exists.'
        return False
    else:
        os.mkdir(newShotDir)
        folderList = {
            'anim' : {'Published' : None, 'WIP' : None},
            'lighting' : {'Published' : None, 'WIP' : None},
            'nuke' : None,
            'plates' : {'misc' : None, 'prep' : None, 'raw' : None,
                        'retime' : None, 'roto' : None, 'undistort' : None},
            'renders' : None
        }
        for k, v in folderList.iteritems():
            os.mkdir('{}/{}'.format(newShotDir, k))
            if v is None:
                continue
            for k2, v2 in v.iteritems():
                os.mkdir('{}/{}/{}'.format(newShotDir, k, k2))
                if v2 is None:
                    continue
                for k3, v3 in v2.iteritems():
                    os.mkdir('{}/{}/{}/{}'.format(newAssetDir, k, k2, k3))
        print 'Created shot directories: {}'.format(newShotDir)



def loadMayaFile(assetName='', typ='', prompt=False, new=False, latest=True, shot=False):
    assetName = assetNameSetup(assetName, prompt, typ='asset' if not shot else 'shot')
    if not assetName:
        return False
    directory = getAssetDir() if not shot else getShotDir()
    subDir = '{}{}/{}/'.format(directory, assetName, typ)
    if not os.path.isdir(subDir):
        print '{} asset does not exist.'.format(assetName)
        return False
    if latest:
        fileName = getLatestVersion(assetName, directory, typ)
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
        print 'Opened File: {}'.format(fileName)
        return True
    return False

def saveMayaFile(assetName='', typ='', prompt=False, autoName=False, removeRefs=False,
                 selectionOnly=False, shot=False):
    assetName = assetNameSetup(assetName, prompt, typ='asset' if not shot else 'shot')
    if not assetName:
        return False
    directory = getAssetDir() if not shot else getShotDir()
    subDir = '{}{}/{}/'.format(directory, assetName, typ)
    if autoName:
        fileName = getLatestVersion(assetName, directory, typ, new=1)
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
        print 'Saved File: {}'.format(fileName)

def treeAssetNamePrompt(typ='asset'):
    if cmds.window('{}NamePrompt'.format(typ), exists=True):
        cmds.deleteUI('{}NamePrompt'.format(typ), window=True)
    window = cmds.window('{}NamePrompt'.format(typ), title='Set {} Name'.format(typ.capitalize()),
                         width=200)
    form = cmds.formLayout()
    treeLister = cmds.treeLister(rc='fileFn.treeAssetNamePrompt("{}")'.format(typ))
    btnCommand = 'fileFn.createNewPipeline{}(prompt=True) \nfileFn.treeAssetNamePrompt("{}")'.format(typ.capitalize(), typ)
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
    if not os.path.isdir(directory):
        return False
    ls = [f for f in os.listdir(directory) if os.path.isdir('{}/{}'.format(directory, f))]
    if 'rigScripts' in ls:
        ls.remove('rigScripts')

    for each in ls:
        # command = 'fileFn.assetNamePromptCommand("{}", "{}")'.format(each, window)
        command = 'fileFn.set{}Name("{}") \ncmds.window("{}", e=1, vis=False)'.format(typ.capitalize(), each, window)
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

def getAssetName(dialog=False):
    name = mel.eval('getenv "assetName"')
    if dialog:
        cmds.confirmDialog(m='Current Asset: {}'.format(name), button=['Ok'])
    return name

def setShotName(shotName=None):
    if not shotName:
        treeAssetNamePrompt(typ='shot')
    if shotName:
        mel.eval('putenv "shotName" {}'.format(shotName))

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
    if not assetName:
        assetName = treeAssetNamePrompt(typ)
    if not assetName:
        print 'Asset Name not specified.'
    return assetName

def reloadReferences():
    assets, refNd = utils.getAssetsInScene()
    for i, each in enumerate(assets):
        referenceRig(each, replace=True, refNd=refNd[i])