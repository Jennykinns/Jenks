import json
import maya.cmds as cmds
from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import fileFunctions as fileFn

reload(utils)
reload(fileFn)

def createNewShader(bump=False, sss=False, disp=True):
    """ Create a new aiStandardSurface shader with colour corrects
    and aiImage nodes for each important input.
    [Args]:
    bump (bool) - Toggles creating the bump map nodes
    sss (bool) - Toggles creating the sss map nodes
    disp (bool) - Toggles creating the displacement map nodes
    [Returns]:
    True
    """
    name = fileFn.textAssetNamePrompt()
    if not name:
        return False
    shad = utils.newNode('aiStandardSurface', name=name, side='ai', skipNum=True, shaderNode='shader')
    sg = utils.newNode('shadingEngine', name=name, side='ai', skipNum=True)
    sg.connect('surfaceShader', '{}.outColor'.format(shad.name), 'to')

    nodesToMake = [
        ('diffuse', 'outColor', 'baseColor'),
        ('spc', 'outColorR', 'specular'),
        ('spcRough', 'outColorR', 'specularRoughness'),
    ]
    if sss:
        nodesToMake.append(('sss', 'outColor', 'subsurfaceColor'))

    for extraName, fromAttr, destAttr in nodesToMake:
        ccNd = utils.newNode('aiColorCorrect', name='{}_{}'.format(name, extraName),
                             side='ai', skipNum=True, shaderNode='utility')
        ccNd.connect(fromAttr, '{}.{}'.format(shad.name, destAttr), 'from')
        imgNd = utils.newNode('aiImage', name='{}_{}'.format(name, extraName),
                              side='ai', skipNum=True, shaderNode='texture')
        imgNd.connect('outColor', '{}.input'.format(ccNd.name), 'from')

    if bump:
        bumpNd = utils.newNode('bump2d', name=name, side='ai', skipNum=True, shaderNode='utility')
        bumpNd.connect('outNormal', '{}.normalCamera'.format(shad.name))
        bumpImg = utils.newNode('aiImage', name='{}_bump'.format(name), side='ai', skipNum=True,
                                shaderNode='texture')
        bumpImg.connect('outColorR', '{}.bumpValue'.format(bumpNd.name))

    if disp:
        displacementNd = utils.newNode('displacementShader', name=name, side='ai', skipNum=True,
                                       shaderNode='shader')
        displacementNd.connect('displacement', '{}.displacementShader'.format(sg.name))
        displacementImgNd = utils.newNode('aiImage', name='{}_disp'.format(name),
                                          side='ai', skipNum=True, shaderNode='texture')
        displacementImgNd.connect('outColorR', '{}.displacement'.format(displacementNd.name))

    return True

def changeKeyframePosition():
    shotName = fileFn.getShotName()
    if not shotName:
        amount = 996
    else:
        path = fileFn.getShotDir()
        with open('{}shotRanges'.format(path), 'r') as f:
            data = json.load(f)
        if shotName in data.keys():
            amount = data[shotName][0]
        else:
            amount = 996
    if cmds.objExists('renderCam'):
        utils.lockAttr('renderCam', attr=['t', 'r'], unlock=True, hide=False)
    nds = cmds.ls()
    cmds.keyframe(nds, edit=True, relative=True, timeChange=amount)
    # cmds.playbackOptions(e=1, min=frameRange[0]+amount, max=frameRange[1]+amount)
    return True


def replaceShaders():
    ## Reference Lookdev > Transfer Shaders > Import Used Shaders > Remove Reference
    assetName = fileFn.getAssetName()
    if not assetName:
        return False
    f = fileFn.referenceLookDev(assetName)
    refNd = cmds.file(f, q=1, rfn=1)
    nds = cmds.referenceQuery(refNd, n=1)
    for each in nds:
        if(not cmds.nodeType(each) == 'shadingEngine'
                or each in ['initialShadingGroup', 'initialParticleSE']):
            continue
        shader = cmds.listConnections('{}.surfaceShader'.format(each), d=False)[0]
        geoList = cmds.listConnections('{}.dagSetMembers'.format(each), d=False)
        ## dupe shader
        newShader = cmds.duplicate(each, un=1, ic=1)
        for geo in geoList:
            oldSel = cmds.ls(sl=1)
            geoName = geo.rpartition(':')[-1]
            cmds.select('*:{}'.format(geo.rpartition(':')[-1]), geoName)
            sameNameGeo = cmds.ls(sl=1)
            cmds.select(oldSel)
            sameNameGeo.remove(geo)
            cmds.sets(sameNameGeo, e=True, forceElement=newShader[0])

    cmds.file(f, rr=1)


