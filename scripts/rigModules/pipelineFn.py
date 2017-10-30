from Jenks.scripts.rigModules import utilityFunctions as utils
from Jenks.scripts.rigModules import fileFunctions as fileFn

def createNewShader(bump=False, sss=False, disp=True):
    name = fileFn.textAssetNamePrompt()
    shad = utils.newNode('aiStandardSurface', name=name, side='ai', skipNum=True)
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
                             side='ai', skipNum=True)
        ccNd.connect(fromAttr, '{}.{}'.format(shad.name, destAttr), 'from')
        imgNd = utils.newNode('aiImage', name='{}_{}'.format(name, extraName),
                              side='ai', skipNum=True)
        imgNd.connect('outColor', '{}.input'.format(ccNd.name), 'from')

    if bump:
        bumpNd = utils.newNode('bump2d', name=name, side='ai', skipNum=True)
        bumpNd.connect('outNormal', '{}.normalCamera'.format(shad.name))
        bumpImg = utils.newNode('aiImage', name='{}_bump'.format(name), side='ai', skipNum=True)
        bumpImg.connect('outColorR', '{}.bumpValue'.format(bumpNd.name))

    if disp:
        displacementNd = utils.newNode('displacementShader', name=name, side='ai', skipNum=True)
        displacementNd.connect('displacement', '{}.displacementShader'.format(sg.name))
        displacementImgNd = utils.newNode('aiImage', name='{}_disp'.format(name),
                                          side='ai', skipNum=True)
        displacementImgNd.connect('outColorR', '{}.displacement'.format(displacementNd.name))
