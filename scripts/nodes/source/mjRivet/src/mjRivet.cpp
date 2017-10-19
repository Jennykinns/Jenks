#include "mjRivet.h"

MTypeId mjRivet::id(0x0012ad41);
MObject mjRivet::aInputSurface;
MObject mjRivet::aParentInverseMatrix;
MObject mjRivet::aParameters;
MObject mjRivet::aParameterU;
MObject mjRivet::aParameterV;
MObject mjRivet::aOperation;
MObject mjRivet::aRotationOrder;
MObject mjRivet::aOutRot;
MObject mjRivet::aOutRotX;
MObject mjRivet::aOutRotY;
MObject mjRivet::aOutRotZ;
MObject mjRivet::aOutTrans;
MObject mjRivet::aOutTransX;
MObject mjRivet::aOutTransY;
MObject mjRivet::aOutTransZ;

mjRivet::mjRivet() {}
mjRivet::~mjRivet() {}

MStatus mjRivet::compute(const MPlug& plug, MDataBlock& data) {
	MStatus returnStatus;
	if (plug == aOutRotX || plug == aOutRotY || plug == aOutRotZ || plug == aOutRot) {
		if (returnStatus != MS::kSuccess) {
			cerr << "ERROR getting data" << endl;
		}
		MDataHandle outRotHdl = data.outputValue(aOutRot, &returnStatus);
		short operation = data.outputValue(aOperation, &returnStatus).asShort();
		short rotationOrder = data.outputValue(aRotationOrder, &returnStatus).asShort();
		// MFnNurbsSurface inSurface = data.inputValue(aInputSurface, &returnStatus).asNurbsSurfaceTransformed();
		MFnNurbsSurface inSurface(data.inputValue(aInputSurface, &returnStatus).asNurbsSurfaceTransformed());
		MMatrix parentInvMatrix = data.inputValue(aParentInverseMatrix, &returnStatus).asMatrix();
		double paramU = data.inputValue(aParameterU, &returnStatus).asDouble();
		double paramV = data.inputValue(aParameterV, &returnStatus).asDouble();

		// rotate
		MVector uTangentVector;
		MVector vTangentVector;
		MVector tangentVector;
		MVector normalVector = inSurface.normal(paramU, paramV, MSpace::kWorld);
		inSurface.getTangents(paramU, paramV, uTangentVector, vTangentVector, MSpace::kWorld);
		if (operation == 0) {
			tangentVector = uTangentVector;
		}
		else {
			tangentVector = vTangentVector;
		}

		MVector binormalVector = normalVector.operator^(tangentVector);

		double matrixDoubles[4][4] = { tangentVector.x, tangentVector.y, tangentVector.z, 0.0,
			                           normalVector.x, normalVector.y, normalVector.z, 0.0,
						               binormalVector.x, binormalVector.y, binormalVector.z, 0.0,
									   0.0, 0.0, 0.0, 0.0 };

		MMatrix rotMatrix = MMatrix(matrixDoubles);
		rotMatrix = rotMatrix.operator*(parentInvMatrix);
		MTransformationMatrix transformMatrix = MTransformationMatrix(rotMatrix);
		MEulerRotation eulerRot = transformMatrix.eulerRotation().reorder(MEulerRotation::RotationOrder(rotationOrder));

		// set values
		outRotHdl.set3Double(eulerRot.x, eulerRot.y, eulerRot.z);
		outRotHdl.setClean();
	}
	else if (plug == aOutTransX || plug == aOutTransY || plug == aOutTransZ || plug == aOutTrans) {
		if (returnStatus != MS::kSuccess) {
			cerr << "ERROR getting data" << endl;
		}
		MDataHandle outTransHdl = data.outputValue(aOutTrans, &returnStatus);
		// MFnNurbsSurface inSurface = data.inputValue(aInputSurface, &returnStatus).asNurbsSurfaceTransformed();
		MFnNurbsSurface inSurface(data.inputValue(aInputSurface, &returnStatus).asNurbsSurfaceTransformed());
		MMatrix parentInvMatrix = data.inputValue(aParentInverseMatrix, &returnStatus).asMatrix();
		double paramU = data.inputValue(aParameterU, &returnStatus).asDouble();
		double paramV = data.inputValue(aParameterV, &returnStatus).asDouble();

		// translate
		MPoint rivetPoint;
		inSurface.getPointAtParam(paramU, paramV, rivetPoint, MSpace::kWorld);

		double rivetPointDoubleMatrix[4][4] = { 1, 0.0, 0.0, 0.0,
												0.0, 1, 0.0, 0.0,
												0.0, 0.0, 1, 0.0,
												rivetPoint.x, rivetPoint.y, rivetPoint.z, 1 };
		MMatrix rivetMatrix = MMatrix(rivetPointDoubleMatrix);
		rivetMatrix = rivetMatrix.operator*(parentInvMatrix);
		MTransformationMatrix rivetTransMatrix = MTransformationMatrix(rivetMatrix);
		MVector rivetTrans = rivetTransMatrix.getTranslation(MSpace::kWorld);

		// set values
		outTransHdl.set3Double(rivetTrans.x, rivetTrans.y, rivetTrans.z);
		outTransHdl.setClean();
	}
	else {
		return MS::kUnknownParameter;
	}

	return MS::kSuccess;
}

