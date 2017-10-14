#=================================================================================================================================================
#=================================================================================================================================================
#	JAMMSoft Joint Orient Tool - Joints Orient Tool
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	This tool allows to orient the selected joint or the hierarchy according 
#	to the selected options (Aim, Up, World Up, etc.)
# 
# REQUIRES:
# 	Nothing
# 
# AUTHOR:
# 	Jose Antonio Martin Martin - JoseAntonioMartinMartin@gmail.com
#				     contact@joseantoniomartinmartin.com
#	http://www.joseantoniomartinmartin.com
# 	Copyright 2010 Jose Antonio Martin Martin - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 01/10/2010 - Basic interface and functionality.
#	0.2 - 03/01/2010 - More options in the interface. More functionality too.
#	0.3 - 04/06/2010 - Added funcionality.
#	0.4 - 04/25/2010 - Prep for initial releate (v.1.0).
#	1.0 - 04/27/2010 - First version.
#	1.1 - 04/30/2010 - Minor bug fixes.
# ====================================================================================================================



import maya.cmds as cmds



# ====================================================================================================================
#
# SIGNATURE:
#	orientJointsWindow()
#
# DESCRIPTION:
#	Main function and interface.
# 
# REQUIRES:
# 	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def orientJointsWindow():
	if cmds.window("jammOrientJointsWindow", ex=True) != True:
        
		version = "v 1.0"
		date = "04/27/2010"
		
		cmds.window("jammOrientJointsWindow", w=500, h=400, t=("JAMMSoft Joint Orient Tool - " + version), sizeable=True, titleBar=True)
	
		cmds.formLayout("mainForm")

		cmds.radioButtonGrp("rbgAim", l="Aim Axis:", nrb=3, la3=("X","Y","Z"), sl=1, cw4=(80,40,40,40))
		cmds.radioButtonGrp("rbgUp", l="Up Axis:", nrb=3, la3=("X","Y","Z"), sl=2, cw4=(80,40,40,40))

		cmds.checkBox("chbReverseAim", l="Reverse")
		cmds.checkBox("chbReverseUp", l="Reverse")	

		cmds.separator("sep1", style="in", h=3)


		cmds.radioButtonGrp("rbgAllOrSelected", l="Operate on:", nrb=2, la2=("Hierarchy","Selected"), sl=1, cw3=(80,80,80))	
		cmds.separator("sep2", style="in", h=3)

		cmds.floatFieldGrp("rbgWorldUp", l="World Up: ", nf=3, v1=0.0, v2=1.0, v3=0.0, cw4=(65,50,50,50))
		cmds.button("btnXUp", l="X", w=20, h=20, c=worldUpX)
		cmds.button("btnYUp", l="Y", w=20, h=20, c=worldUpY)
		cmds.button("btnZUp", l="Z", w=20, h=20, c=worldUpZ)			
		cmds.checkBox("chbGuess", l="Guess Up Direction")
		cmds.separator("sep3", style="in", h=3)
	
		cmds.button("btnOrientJoints", l="Orient Joints", al="center", h=40, c=orientJointsUI, ann="Orient Joints")

		cmds.separator("sep4", style="double", h=3)

		cmds.button("btnOrientJointAsOther", l="Orient Joint as Object Selected (Select object + SHIFT Select joint)", al="center", h=25, c=orientJointAsObjectUiManager, ann="Orient Joint as Object Selected (Select object + SHIFT Select joint)")

		cmds.separator("sep5", style="in", h=3)

		cmds.button("btnOrientJointAsWorld", l="Orient Joint as World Axis", al="center", h=25, c=orientJointAsWorldUiManager, ann="Orient Joint as World Axis")

		cmds.separator("sep6", style="double", h=3)

		cmds.floatFieldGrp("rbgManualTweak", l="Manual Tweak: ", nf=3, v1=0.0, v2=0.0, v3=0.0, cw4=(90,60,60,60))	
		cmds.button("btnPlusX", l="+", w=25, h=20, c=addInXValue)
		cmds.button("btnMinusX", l="-", w=25, h=20, c=minusInXValue)
		cmds.button("btnPlusY", l="+", w=25, h=20, c=addInYValue)
		cmds.button("btnMinusY", l="-", w=25, h=20, c=minusInYValue)
		cmds.button("btnPlusZ", l="+", w=25, h=20, c=addInZValue)
		cmds.button("btnMinusZ", l="-", w=25, h=20, c=minusInZValue)	

		cmds.button("btnPlusAll", l="Tweak All +", w=120, h=20, c=rotateAxisManualTweakPlus)
		cmds.button("btnMinusAll", l="Tweak All -", w=120, h=20, c=rotateAxisManualTweakMinus)

		cmds.separator("sep7", style="double", h=3)

		cmds.button("btnShowAxisAll", l="Show Axis on Hierarchy", w=150, h=20, c=showHierarchyLocalAxis)	
		cmds.button("btnHideAxisAll", l="Hide Axis on Hierarchy", w=150, h=20, c=hideHierarchyLocalAxis)	
		cmds.button("btnShowAxisSelected", l="Show Axis on Selected", w=150, h=20, c=showSelectedLocalAxis)	
		cmds.button("btnHideAxisSelected", l="Hide Axis on Selected", w=150, h=20, c=hideSelectedLocalAxis)

		cmds.separator("sep8", style="double", h=3)

		cmds.iconTextButton("lblCopyright", l="Copyright 2010 - Jose Antonio Martin Martin.", w=310, h=20, style="textOnly", c="cmds.showHelp(\"http://www.joseantoniomartinmartin.com\", a=1)")
		cmds.iconTextButton("lblCopyright2", l="All Rights Reserved.", w=310, h=20, style="textOnly", c="cmds.showHelp(\"http://www.joseantoniomartinmartin.com\", a=1)")
		
		cmds.formLayout("mainForm", e=True, attachForm=[('rbgAim', 'left', 0), 
								('rbgAim', 'top', 0),
								('chbReverseAim', 'top', 0), 
								('chbReverseAim', 'left', 210), 
								('chbReverseAim', 'right', 0), 
								('rbgUp', 'left', 0), 
								('rbgUp', 'top', 20), 
								('chbReverseUp', 'top', 20), 
								('chbReverseUp', 'left', 210), 
								('chbReverseUp', 'right', 0), 

								('sep1', 'left', 0), 
								('sep1', 'top', 40),
								('sep1', 'right', 0), 


								('rbgAllOrSelected', 'left', 0), 
								('rbgAllOrSelected', 'top', 45), 
								('rbgAllOrSelected', 'right', 0), 

								('sep2', 'left', 0), 
								('sep2', 'top', 65), 
								('sep2', 'right', 0), 


								('rbgWorldUp', 'left', 0), 
								('rbgWorldUp', 'top', 70), 
									
								('btnXUp', 'left', 255),
								('btnXUp', 'top', 71),
								('btnYUp', 'left', 280),
								('btnYUp', 'top', 71),
								('btnZUp', 'left', 305),
								('btnZUp', 'top', 71),


								('chbGuess', 'left', 10), 
								('chbGuess', 'top', 90), 
								('chbGuess', 'right', 0), 

								('sep3', 'left', 0), 
								('sep3', 'top', 110), 
								('sep3', 'right', 0), 


								('btnOrientJoints', 'left', 0), 
								('btnOrientJoints', 'top', 115), 
								('btnOrientJoints', 'right', 0),
								

								('sep4', 'left', 0), 
								('sep4', 'top', 160), 
								('sep4', 'right', 0), 


								('btnOrientJointAsOther', 'left', 0), 
								('btnOrientJointAsOther', 'top', 165), 
								('btnOrientJointAsOther', 'right', 0),


								('sep5', 'left', 0), 
								('sep5', 'top', 195), 
								('sep5', 'right', 0), 


								('btnOrientJointAsWorld', 'left', 0), 
								('btnOrientJointAsWorld', 'top', 200), 
								('btnOrientJointAsWorld', 'right', 0),


								('sep6', 'left', 0), 
								('sep6', 'top', 230), 
								('sep6', 'right', 0), 


								('rbgManualTweak', 'left', 0), 
								('rbgManualTweak', 'top', 238), 
								('rbgManualTweak', 'right', 0), 

								('btnPlusX', 'left', 97), 
								('btnPlusX', 'top', 258),
								('btnMinusX', 'left', 122), 
								('btnMinusX', 'top', 258),

								('btnPlusY', 'left', 160), 
								('btnPlusY', 'top', 258),
								('btnMinusY', 'left', 185), 
								('btnMinusY', 'top', 258),

								('btnPlusZ', 'left', 222), 
								('btnPlusZ', 'top', 258),
								('btnMinusZ', 'left', 247), 
								('btnMinusZ', 'top',  258),	

								('btnPlusAll', 'left', 45), 
								('btnPlusAll', 'top', 278),
								('btnMinusAll', 'left', 165), 
								('btnMinusAll', 'top', 278),	

								('sep7', 'left', 0), 
								('sep7', 'top', 303), 
								('sep7', 'right', 0), 							

								('btnShowAxisSelected', 'left', 10), 
								('btnShowAxisSelected', 'top', 311), 
								('btnHideAxisSelected', 'left', 170), 
								('btnHideAxisSelected', 'top', 311), 

								('btnShowAxisAll', 'left', 10), 
								('btnShowAxisAll', 'top', 331), 
								('btnHideAxisAll', 'left', 170), 
								('btnHideAxisAll', 'top', 331), 

								('sep8', 'left', 0), 
								('sep8', 'top', 356), 
								('sep8', 'right', 0), 
						
								('lblCopyright', 'left', 10), 
								('lblCopyright', 'top', 361),
								('lblCopyright2', 'left', 10), 
								('lblCopyright2', 'top', 381)

								])


		cmds.showWindow("jammOrientJointsWindow")
    	else:
	    	cmds.showWindow("jammOrientJointsWindow")



