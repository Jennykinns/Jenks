import os
import json
import sys
import maya.cmds as cmds
import maya.mel as mel

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import apiFuncitons as api
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

def abcExport(fileName, selection=True, frameRange=(1, 1)):
    if selection:
        sel = cmds.ls(sl=True)
    else:
        a = cmds.ls(dag=1, v=1)
        b = cmds.ls(lights=1, cameras=1)
        sel = list(set(a)-set(b))
    args = '-f {0} -fr {1[0]} {1[1]} -ro -sn -uv -ws -wv -ef'.format(fileName, frameRange, sel)
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

def referenceRig(assetName=None, prompt=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    path = getAssetDir()
    fileName = getLatestVersion(assetName, path, 'rig/Published')
    cmds.file(fileName, r=1, ns=newNameSpace(assetName))
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
    for each in cmds.listRelatives(geoGrp.name, c=1):
        print '## ADD A QUICK FUNCTION TO AVOID NAMING CONFLICTS FOR LOOKDEV MESH SET NAMES'
        i = 1
        geoSetName = '{}{}'.format(each.rstrip(suffix['geometry']), str(i).zfill(2))
        while cmds.objExists(geoSetName):
            i += 1
            geoSetName = '{}{}'.format(each.rstrip(suffix['geometry']), str(i).zfill(2))
        cmds.sets(each, n='geoSet_{}'.format(geoSetName))


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
    assetName = assetNameSetup(assetName, prompt)
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



def loadMayaFile(assetName='', typ='', prompt=False, new=False, latest=True):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    assetDir = getAssetDir()
    subDir = '{}{}/{}/'.format(assetDir, assetName, typ)
    if not os.path.isdir(subDir):
        print '{} asset does not exist.'.format(assetName)
        return False
    if latest:
        fileName = getLatestVersion(assetName, assetDir, typ)
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
                 selectionOnly=False):
    assetName = assetNameSetup(assetName, prompt)
    if not assetName:
        return False
    assetDir = getAssetDir()
    subDir = '{}{}/{}/'.format(assetDir, assetName, typ)
    if autoName:
        fileName = getLatestVersion(assetName, assetDir, typ, new=1)
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
            pass
        else:
            cmds.file(rename=fileName)
            cmds.file(save=True, type='mayaAscii')
            print 'Saved File: {}'.format(fileName)

def assetNamePrompt():
    result = cmds.promptDialog(title='Asset Name',
                               message='Asset Name:',
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
        assetName = assetNamePrompt()
    if assetName:
        mel.eval('putenv "assetName" {}'.format(assetName))


def getAssetName(dialog=False):
    name = mel.eval('getenv "assetName"')
    if dialog:
        cmds.confirmDialog(m='Current Asset: {}'.format(name), button=['Ok'])
    return name

def assetNameSetup(assetName, prompt):
    if prompt:
        assetName = assetNamePrompt()
    if not assetName:
        assetName = getAssetName()
    if not assetName:
        assetName = assetNamePrompt()
    if not assetName:
        print 'Asset Name not specified.'
    return assetName