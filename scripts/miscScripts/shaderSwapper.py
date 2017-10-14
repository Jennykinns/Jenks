#############################################################################
#                                                                           #
#   Name:                                                                   #
#       shaderSwapper.py                                                    #
#                                                                           #
#   Desc:                                                                   #
#       Creates an alternate set of Blinn materials so that alSurface       #
#       shaders can be seen in the viewport                                 #
#                                                                           #
#   Author:                                                                 #
#       Matt Jenkins                                                        #
#                                                                           #
#############################################################################


import maya.cmds as cmds

def disconnectAll(node, source=True, destination=True):
    connectionPairs = []
    if source:
        conns = cmds.listConnections(node, plugs=True, connections=True, destination=False)
        if conns:
            connectionPairs.extend(zip(conns[1::2], conns[::2]))

    if destination:
        conns = cmds.listConnections(node, plugs=True, connections=True, source=False)
        if conns:
            connectionPairs.extend(zip(conns[::2], conns[1::2]))

    for srcAttr, destAttr in connectionPairs:
        cmds.disconnectAttr(srcAttr, destAttr)



def getShaderName(obj):
    if obj:
        selShape=cmds.listRelatives(obj)
        for x in selShape:
            shadingGroupName=cmds.listConnections(x,t='shadingEngine')
            for y in shadingGroupName:
                shaderName=cmds.listConnections(y, t='alSurface')
                if shaderName:
                    return shaderName
                else:
                    cmds.error('No alSurface shader found.')

def matchShaders(*args):
    alSurfaceShaders=cmds.ls(type='alSurface')
    for shader in alSurfaceShaders:
        if cmds.objExists('tmp_'+shader):
            shaderName='tmp_'+shader
            disconnectAll(shaderName,True,False)
            # -- Diff colour -- #
            diffColorConn=cmds.listConnections('%s.diffuseColor' %shader, p=True)
            if diffColorConn:
                for x in diffColorConn:
                    cmds.connectAttr(x,'%s.color' %shaderName,)
            else:
                diffColorValue=cmds.getAttr('%s.diffuseColor' %shader)
                diffColorValue= str(diffColorValue).split(', ')
                diffColorValue=[x.replace('(','') for x in diffColorValue]
                diffColorValue=[x.replace(')','') for x in diffColorValue]
                diffColorValue=[x.replace('[','') for x in diffColorValue]
                diffColorValue=[x.replace(']','') for x in diffColorValue]
                cmds.setAttr('%s.color' %shaderName, float(diffColorValue[0]),float(diffColorValue[1]),float(diffColorValue[2]))

            # -- Diff Strength -- #
            diffStrengthConn=cmds.listConnections('%s.diffuseStrength' %shader, p=True)
            if diffStrengthConn:
                for x in diffStrengthConn:
                    cmds.connectAttr(x,'%s.diffuse' %shaderName,)
            else:
                diffStrengthValue=cmds.getAttr('%s.diffuseStrength' %shader)
                diffStrengthValue= str(diffStrengthValue).split(', ')
                diffStrengthValue=[x.replace('(','') for x in diffStrengthValue]
                diffStrengthValue=[x.replace(')','') for x in diffStrengthValue]
                diffStrengthValue=[x.replace('[','') for x in diffStrengthValue]
                diffStrengthValue=[x.replace(']','') for x in diffStrengthValue]
                cmds.setAttr('%s.diffuse' %shaderName, float(diffStrengthValue[0]))
            # -- Spec Strength -- #
            specStrengthConn=cmds.listConnections('%s.specular1Strength' %shader, p=True)
            if specStrengthConn:
                for x in specStrengthConn:
                    cmds.connectAttr(x,'%s.sro' %shaderName,)
            else:
                specStrengthValue=cmds.getAttr('%s.specular1Strength' %shader)
                specStrengthValue= str(specStrengthValue).split(', ')
                specStrengthValue=[x.replace('(','') for x in specStrengthValue]
                specStrengthValue=[x.replace(')','') for x in specStrengthValue]
                specStrengthValue=[x.replace('[','') for x in specStrengthValue]
                specStrengthValue=[x.replace(']','') for x in specStrengthValue]
                cmds.setAttr('%s.sro' %shaderName, float(specStrengthValue[0]))
            # -- Spec Colour -- #
            specColorConn=cmds.listConnections('%s.specular1Color' %shader, p=True)
            if specColorConn:
                for x in specColorConn:
                    cmds.connectAttr(x,'%s.sc' %shaderName,)
            else:
                specColorValue=cmds.getAttr('%s.specular1Color' %shader)
                specColorValue= str(specColorValue).split(', ')
                specColorValue=[x.replace('(','') for x in specColorValue]
                specColorValue=[x.replace(')','') for x in specColorValue]
                specColorValue=[x.replace('[','') for x in specColorValue]
                specColorValue=[x.replace(']','') for x in specColorValue]
                cmds.setAttr('%s.sc' %shaderName, float(specColorValue[0]),float(specColorValue[1]),float(specColorValue[2]))
            # -- Spec Roughness -- #
            specRoughnessConn=cmds.listConnections('%s.specular1Roughness' %shader, p=True)
            if specRoughnessConn:
                for x in specRoughnessConn:
                    cmds.connectAttr(x,'%s.ec' %shaderName,)
            else:
                specRoughnessValue=cmds.getAttr('%s.specular1Roughness' %shader)
                specRoughnessValue= str(specRoughnessValue).split(', ')
                specRoughnessValue=[x.replace('(','') for x in specRoughnessValue]
                specRoughnessValue=[x.replace(')','') for x in specRoughnessValue]
                specRoughnessValue=[x.replace('[','') for x in specRoughnessValue]
                specRoughnessValue=[x.replace(']','') for x in specRoughnessValue]
                cmds.setAttr('%s.ec' %shaderName, float(specRoughnessValue[0]))
            # -- Opacity -- #
            opacityConn=cmds.listConnections('%s.opacity' %shader, p=True)
            if opacityConn:
                for x in opacityConn:
                    cmds.connectAttr(x,'%s.it' %shaderName,)
            else:
                opacityValue=cmds.getAttr('%s.opacity' %shader)
                opacityValue= str(opacityValue).split(', ')
                opacityValue=[x.replace('(','') for x in opacityValue]
                opacityValue=[x.replace(')','') for x in opacityValue]
                opacityValue=[x.replace('[','') for x in opacityValue]
                opacityValue=[x.replace(']','') for x in opacityValue]
                cmds.setAttr('%s.it' %shaderName, 1-float(opacityValue[0]),1-float(opacityValue[1]),1-float(opacityValue[2]))
            # -- Bump Map -- #
            bumpConn=cmds.listConnections('%s.n' %shader, p=True)
            if bumpConn:
                for x in bumpConn:
                    cmds.connectAttr(x,'%s.n' %shaderName,)

