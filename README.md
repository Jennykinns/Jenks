# Jenks Maya Scripts (mainly autoRigging)

Scripts made by Matt Jenkins - and some not made by me that were just left in my scripts directory, I'm lazy.

## Getting Started

### Installing

Download the zip or clone the repo into maya/scripts. Your folder structure should look something like:

```
C:/Docs/maya/scripts/Jenks/...
```

For best results on windows use the same maya preference location as the uni computers - anything else is untested and might not work... don't blame me for that one, windows just sucks (on linux anywhere should be fine... maybe... I don't remember)

To get the 'Jenks' and 'Jenks Pipeline' menus run the following from inside maya (or add to userSetup.mel)

```
//--- Jenks Custom ---\\

$mayaDir=`getenv "MAYA_APP_DIR"`;

//Jenks Menu
$jenksMenuLoc = $mayaDir + "/scripts/Jenks/jenksMenu";
string $command = "source \""+$jenksMenuLoc+"\"";
eval $command ;

//Jenks Pipeline Menu
$pipeMenuLoc = $mayaDir + "/scripts/Jenks/scripts/pipelineMenu";
string $command = "source \""+$pipeMenuLoc+"\"";
eval $command;
```

## Running the Auto-Rigger

First of all you need to setup your maya project in a certain way. At some point I'll add a template that can just be copied and slightly tweaked.

Then add a new asset from the Jenks Pipeline menu.

Open your asset geometry and publish through the pipeline menu

Open a fresh new scene and create your guide joints and locators (I'll also add an example scene of this)

Make sure everything in the guide scene is named properly. IT WON'T WORK OTHERWISE!

Save your guide scene through the pipeline menu

Create the rig script - something like this:
```
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

    rig = setupFn.rig(rigName, debug=True)
    fileFn.loadGuides(rigName)
    fileFn.loadGeo(rigName, rig.geoGrp.name)

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

    ##

    skinFn.loadAllSkin(rigName)
    ctrlFn.loadCtrls(rigName)

rigName = 'NameOfTheAsset_CHANGETHIS'

create()
```

Build the rig from the pipeline menu (Load rig script option box)

Skin the asset, save your skinning for future builds through the pipeline menu

Change any controls shapes and save them, again with the pipeline menu (Make sure to only edit the curve shapes and not the transform)

To finish, publish your rig through the pipeline menu. Maya file will be located in:
```
{mayaProjectName}/assets/{assetName}/rig/Published/
```

At anytime you can go back and edit your guide scene and rebuild the rig.

## Bugs

Bugs should be submitted through github [Link](https://github.com/Jennykinns/Jenks/issues). When subitting a bug be as specific as you can, check the script editor and include any errors or warnings that are related to my scripts.

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

## Updating

This repo will most likely be updated frequently - to make sure your rigs stay up to date, you may have to rebuild them mutiliple times, this won't be much of an issue if you make sure to save the skinning and control shapes. I'll do my best to not break any animations with updates, but no promises. Worst case scenario you can always just not update and stick to a rig with slightly fewer features.

If you clone the repo it will automatically update otherwise you'll have to manually download each time an update is released.

## Contributing

For those of you that actually understand python feel free to fork and add your own functionality or tweak things - just give me a heads up first.

## Authors

* **Matt Jenkins** - *Initial work* - [Website Link](https://www.JenksProductions.co.uk)

## Acknowledgments

* Thanks to all the people who's scripts I have used as guides as well as the documentation that poeple have put together.
* Also for all the scripts I have left in the repo out of laziness, hopefully the credits for that stuff should be in the scripts themselves otherwise a quick google should do the trick - at some point I'll get around to removing the ones I don't use anymore