# ====================================================================================================================
#
# SIGNATURE:
#	orientJointsUI(* args)
#
# DESCRIPTION:
# 	Manage the options selected in the interface and 
# 	calls the actual orientJoint method.
# 
# REQUIRES:
# 	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def orientJointsUI(* args):
	aimSelected = cmds.radioButtonGrp("rbgAim", q=True, sl=True)
	upSelected = cmds.radioButtonGrp("rbgUp", q=True, sl=True)

	aimReverse = cmds.checkBox("chbReverseAim", q=True, v=True)
	upReverse = cmds.checkBox("chbReverseUp", q=True, v=True)

	operateOn = cmds.radioButtonGrp("rbgAllOrSelected", q=True, sl=True)

	worldUp = [0,0,0]
	worldUp[0] = cmds.floatFieldGrp("rbgWorldUp", q=True, v1=True)
	worldUp[1] = cmds.floatFieldGrp("rbgWorldUp", q=True, v2=True)
	worldUp[2] = cmds.floatFieldGrp("rbgWorldUp", q=True, v3=True)

	guessUp = cmds.checkBox("chbGuess", q=True, v=True)

	aimAxis = [0,0,0]
	upAxis = [0,0,0]

	if aimReverse == 1:
		aimAxis[aimSelected - 1] = -1
	else:
		aimAxis[aimSelected - 1] = 1

	if upReverse == 1:
		upAxis[upSelected - 1] = -1
	else:
		upAxis[upSelected - 1] = 1

	elemSelected = cmds.ls(typ="joint", sl=True)

	cmds.undoInfo(ock=True)

	if aimSelected == upSelected:
		print("USE: Aim Axis and Up Axis can't be the same.")
	else:
		if elemSelected == None or len(elemSelected) == 0:
			print("USE: Select at least one joint to orient.")
		else:
			if operateOn == 1:
				#Hierarchy
				cmds.select(hi=True)
				jointsToOrient = cmds.ls(typ="joint", sl=True)
			else:
				#Selected
				jointsToOrient = cmds.ls(typ="joint", sl=True)

		

			doOrientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp)
			cmds.select(elemSelected, r=True)

	cmds.undoInfo(cck=True)



