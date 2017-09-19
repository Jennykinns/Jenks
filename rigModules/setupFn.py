import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn


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
        self.globalCtrl = ctrlFn.ctrl(name='global', parent=self.grp.name, skipNum=True)
        self.globalCtrl.modifyShape(color=30, shape='global')
        self.ctrlsGrp = utils.newNode('group', name='controls',
                                      parent=self.globalCtrl.ctrlEnd, skipNum=True)
        self.settingCtrlsGrp = utils.newNode('group', name='settingCtrls',
                                             parent=self.ctrlsGrp.name, skipNum=True)
        self.skelGrp = utils.newNode('group', name='skeleton',
                                      parent=self.globalCtrl.ctrlEnd, skipNum=True)
        self.mechGrp = utils.newNode('group', name='mechanics',
                                      parent=self.globalCtrl.ctrlEnd, skipNum=True)
        cmds.setAttr('{}.v'.format(self.mechGrp.name), 0)
        self.scaleAttr = '{}.sy'.format(self.globalCtrl.ctrl.name)