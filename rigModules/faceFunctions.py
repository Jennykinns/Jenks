import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ikFunctions as ikFn
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules import miscFunctions as miscFn
from Jenks.scripts.rigModules.suffixDictionary import suffix
from Jenks.scripts.rigModules import defaultBodyOptions
from Jenks.scripts.rigModules import orientJoints

reload(orientJoints)
reload(utils)
reload(ikFn)
reload(ctrlFn)
reload(miscFn)
reload(defaultBodyOptions)


class face:
    def __init__(self, rig, extraName='', side='C'):
        self.moduleName = utils.setupBodyPartName(extraName, side)
        self.extraName = extraName
        self.side = side
        self.rig = rig

    def createEyes(self, side='C'):
        extraName = '{}_'.format(self.extraName) if self.extraName else ''
        crvs = [
            'eyeLow',
            'eyeHigh'
        ]
        for name in crvs:
            print name
            crv = '{}_{}face_{}{}'.format(side, extraName, name, suffix['nurbsCrv'])
            jnts = utils.createJntsFromCrv(crv, numOfJnts=5, chain=False,
                                           name='{}face_{}'.format(extraName, name))
        pass


    def createMouth(self):
        pass

    def createDetailMech(self):
        crvs = cmds.listRelatives('{}faceCrvs{}'.format(self.moduleName, suffix['group']))
        for crv in crvs:
            name = crv.strip('{}face'.format(self.moduleName))
            name = name.rstrip(suffix['nurbsCrv'])
            jnts = utils.createJntsFromCrv(crv, numOfJnts=5, chain=False,
                                           name='face_{}'.format(name))
        ## create joints on curves
        ## constrain joints on crv
        ##
        pass

    def createBaseMech(self):
        pass