# ====================================================================================================================
#
# SIGNATURE:
#	doOrientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp)
#
# DESCRIPTION:
# 	Does the actual joint orientation.
# 
# REQUIRES:
#	jointsToOrient - List of joints to orient.
# 	aimAxis - Aim axis for the joint orient.
# 	upAxis - Up axis for the joint orient.
# 	worldUp - World Up for the joint orient.
# 	guessUp - If selected will calculate the correct Up axis.
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def doOrientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp):
	firstPass = 0
	prevUpVector = [0,0,0]
	for eachJoint in jointsToOrient:
		childJoint = cmds.listRelatives(eachJoint, type="joint", c=True) 
		if childJoint != None:
			if len(childJoint) > 0:

				childNewName = cmds.parent(childJoint, w=True)	#Store the name in case when unparented it changes it's name.

				if guessUp == 0:
					#Not guess Up direction
					
					cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=worldUp, worldUpType="vector"))
					freezeJointOrientation(eachJoint)
					cmds.parent(childNewName, eachJoint)
				else:
					if guessUp == 1:
						#Guess Up direction
						

						parentJoint = cmds.listRelatives(eachJoint, type="joint", p=True) 
						if parentJoint != None :
							if len(parentJoint) > 0:
								posCurrentJoint = cmds.xform(eachJoint, q=True, ws=True, rp=True)
								posParentJoint = cmds.xform(parentJoint, q=True, ws=True, rp=True)
								tolerance = 0.0001

								if (abs(posCurrentJoint[0] - posParentJoint[0]) <= tolerance and abs(posCurrentJoint[1] - posParentJoint[1]) <= tolerance and abs(posCurrentJoint[2] - posParentJoint[2]) <= tolerance):
									aimChild = cmds.listRelatives(childNewName[0], type="joint", c=True) 
									upDirRecalculated = crossProduct(eachJoint, childNewName[0], aimChild[0])
									cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))
								else:
									upDirRecalculated = crossProduct(parentJoint, eachJoint, childNewName[0])
									cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))
							else:
								aimChild = cmds.listRelatives(childNewName[0], type="joint", c=True) 
								upDirRecalculated = crossProduct(eachJoint, childNewName[0], aimChild[0])
						else:
							aimChild = cmds.listRelatives(childNewName[0], type="joint", c=True) 
							upDirRecalculated = crossProduct(eachJoint, childNewName[0], aimChild[0])
							cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0,0,0), aim=aimAxis, upVector=upAxis, worldUpVector=upDirRecalculated, worldUpType="vector"))

				



					dotProduct = upDirRecalculated[0] * prevUpVector[0] + upDirRecalculated[1] * prevUpVector[1] + upDirRecalculated[2] * prevUpVector[2]

					#For the next iteration
					prevUpVector = upDirRecalculated

					if firstPass > 0 and  dotProduct <= 0.0:
						#dotProduct
						cmds.xform(eachJoint, r=1, os=1, ra=(aimAxis[0] * 180.0, aimAxis[1] * 180.0, aimAxis[2] * 180.0))
						prevUpVector[0] *= -1
						prevUpVector[1] *= -1
						prevUpVector[2] *= -1
		
					freezeJointOrientation(eachJoint)
					cmds.parent(childNewName, eachJoint)




			else:
				#Child joint. Use the same rotation as the parent.
				if len(childJoint) == 0:
					parentJoint = cmds.listRelatives(eachJoint, type="joint", p=True) 
					if parentJoint != None :
						if len(parentJoint) > 0:
							cmds.delete(cmds.orientConstraint(parentJoint[0], eachJoint, w=1, o=(0,0,0)))
							freezeJointOrientation(eachJoint)
		else:
			#Child joint. Use the same rotation as the parent.
			parentJoint = cmds.listRelatives(eachJoint, type="joint", p=True) 
			if parentJoint != None :
				if len(parentJoint) > 0:
					cmds.delete(cmds.orientConstraint(parentJoint[0], eachJoint, w=1, o=(0,0,0)))
					freezeJointOrientation(eachJoint)			

	

		firstPass += 1