def newBlinnForSelection(*args):
    selection=cmds.ls(sl=True)
    if selection:
        for selObject in selection:
            shaderNames=getShaderName(selObject)
            for shader in shaderNames:
                if not cmds.objExists('tmp_'+shader):
                    newBlinn=cmds.shadingNode("blinn", asShader=True)
                    newBlinnSG=cmds.sets(renderable=True,noSurfaceShader=True,empty=True)
                    cmds.connectAttr('%s.outColor' %newBlinn ,'%s.surfaceShader' %newBlinnSG)
                    cmds.rename('%s' %newBlinn, 'tmp_'+shader)
                    cmds.rename('%s' %newBlinnSG, 'tmp_'+shader+'SG')
                else:
                    cmds.warning('Blinn with that name already exists. Skipping creation.')
                cmds.select(selObject)
                cmds.sets(e=True,forceElement='tmp_'+shader+'SG')
        cmds.select(selection)
        matchShaders()
    else:
        cmds.warning('Please select an object.')


def toggleSelectedShaders(*args):
    selectedObjs=cmds.ls(sl=True)
    if selectedObjs:
        for x in selectedObjs:
            selShape=cmds.listRelatives(x)
            shadingGroupName=cmds.listConnections(selShape,t='shadingEngine')
            for y in shadingGroupName:
                shaderName=cmds.listConnections(y, t='alSurface')
                if shaderName:
                    for z in shaderName:
                        if cmds.objExists('tmp_'+z):
                            shaderObjs=cmds.sets(z+'SG',q=True)
                            cmds.select(shaderObjs)
                            cmds.sets(e=True,forceElement='tmp_'+z+'SG')
                            cmds.select(selectedObjs)
                else:
                    shaderName=cmds.listConnections(y,t='blinn')
                    if shaderName:
                        for z in shaderName:
                            z2=z.replace('tmp_','',1)
                            if cmds.objExists(z2):
                                shaderObjs=cmds.sets(z+'SG',q=True)
                                cmds.select(shaderObjs)
                                cmds.sets(e=True,forceElement=z2+'SG')
                                cmds.select(selectedObjs)
                    else:
                        cmds.warning('No selected shaders to swap.')
    else:
        cmds.warning('Please select an object.')

def setBlinnShaders(*args):
    alSurfaceShaders=cmds.ls(type='alSurface')
    for x in alSurfaceShaders:
        if cmds.objExists('tmp_'+x):
            shaderObjs=cmds.sets(x+'SG',q=True)
            cmds.select(shaderObjs)
            cmds.sets(e=True,forceElement='tmp_'+x+'SG')
            cmds.select(cl=True)

def setArnoldShaders(*args):
    blinnShaders=cmds.ls(type='blinn')
    for x in blinnShaders:
        x2=x.replace('tmp_','',1)
        if cmds.objExists(x2):
            shaderObjs=cmds.sets(x+'SG',q=True)
            cmds.select(shaderObjs)
            cmds.sets(e=True,forceElement=x2+'SG')
            cmds.select(cl=True)


def runShaderSwapperUI():
    uiWindow=cmds.window(title='shader Swapper')
    cmds.rowColumnLayout(numberOfColumns=1, w=270, columnOffset=[1,'both',10], rowSpacing=[1,5], rowOffset=[(1,'top',10), (5,'bottom',10)])
    cmds.button(l='Create Blinn Shaders', c=newBlinnForSelection, w=250, h=50)
    cmds.button(l='Set all Blinn Shaders to alSurface', c=setArnoldShaders, w=250)
    cmds.button(l='Toggle Selected Shaders', c=toggleSelectedShaders, w=250)
    cmds.button(l='Set all alSurface Shaders to Blinn', c=setBlinnShaders, w=250)
    cmds.button(l='Update Shaders', c=matchShaders, w=250, h=50)
    cmds.showWindow(uiWindow)

cmds.setAttr('defaultRenderGlobals.preMel', 'python("shaderSwapper.setArnoldShaders()")', type='string')
cmds.setAttr('defaultRenderGlobals.postMel', 'python("shaderSwapper.setBlinnShaders()")', type='string')

