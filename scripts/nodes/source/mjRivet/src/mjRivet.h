#include <string.h>
#include <math.h>
#include <maya/MIOStream.h>

#include <maya/MPxNode.h>

#include <maya/MTypeId.h>
#include <maya/MPlug.h>
//#include <maya/MPlugArray.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
//#include <maya/MArrayDataHandle.h>
//#include <maya/MArrayDataBuilder.h>
//#include <maya/MNodeMessage.h>
#include <maya/MDistance.h>
#include <maya/MAngle.h>
#include <maya/MFnNurbsSurface.h>
//#include <maya/MFnNurbsSurfaceData.h>
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
//#include <maya/MIntArray.h>
//#include <maya/MDoubleArray.h>
#include <maya/MGlobal.h>

class mjRivet : public MPxNode {
public:
	mjRivet();
	virtual ~mjRivet();

	virtual MStatus compute(const MPlug& plug, MDataBlock& data);
	static void* creator();
	static MStatus initialize();

	static MTypeId id;
	static MObject aInputSurface;
	static MObject aParentInverseMatrix;
	static MObject aParameters;
	static MObject aParameterU;
	static MObject aParameterV;
	static MObject aOperation;
	static MObject aRotationOrder;
	static MObject aOutRot;
	static MObject aOutRotX;
	static MObject aOutRotY;
	static MObject aOutRotZ;
	static MObject aOutTrans;
	static MObject aOutTransX;
	static MObject aOutTransY;
	static MObject aOutTransZ;

};