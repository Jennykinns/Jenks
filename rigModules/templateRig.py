import maya.cmds as cmds

from Jenks.scripts.rigModules import fileFunctions as fileFn
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules import skinFunctions as skinFn
from Jenks.scripts.rigModules import bodyFunctions as bodyFn
from Jenks.scripts.rigModules import setupFn

reload(fileFn)
reload(ctrlFn)
reload(skinFn)
reload(bodyFn)
reload(setupFn)

def create():

    rig = setupFn.rig(debug=True)
    fileFn.loadGuides(rigName)
    fileFn.loadGeo(rigName, rig.geoGrp.name)

    ## DO STUFF

    # ctrl1 = ctrlFn.ctrl(name='test', guide='joint1')
    # ctrl1.modifyShape(color=10, shape='cube', scale=(0.3, 0.3, 0.3), rotation=(10, 10, 10))
    # ctrl1.constrain('joint1')
    # ctrl2 = ctrlFn.ctrl(name='test', guide='joint2')
    # ctrl2.constrain('joint2')
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

    ##

    skinFn.loadAllSkin(rigName)
    ctrlFn.loadCtrls(rigName)

rigName = 'testRigStuff'

create()