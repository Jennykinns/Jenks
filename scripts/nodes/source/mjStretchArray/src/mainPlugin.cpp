#include "mjStretchArray.h"
#include <maya/MFnPlugin.h>

MStatus initializePlugin(MObject obj) {
	MStatus result;
	MFnPlugin plugin(obj, "MattJenkins", "3.0", "Any");
	result = plugin.registerNode("mjStretchArray", mjStretchArray::id, mjStretchArray::creator,
		mjStretchArray::initialize, MPxNode::kDependNode);

	MGlobal::executeCommand("global proc modeUpdate ( string $nodeName ){\n\
							    string $attrName = $nodeName + \".mode\";\n\
							    if (`getAttr $attrName` == 1){\n\
							        editorTemplate -dimControl $nodeName \"curveDistance\" false;\n\
							        editorTemplate -dimControl $nodeName \"startMatrix\" true;\n\
							        editorTemplate -dimControl $nodeName \"endMatrix\" true;\n\
							    } else {\n\
							        editorTemplate -dimControl $nodeName \"curveDistance\" true;\n\
							        editorTemplate -dimControl $nodeName \"startMatrix\" false;\n\
							        editorTemplate -dimControl $nodeName \"endMatrix\" false;\n\
							    }\n\
							}\n\
							\n\
							global proc origTransUpdate (string $attrArrayName){\n\
							    string $buffer[];\n\
							    tokenize $attrArrayName \".\" $buffer;\n\
							    string $nodeName = ($buffer[0] + $buffer[1]);\n\
							    $layoutName = \"origTransLay\";\n\
							    if(`columnLayout -ex $layoutName`){\n\
							        deleteUI -layout $layoutName;\n\
							    }\n\
							    columnLayout $layoutName;\n\
							    int $arrayLen = `getAttr -size $attrArrayName`;\n\
							    for($i=0; $i<$arrayLen; ++$i){\n\
							        string $attrName = $attrArrayName+\"[\"+(string)$i+\"]\";\n\
							        string $fieldID = \"origTransAttrGrp\"+(string)($i);\n\
							        string $label = \"Original Joint Distance \"+ ($i);\n\
							        attrFieldSliderGrp -attribute $attrName -parent $layoutName -label $label -cw2 175 150 -co2 0 40 $fieldID;\n\
							    }\n\
							}\n\
							\n\
							global proc addOrigTrans (string $attrArray){\n\
							    $attrArrayLen = `getAttr -s $attrArray`;\n\
							    $attr = $attrArray+\"[\"+(string)$attrArrayLen+\"]\";\n\
							    setAttr $attr 0;\n\
							}\n\
							\n\
							global proc delOrigTrans (string $attrArray){\n\
							    $attrArrayLen = `getAttr -s $attrArray`;\n\
							    $attr = $attrArray+\"[\"+(string)($attrArrayLen-1)+\"]\";\n\
							    removeMultiInstance -b true $attr;\n\
							}\n\
							\n\
							global proc origTransBtnBuild (string $nodeName){\n\
							    $layout = `rowLayout -nc 2 -adj 1 \"origTransBtnsLay\"`;\n\
							    $command = \"addOrigTrans(\\\"\"+$nodeName+\"\\\")\";\n\
							    $btnName = \"addOrigTransBtn\";\n\
							    button -label \"Add Entry\" -c $command -p \"origTransBtnsLay\" $btnName;\n\
							    $delCommand = \"delOrigTrans(\\\"\"+$nodeName+\"\\\")\";\n\
							    $delBtnName = \"delOrigTransBtn\";\n\
							    button -label \"Remove Entry\" -c $delCommand $delBtnName;\n\
							}\n\
							\n\
							global proc origTransBtnUpdate (string $nodeName){\n\
							    $command = \"addOrigTrans(\\\"\"+$nodeName+\"\\\")\";\n\
							    $btnName = \"addOrigTransBtn\";\n\
							    button -e -c $command $btnName;\n\
							    $delCommand = \"delOrigTrans(\\\"\"+$nodeName+\"\\\")\";\n\
							    $delBtnName = \"delOrigTransBtn\";\n\
							    button -e -c $delCommand $delBtnName;\n\
							}\n\
							\n\
							global proc matrixBuild (string $attrName){\n\
							    string $buffer[];\n\
							    tokenize $attrName \".\" $buffer;\n\
							    $id = $buffer[1]+\"Txt\";\n\
							    $command = \"connectMatrix(\\\"\"+$attrName+\"\\\")\";\n\
								$label = capitalizeString(substitute(\"Matrix\", $buffer[1], \"\"))+\" Object\";\n\
							    textFieldGrp -label $label -cc $command $id;\n\
							    $connObj = `listConnections $attrName`;\n\
							    textFieldGrp -e -tx $connObj $id;\n\
							}\n\
							\n\
							global proc matrixUpdate (string $attrName){\n\
							    string $buffer[];\n\
							    tokenize $attrName \".\" $buffer;\n\
							    $id = $buffer[1]+\"Txt\";\n\
							    $destAttr = $attrName;\n\
							    $connObj = `listConnections $destAttr`;\n\
							    $command = \"connectMatrix(\\\"\"+$attrName+\"\\\")\";\n\
							    textFieldGrp -e -tx $connObj $id;\n\
							    textFieldGrp -e -cc $command $id;\n\
							}\n\
							\n\
							global proc connectMatrix (string $attrName){\n\
							    string $buffer[];\n\
							    tokenize $attrName \".\" $buffer;\n\
							    $destAttr = $attrName;\n\
							    $id = $buffer[1]+\"Txt\";\n\
							    $text = `textFieldGrp -q -tx $id`;\n\
							    $attr = $text + \".wm\";\n\
							    $connObj = `listConnections $destAttr`;\n\
							    if ($text == \"\"){\n\
							        $inConn = `listConnections -plugs true $destAttr`;\n\
							        catchQuiet(`disconnectAttr $inConn $destAttr`);\n\
							    } else {\n\
							        if (`objExists $text`){\n\
							            $objAttr = `listAttr $text`;\n\
							            if (`stringArrayFind \"worldMatrix\" 0 $objAttr` > 0){\n\
							                $inConn = `listConnections -plugs true $destAttr`;\n\
							                catchQuiet(`disconnectAttr $inConn $destAttr`);\n\
							                connectAttr $attr $destAttr;\n\
							            } else {\n\
							                warning \"No WorldMatrix attribute on node\";\n\
							                textFieldGrp -e -tx $connObj $id;\n\
							            }\n\
							        } else {\n\
							            warning \"No matching object\";\n\
							            textFieldGrp -e -tx $connObj $id;\n\
							        }\n\
							    }\n\
							}\n\
							\n\
							\n\
							global proc AEmjStretchArrayTemplate ( string $nodeName ){\n\
							    editorTemplate -beginScrollLayout;\n\
							        editorTemplate -addControl \"currentDistance\";\n\
							        editorTemplate -beginLayout (\"mjStretch Attributes\") -collapse 0;\n\
							            editorTemplate -addControl \"globalScale\";\n\
							            editorTemplate -addControl \"operation\";\n\
							            editorTemplate -addControl \"mode\" modeUpdate;\n\
							            editorTemplate -callCustom \"matrixBuild\" \"matrixUpdate\" \"startMatrix\";\n\
							            editorTemplate -callCustom \"matrixBuild\" \"matrixUpdate\" \"endMatrix\";\n\
							            editorTemplate -addControl \"curveDistance\";\n\
							            editorTemplate -addControl \"originalDistance\";\n\
							            editorTemplate -addSeparator;\n\
							            editorTemplate -callCustom \"origTransBtnBuild\" \"origTransBtnUpdate\" \"originalJointDistance\";\n\
							            editorTemplate -callCustom \"origTransUpdate\" \"origTransUpdate\" \"originalJointDistance\";\n\
							        editorTemplate -endLayout;\n\
							        AEabstractBaseCreateTemplate $nodeName;\n\
							    editorTemplate -endScrollLayout;\n\
							}");
	return result;
}

MStatus uninitializePlugin(MObject obj) {
	MStatus result;
	MFnPlugin plugin(obj);
	result = plugin.deregisterNode(mjStretchArray::id);
	return result;
}