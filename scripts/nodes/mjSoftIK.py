import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import maya.mel as mel

import os
import math

NAME = 'Matt Jenkins'
VERSION = '0.1'
MAYAVERSION = '2017'
NODENAME = 'mjSoftIK'
NODEID = om.MTypeId(0x0012ad42)

class mjSoftIK(ompx.MPxNode):
    def __init__(self):
        ompx.MPxNode.__init__(self)


    def compute(self, pPlug, pDataBlock):
        if pPlug == mjSoftIK.outIKTrans:
            toggle = pDataBlock.inputValue(mjSoftIK.toggle).asBool()

            startMatrix = pDataBlock.inputValue(mjSoftIK.baseLocMat).asMatrix()
            ctrlMatrix = pDataBlock.inputValue(mjSoftIK.ctrlLocMat).asMatrix()

            startP = om.MPoint(startMatrix(3, 0), startMatrix(3, 1), startMatrix(3, 2))
            endP = om.MPoint(ctrlMatrix(3, 0), ctrlMatrix(3, 1), ctrlMatrix(3, 2))
            outIKTransX = pDataBlock.outputValue(mjSoftIK.outIKTransX)
            outIKTransY = pDataBlock.outputValue(mjSoftIK.outIKTransY)
            outIKTransZ = pDataBlock.outputValue(mjSoftIK.outIKTransZ)

            if toggle:
                chainDist = pDataBlock.inputValue(mjSoftIK.chainLength).asDouble()
                softDist = pDataBlock.inputValue(mjSoftIK.softAttr).asDouble()
                hardDist = chainDist - softDist

                ctrlDist = startP.distanceTo(endP)

                if ctrlDist >= hardDist and not softDist == 0:
                    ikDist = softDist*(1-math.exp((-(ctrlDist-hardDist))/softDist))+hardDist
                else:
                    ikDist = ctrlDist

                startVector = om.MVector(startP)
                endVector = om.MVector(endP)

                normalVector = (startVector - endVector).normal()
                ikVector = startVector + normalVector * -ikDist

            else:
                ikVector = om.MVector(endP)

            outIKTransX.setDouble(ikVector.x)
            outIKTransY.setDouble(ikVector.y)
            outIKTransZ.setDouble(ikVector.z)
            outIKTransX.setClean()
            outIKTransY.setClean()
            outIKTransZ.setClean()


def nodeCreator():
    return ompx.asMPxPtr(mjSoftIK())

def nodeInitializer():
    nAttr = om.MFnNumericAttribute()
    uAttr = om.MFnUnitAttribute()
    mAttr = om.MFnMatrixAttribute()

    mjSoftIK.baseLocMat = mAttr.create('startMatrix', 'sm', om.MFnMatrixAttribute.kDouble)
    mjSoftIK.addAttribute(mjSoftIK.baseLocMat)
    mjSoftIK.ctrlLocMat = mAttr.create('ctrlMatrix', 'cm', om.MFnMatrixAttribute.kDouble)
    mjSoftIK.addAttribute(mjSoftIK.ctrlLocMat)

    mjSoftIK.softAttr = nAttr.create('softDistance', 'sd', om.MFnNumericData.kDouble, 0.2)
    mjSoftIK.addAttribute(mjSoftIK.softAttr)
    mjSoftIK.chainLength = nAttr.create('chainLength', 'cl', om.MFnNumericData.kDouble)
    mjSoftIK.addAttribute(mjSoftIK.chainLength)

    mjSoftIK.toggle = nAttr.create('softIkToggle', 'tog', om.MFnNumericData.kInt, 1)
    nAttr.setMin(0)
    nAttr.setMax(1)
    mjSoftIK.addAttribute(mjSoftIK.toggle)

    mjSoftIK.outIKTransX = uAttr.create('outIkTranslateX', 'otX', om.MFnUnitAttribute.kDistance)
    mjSoftIK.outIKTransY = uAttr.create('outIkTranslateY', 'otY', om.MFnUnitAttribute.kDistance)
    mjSoftIK.outIKTransZ = uAttr.create('outIkTranslateZ', 'otZ', om.MFnUnitAttribute.kDistance)
    mjSoftIK.outIKTrans = nAttr.create('outIkTranslate', 'ot', mjSoftIK.outIKTransX,
                                       mjSoftIK.outIKTransY, mjSoftIK.outIKTransZ)
    mjSoftIK.addAttribute(mjSoftIK.outIKTrans)

    mjSoftIK.attributeAffects(mjSoftIK.baseLocMat, mjSoftIK.outIKTrans)
    mjSoftIK.attributeAffects(mjSoftIK.ctrlLocMat, mjSoftIK.outIKTrans)
    mjSoftIK.attributeAffects(mjSoftIK.softAttr, mjSoftIK.outIKTrans)
    mjSoftIK.attributeAffects(mjSoftIK.chainLength, mjSoftIK.outIKTrans)
    mjSoftIK.attributeAffects(mjSoftIK.toggle, mjSoftIK.outIKTrans)


def initializePlugin(obj):
    plugin = ompx.MFnPlugin(obj, NAME, VERSION, MAYAVERSION)
    try:
        plugin.registerNode(NODENAME, NODEID, nodeCreator, nodeInitializer)
    except RuntimeError:
        sys.stderr.write("Failed to register node: %s" % NODENAME)


def uninitializePlugin(obj):
    plugin = ompx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(NODEID)
    except Exception as err:
        sys.stderr.write("Failed to deregister node: %s\n%s" % (NODENAME, err))