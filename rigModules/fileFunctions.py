import os
import json
import sys
import maya.cmds as cmds
import maya.mel as mel

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import apiFuncitons as api

def getLatestVersion(assetName, path, location, new=False, name=None, suffix=None):
    if location == 'rig/WIP/guides':
        suffix = 'ma'
        name = 'guides'
    elif location == 'rig/WIP/skin':
        suffix = 'skin'
    elif location == 'rig/WIP/controlShapes':
        suffix = 'shape'
    elif location == 'model/Published':
        suffix = 'ma'
        name = assetName
    fileDirectory = '{}{}/{}/'.format(path, assetName, location)
    ls = os.listdir(fileDirectory)
    relevantFiles = []
    for each in sorted(ls):
        lsGeo = each.rsplit('_', 1 if not location == 'model/Published' else 2)[0]
        if lsGeo == name:
            relevantFiles.append(each)
    if new:
        if not relevantFiles:
            newFile = '{}{}_01.{}'.format(fileDirectory, name, suffix)
        else:
            nameWithoutSuffix = relevantFiles[-1].rsplit('.')[0]
            latestNum = nameWithoutSuffix.rsplit('_', 1)[1]
            newNum = str(int(latestNum)+1).zfill(2)
            newFile = '{}{}_{}.{}'.format(fileDirectory, name, newNum, suffix)
    else:
        if not relevantFiles:
            return False
        else:
            newFile = '{}{}'.format(fileDirectory, relevantFiles[-1])
    return newFile

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

def loadGuides(assetName=None, prompt=False, new=False):
    if prompt:
        assetName = assetNamePrompt()
    if not assetName:
        assetName = getAssetName()
    if not assetName:
        print 'Asset Name not specified.'
        return False
    path = getAssetDir()
    fileName = getLatestVersion(assetName, path, 'rig/WIP/guides')
    if new:
        if not newScene():
            return False
    cmds.file(fileName, i=1, dns=1, type='mayaAscii')
    print 'Loaded guides: {}'.format(fileName)
    return True

def saveGuides(assetName=None, autoName=False, prompt=False):
    if prompt:
        assetName = assetNamePrompt()
    if not assetName:
        assetName = getAssetName()
    if not assetName:
        print 'Asset Name not specified.'
        return False
    path = getAssetDir()
    if not autoName:
        fileFilter = fileDialogFilter([('Maya Ascii', '*.ma')])
        fileName = cmds.fileDialog2(dialogStyle=2, caption='Save Rig Guides',
                                    fileMode=0, fileFilter=fileFilter,
                                    dir='{}{}/rig/WIP/guides'.format(path, assetName))
        if fileName:
            fileName = fileName[0]
        else:
            return False
    else:
        fileName = getLatestVersion(assetName, path, 'rig/WIP/guides', new=True)
    removeReferences()
    cmds.file(rename=fileName)
    cmds.file(save=True, type='mayaAscii')
    print 'Saved guides: {}'.format(fileName)
    return True

def loadGeo(assetName=None, group=None, prompt=False):
    if prompt:
        assetName = assetNamePrompt()
    if not assetName:
        assetName = getAssetName()
    if not assetName:
        print 'Asset Name not specified.'
        return False
    path = getAssetDir()
    fileName = getLatestVersion(assetName, path, 'model/Published')
    # nodes = cmds.file(fileName, i=1, dns=1, type='mayaAscii', rnn=1)
    cmds.AbcImport(fileName, mode='import', rpr=group)
    print 'Loaded geometry: {}'.format(fileName)
    # mNodes = []
    # for each in nodes:
    #     mNodes.append(api.getMObj(each))
    # if group:
    #     for each in mNodes:
    #         lN, sN = api.getPath(each)
    #         if cmds.nodeType(lN) == 'transform':
    #             cmds.parent(lN, group)
    return True

def referenceGeo(assetName=None, prompt=False):
    if prompt:
        assetName = assetNamePrompt()
    if not assetName:
        assetName = getAssetName()
    if not assetName:
        print 'Asset Name not specified.'
        return False
    path = getAssetDir()
    fileName = getLatestVersion(assetName, path, 'model/Published')
    cmds.file(fileName, r=1)
    print 'Referenced geometry: {}'.format(fileName)
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
        fileName = fileOverride[0]
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
    if prompt:
        assetName = assetNamePrompt()
    if not assetName:
        assetName = getAssetName()
    if not assetName:
        print 'Asset Name not specified.'
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



def loadMayaFile(assetName='', typ='', prompt=False):
    if prompt:
        assetName = assetNamePrompt()
    if not assetName:
        assetName = getAssetName()
    if not assetName:
        print 'Asset Name not specified.'
        return False
    assetDir = getAssetDir()
    subDir = '{}{}/{}/WIP/'.format(assetDir, assetName, typ)
    if not os.path.isdir(subDir):
        print '{} asset does not exist.'.format(assetName)
        return False
    fileFilter = fileDialogFilter([('Maya Ascii', '*.ma')])
    fileName = cmds.fileDialog2(dialogStyle=2,
                                caption='Load {}'.format(typ.capitalize()),
                                fileMode=1,
                                fileFilter=fileFilter,
                                dir=subDir)
    if fileName:
        cmds.file(fileName, open=1, force=1)
        print 'Opened File: {}'.format(fileName)
        return True
    return False

def saveMayaFile(assetName='', typ='', prompt=False):
    if prompt:
        assetName = assetNamePrompt()
    if not assetName:
        assetName = getAssetName()
    if not assetName:
        print 'Asset Name not specified.'
        return False
    assetDir = getAssetDir()
    subDir = '{}{}/{}/WIP/'.format(assetDir, assetName, typ)
    fileFilter = fileDialogFilter([('Maya Ascii', '*.ma')])
    fileName = cmds.fileDialog2(dialogStyle=2,
                                caption='Save {}'.format(typ.capitalize()),
                                fileMode=0,
                                fileFilter=fileFilter,
                                dir=subDir)[0]
    if fileName:
        cmds.file(rename=fileName)
        cmds.file(save=True)

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


def getAssetName():
    name = mel.eval('getenv "assetName"')
    return name