import maya.cmds as cmds
from Jenks.scripts.rigModules import fileFunctions as fileFn
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn
from Jenks.scripts.rigModules import skinFunctions as skinFn
from Jenks.scripts.rigModules import setupFn

reload(fileFn)
reload(ctrlFn)
reload(skinFn)
reload(setupFn)

def create():

    rig = setupFn.rig()
    fileFn.loadGuides(rigName)
    fileFn.loadGeo(rigName, rig.geoGrp.name)

    ## DO STUFF


    ##

    skinFn.loadAllSkin(rigName, path)

    # load control shapes

rigName = 'testRigStuff'
path = '{}assets/'.format('/home/Jenks/Documents/USB/Uni_Tomfoolery/Year_3/finalProject/')

create()