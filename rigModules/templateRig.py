import maya.cmds as cmds
from Jenks.scripts.rigModules import fileFunctions as file
from Jenks.scripts.rigModules import ctrlFunctions as ctrlFn

reload(file)
reload(ctrlFn)

def create():

    rig = file.rig()
    file.loadGuides(rigName, path)
    file.loadGeo(rigName, path, rig.geoGrp.name)

    ## DO STUFF
    newCtrl = ctrlFn.ctrl()

    ##

    # load skin
    # load control shapes

rigName = 'testRigStuff'
path = '/home/Jenks/Documents/USB/Uni_Tomfoolery/Year_3/finalProject/assets/'

create()