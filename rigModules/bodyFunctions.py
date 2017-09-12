import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import ikFunctions
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules import suffixDictionary
from Jenks.scripts.rigModules import defaultBodyOptions
from Jenks.scripts.rigModules import orientJoints

reload(utils)
reload(ikFunctions)
reload(ctrlFn)
reload(suffixDictionary)

class armModule:
    def __init__(self, extraName='', side='C'):
        self.moduleName = utils.setupBodyPartName(extraName, side)

    def create(self, options=defaultBodyOptions.arm, autoOrient=False):
        jntSuffix = suffixDictionary.suffix['joint']
        jnts = [
            '{}clavicle{}'.format(self.moduleName, jntSuffix),
            '{}shoulder{}'.format(self.moduleName, jntSuffix),
            '{}elbow{}'.format(self.moduleName, jntSuffix),
            '{}wrist{}'.format(self.moduleName, jntSuffix),
        ]
        ## orient joints
        if autoOrient:
            orientJoints.doOrientJoint(jointsToOrient=jnts.items(), aimAxis=(1, 0, 0), upAxis=(0, 1, 0),
                                       worldUp=(0, 1, 0), guessUp=1)
        ## ik/fk
        if options['IK'] and options['FK']:
            newJntChains = []
            ##- create setting control
            ##- result chain
            for chain in ['IK', 'FK']:
                newJnts = []
                newChainJnts = cmds.duplicate(jnts[0], rc=1)
                for each in newChainJnts:
                    newName = '{}_{}{}'.format(each.rsplit('_', 1)[0], chain, jntSuffix)
                    newJnts.append(cmds.rename(each, newName))
                newJntChains.append(newJnts)
            ikJnts = newJntChains[0]
            fkJnts = newJntChains[1]
            for i, each in enumerate(jnts):
                newName = '{}_result{}'.format(each.rsplit('_', 1)[0], jntSuffix)
                jnts[i] = cmds.rename(each, newName)
        else:
            ikJnts = jnts
            fkJnts = jnts
        ##- ik
        if options['IK']:
            print 'do IK stuff'
            ##-- mechanics
            ##-- controls
            ## autoClav
            if options['autoClav']:
                print 'do auto clav'
        ##- fk
        if options['FK']:
            print 'do FK stuff'
            ##-- controls
        ## stretchy
        if options['stretchy']:
            print 'do stretchy'
        ## softIK
        if options['softIK']:
            print 'do soft IK'
        ## ribbon
        if options['ribbon']:
            print 'do ribbon'
        print 'arm'



class legModule:
    def __init__(self):
        print 'leg'


class spineModule:
    def __init__(self):
        print 'spine'


class headModule:
    def __init__(self):
        print 'head'


class digitsModule:
    def __init__(self):
        print 'digits'


class tailModule:
    def __init__(self):
        print 'tail'
