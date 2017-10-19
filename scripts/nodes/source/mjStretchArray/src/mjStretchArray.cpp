#include "mjStretchArray.h"


MTypeId mjStretchArray::id(0x0012ad40);
MObject mjStretchArray::aCurrentDistance;
MObject mjStretchArray::aStartMatrix;
MObject mjStretchArray::aEndMatrix;
MObject mjStretchArray::aOperation;
MObject mjStretchArray::aMode;
MObject mjStretchArray::aGlobalScale;
MObject mjStretchArray::aCurveDistance;
MObject mjStretchArray::aOriginalDistance;
MObject mjStretchArray::aOriginalJointDistance;
MObject mjStretchArray::aOutDistance;
MIntArray mjStretchArray::jointDistanceIndices;
MDoubleArray mjStretchArray::jointDistanceVals;

mjStretchArray::mjStretchArray() {}
mjStretchArray::~mjStretchArray() {}

void mjStretchArray::postConstructor() {
	MObject node = thisMObject();
	MCallbackId id = MNodeMessage::addAttributeChangedCallback(node, attributeChangedCallback, NULL);
}

MStatus mjStretchArray::compute(const MPlug& plug, MDataBlock& data) {
	MStatus returnStatus;
	int jointDistanceArrayLen = jointDistanceIndices.length();
	if (plug == aOutDistance) {
		if (returnStatus != MS::kSuccess) {
			cerr << "ERROR getting data" << endl;
		}
		else {
			MArrayDataHandle outDistanceArrayHdl = data.outputArrayValue(aOutDistance, &returnStatus);
			MArrayDataBuilder outDistanceBuilder = outDistanceArrayHdl.builder();
			MMatrix startMatrix = data.inputValue(aStartMatrix, &returnStatus).asMatrix();
			MMatrix endMatrix = data.inputValue(aEndMatrix, &returnStatus).asMatrix();
			float globalScale = data.inputValue(aGlobalScale, &returnStatus).asFloat();
			double curveDistance = data.inputValue(aCurveDistance, &returnStatus).asDouble();
			double originalDistance = data.inputValue(aOriginalDistance, &returnStatus).asDouble();
			short operation = data.inputValue(aOperation, &returnStatus).asShort();
			short mode = data.inputValue(aMode, &returnStatus).asShort();
			double outValue;
			double scaledDistance;
			double percentage;
			// distance
			double distance;
			if (mode == 1) {
				distance = curveDistance;
			}
			else {
				MPoint startPoint = MPoint(startMatrix(3, 0), startMatrix(3, 1), startMatrix(3, 2));
				MPoint endPoint = MPoint(endMatrix(3, 0), endMatrix(3, 1), endMatrix(3, 2));
				distance = startPoint.distanceTo(endPoint);
			}
			// percentage
			if (originalDistance == 0 || globalScale == 0) {
				scaledDistance = 0;
				percentage = 0;
			}
			else {
				scaledDistance = originalDistance * globalScale;
				percentage = distance / scaledDistance;
			}
			// joint translate
			for (int i = 0; i < jointDistanceArrayLen; i++) {
				MDataHandle newValueHdl = outDistanceBuilder.addElement(jointDistanceIndices[i]);
				if ((operation == 0 && distance > scaledDistance)
					|| (operation == 1 && distance < scaledDistance)
					|| operation == 2) {
					outValue = percentage * jointDistanceVals[i];
				}
				else {
					outValue = jointDistanceVals[i];
				}
				newValueHdl.setDouble(outValue);
			}
			outDistanceArrayHdl.setAllClean();
		}
	}
	else if (plug == aCurrentDistance) {
		if (returnStatus != MS::kSuccess) {
			cerr << "ERROR getting data" << endl;
		}
		else {
			MDataHandle currentDistanceOutHdl = data.outputValue(aCurrentDistance);
			double distance = 0;
			for (int i = 0; i < jointDistanceArrayLen; i++) {
				distance += jointDistanceVals[i];
			}
			currentDistanceOutHdl.setDouble(distance);
			currentDistanceOutHdl.setClean();
		}
	}
	else {
		return MS::kUnknownParameter;
	}

	return MS::kSuccess;
}

