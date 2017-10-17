import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules import fileFunctions as fileFn


def createRigNode(rigNode):
    rigNode.addAttr(name='rigCtrls', nn='Rig Controls', typ='message')
    rigNode.addAttr(name='rigSkinJnts', nn='Rig Skinning Joints', typ='message')
    return rigNode, rigNode.rigCtrls, rigNode.rigSkinJnts
class rig:
    def __init__(self, name, scaleOffset=1, debug=False):
        cmds.file(force=1, new=1)
        fileFn.loadPlugin('mjSoftIK', '.py')
        self.scaleOffset = scaleOffset
        self.grp = utils.newNode('group', name='RIG_', skipNum=True, side='')
        self.worldLoc = utils.newNode('locator', name='world',
                                      parent=self.grp.name, skipNum=True)
        cmds.setAttr('{}.v'.format(self.worldLoc.name), 0)
        self.worldLoc.lockAttr()
        self.geoGrp = utils.newNode('group', name='geometry',
                                    parent=self.grp.name, skipNum=True)
        cmds.setAttr('{}.overrideEnabled'.format(self.geoGrp.name), 1)
        self.globalCtrl = ctrlFn.ctrl(name='global', parent=self.grp.name, skipNum=True,
                                      scaleOffset=self.scaleOffset)
        self.rigNode, self.ctrlsAttr, self.skinJntsAttr = createRigNode(self.globalCtrl.ctrl)
        self.globalCtrl.modifyShape(color=30, shape='global')
        self.ctrlsGrp = utils.newNode('group', name='controls',
                                      parent=self.globalCtrl.ctrlEnd, skipNum=True)
        cmds.setAttr('{}.overrideEnabled'.format(self.ctrlsGrp.name), 1)
        self.settingCtrlsGrp = utils.newNode('group', name='settingCtrls',
                                             parent=self.ctrlsGrp.name, skipNum=True)
        self.skelGrp = utils.newNode('group', name='skeleton',
                                     parent=self.globalCtrl.ctrlEnd, skipNum=True)
        cmds.setAttr('{}.overrideEnabled'.format(self.skelGrp.name), 1)
        self.mechGrp = utils.newNode('group', name='mechanics',
                                     parent=self.globalCtrl.ctrlEnd, skipNum=True)
        cmds.setAttr('{}.overrideEnabled'.format(self.mechGrp.name), 1)
        cmds.setAttr('{}.v'.format(self.mechGrp.name), 0)
        self.scaleAttr = '{}.sy'.format(self.globalCtrl.ctrl.name)
        globalCtrlAttrs = [
            ('visSep', '___   Visibilities', ['___'], 0, '', ''),
            ('visGeo', 'Geometry', ['Hide', 'Show'], 1, '{}.v'.format(self.geoGrp.name)),
            ('visCtrls', 'Controls', ['Hide', 'Show'], 1, '{}.v'.format(self.ctrlsGrp.name)),
            ('visSkel', 'Skeleton', ['Hide', 'Show'], 0 if not debug else 1,
                '{}.v'.format(self.skelGrp.name)),
            ('visMech', 'Mechanics', ['Hide', 'Show'], 0,
                '{}.v'.format(self.mechGrp.name)),
            ('mdSep', '___ Display Mode', ['___'], 0, '', ''),
            ('mdGeo', 'Geometry', ['Normal', 'Template', 'Reference'], 2 if not debug else 0,
                '{}.overrideDisplayType'.format(self.geoGrp.name)),
            ('mdSkel', 'Skeleton', ['Normal', 'Template', 'Reference'], 2 if not debug else 0,
                '{}.overrideDisplayType'.format(self.skelGrp.name)),
            ('sep1', '___   ', ['___'], 0, '', ''),
            ('credits', 'Rig by Matt Jenkins', ['___'], 0, '', '')
        ]
        for each in globalCtrlAttrs:
            self.globalCtrl.addAttr(each[0], each[1], typ='enum', defaultVal=each[3],
                                    enumOptions=each[2])
            if each[4]:
                exec('cmds.connectAttr(self.globalCtrl.ctrl.{}, each[4])'.format(each[0]))