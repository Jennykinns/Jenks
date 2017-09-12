import maya.cmds as cmds
import maya.OpenMaya as om


def getMObj(objName):
    mSelList = om.MSelectionList()
    mObj = om.MObject()
    om.MGlobal.getSelectionListByName(objName, mSelList)
    mSelList.getDependNode(0, mObj)
    return mObj

def getPath(mObj):
    if mObj.hasFn(om.MFn.kTransform) or mObj.hasFn(om.MFn.kShape):
        dagNode = om.MFnDagNode(mObj)
        dagPath = om.MDagPath()
        dagNode.getPath(dagPath)
        objPath = dagPath.fullPathName()
        objName = objPath.rpartition('|')
        objName = objName[-1]
    else:
        depNode = om.MFnDependencyNode(mObj)
        objPath = depNode.name()
        objName = objPath

    return objPath, objName

def getNurbsCurve(crvShape):
    mObj = getMObj(crvShape)
    MFnNurbs = om.MFnNurbsCurve(mObj)
    return MFnNurbs