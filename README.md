# Jenks Pipeline & Auto-Rigging Tools.

## Getting Started

### Quick Start (Automatic Installation)

* Download the [latest installer](https://github.com/Jennykinns/Jenks/releases)
* Run the installer, if necessary change the install directory to your Maya directory.
* Optional: To avoid conflict of existing userSetup.mel file, manual installation may be required - to do this simply add the following lines to your userSetup.mel file:
```
$mayaDir=`getenv "MAYA_APP_DIR"`;

//Jenks Pipeline Menu
$pipeMenuLoc = $mayaDir + "/scripts/Jenks/scripts/pipelineMenu";
string $command = "source \""+$pipeMenuLoc+"\"";
eval $command;
```


### Manual Installation

* Download the [latest source release](https://github.com/Jennykinns/Jenks/releases), extract the contents to:
```
(Linux)$HOME/maya/scripts/
(Mac OS X)$HOME/Library/Preferences/Autodesk/maya/scripts/
(Windows) \Users\<username>\Documents\maya\scripts\
```
NOTE: The folder structure should be:
```
./maya/scripts/Jenks/[lots of folders and files]
```

* To get the menu in Maya, copy the userSetup.mel to the scripts folder as well. Or add the following to an existing userSetup file:
```
$mayaDir=`getenv "MAYA_APP_DIR"`;

//Jenks Pipeline Menu
$pipeMenuLoc = $mayaDir + "/scripts/Jenks/scripts/pipelineMenu";
string $command = "source \""+$pipeMenuLoc+"\"";
eval $command;
```

### Setting up the project folder

* Extract the contents of TemplateFolder.zip to your desired location, rename it appropriately.
* Most other project related actions can be performed from within the pipeline menu in Maya

## Features


## Using the Auto-Rigging Tools

* Set the asset (or create a new one) from the pipeline menu
* Make sure the geometry has gone through the modelling stage of the pipeline
* Open a fresh new scene and create the guide joints and locators (There is an example guide scene in the main Jenks directory)
* Double check everything in the guide scene is name properly - IT WON'T WORK OTHERWISE!
* To name things easier group each body part and click 'Name Guides' from the pipeline menu
```
{side}_{bodyPart}_GRP
or
{side}_{extraName}_{bodyPart}_GRP

e.g. L_arm_GRP or L_front_arm_GRP
```
* Save the guide scene through the pipeline menu
* Create the rig script - something like this:
```
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

rigName = 'NameOfAsset_CHANGE_THIS_FOR_EACH_RIG'

create()
cmds.viewFit()
cmds.progressWindow(e=1, ep=1)

```
You should only need to change what's inside the 'Do Stuff' comments and the rigName.

* Build the rig from the pipeline menu
* Skin the asset, save the skinning for future builds by selecting all the geometry and selecting 'Save Selected Rig Skin' from the pipeline menu
* Modify any control shapes and save them through the pipeline menu - IMPORTANT: Only modify the curve EP's or CP's NOT the transform
* Once the rig is finished, rerun the rig script but change the debug option to False
* Publish the rig through the pipeline menu

At any time (If done correctly) you are able to edit the guide scene and rebuild the rig - if the model proportions change etc

## Bugs

Bugs should be submitted [through github](https://github.com/Jennykinns/Jenks/issues). When subitting a bug be as specific as you can, check the script editor and include any errors or warnings that are related to my scripts. Enabling 'Show Stack Track' in the script editor makes debugging much easier.

Use the following as a guide to submitting:

```
[TITLE] Short and to the point.

**Expected Behavior:**
What you expected to happen.

**Actual Behavior:**
What actually happened.

**How To Reproduce:**
The steps in order to reproduce this issue.

**Extra Information:**
Errors, warnings or other details worthy of including.
```

If you know how to fix an open bug, feel free to contribute and submit a pull request.

## Updating

The pipeline may be updated frequently - to make sure everything stays up to date, you may want to clone the repo through git to make things easier.
Alternatively keep an eye out for new releases and reinstall.

At some point I might work on an auto-update system (Although no guarantees).

## Contributing

Feel free to contribute by fixing bugs, tweaking things and/or adding features.

## Authors

* **Matt Jenkins** - *Initial work* - [Website Link](https://www.Matt-Jenkins.co.uk)

## Ackonowledgements

* Thanks to all the people who's scripts I have used as guides as well as the documentation that poeple have put together.