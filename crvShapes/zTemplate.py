import maya.cmds as cmds
#Settings Control
def create(n,suf):
    n=str(n+suf)
    c=[]
    #insert curve creation here
    cmds.rename(c[0],n)
    c[0]=n
    return c