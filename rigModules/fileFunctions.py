import maya.cmds as cmds
import os
import json
import sys
from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import apiFuncitons as api

def getLatestVersion(rigName, path, location, new=False, name=None, suffix=None):
    if location == 'rig/WIP/guides':
        suffix = 'ma'
        name = 'guides'
    elif location == 'rig/WIP/skin':
        suffix = 'skin'
    elif location == 'model/Published':
        suffix = 'ma'
        name = rigName
    fileDirectory = '{}{}/{}/'.format(path, rigName, location)
    ls = os.listdir(fileDirectory)
    relevantFiles = []
    for each in ls:
        lsGeo = each.rsplit('_')[0]
        if lsGeo == name:
            relevantFiles.append(each)
    if new:
        if not relevantFiles:
            newFile = '{}{}_01.{}'.format(fileDirectory, name, suffix)
        else:
            nameWithoutSuffix = relevantFiles[-1].rsplit('.')[0]
            latestNum = nameWithoutSuffix.rsplit('_')[1]
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
    scriptPath = sys.path[-1]
    return scriptPath

def getAssetDir():
    path = cmds.workspace(q=1, rd=1)
    return '{}assets/'.format(path)

def loadGuides(rigName):
    path = getAssetDir()
    fileName = getLatestVersion(rigName, path, 'rig/WIP/guides')
    cmds.file(fileName, i=1, dns=1, type='mayaAscii')
    print 'Loaded guides: {}'.format(fileName)

def saveGuides(rigName):
    print 'save guides'

def loadGeo(rigName, group=None):
    path = getAssetDir()
    fileName = getLatestVersion(rigName, path, 'model/Published')
    print 'Loaded geometry: {}'.format(fileName)
    nodes = cmds.file(fileName, i=1, dns=1, type='mayaAscii', rnn=1)
    mNodes = []
    for each in nodes:
        mNodes.append(api.getMObj(each))
    if group:
        for each in mNodes:
            lN, sN = api.getPath(each)
            if cmds.nodeType(lN) == 'transform':
                cmds.parent(lN, group)

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
        fileName = cmds.fileDialog2(dialogStyle=1,
                                    caption=caption,
                                    fileMode=0,
                                    fileFilter=fileFilter,
                                    dir=defaultDir)
    else:
        fileName = fileOverride
    if fileName:
        with open(fileName[0], 'w') as f:
            json.dump(data, f, indent=4)
        print 'File Saved to: {}'.format(fileName)
        return True
    else:
        return False

def loadJson(defaultDir=None, caption='Load Json', fileFormats=[('JSON', '*.json')],
             fileOverride=False):
    if not fileOverride:
        fileFilter = fileDialogFilter(fileFormats)
        fileName = cmds.fileDialog2(dialogStyle=1,
                                    caption=caption,
                                    fileMode=1,
                                    fileFilter=fileFilter,
                                    dir=defaultDir)
    else:
        fileName = fileOverride
    if fileName:
        with open(fileName[0], 'r') as f:
            data = json.load(f)
    return data
