#include "mjSoftIK.h"

MTypeId mjSoftIK::id(0x0012ad42);


mjSoftIK::mjSoftIK() {}
mjSoftIK::~mjSoftIK() {}

MStatus mjSoftIK::compute(const MPlug& plug, MDataBlock& data) {
	MStatus returnStatus;
	if (plug == aOutIKTrans) {
		if (returnStatus != MS::kSuccess) {
			cerr << "ERROR getting data" << endl;
		}
		MDataHandle outTransXHdl = data.outputValue(aOutIKTransX, &returnStatus);
		MDataHandle outTransYHdl = data.outputValue(aOutIKTransY, &returnStatus);
		MDataHandle outTransZHdl = data.outputValue(aOutIKTransZ, &returnStatus);
		MMatrix startMatrix = data.inputValue(aBaseLocMat, &returnStatus).asMatrix();
		MMatrix endMatrix = data.inputValue(aCtrlLocMat, &returnStatus).asMatrix();
		bool toggle = data.inputValue(aToggle, &returnStatus).asBool();


		MPoint startP = MPoint(startMatrix(3, 0), startMatrix(3, 1), startMatrix(3, 2));
		MPoint endP = MPoint(endMatrix(3, 0), endMatrix(3, 1), endMatrix(3, 2));

		if (toggle) {
			double chainDist = data.inputValue(aChainLength, &returnStatus).asDouble();
			double softDist = data.inputValue(aSoftAttr, &returnStatus).asDouble();
			double hardDist = chainDist - softDist;

			double ctrlDist = startP.distanceTo(endP);

			double ikDist;
			if (ctrlDist >= hardDist && softDist != 0) {
				ikDist = softDist*(1-exp((-(ctrlDist-hardDist))/softDist))+hardDist;
			}
			else {
				ikDist = ctrlDist
			}

			MVector startV = MVector(startP);
			MVector endV = MVector(endP);

			MVector normalV = (startV - endV).normal()
			MVector ikV = startV + normalV * -ikDist
		}
		else {
			MVector ikV = MVector(endP)
		}

		outTransXHdl.setDouble(ikV.x)
		outTransYHdl.setDouble(ikV.y)
		outTransZHdl.setDouble(ikV.z)
		outTransXHdl.setClean()
		outTransYHdl.setClean()
		outTransZHdl.setClean()





	}
	else {
		return MS::kUnknownParameter;
	}

	return MS::kSuccess;
}

void* mjSoftIK::creator() {
	return new mjSoftIK();
}

MStatus mjSoftIK::initialize() {
	MFnNumericAttribute nAttr;
	MFnUnitAttribute uAttr;
	MFnTypedAttribute tAttr;
	MFnEnumAttribute eAttr;
	MFnMatrixAttribute mAttr;

	aBaseLocMat = mAttr.create("startMatrix", "sm", MFnMatrixAttribute::kDouble);
	addAttribute(aBaseLocMat);
	aCtrlLocMat = mAttr.create("ctrlMatrix", "cm", MFnMatrixAttribute::kDouble);
	addAttribute(aCtrlLocMat);

	aSoftAttr = nAttr.create("softDistance", "sd", MFnNumericAttribute::kDouble);
	addAttribute(aSoftAttr);
	aChainLength = nAttr.create("chainLength", "cd", MFnNumericAttribute::kDouble);
	addAttribute(aChainLength);

	aToggle = nAttr.create("softIkToggle", "tog", MFnNumericAttribute::kInt);
	nAttr.setMin(0);
	nAttr.setMax(1);
	addAttribute(aToggle);

	aOutIKTransX = uAttr.create("outIkTranslateX", "otX", MFnUnitAttribute::kDistance);
	aOutIKTransY = uAttr.create("outIkTranslateX", "otY", MFnUnitAttribute::kDistance);
	aOutIKTransZ = uAttr.create("outIkTranslateX", "otZ", MFnUnitAttribute::kDistance);
	aOutIKTrans = nAttr.create("outIkTranslate", "ot", aOutIKTransX, aOutIKTransY, aOutIKTransZ);
	addAttribute(aOutIKTrans);

	attributeAffects(aBaseLocMat, aOutIKTrans);
	attributeAffects(aCtrlLocMat, aOutIKTrans);
	attributeAffects(aSoftAttr, aOutIKTrans);
	attributeAffects(aChainLength, aOutIKTrans);
	attributeAffects(aToggle, aOutIKTrans);

	return MS::kSuccess;
}