#pragma once
#include <string.h>
#include <math.h>
#include <maya/MIOStream.h>

#include <maya/MPxNode.h>

#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MArrayDataHandle.h>
#include <maya/MArrayDataBuilder.h>
#include <maya/MNodeMessage.h>

#include <maya/MFnNumericAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnDependencyNode.h>

#include <maya/MPoint.h>
#include <maya/MMatrix.h>
#include <maya/MIntArray.h>
#include <maya/MDoubleArray.h>
#include <maya/MGlobal.h>

class mjStretchArray : public MPxNode {
public:
	mjStretchArray();
	virtual ~mjStretchArray();

	virtual MStatus compute(const MPlug& plug, MDataBlock& data);

	static void* creator();
	virtual void postConstructor();
	static MStatus initialize();

	static void attributeChangedCallback(MNodeMessage::AttributeMessage msg, MPlug & plug, MPlug & otherPlug, void*);

	static MTypeId id;
	static MObject aCurrentDistance;
	static MObject aStartMatrix;
	static MObject aEndMatrix;
	static MObject aOperation;
	static MObject aMode;
	static MObject aGlobalScale;
	static MObject aCurveDistance;
	static MObject aOriginalDistance;
	static MObject aOriginalJointDistance;
	static MObject aOutDistance;

	static MIntArray jointDistanceIndices;
	static MDoubleArray jointDistanceVals;

};