# ====================================================================================================================
#
# SIGNATURE:
#	showSelectedLocalAxis(* args)
#	showHierarchyLocalAxis(* args)
#	hideSelectedLocalAxis(* args)
#	hideHierarchyLocalAxis(* args)
#
# DESCRIPTION:
# 	Hides or Shows the Joints Local Axis.
# 
# REQUIRES:
#	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def showSelectedLocalAxis(* args):
	elemSelected = cmds.ls(typ="joint", sl=True)

	if elemSelected == None or len(elemSelected) == 0:
		print("USE: Select at least one joint.")
	else:
		doToggleLocalAxis(elemSelected, 1)
		cmds.select(elemSelected, r=True)

def showHierarchyLocalAxis(* args):
	elemSelected = cmds.ls(typ="joint", sl=True)

	if elemSelected == None or len(elemSelected) == 0:
		print("USE: Select at least one joint.")
	else:
		cmds.select(hi=True)
		jointsToToggle = cmds.ls(typ="joint", sl=True)
		doToggleLocalAxis(jointsToToggle, 1)
		cmds.select(elemSelected, r=True)

def hideSelectedLocalAxis(* args):
	elemSelected = cmds.ls(typ="joint", sl=True)

	if elemSelected == None or len(elemSelected) == 0:
		print("USE: Select at least one joint.")
	else:
		doToggleLocalAxis(elemSelected, 0)
		cmds.select(elemSelected, r=True)	

