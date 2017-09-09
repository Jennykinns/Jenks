import maya.cmds as cmds
from Jenks.scripts.rigModules import fileFunctions as file
reload(file)

def create():

    rig = file.rig()
    file.loadGuides(rigName, path)
    file.loadGeo(rigName, path, rig.geoGrp.name)

rigName = 'testRigStuff'
path = '/home/Jenks/Documents/USB/Uni_Tomfoolery/Year_3/finalProject/assets/'
create()