import maya.cmds as cmds

def _getSelection(*args):
    sel=list()
    sel=zip(cmds.ls(sl=True,l=True),cmds.ls(sl=True))
    return sel

def setSubdiv(t,i,*args):
    sel=_getSelection()
    for x in sel:
        lN,sN=x
        try:
            cmds.setAttr(lN+'.aiSubdivType', t)
            cmds.setAttr(lN+'.aiSubdivIterations', i)
        except:
            pass