void mjStretchArray::attributeChangedCallback(MNodeMessage::AttributeMessage msg, MPlug & plug, MPlug & otherPlug, void*) {
	if (msg & MNodeMessage::kAttributeSet
			|| msg & MNodeMessage::kAttributeArrayAdded
			|| msg & MNodeMessage::kAttributeArrayRemoved) {
		MPlug parentPlug;
		MIntArray childrenPlugs;
		MObject plugAttribute = plug.attribute();
		MObject originalJointDistanceAttribute = aOriginalJointDistance;
		if (plugAttribute.operator==(originalJointDistanceAttribute)) {
			parentPlug = plug.array();
			parentPlug.getExistingArrayAttributeIndices(childrenPlugs);
			jointDistanceIndices.setLength(childrenPlugs.length());
			jointDistanceVals.setLength(childrenPlugs.length());
			int childrenPlugsLen = childrenPlugs.length();
			for (int i = 0; i < childrenPlugsLen; i++) {
				int index = childrenPlugs[i];
				MPlug childPlug = parentPlug.elementByLogicalIndex(i);
				jointDistanceIndices[i] = index;
				jointDistanceVals[i] = childPlug.asDouble();
			}
		}
	}
	else {
		return;
	}
}

void* mjStretchArray::creator() {
	return new mjStretchArray();
}

MStatus mjStretchArray::initialize() {
	MFnNumericAttribute nAttr;
	MFnUnitAttribute uAttr;
	MFnMatrixAttribute mAttr;
	MFnEnumAttribute eAttr;

	MStatus stat;

	aCurrentDistance = uAttr.create("currentDistance", "curD", MFnUnitAttribute::kDistance);
	uAttr.setWritable(false);
	addAttribute(aCurrentDistance);

	aStartMatrix = mAttr.create("startMatrix", "sm", MFnMatrixAttribute::kDouble);
	uAttr.setReadable(false);
	addAttribute(aStartMatrix);

	aEndMatrix = mAttr.create("endMatrix", "em", MFnMatrixAttribute::kDouble);
	uAttr.setReadable(false);
	addAttribute(aEndMatrix);

	aOperation = eAttr.create("operation", "op", 0);
	eAttr.addField("Greater Than", 0);
	eAttr.addField("Less Than", 1);
	eAttr.addField("Both", 2);
	eAttr.setKeyable(true);
	addAttribute(aOperation);

	aMode = eAttr.create("mode", "md", 0);
	eAttr.addField("Between Points", 0);
	eAttr.addField("Distance", 1);
	eAttr.setKeyable(true);
	addAttribute(aMode);

	aGlobalScale = nAttr.create("globalScale", "gs", MFnNumericData::kFloat, 1);
	nAttr.setKeyable(true);
	nAttr.setReadable(false);
	addAttribute(aGlobalScale);

	aCurveDistance = uAttr.create("curveDistance", "cd", MFnUnitAttribute::kDistance);
	uAttr.setKeyable(true);
	uAttr.setReadable(false);
	addAttribute(aCurveDistance);

	aOriginalDistance = uAttr.create("originalDistance", "origD", MFnUnitAttribute::kDistance);
	uAttr.setKeyable(true);
	uAttr.setReadable(false);
	addAttribute(aOriginalDistance);

	aOriginalJointDistance = uAttr.create("originalJointDistance", "ojd", MFnUnitAttribute::kDistance);
	uAttr.setArray(true);
	uAttr.setKeyable(true);
	uAttr.setReadable(false);
	addAttribute(aOriginalJointDistance);

	aOutDistance = uAttr.create("outDistance", "od", MFnUnitAttribute::kDistance);
	uAttr.setArray(true);
	uAttr.setUsesArrayDataBuilder(true);
	uAttr.setWritable(false);
	addAttribute(aOutDistance);

	attributeAffects(aStartMatrix, aOutDistance);
	attributeAffects(aEndMatrix, aOutDistance);
	attributeAffects(aOperation, aOutDistance);
	attributeAffects(aMode, aOutDistance);
	attributeAffects(aGlobalScale, aOutDistance);
	attributeAffects(aCurveDistance, aOutDistance);
	attributeAffects(aOriginalDistance, aOutDistance);
	attributeAffects(aOriginalJointDistance, aOutDistance);

	attributeAffects(aStartMatrix, aCurrentDistance);
	attributeAffects(aEndMatrix, aCurrentDistance);
	attributeAffects(aOriginalJointDistance, aCurrentDistance);


	return MS::kSuccess;
}