void* mjRivet::creator() {
	return new mjRivet();
}

MStatus mjRivet::initialize() {
	MFnNumericAttribute nAttr;
	MFnUnitAttribute uAttr;
	MFnTypedAttribute tAttr;
	MFnEnumAttribute eAttr;
	MFnMatrixAttribute mAttr;

	MStatus stat;

	aInputSurface = tAttr.create("inputSurface", "is", MFnData::kNurbsSurface);
	tAttr.setReadable(false);
	tAttr.setHidden(true);
	addAttribute(aInputSurface);

	aParentInverseMatrix = mAttr.create("parentInverseMatrix", "pim", MFnMatrixAttribute::kDouble);
	mAttr.setReadable(false);
	addAttribute(aParentInverseMatrix);

	aParameterU = nAttr.create("parameterU", "pu", MFnNumericData::kDouble);
	aParameterV = nAttr.create("parameterV", "pv", MFnNumericData::kDouble);
	aParameters = nAttr.create("parameterUV", "p", aParameterU, aParameterV);
	nAttr.setKeyable(true);
	nAttr.setReadable(false);
	addAttribute(aParameters);

	aOperation = eAttr.create("operation", "op", 0);
	eAttr.addField("U Tangent", 0);
	eAttr.addField("V Tangent", 1);
	eAttr.setKeyable(true);
	addAttribute(aOperation);

	aRotationOrder = eAttr.create("rotationOrder", "ro", 0);
	eAttr.addField("xyz", 0);
	eAttr.addField("yzx", 1);
	eAttr.addField("zxy", 2);
	eAttr.addField("xzy", 3);
	eAttr.addField("yxz", 4);
	eAttr.addField("zyx", 5);
	eAttr.setKeyable(true);
	addAttribute(aRotationOrder);

	aOutRotX = uAttr.create("outRotateX", "orX", MFnUnitAttribute::kAngle);
	aOutRotY = uAttr.create("outRotateY", "orY", MFnUnitAttribute::kAngle);
	aOutRotZ = uAttr.create("outRotateZ", "orZ", MFnUnitAttribute::kAngle);
	aOutRot = nAttr.create("outRotate", "or", aOutRotX, aOutRotY, aOutRotZ);
	nAttr.setWritable(false);
	addAttribute(aOutRot);

	aOutTransX = uAttr.create("outTranslateX", "otX", MFnUnitAttribute::kDistance);
	aOutTransY = uAttr.create("outTranslateY", "otY", MFnUnitAttribute::kDistance);
	aOutTransZ = uAttr.create("outTranslateZ", "otZ", MFnUnitAttribute::kDistance);
	aOutTrans = nAttr.create("outTranslate", "ot", aOutTransX, aOutTransY, aOutTransZ);
	nAttr.setWritable(false);
	addAttribute(aOutTrans);

	attributeAffects(aInputSurface, aOutRot);
	attributeAffects(aParentInverseMatrix, aOutRot);
	attributeAffects(aParameters, aOutRot);
	attributeAffects(aOperation, aOutRot);
	attributeAffects(aRotationOrder, aOutRot);

	attributeAffects(aInputSurface, aOutTrans);
	attributeAffects(aParentInverseMatrix, aOutTrans);
	attributeAffects(aParameters, aOutTrans);

	return MS::kSuccess;
}