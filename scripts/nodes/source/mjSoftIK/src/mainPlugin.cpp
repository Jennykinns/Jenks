#include "mjSoftIK.h"
#include <maya/MFnPlugin.h>

MStatus initializePlugin(MObject obj) {
	MStatus result;
	MFnPlugin plugin(obj, "MattJenkins", "3.0", "Any");
	result = plugin.registerNode("mjSoftIK", mjSoftIK::id, mjSoftIK::creator,
		mjSoftIK::initialize, MPxNode::kDependNode);

	return result;
}

MStatus uninitializePlugin(MObject obj) {
	MStatus result;
	MFnPlugin plugin(obj);
	result = plugin.deregisterNode(mjSoftIK::id);
	return result;
}