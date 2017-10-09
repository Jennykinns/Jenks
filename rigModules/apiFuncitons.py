import math
import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

def getMObj(objName):
    #mSelList = om.MSelectionList()
    #mObj = om.MObject()
    mSelList = om.MGlobal.getSelectionListByName(objName)
    mObj = mSelList.getDependNode(0)
    return mObj

def getSelectionAsMObjs():
    selectionList = om.MGlobal.getActiveSelectionList()
    objs = []
    for i in range(selectionList.length()):
        mObj = selectionList.getDependNode(i)
        objs.append(mObj)
    return objs

def getPath(mObj, returnString=True):
    if mObj.hasFn(om.MFn.kTransform) or mObj.hasFn(om.MFn.kShape):
        dagNode = om.MFnDagNode(mObj)
        dagPath = om.MDagPath()
        #dagNode.getPath(dagPath)
        dagPath = dagNode.getPath()
        objPath = dagPath.fullPathName()
        objName = objPath.rpartition('|')
        objName = objName[-1]
    else:
        depNode = om.MFnDependencyNode(mObj)
        objPath = depNode.name()
        objName = objPath

    if returnString:
        return objPath, objName
    else:
        return dagPath

def getNurbsCurve(crvShape):
    mObj = getMObj(crvShape)
    MFnNurbs = om.MFnNurbsCurve(mObj)
    return MFnNurbs

def getEulerRot(x, y, z, ro=1):
    rot = om.MEulerRotation(math.radians(x), math.radians(y), math.radians(z), ro)
    return rot

def transformMPoint(mP, rot=(0, 0, 0), trans=(0, 0, 0), scale=(1, 1, 1)):
    pointVector = om.MVector(mP)
    transVector = om.MVector(trans)
    transMatrix = om.MTransformationMatrix()
    transMatrix.setTranslation(pointVector, 1)
    scale = (1.0 / scale[0], 1.0 / scale[1], 1.0 / scale[2])
    eulerRot = getEulerRot(rot[0], rot[1], rot[2], om.MEulerRotation.kXYZ)
    transMatrix.translateBy(transVector, om.MSpace.kObject)
    transMatrix.scaleBy(scale, om.MSpace.kObject)
    transMatrix.rotateBy(eulerRot, om.MSpace.kObject)
    return transMatrix.translation(om.MSpace.kObject)
