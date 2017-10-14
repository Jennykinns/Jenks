import maya.cmds as cmds
#Settings Control
def create(n,suf):
    n=str(n+suf)
    c=[]
    c.append(cmds.curve(degree = 1,\
                knot = [\
                        0, 1, 2, 3, 4, 5, 6, 7\
                ],\
                point = [\
                            (0.0, 0.0, 0.0),\
                            (0.0, 2.4, -2.4),\
                            (0.0, 2.4, -1.6),\
                            (0.0, 4.8, -1.6),\
                            (0.0, 4.8, 1.6),\
                            (0.0, 2.4, 1.6),\
                            (0.0, 2.4, 2.4),\
                            (0.0, 0.0, 0.0)\
                ]\
              ))
    cmds.rename(c[0],n)
    c[0]=n
    return c