sel=cmds.ls(sl=True)
for x in sel:
    existingAttr=cmds.listAttr(x)
    newAttr=["visSep","visGeo","visCtrls","visSkel","visMech","mdSep","mdGeo","mdSkel","sep1","credits"]

    #create attributes
    if newAttr[0] not in existingAttr:
        cmds.addAttr(x, ln="visSep",nn="___   Visibilities", at="enum", en="___:", k=True)
    if newAttr[1] not in existingAttr:
        cmds.addAttr(x, ln="visGeo",nn="Geometry", at="enum", en="Hide:Show", k=True, dv=1)
    if newAttr[2] not in existingAttr:
        cmds.addAttr(x, ln="visCtrls",nn="Controls", at="enum", en="Hide:Show", k=True, dv=1)
    if newAttr[3] not in existingAttr:
        cmds.addAttr(x, ln="visSkel",nn="Skeleton", at="enum", en="Hide:Show", k=True)
    if newAttr[4] not in existingAttr:
        cmds.addAttr(x, ln="visMech",nn="Mechanics", at="enum", en="Hide:Show", k=True)
    if newAttr[5] not in existingAttr:
        cmds.addAttr(x, ln="mdSep",nn="___   Display Mode", at="enum", en="___:", k=True)
    if newAttr[6] not in existingAttr:
        cmds.addAttr(x, ln="mdGeo",nn="Geometry", at="enum", en="Normal:Template:Reference", k=True, dv=2)
    if newAttr[7] not in existingAttr:
        cmds.addAttr(x, ln="mdSkel",nn="Skeleton", at="enum", en="Normal:Template:Reference", k=True)
    if newAttr[8] not in existingAttr:
        cmds.addAttr(x, ln="sep1",nn="___   ",at="enum",en="___", k=True)
    if newAttr[9] not in existingAttr:
        cmds.addAttr(x, ln="credits",nn="Rig by Matt Jenkins",at="enum",en="___", k=True)

    #find prefix
    name=x.split("_")
    prefix=name[0]+"_"

    #connect attributes
    if cmds.listConnections(x+".visGeo") == None:
        cmds.connectAttr(x+".visGeo",prefix+"geometry_GRP.visibility")
    if cmds.listConnections(x+".visCtrls") == None:
        cmds.connectAttr(x+".visCtrls",prefix+"controls_GRP.visibility")
    if cmds.listConnections(x+".visSkel") == None:
        cmds.connectAttr(x+".visSkel",prefix+"skeleton_GRP.visibility")
    if cmds.listConnections(x+".visMech") == None:
        cmds.connectAttr(x+".visMech",prefix+"mechanics_GRP.visibility")
    cmds.setAttr(prefix+"geometry_GRP.overrideEnabled",1)
    if cmds.listConnections(x+".mdGeo") == None:
        cmds.connectAttr(x+".mdGeo",prefix+"geometry_GRP.overrideDisplayType")
    cmds.setAttr(prefix+"skeleton_GRP.overrideEnabled",1)
    if cmds.listConnections(x+".mdSkel") == None:
        cmds.connectAttr(x+".mdSkel",prefix+"skeleton_GRP.overrideDisplayType")

