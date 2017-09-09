import maya.cmds as cmds
from Jenks.scripts.rigModules import utilityFunctions as utils

reload(utils)

class ctrl:
    def __init__(self, name='control', gimbal=False, offsetGrpNum=1, guide=None,
                 deleteGuide=False, side='C', skipNum=False, parent=None):
        self.side = side
        self.gimbal = False
        if not guide:
            deleteGuide = True
            guideLoc = utils.newNode('locator', name='controlGuide')
            guide = guideLoc.name

        self.guide = False if deleteGuide else guide
        self.ctrl = utils.newNode('control', name=name, side=self.side, skipNum=True)
        if offsetGrpNum > 0:
            self.createCtrlOffsetGrps(offsetGrpNum, name, guide, skipNum)
            self.ctrl.parent(self.offsetGrps[-1].name, relative=True)
            self.constGrp = utils.newNode('group', name=name,suffixOverride='controlConst',
                                          side=side, skipNum=skipNum, parent=self.ctrl.name)
            self.ctrlRoot = self.rootGrp.name
            self.ctrlEnd = self.constGrp.name
        else:
            self.ctrlRoot = self.ctrl
            self.ctrlEnd = self.ctrl
        if deleteGuide:
            cmds.delete(guide)
        if parent:
            cmds.parent(self.ctrlRoot, parent)

        # create const grp

    def createCtrlOffsetGrps(self, num, name, guide=None, skipNum=False):
        self.rootGrp = utils.newNode('group', name=name, suffixOverride='controlRootGrp',
                                      side=self.side, skipNum=skipNum)
        if guide:
            utils.matchTransforms([self.rootGrp.name], guide)
        self.offsetGrps = []
        par = self.rootGrp.name
        for i in range(num):
            self.offsetGrps.append(utils.newNode('group', name=name,
                                                 suffixOverride='controlOffset', side=self.side,
                                                 skipNum=skipNum))
            self.offsetGrps[-1].parent(par, relative=True)
            par = self.offsetGrps[-1]

    def controlShape(self, shape=None, color=None):
        if color:
            utils.setShapeColor(self.ctrl.name, color=color)
        if shape:
            print 'control Shape'


    def modifyShape(self, shape=None, color=None, rotation=(0, 0, 0), translation=(0, 0, 0)):
        print 'modify shape'

    def constrain(self, type='parent', mo=False):
        print 'constrain ctrl to joint/obj'