def hideHierarchyLocalAxis(* args):
	elemSelected = cmds.ls(typ="joint", sl=True)

	if elemSelected == None or len(elemSelected) == 0:
		print("USE: Select at least one joint.")
	else:
		cmds.select(hi=True)
		jointsToToggle = cmds.ls(typ="joint", sl=True)
		doToggleLocalAxis(jointsToToggle, 0)
		cmds.select(elemSelected, r=True)



# ====================================================================================================================
#
# SIGNATURE:
#	doToggleLocalAxis(jointsSelected, showOrHide)
#
# DESCRIPTION:
# 	Hides or Shows the selected joints Local Rotation Axis.
# 
# REQUIRES:
# 	jointsSelected - Selected joints.
# 	showOrHide - 1 - show - 0 - hide.
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def doToggleLocalAxis(jointsSelected, showOrHide):
	for eachJoint in jointsSelected:
		cmds.toggle(eachJoint, localAxis=True, state=showOrHide)



# ====================================================================================================================
#
# SIGNATURE:
#	crossProduct(firstObj, secondObj, thirdObj)
#
# DESCRIPTION:
# 	Calculates the dot product among 3 joints forming 2 vectors.
# 
# REQUIRES:
#	firstObj - First object to the Cross Product.
# 	secondObj - Second object to the Cross Product.
# 	thirdObj - Third object to the Cross Product.
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def crossProduct(firstObj, secondObj, thirdObj):
	#We have 3 points in space so we have to calculate the vectors from 
	#the secondObject (generally the middle joint and the one to orient)
	#to the firstObject and from the secondObject to the thirdObject.

	xformFirstObj = cmds.xform(firstObj, q=True, ws=True, rp=True)
	xformSecondObj = cmds.xform(secondObj, q=True, ws=True, rp=True)
	xformThirdObj = cmds.xform(thirdObj, q=True, ws=True, rp=True)

	#B->A so A-B.
	firstVector = [0,0,0]
	firstVector[0] = xformFirstObj[0] - xformSecondObj[0];
	firstVector[1] = xformFirstObj[1] - xformSecondObj[1];
	firstVector[2] = xformFirstObj[2] - xformSecondObj[2];

	#B->C so C-B.
	secondVector = [0,0,0]
	secondVector[0] = xformThirdObj[0] - xformSecondObj[0];
	secondVector[1] = xformThirdObj[1] - xformSecondObj[1];
	secondVector[2] = xformThirdObj[2] - xformSecondObj[2];

	#THE MORE YOU KNOW - 3D MATH
	#========================================
	#Cross Product u x v:
	#(u2v3-u3v2, u3v1-u1v3, u1v2-u2v1)
	crossProductResult = [0,0,0]
	crossProductResult[0] = firstVector[1]*secondVector[2] - firstVector[2]*secondVector[1]
	crossProductResult[1] = firstVector[2]*secondVector[0] - firstVector[0]*secondVector[2]
	crossProductResult[2] = firstVector[0]*secondVector[1] - firstVector[1]*secondVector[0]

	return crossProductResult

	

# ====================================================================================================================
#
# SIGNATURE:
#	orientJointAsObjectUiManager(* args)
#
# DESCRIPTION:
# 	Orient the joint the same way as another object.
# 
# REQUIRES:
#	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def orientJointAsObjectUiManager(* args):
	cmds.undoInfo(ock=True)

	objectsSelected = cmds.ls(sl=True)
	if len(objectsSelected) < 2:
		print "USE: Select the object to copy from, then SHIFT select the joint to orient."
	else:
		if cmds.objectType(objectsSelected[1]) != "joint":
			print "USE: Select the object to copy from, then SHIFT select the joint to orient."
		else:
			orientJointAsObject(objectsSelected[1], objectsSelected[0])
			
	cmds.select(objectsSelected, r=True)

	cmds.undoInfo(cck=True)



