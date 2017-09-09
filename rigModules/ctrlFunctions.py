import maya.cmds as cmds
from Jenks.scripts.rigModules import utilityFunctions as utils

reload(utils)

class ctrl:
    def __init__(self, name='control', gimbal=False, offsetGrpNum=1, guide=None,
                 deleteGuide=False, side='C'):
        self.side = side
        self.gimbal = False
        self.guide = False if deleteGuide or not guide else guide

        ctlName = utils.setupName(name, obj='control', side=side)

        if offsetGrpNum > 0:
            self.createCtrlOffsetGrps(offsetGrpNum, name, guide, deleteGuide)
        ## create ctrl curve
        ## creat const grp

    def createCtrlOffsetGrps(self, num, name, guide=None, deleteGuide=False):
        rootGrpName = utils.setupName(name, obj='controlRoot')
        offsetGrpName = utils.setupName(name, obj='controlOffset')
        self.rootGrp = utils.newNode('group', name=rootGrpName)
        if guide:
            utils.matchTransforms([rootGrp.name], guide)
        self.offsetGrps = []
        par = self.rootGrp.name
        for each in num:
            self.offsetGrps.append(utils.newNode('group', name=offsetGrpName))
            self.offsetGrps[-1].name.parent(par, relative=True)
            par = self.offsetGrps[-1]

    def controlShape(self):
        print 'control Shape'

    def modifyShape(self, shape=None, color=None, rotation=(0, 0, 0), translation=(0, 0, 0)):
        print 'modify shape'

    def constrain(self, type='parent', mo=False):
        print 'constrain ctrl to joint/obj'

