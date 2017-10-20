#include <string.h>
#include <math.h>
#include <maya/MIOStream.h>

#include <maya/MPxNode.h>

#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MDistance.h>
#include <maya/MAngle.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MEulerRotation.h>

#include <maya/MFnNumericAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnDependencyNode.h>

#include <maya/MPoint.h>
#include <maya/MMatrix.h>
#include <maya/MGlobal.h>

class mjSoftIK : public MPxNode {
public:
	mjSoftIK();
	virtual ~mjSoftIK();

	virtual MStatus compute(const MPlug& plug, MDataBlock& data);
	static void* creator();
	static MStatus initialize();

	static MTypeId id;
	static MObject aBaseLocMat;
	static MObject aCtrlLocMat;
	static MObject aSoftAttr;
	static MObject aChainLength;
	static MObject aToggle;
	static MObject aOutIKTransX;
	static MObject aOutIKTransY;
	static MObject aOutIKTransZ;
	static MObject aOutIKTrans;


	static MTypeId id;
};