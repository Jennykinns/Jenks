#include "mjRivet.h"
#include <maya/MFnPlugin.h>

MStatus initializePlugin(MObject obj) {
	MStatus result;
	MFnPlugin plugin(obj, "MattJenkins", "3.0", "Any");
	result = plugin.registerNode("mjRivet", mjRivet::id, mjRivet::creator,
		mjRivet::initialize, MPxNode::kDependNode);

	MGlobal::executeCommand("global proc inputSurfaceBuild (string $attrName) {\n\
							    $command = \"connectInputSurface(\\\"\"+$attrName+\"\\\")\";\n\
							    textFieldGrp -label \"Input Surface\" -cc $command \"inputSurfaceTxt\";\n\
							    $connObj = `listConnections $attrName`;\n\
							    textFieldGrp -e -tx $connObj \"inputSurfaceTxt\";\n\
							}\n\
							\n\
							global proc inputSurfaceUpdate (string $attrName) {\n\
							    $connObj = `listConnections $attrName`;\n\
							    $command = \"connectInputSurface(\\\"\"+$attrName+\"\\\")\";\n\
							    textFieldGrp -e -tx $connObj \"inputSurfaceTxt\";\n\
							    textFieldGrp -e -cc $command \"inputSurfaceTxt\";\n\
							}\n\
							\n\
							global proc connectInputSurface(string $attrName) {\n\
							    $text = `textFieldGrp -q -tx \"inputSurfaceTxt\"`;\n\
							    if ($text == \"\"){\n\
							        $inConn = `listConnections -plugs true $attrName`;\n\
							        catchQuiet(`disconnectAttr $inConn $attrName`);\n\
							    } else {\n\
							        $nodeChildren = `listRelatives -c -s $text`;\n\
							        string $shapeNode = $nodeChildren[0];\n\
							        $attr = $shapeNode +\".ws\";\n\
							        $connObj = `listConnections $attrName`;\n\
							        if (`objExists $text`){\n\
							            $objAttr = `listAttr $shapeNode`;\n\
							            if (`stringArrayFind \"worldSpace\" 0 $objAttr` > 0){\n\
							                $inConn = `listConnections -plugs true $attrName`;\n\
							                catchQuiet(`disconnectAttr $inConn $attrName`);\n\
							                connectAttr $attr $attrName;\n\
							            } else {\n\
							                warning \"No WorldSpace attribute on node\";\n\
							                textFieldGrp -e -tx $connObj \"inputSurfaceTxt\";\n\
							            }\n\
							        } else {\n\
							            warning \"No matching object\";\n\
							            textFieldGrp -e -tx $connObj \"inputSurfaceTxt\";\n\
							        }\n\
							    }\n\
							}\n\
							global proc parInvMatrixBuild (string $attrName) {\n\
							    $command = \"connectParInvMatrix(\\\"\"+$attrName+\"\\\")\";\n\
							    textFieldGrp -label \"Parent Inverse Matrix\" -cc $command \"parentInverseMatrixTxt\";\n\
							    $connObj = `listConnections $attrName`;\n\
							    textFieldGrp -e -tx $connObj \"parentInverseMatrixTxt\";\n\
							}\n\
							\n\
							global proc parInvMatrixUpdate (string $attrName) {\n\
							    $connObj = `listConnections $attrName`;\n\
							    $command = \"connectParInvMatrix(\\\"\"+$attrName+\"\\\")\";\n\
							    textFieldGrp -e -tx $connObj \"parentInverseMatrixTxt\";\n\
							    textFieldGrp -e -cc $command \"parentInverseMatrixTxt\";\n\
							}\n\
							global proc connectParInvMatrix (string $attrName){\n\
							    string $buffer[];\n\
							    tokenize $attrName \".\" $buffer;\n\
							    $id = $buffer[1]+\"Txt\";\n\
							    $text = `textFieldGrp -q -tx $id`;\n\
							    $attr = $text + \".parentInverseMatrix\";\n\
							    $connObj = `listConnections $attrName`;\n\
							    if ($text == \"\"){\n\
							        $inConn = `listConnections -plugs true $attrName`;\n\
							        catchQuiet(`disconnectAttr $inConn $attrName`);\n\
							    } else {\n\
							        if (`objExists $text`){\n\
							            $objAttr = `listAttr $text`;\n\
							            if (`stringArrayFind \"parentInverseMatrix\" 0 $objAttr` > 0){\n\
							                $inConn = `listConnections -plugs true $attrName`;\n\
							                catchQuiet(`disconnectAttr $inConn $attrName`);\n\
							                connectAttr $attr $attrName;\n\
							            } else {\n\
							                warning \"No Parent Inverse Matrix attribute on node\";\n\
							                textFieldGrp -e -tx $connObj $id;\n\
							            }\n\
							        } else {\n\
							            warning \"No matching object\";\n\
							            textFieldGrp -e -tx $connObj $id;\n\
							        }\n\
							    }\n\
							}\n\
							\n\
							global proc AEmjRivetTemplate ( string $nodeName ){\n\
							    editorTemplate -beginScrollLayout;\n\
							        editorTemplate -beginLayout (\"mjRivet Attributes\") -collapse 0;\n\
							            editorTemplate -callCustom \"inputSurfaceBuild\" \"inputSurfaceUpdate\" \"inputSurface\";\n\
							            editorTemplate -callCustom \"parInvMatrixBuild\" \"parInvMatrixUpdate\" \"parentInverseMatrix\";\n\
							            editorTemplate -addControl \"parameterUV\";\n\
										editorTemplate -addControl \"operation\";\n\
							            editorTemplate -addControl \"rotationOrder\";\n\
							        editorTemplate -endLayout;\n\
							        AEabstractBaseCreateTemplate $nodeName;\n\
							    editorTemplate -endScrollLayout;\n\
							}");
	return result;
}

MStatus uninitializePlugin(MObject obj) {
	MStatus result;
	MFnPlugin plugin(obj);
	result = plugin.deregisterNode(mjRivet::id);
	return result;
}