import maya.cmds as cmds
import os
from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ctrlFunctions
from Jenks.scripts.rigModules import apiFuncitons as api

reload(utils)
reload(ctrlFunctions)
reload(api)


def getLatestVersion(rigName, path, location):
    fileDirectory = '{}{}/{}/'.format(path, rigName, location)
    ls = os.listdir(fileDirectory)
    fileName = '{}{}'.format(fileDirectory, ls[-1])
    return fileName


def loadGuides(rigName, path):
    fileName = getLatestVersion(rigName, path, 'rig/WIP/guides')
    cmds.file(fileName, i=1, dns=1, type='mayaAscii')
    print 'Loaded guides: {}'.format(fileName)


def saveGuides(rigName=None, path=None):
    print 'saveGuides'


def loadGeo(rigName, path, group=None):
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


class rig:
    def __init__(self):
        cmds.file(force=1, new=1)
        self.grp = utils.newNode('group', name='RIG_', skipNum=True, side='')
        self.worldLoc = utils.newNode('locator', name='world',
                                      parent=self.grp.name, skipNum=True)
        cmds.setAttr('{}.v'.format(self.worldLoc.name), 0)
        self.worldLoc.lockAttr()
        self.geoGrp = utils.newNode('group', name='geometry',
                                      parent=self.grp.name, skipNum=True)
        self.globalCtrl = ctrlFunctions.ctrl(name='global', parent=self.grp.name, skipNum=True)
        self.globalCtrl.controlShape(color=30)
        self.ctrlsGrp = utils.newNode('group', name='controls',
                                      parent=self.globalCtrl.ctrlEnd, skipNum=True)
        self.skelGrp = utils.newNode('group', name='skeleton',
                                      parent=self.globalCtrl.ctrlEnd, skipNum=True)
        self.mechGrp = utils.newNode('group', name='mechanics',
                                      parent=self.globalCtrl.ctrlEnd, skipNum=True)