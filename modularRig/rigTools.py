import maya.cmds as cmds

def updateBodyPiv(rigName):
    bodyCtrlLoc = cmds.spaceLocator()

    cmds.delete(cmds.parentConstraint('{0}_body_CTRL'.format(rigName), bodyCtrlLoc))
    cmds.xform('{0}_bodyPivot_CTRL'.format(rigName), ro=[0, 0, 0])
    cmds.delete(cmds.parentConstraint(bodyCtrlLoc, '{0}_body_CTRL'.format(rigName)))
    cmds.delete(bodyCtrlLoc)