# ====================================================================================================================
#
# SIGNATURE:
#	orientJointAsObject(jointToOrient, objectToCopyFrom)
#
# DESCRIPTION:
# 	Orient the joint the same way as another object.
# 
# REQUIRES:
#	jointToOrient - Joint to Orient.
# 	objectToCopyFrom - Object to copy the orientation.
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def orientJointAsObject(jointToOrient, objectToCopyFrom):
	hijos = cmds.listRelatives(jointToOrient, c=True)
	if hijos != None:
		if len(hijos) > 0:
			hijosRenamed = cmds.parent(hijos, w=True)

	cmds.delete(cmds.orientConstraint(objectToCopyFrom, jointToOrient, w=1, o=(0,0,0)))
		
	freezeJointOrientation(jointToOrient)

	if hijos != None:
		if len(hijos) > 0:
			cmds.parent(hijosRenamed, jointToOrient)



# ====================================================================================================================
#
# SIGNATURE:
#	orientJointAsObjectUiManager(* args)
#
# DESCRIPTION:
# 	Orient the joint as World Space.
# 
# REQUIRES:
#	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def orientJointAsWorldUiManager(* args):
	cmds.undoInfo(ock=True)

	objectsSelected = cmds.ls(sl=True, type="joint")
	if objectsSelected != None:
		if len(objectsSelected) == 0:
			print "USE: Select one or more joints."
		else:
			locatorName = cmds.spaceLocator()	
			for eachJointSelected in objectsSelected:
				orientJointAsObject(eachJointSelected, locatorName)
			cmds.delete(locatorName)
	else:
		print "USE: Select one or more joints."

	cmds.select(objectsSelected, r=True)

	cmds.undoInfo(cck=True)



# ====================================================================================================================
#
# SIGNATURE:
#	orientJointAsWorld(jointToOrient)
#
# DESCRIPTION:
# 	Orient the joint as World Space.
# 
# REQUIRES:
#	jointToOrient - Joint to orient.
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def orientJointAsWorld(jointToOrient):
	cmds.select(jointToOrient, r=True)
	objectsSelected = cmds.ls(sl=True, type="joint")
	if objectsSelected != None:
		if len(objectsSelected) == 0:
			print "USE: Select one or more joints."
		else:
			locatorName = cmds.spaceLocator()	
			for eachJointSelected in objectsSelected:
				orientJointAsObject(eachJointSelected, locatorName)
			cmds.delete(locatorName)
	else:
		print "USE: Select one or more joints."

	cmds.select(objectsSelected, r=True)



# ====================================================================================================================
#
# SIGNATURE:
#	addInXValue(* args)
#	minusInXValue(* args)
#	addInYValue(* args)
#	minusInYValue(* args)
#	addInZValue(* args)
#	minusInZValue(* args)
#
# DESCRIPTION:
# 	Plus or Minus by 0.1 the value on the Textbox.
# 
# REQUIRES:
#	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def addInXValue(* args):
	cmds.floatFieldGrp("rbgManualTweak", e=True, v1=(cmds.floatFieldGrp("rbgManualTweak", q=True, v1=True) + 0.1))

def minusInXValue(* args):
	cmds.floatFieldGrp("rbgManualTweak", e=True, v1=(cmds.floatFieldGrp("rbgManualTweak", q=True, v1=True) - 0.1))

def addInYValue(* args):
	cmds.floatFieldGrp("rbgManualTweak", e=True, v2=(cmds.floatFieldGrp("rbgManualTweak", q=True, v2=True) + 0.1))

def minusInYValue(* args):
	cmds.floatFieldGrp("rbgManualTweak", e=True, v2=(cmds.floatFieldGrp("rbgManualTweak", q=True, v2=True) - 0.1))

def addInZValue(* args):
	cmds.floatFieldGrp("rbgManualTweak", e=True, v3=(cmds.floatFieldGrp("rbgManualTweak", q=True, v3=True) + 0.1))

def minusInZValue(* args):
	cmds.floatFieldGrp("rbgManualTweak", e=True, v3=(cmds.floatFieldGrp("rbgManualTweak", q=True, v3=True) - 0.1))



