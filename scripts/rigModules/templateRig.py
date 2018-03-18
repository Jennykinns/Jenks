import maya.cmds as cmds

from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import fileFunctions as fileFn
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules import skinFunctions as skinFn
from Jenks.scripts.rigModules import bodyFunctions as bodyFn
from Jenks.scripts.rigModules import mechFunctions as mechFn
from Jenks.scripts.rigModules import faceFunctions as faceFn
from Jenks.scripts.rigModules import ikFunctions as ikFn
from Jenks.scripts.rigModules import setupFn

reload(fileFn)
reload(ctrlFn)
reload(skinFn)
reload(bodyFn)
reload(mechFn)
reload(faceFn)
reload(setupFn)

def create():

    cmds.progressWindow(t='Creating Rig', progress=0, status='Setting Up.', isInterruptable=1)

    rig = setupFn.rig(rigName, debug=True, scaleOffset=1)
    fileFn.loadGuides(rigName)
    fileFn.loadGeo(rigName, rig.geoGrp.name)

    if cmds.progressWindow(q=1, isCancelled=1):
        return False

    ## DO STUFF

    spine = bodyFn.spineModule(rig, side='C')
    spine.createFromJnts()
    head = bodyFn.headModule(rig, side='C')
    head.create(parent=spine.endJnt, extraSpaces=spine.bodyCtrl.ctrlEnd)
    for s in 'RL':
        arm = bodyFn.armModule(rig, side=s)
        arm.create(autoOrient=True, parent=spine.armJnt)
        leg = bodyFn.legModule(rig, side=s)
        leg.create(autoOrient=True, parent=spine.baseJnt)
        fingers = bodyFn.digitsModule(rig, side=s)
        fingers.create('hand', parent=arm.handJnt, thumb=True)
        toes = bodyFn.digitsModule(rig, side=s)
        toes.create('foot', parent=leg.footJnt, thumb=False)
    tail = bodyFn.tailModule(rig, side='C')
    tail.create()
    face = faceFn.face(rig, side='C')
    face.basicFace(jntPar=spine.endJnt, ctrlPar=head.headCtrl.ctrlEnd)

    ##

    ctrlFn.loadCtrls(rigName)
    skinFn.loadAllSkin(rigName)

rigName = 'testRigStuff'

create()
cmds.viewFit()
cmds.progressWindow(e=1, ep=1)