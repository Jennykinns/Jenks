import maya.cmds as cmds
# ======================================================================
#
#   doOrientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp)
#   crossProduct(firstObj, secondObj, thirdObj)
#   freezeJointOrientation(jointToOrient)
#
# AUTHOR:
#   Jose Antonio Martin Martin - JoseAntonioMartinMartin@gmail.com
#                    contact@joseantoniomartinmartin.com
#   http://www.joseantoniomartinmartin.com
#   Copyright 2010 Jose Antonio Martin Martin - All Rights Reserved.
#
# ======================================================================


def doOrientJoint(jointsToOrient, aimAxis, upAxis, worldUp, guessUp):
    firstPass = 0
    prevUpVector = [0,0,0]
    for eachJoint in jointsToOrient:
        childJoint = cmds.listRelatives(eachJoint, type="joint", c=True)
        if childJoint != None:
            if len(childJoint) > 0:
                #Store the name in case when unparented it changes it's name.
                childNewName = cmds.parent(childJoint, w=True)
                if guessUp == 0:
                    #Not guess Up direction
                    cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1, o=(0, 0, 0),
                        aim=aimAxis, upVector=upAxis, worldUpVector=worldUp, worldUpType="vector"))
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
                                tol = 0.0001

                                if (abs(posCurrentJoint[0] - posParentJoint[0]) <= tol
                                    and abs(posCurrentJoint[1] - posParentJoint[1]) <= tol
                                    and abs(posCurrentJoint[2] - posParentJoint[2]) <= tol):
                                    aimChild = cmds.listRelatives(childNewName[0],
                                                                  type="joint", c=True)
                                    upDirRecalculated = crossProduct(eachJoint, childNewName[0],
                                                                     aimChild[0])
                                    if upDirRecalculated == [0, 0, 0]:
                                        if prevUpVector == [0, 0, 0]:
                                            upDirRecalculated = [0, 1, 0]
                                        else:
                                            upDirRecalculated = prevUpVector
                                    cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint,
                                                                   w=1, o=(0, 0, 0), aim=aimAxis,
                                                                   upVector=upAxis,
                                                                   worldUpVector=upDirRecalculated,
                                                                   worldUpType="vector"))
                                else:
                                    upDirRecalculated = crossProduct(parentJoint, eachJoint,
                                                                     childNewName[0])
                                    if upDirRecalculated == [0, 0, 0]:
                                        if prevUpVector == [0, 0, 0]:
                                            upDirRecalculated = [0, 1, 0]
                                        else:
                                            upDirRecalculated = prevUpVector
                                    cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint,
                                                                   w=1, o=(0, 0, 0), aim=aimAxis,
                                                                   upVector=upAxis,
                                                                   worldUpVector=upDirRecalculated,
                                                                   worldUpType="vector"))
                            else:
                                aimChild = cmds.listRelatives(childNewName[0], type="joint",
                                                              c=True)
                                upDirRecalculated = crossProduct(eachJoint, childNewName[0],
                                                                 aimChild[0])
                        else:
                            aimChild = cmds.listRelatives(childNewName[0], type="joint", c=True)
                            upDirRecalculated = crossProduct(eachJoint, childNewName[0],
                                                             aimChild[0])
                            if upDirRecalculated == [0, 0, 0]:
                                if prevUpVector == [0, 0, 0]:
                                    upDirRecalculated = [0, 1, 0]
                                else:
                                    upDirRecalculated = prevUpVector
                            cmds.delete(cmds.aimConstraint(childNewName[0], eachJoint, w=1,
                                                           o=(0, 0, 0), aim=aimAxis,
                                                           upVector=upAxis,
                                                           worldUpVector=upDirRecalculated,
                                                           worldUpType="vector"))




                    dotProduct = (upDirRecalculated[0] * prevUpVector[0]
                                 + upDirRecalculated[1] * prevUpVector[1]
                                 + upDirRecalculated[2] * prevUpVector[2])

                    #For the next iteration
                    prevUpVector = upDirRecalculated

                    if firstPass > 0 and  dotProduct <= 0.0:
                        #dotProduct
                        cmds.xform(eachJoint, r=1, os=1,
                                   ra=(aimAxis[0] * 180.0, aimAxis[1] * 180.0, aimAxis[2] * 180.0))
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
                            cmds.delete(cmds.orientConstraint(parentJoint[0], eachJoint,
                                        w=1, o=(0,0,0)))
                            freezeJointOrientation(eachJoint)
        else:
            #Child joint. Use the same rotation as the parent.
            parentJoint = cmds.listRelatives(eachJoint, type="joint", p=True)
            if parentJoint != None :
                if len(parentJoint) > 0:
                    cmds.delete(cmds.orientConstraint(parentJoint[0], eachJoint, w=1, o=(0,0,0)))
                    freezeJointOrientation(eachJoint)



        firstPass += 1


def crossProduct(firstObj, secondObj, thirdObj):
    #We have 3 points in space so we have to calculate the vectors from
    #the secondObject (generally the middle joint and the one to orient)
    #to the firstObject and from the secondObject to the thirdObject.

    xformFirstObj = cmds.xform(firstObj, q=True, ws=True, t=True)
    xformSecondObj = cmds.xform(secondObj, q=True, ws=True, t=True)
    xformThirdObj = cmds.xform(thirdObj, q=True, ws=True, t=True)

    for i in range(3):
        xformFirstObj[i] = float('{:3f}'.format(xformFirstObj[i]))
        xformSecondObj[i] = float('{:3f}'.format(xformSecondObj[i]))
        xformThirdObj[i] = float('{:3f}'.format(xformThirdObj[i]))

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

    for i in range(3):
        crossProductResult[i] = float('{:3f}'.format(crossProductResult[i]))

    for i, x in enumerate(crossProductResult):
        if x == -0.0:
            crossProductResult[i] = 0
    return crossProductResult


def freezeJointOrientation(jointToOrient):
    cmds.joint(jointToOrient, e=True, zeroScaleOrient=True)
    cmds.makeIdentity(jointToOrient, apply=True, t=0, r=1, s=0, n=0)