# ====================================================================================================================
#
# SIGNATURE:
#	rotateAxisManualTweakPlus(* args)
#	rotateAxisManualTweakMinus(* args)
#
# DESCRIPTION:
# 	Rotate the axis as specified.
# 
# REQUIRES:
#	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def rotateAxisManualTweakPlus(* args):
	cmds.undoInfo(ock=True)

	rotationValues = [0.0, 0.0, 0.0]
	rotationValues[0] = cmds.floatFieldGrp("rbgManualTweak", q=True, v1=True)
	rotationValues[1] = cmds.floatFieldGrp("rbgManualTweak", q=True, v2=True)
	rotationValues[2] = cmds.floatFieldGrp("rbgManualTweak", q=True, v3=True)

	selecccionados = cmds.ls(sl=True, type="joint")
	rotateAxisManualTweak(selecccionados, rotationValues)
	cmds.select(selecccionados, r=True)

	cmds.undoInfo(cck=True)



def rotateAxisManualTweakMinus(* args):
	cmds.undoInfo(ock=True)

	rotationValues = [0.0, 0.0, 0.0]
	rotationValues[0] = cmds.floatFieldGrp("rbgManualTweak", q=True, v1=True) * -1
	rotationValues[1] = cmds.floatFieldGrp("rbgManualTweak", q=True, v2=True) * -1
	rotationValues[2] = cmds.floatFieldGrp("rbgManualTweak", q=True, v3=True) * -1

	selecccionados = cmds.ls(sl=True, type="joint")
	rotateAxisManualTweak(selecccionados, rotationValues)
	cmds.select(selecccionados, r=True)

	cmds.undoInfo(cck=True)



# ====================================================================================================================
#
# SIGNATURE:
#	rotateAxisManualTweak(jointsSelected, rotationValues)
#
# DESCRIPTION:
# 	Rotate the axis as specified.
# 
# REQUIRES:
#	jointsSelected - Joint to do the manual tweak.
# 	rotationValues - Values to the rotation (X, Y and Z).
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def rotateAxisManualTweak(jointsSelected, rotationValues):
	for eachJointSelected in jointsSelected:
		cmds.xform(eachJointSelected, r=1, os=1, ra=(rotationValues[0], rotationValues[1], rotationValues[2]))
		freezeJointOrientation(eachJointSelected)
			



# ====================================================================================================================
#
# SIGNATURE:
#	freezeJointOrientation(jointToOrient)
#
# DESCRIPTION:
# 	Freezes the joint orientation.
# 
# REQUIRES:
#	jointToOrient - Joint to orient.
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def freezeJointOrientation(jointToOrient):
	cmds.joint(jointToOrient, e=True, zeroScaleOrient=True)
	cmds.makeIdentity(jointToOrient, apply=True, t=0, r=1, s=0, n=0)



# ====================================================================================================================
#
# SIGNATURE:
#	worldUpX(* args)
#
# DESCRIPTION:
# 	Sets and 1.0 on the X world Up Field.
# 
# REQUIRES:
#	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def worldUpX(* args):
	cmds.floatFieldGrp("rbgWorldUp", e=True, v1=1.0)
	cmds.floatFieldGrp("rbgWorldUp", e=True, v2=0.0)
	cmds.floatFieldGrp("rbgWorldUp", e=True, v3=0.0)



# ====================================================================================================================
#
# SIGNATURE:
#	worldUpY(* args)
#
# DESCRIPTION:
# 	Sets and 1.0 on the Y world Up Field.
# 
# REQUIRES:
#	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def worldUpY(* args):
	cmds.floatFieldGrp("rbgWorldUp", e=True, v1=0.0)
	cmds.floatFieldGrp("rbgWorldUp", e=True, v2=1.0)
	cmds.floatFieldGrp("rbgWorldUp", e=True, v3=0.0)



# ====================================================================================================================
#
# SIGNATURE:
#	worldUpZ(* args)
#
# DESCRIPTION:
# 	Sets and 1.0 on the Z world Up Field.
# 
# REQUIRES:
#	Nothing
#
# RETURNS:
#	Nothing
#
# ====================================================================================================================
def worldUpZ(* args):
	cmds.floatFieldGrp("rbgWorldUp", e=True, v1=0.0)
	cmds.floatFieldGrp("rbgWorldUp", e=True, v2=0.0)
	cmds.floatFieldGrp("rbgWorldUp", e=True, v3=1.0)




