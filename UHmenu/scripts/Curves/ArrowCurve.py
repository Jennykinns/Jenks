import maya.cmds as cmds
list = []
list.append(cmds.curve( p =[(-1.0, 0.0, 0.0), (-1.0, 0.0, 2.0), (1.0, 0.0, 2.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0), (0.0, 0.0, -2.0), (-2.0, 0.0, 0.0), (-1.0, 0.0, 0.0)],per = False, d=1, k=[0, 1, 2, 3, 4, 5, 6, 7]))
for x in range(len(list)-1):
	cmds.makeIdentity(list[x+1], apply=True, t=1, r=1, s=1, n=0)
	shapeNode = cmds.listRelatives(list[x+1], shapes=True)
	cmds.parent(shapeNode, list[0], add=True, s=True)
	cmds.delete(list[x+1])
cmds.select(list[0])