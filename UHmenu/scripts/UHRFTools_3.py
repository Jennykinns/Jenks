# version 2 of the UH Renderfarm Tools
# release note:
# now able to be extended to enable additional nodeTypes
# checks to see if the maya scene is in the project
# checks for approved texture formats
# checks for spaces in scene file name

import maya.cmds as cmds
import os.path
from functools import partial
import UHRFTools_UI as customUI
import maya.OpenMayaUI as omUi
import SkinnyMayaTractorSpool as tractorSpool

try:
    from PySide import QtGui, QtCore
    import PySide.QtGui as QtWidgets
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets

from shiboken2 import wrapInstance

# Temporary reloads for dev
reload(customUI)
reload(tractorSpool)

filteredTypes = ['abc_File', 'filename', 'fileTextureName','VdbFilePath','rman__EnvMap','barnDoorMap'] # add path node types to look for


def maya_main_window():
    main_window_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def main():
    #if testProject() != True:
    if 1 == 2:
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText("This tool will not work properly as your Project is not set correctly, please set your project correctly and try again.")
        msgBox.exec_()
    else:
        global myWindow

        try:
            myWindow.close()
        except: pass
        myWindow = UHRFTools_3(parent=maya_main_window())
        myWindow.show()

def testProject():
    sceneLocation = os.path.dirname(cmds.file(query=True, l=True)[0])
    workspaceLocation = cmds.workspace(q = True, rootDirectory = True)

    if (sceneLocation.split('scenes')[0] == workspaceLocation):
        return True
    else:
        return False

class UHRFTools_3(QtWidgets.QDialog):
    def __init__(self,parent = None):

        # script global variables
        self.objList = [] # Dictionary of all objects that have a file associated
        self.findPathNodes() # locate all scene objects with path nodes

        self.farmMappedDriveLetter = "R" # should be set to the windows drive letter for the renderfarm storage server
        self.linuxFarmMountPoint = "/mnt/RenderStore/" # should be set to the linux mount point for the farm
        self.linuxShareName = "/RenderStore/"

        # Constants
        self.udimDefinitions = ('Normal','Z-Brush','Mudbox','Mari','Explicit')
        self.approvedFileFormats = ('exr','tx','tex','abc','vdb','ies','IES','ass','XGC','xgc','ptx','PTX','ptex','PTEX','xml','mcx','mcc')
        self.renderers = {'renderManRIS':'rman','renderMan':'rman','mayaSoftware':'sw', 'mayaHardware':'hw', 'mentalRay':'mr', 'arnold':'arnold'}

        # define UI
        super(UHRFTools_3, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui =  customUI.Ui_MainWindow() #Define UI class in module

        self.ui.setupUi(self) # start window
            # hide unused ui elements
        self.ui.cbTurtle.setText('No Spaces')
        self.ui.cbNoUncached.setText('Scene on R:')

            #self.ui.btnSanity.clicked.connect(self.testData) depricated (to be auto update)
        self.ui.btnUpdatePaths.clicked.connect(self.UpdatePaths)
            # path in table.changed - CHECK THIS make it re-run sanity
        self.ui.btnRefresh.clicked.connect(self.RefreshList)

        self.ui.rbLocal.clicked.connect(partial(self.setPathChoice, "Local"))
        self.ui.rbRenderFarm.clicked.connect(partial(self.setPathChoice, "Farm"))

            # if index changes then
        self.ui.cboJobType.currentIndexChanged.connect(self.jobTypeChanged)

            # Spool job to tractor Button
        self.ui.btnSpool.clicked.connect(self.submitJob)

        self.ui.btnSpool.setEnabled(False)
        self.ui.cboFrameNum.setEnabled(False)
        self.ui.cboJobType.setEnabled(False)

        self.ui.label.setText(QtWidgets.QApplication.translate("MainWindow", "RenderFarm Tools v3 - BETA", None))

            # CREATE A NULL Object to hold persistant Data
            # if object doesnt exist then create a locator with the attribute Location
        if cmds.objExists('RFToolsData') != True:
            cmds.spaceLocator(n = "RFToolsData") # create an object to hold the File Location data persistantly
            cmds.addAttr( shortName='ff', longName='JobLocation', dataType='string')
            cmds.setAttr('RFToolsData.JobLocation','Local', type="string", lock = True) # assume that when script is first run that the scenes are configured for local pathing

        self.pathLocation = cmds.getAttr('RFToolsData.JobLocation') # holds the current setting for path location
            # from the variable set the radio button starting setting
        if self.pathLocation == 'Local':
            self.ui.rbLocal.setChecked(True)
        else:
            self.ui.rbRenderFarm.setChecked(True)

        # begin script
        self.PopulateTable()

        self.qualityChecks()

        self.getRenderSettings()

    # feed this function a path and return location and receive the path as if from the return
    def returnAltPath(self,path, returnLocation):
        finalPath = ''
        FilePath = ''
        # check data is in path
        if (len(path) > 0) and (len(returnLocation) > 0):

            # flip the slashes
            texturePath = path.replace('\\','/')
            texturePath = path.replace('//','/')

            newTexturePath = texturePath

            print(texturePath)

            projectPath = cmds.workspace(q = True, rootDirectory = True) # get the project name to split the path with

                        # get drive letter
            driveLetter = projectPath.split(':')[0]

            projectPath = filter(None, projectPath.split('/')) # project folder name at source

            if projectPath[0] == 'mnt':
                projectPath.pop(0) # remove mnt
                projectPath.pop(1) # remove RenderStore
            else:
                projectPath.pop(0) # remove R:

            # removes the project path from the texture location

            projectPath = '/'.join(projectPath)
            print (projectPath)
            print ('texture Path is :' + str(texturePath))

            try:
                # if splitable by sourceimages then do so else use the project path
                if len(texturePath.split('sourceimages')) > 1:
                    texturePath = texturePath.split('sourceimages')[1]
                    newTexturePath = projectPath  + '/sourceimages' + texturePath
                if len(texturePath.split('cache')) > 1:
                    texturePath = texturePath.split('cache')[1]
                    newTexturePath = projectPath  + '/cache' + texturePath
                elif len(texturePath.split(projectPath)) > 1:
                    texturePath = texturePath.split(projectPath)
                    newTexturePath = projectPath  + texturePath
            except:
                print('ERROR ' + str(texturePath))

            # add the requested target
            if returnLocation == 'Local':
                newTexturePath = driveLetter + ':/' + newTexturePath
            else:
                newTexturePath = '/mnt/RenderStore/' + newTexturePath

            return (newTexturePath)

    # when update button pressed swaps from local to farm or visa versa - REFINE THIS
    def UpdatePaths(self,*args):

        if self.checkProject():
            # set scene persistant attributes to the current button setting
            cmds.setAttr('RFToolsData.JobLocation', lock = False)
            cmds.setAttr('RFToolsData.JobLocation',self.pathLocation, type="string", lock = True)

            # dictObject = {'nodeName': '','nodeType':'','uvTilingMode':''}
            # for each object in the object list change the path to match the currently selected location
            for I in range(len(self.objList)):
                objectName = self.objList[I]['nodeName']
                attribute = self.objList[I]['nodeType']
                oldPath = cmds.getAttr(objectName + "." + attribute)
                oldPath = oldPath.replace('\\','/')
                oldPath = oldPath.replace('//','/')

                cmds.setAttr(objectName + "." + attribute, oldPath , type="string")
                cmds.setAttr(objectName + "." + attribute, self.returnAltPath(oldPath, self.pathLocation) , type="string")
             #update userView
            self.RefreshList()
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("Please set the project first otherwise all of your paths will be mangled.")
            msgBox.exec_()



# put objlist into the tableview
    def PopulateTable(self,*args):
        # disable events on this table while loading
        self.ui.tableWidget.blockSignals(True)
        # copy function here
        self.ui.tableWidget.setColumnCount(5)
        # create correct number of rows
        self.ui.tableWidget.setRowCount(len(self.objList))
        # set column headers
        self.ui.tableWidget.setHorizontalHeaderLabels(['Connected Node','Shader Model', 'Path','uv Type','Status'])
        #self.ui.tableWidget.setHorizontalHeaderLabels(self.objList[0].keys())
        # change column widths
        self.ui.tableWidget.setColumnWidth(0,110)
        self.ui.tableWidget.setColumnWidth(1,200)
        self.ui.tableWidget.setColumnWidth(2,892)
        self.ui.tableWidget.setColumnWidth(3,100)
        self.ui.tableWidget.setColumnWidth(4,100)

        for row in range(len(self.objList)):
            self.ui.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(self.objList[row][self.objList[0].keys()[1]]))) # Node
            self.ui.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem("")) # Attribute # TO BE SORTED
            # get path from attribute
            newEditableItem = self.ui.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(cmds.getAttr(
                                str(self.objList[row][self.objList[0].keys()[1]])
                                + "." +
                                str(self.objList[row][self.objList[0].keys()[0]]))))

            self.ui.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(self.udimDefinitions[self.objList[row][self.objList[0].keys()[2]]]))) # uv Type

            # sanity check results
            self.ui.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(""))
            self.ui.tableWidget.item(row, 4).setBackground(QtGui.QColor(0,0,0)) # set colour of sanity check result
            self.sanityCheck(row)


        # Enable Events again
        self.ui.tableWidget.blockSignals(False)
        # when table is changed run this function
        self.ui.tableWidget.cellChanged.connect(self.updateNode)
        # when cell is clicked
        #self.ui.tableWidget.itemClicked.connect(self.selectNode)

# triggered when path is changed in the ui
    def updateNode(self,row,column):
        # if updating the path
        if column == 2:
            newPath = ""
            # put new path to the object...
            cmds.setAttr(self.objList[row]['nodeName'] + "." + self.objList[row]['nodeType'],self.ui.tableWidget.item(row,2).text(), type = "string" )
        #rerun sanity check for this row
        self.sanityCheck(row)

        self.qualityChecks()

# when triggered will update the attribute for the Node path
    def selectNode(self,row):
        print(row)
        #print(objList[row])

# submits the job to the tractor queue
    def submitJob(self):

        testFrame = True
        # set tractor Spool Globals
        tractorSpool.tractorEngineName = "147.197.217.242"
        tractorSpool.tractorEnginePort = '80'

        #to be set by RFTOOLS
        renderer =  self.renderers[cmds.getAttr('defaultRenderGlobals.ren')]

        #to be set by RFTOOLS
        tractorSpool.renderer = renderer # should be 'default''sw','hw', 'mr', 'prman', arnold

        #dont pause the job let it run
        tractorSpool.doJobPause = 0

        tractorSpool.sceneName = cmds.file(query=True, l=True)[0].split("/")[-1]

        # tell tractor what application is submitting

        aboutString = cmds.about(p=True)
        aboutStringTokens = aboutString.split(' ') # get maya year

        tractorSpool.envKey = 'maya' + aboutStringTokens[ len(aboutStringTokens)-1 ] # echos maya2016

        tractorSpool.jobCmdTags = "Render "+ str(cmds.getAttr('defaultRenderGlobals.ren'))  # feeds the limits system

        if (self.ui.cboJobType.currentText() == "Test Frame"):
            # Test Render
            # for test frames these should match and be pulled from the dropdown box
            tractorSpool.startFrame = int(self.ui.cboFrameNum.currentText())
            tractorSpool.stopFrame = int(self.ui.cboFrameNum.currentText())
            tractorSpool.spoolJob(100.0) # spoolJob(priority as float)

        else:
            # Full Render
            # for full renders grab values from scene
            tractorSpool.startFrame = int(cmds.getAttr('defaultRenderGlobals.startFrame') )
            tractorSpool.stopFrame = int(cmds.getAttr('defaultRenderGlobals.endFrame') )
            tractorSpool.spoolJob(50.0) # spoolJob(priority as float)


    def jobTypeChanged(self):
        print("Render Job Type changed")

        if self.ui.cboJobType.currentText() == "Test Frame":
            print("Test frame numbers loading")
            self.ui.cboFrameNum.clear()

            for frameNum in range(int(cmds.playbackOptions(q = True, ast = True)),int(cmds.playbackOptions(q = True, aet = True))):
                self.ui.cboFrameNum.addItem(str(frameNum))
            self.ui.cboFrameNum.setEnabled(True)

        else:
            print("Full Render")
            for i in range(self.ui.cboFrameNum.count()):
                self.ui.cboFrameNum.removeItem(i)
            self.ui.cboFrameNum.clear()
            self.ui.cboFrameNum.setEnabled(False)


    # checkAttr function tests if attribute defined exists in object -  returns BOOL
    def checkAttr(self,Object,Attribute):
        # more efficient as no loop required
        if (Attribute in cmds.listAttr(Object)):
            return True
        else:
            return False

    def qualityChecks(self):
        self.ui.cbProject.setChecked(False)
        self.ui.cbNoJpg.setChecked(False)
        self.ui.cbMissingTextures.setChecked(False)
        self.checkProject()
        self.checkTextures()
        self.checkExtensions()
        self.checkSpaces()
        self.checkLocation()

        # checking scripts
        if self.checkProject() and self.checkTextures() and self.checkExtensions() and self.checkSpaces() and self.checkLocation():
            self.ui.lblQCFeedback.setText('Passed')
            self.ui.btnSpool.setEnabled(True)
            self.ui.cboFrameNum.setEnabled(True)
            self.ui.cboJobType.setEnabled(True)

        else:
            self.ui.lblQCFeedback.setText('Failed')
            self.ui.btnSpool.setEnabled(False)
            self.ui.cboFrameNum.setEnabled(False)
            self.ui.cboJobType.setEnabled(False)


    # checks to see that the scene path is in the project /scenes/ dir
    def checkProject(self):

        sceneLocation = os.path.dirname(cmds.file(query=True, l=True)[0])
        workspaceLocation = cmds.workspace(q = True, rootDirectory = True)

        self.ui.lblWorkspace.setText(workspaceLocation) # update the UI with workspace location
        self.ui.lblWorkspace.setWordWrap(True)

        self.ui.lblSceneName.setText(cmds.file(query=True, l=True)[0].split("/")[-1]) # update sceneName label
        self.ui.lblSceneName.setWordWrap(True)

        # refresh the frame range because there is no auto check on this
        self.ui.lblFrameRange.setText(str(int(cmds.playbackOptions(q = True, ast = True))) + " - " + str(int(cmds.playbackOptions(q = True, aet = True))))

        # change the tickbox Status
        if (sceneLocation.split('scenes')[0] == workspaceLocation):
            print('Quality Test: Project Set - Passed')
            self.ui.cbProject.setChecked(True)
            return True
        else:
            print('Quality Test: Project Set - Failed')
            print('Detail: Please set your project currently your scene is not within your workspace')
            print('current Scene location     :' + str(sceneLocation))
            print('current Workspace location :' + str(workspaceLocation))
            return False


# checks texture files that may cause issues
    def checkExtensions(self):
        # has errors if you have two "." in the filename
        testPassed = True

        for I in range(len(self.objList)):
            if testPassed == True:
                objectName = self.objList[I]['nodeName']
                attribute = self.objList[I]['nodeType']
                path = cmds.getAttr(objectName + "." + attribute)

                # splits to .
                splitPath = path.split('.')
                # extract the extension
                extension = splitPath[len(splitPath)-1]

                # test if current line has a texture in the right format
                formatSupported = False
                # test each format and return true if the extension is in the list
                for format in self.approvedFileFormats:
                    if extension == format:
                        formatSupported = True

                # if the extension is not supported then report error
                if formatSupported != True:
                    testPassed = False
                    print("Quality Test: Texture File format - FAILED")
                    print("Detail: " +  objectName + " has a " + extension + " texture - please use" + str(self.approvedFileFormats))

        self.ui.cbNoJpg.setChecked(testPassed)
        if testPassed:
            print("Quality Test: Texture File format - PASSED")
        return testPassed

    # checks that all sanity checks have passed
    def checkTextures(self):
        allTexturesExist = True
        for object in range(len(self.objList)):
            if self.objList[object]['exists'] != True:
                allTexturesExist = False
        #update the texture report
        self.ui.cbMissingTextures.setChecked(allTexturesExist)
        print("Quality Test: Textures Exist - PASSED")
        return allTexturesExist

    def checkSpaces(self):
        testPath =  cmds.file(query=True, l=True)[0]

        if len(testPath.split(" ")) == 1:
            #no spaces in the path
            self.ui.cbTurtle.setChecked(True)
            print("Quality Test: No Spaces in project or Scene path - PASSED")
            return True
        else:
            self.ui.cbTurtle.setChecked(False)
            print("Quality Test: No Spaces in project or Scene path - FAILED")
            return False

    def checkLocation(self):
        # check drive is R
        sceneLocation = os.path.dirname(cmds.file(query=True, l=True)[0])
        drive = sceneLocation.split(':')[0] # drive letter
        if drive != 'R':
            print('Quality Test: File Not on the R Drive - FAILED')
            self.ui.cbNoUncached.setChecked(False)
            return False
        else:
            print('Quality Test: File Not on the R Drive - TRUE')
            self.ui.cbNoUncached.setChecked(True)
            return True

    def getRenderSettings(self):
        # set the renderer
        self.ui.lblRenderer.setText(cmds.getAttr('defaultRenderGlobals.ren'))
         # refresh the frame range
        self.ui.lblFrameRange.setText(str(int(cmds.getAttr('defaultRenderGlobals.startFrame'))) + " - " + str(int(cmds.getAttr('defaultRenderGlobals.endFrame'))))
        #self.ui.lblFrameRange.setText(str(int(cmds.playbackOptions(q = True, ast = True))) + " - " + str(int(cmds.playbackOptions(q = True, aet = True))))

    # finds all scene nodes with the filtered types - outputs objList containing path nodes
    def findPathNodes(self):
        # gets all objects in scene and looks for specified attributes
        self.objList = []
        filteredObjList = []
        # get all objects in scene

        self.objList = self.objList + cmds.ls(type = 'file')
        self.objList = self.objList + cmds.ls(type = 'AlembicNode')
        self.objList = self.objList + cmds.ls(type = 'aiVolume')
        self.objList = self.objList + cmds.ls(type = 'OpenVDBRead')
        self.objList = self.objList + cmds.ls(type = 'aiImage')
        # renderman specific
        self.objList = self.objList + cmds.ls(type = 'PxrTexture')
        self.objList = self.objList + cmds.ls(type = 'PxrBump')
        self.objList = self.objList + cmds.ls(type = 'PxrNormalMap')
        self.objList = self.objList + cmds.ls(type = 'PxrStdEnvMapLight')
        #only show barndoors if in use not in use
        for light in cmds.ls(type = 'PxrStdAreaLight'):
            if cmds.getAttr(light + '.enableBarnDoors') == True:
                 self.objList = self.objList + light


        self.objList = filter(None, self.objList)

        for P in range(len(self.objList)):
            dictObject = {'nodeName': '','nodeType':'','uvTilingMode':'','exists':False} # could be extended to further parameters if necessary
            dictObject['nodeName'] = self.objList[P]

            for types in range(len(filteredTypes)):
                if self.checkAttr(self.objList[P],filteredTypes[types]) :
                    dictObject['nodeType'] = filteredTypes[types]

            dictObject['uvTilingMode'] = "BLANK"#cmds.getAttr(self.objList[P] + ".uvTilingMode")
            filteredObjList.append(dictObject)


        # scan each object in self.objList and check to see if any path attributes are attached
        #for P in range(len(self.objList)):

            # scan throught the filtering types defined in init stage and
        #    if self.objList[P] != "defaultHardwareRenderGlobals":
        #        dictObject = {'nodeName': '','nodeType':'','uvTilingMode':'','exists':False} # could be extended to further parameters if necessary
        #        for types in range(len(filteredTypes)):
        #            if self.checkAttr(self.objList[P],filteredTypes[types]) :
        #                dictObject['nodeName'] = self.objList[P]
        #                dictObject['nodeType'] = filteredTypes[types]
        #                dictObject['uvTilingMode'] = "BLANK"#cmds.getAttr(self.objList[P] + ".uvTilingMode")
        #                filteredObjList.append(dictObject)

        self.objList[:] =[]
        # update objList with the new filtered List
        self.objList = filteredObjList
        print self.objList

    def RefreshList(self):
        print('########################################################################')
        print('                          UHRFTOOLS REFRESHED                           ')
        print('########################################################################')
        self.findPathNodes() # locate all scene objects with path nodes
        self.PopulateTable() # update table
        self.qualityChecks()

    # Update path selection when radio buttons pressed
    def setPathChoice(self,Location,*args):
        self.pathLocation = Location

    def testData(self):
        sender = self.sender()
        print(self.objList)

    # Check if the files in paths exist
    def sanityCheck(self,objectIndex,*args):
        udimTiles = 0
        completePath = ''
        # get path to file
        filePath = cmds.getAttr(self.objList[objectIndex]['nodeName'] + "." + self.objList[objectIndex]['nodeType']) # path
        if len(filePath) > 0:

            # if set to farm then test with the local path variant

            if (self.pathLocation == 'Farm'):
                filePath = self.returnAltPath(filePath, 'Local')

            # split the path by . to find the udims

            splitpath = filePath.split('.')

            # if it was a udim report the number of tiles found
            if ('<udim>' in splitpath) or ('<UDIM>' in splitpath) or ('_MAPID_' in splitpath):
                udimTiles = self.udimFileDetector(splitpath)
                self.ui.tableWidget.setItem(objectIndex, 3, QtWidgets.QTableWidgetItem(str(udimTiles) + ' Tiles'))

                if (udimTiles > 0):
                    # if the files are found using udim scanner then set the sanity fields
                    if self.pathLocation == 'Local':
                        # files exist and set to local
                        self.ui.tableWidget.item(objectIndex,4).setBackground(QtGui.QColor(200,200,0)) #Yellow
                    else:
                        # files exist and set to farm
                        self.ui.tableWidget.item(objectIndex,4).setBackground(QtGui.QColor(0,200,0)) # Green
                    self.objList[objectIndex]['exists'] = True # store exists status for the quality test
                else:
                    # file doesn't exist
                    self.ui.tableWidget.item(objectIndex,4).setBackground(QtGui.QColor(200,0,0)) # RED
                    print("Texture File missing: " + cmds.getAttr(self.objList[objectIndex]['nodeName'] + "." + self.objList[objectIndex]['nodeType'])) # path)
                    self.objList[objectIndex]['exists'] = False # store exists status for the quality test

            # to enable VDB Cache files
            elif ('$F4' in splitpath) or ('####' in splitpath):
                # check if the number of vdb files that exist matches the render frame range
                if self.frameBufferDetector(splitpath):
                    self.ui.tableWidget.setItem(objectIndex, 3, QtWidgets.QTableWidgetItem('frames present'))
                    if self.pathLocation == 'Local':
                        # files exist and set to local
                        self.ui.tableWidget.item(objectIndex,4).setBackground(QtGui.QColor(200,200,0)) #Yellow
                    else:
                        # files exist and set to farm
                        self.ui.tableWidget.item(objectIndex,4).setBackground(QtGui.QColor(0,200,0)) # Green
                    self.objList[objectIndex]['exists'] = True # store exists status for the quality test
                else:
                    self.ui.tableWidget.setItem(objectIndex, 3, QtWidgets.QTableWidgetItem('frames missing'))
                    # file doesn't exist
                    self.ui.tableWidget.item(objectIndex,4).setBackground(QtGui.QColor(200,0,0)) # RED
                    print("Texture File missing: " + cmds.getAttr(self.objList[objectIndex]['nodeName'] + "." + self.objList[objectIndex]['nodeType'])) # path)
                    self.objList[objectIndex]['exists'] = False # store exists status for the quality test

            else:
                if os.path.isfile(filePath):
                    # if the files are found using udim scanner then set the sanity fields
                    if self.pathLocation == 'Local':
                        # files exist and set to local
                        self.ui.tableWidget.item(objectIndex,4).setBackground(QtGui.QColor(200,200,0)) #Yellow
                    else:
                        # files exist and set to farm
                        self.ui.tableWidget.item(objectIndex,4).setBackground(QtGui.QColor(0,200,0)) # Green
                    self.objList[objectIndex]['exists'] = True # store exists status for the quality test
                else:
                     # file doesn't exist
                    self.ui.tableWidget.item(objectIndex,4).setBackground(QtGui.QColor(200,0,0)) # RED
                    print("Texture File missing: " + cmds.getAttr(self.objList[objectIndex]['nodeName'] + "." + self.objList[objectIndex]['nodeType'])) # path)
                    self.objList[objectIndex]['exists'] = False # store exists status for the quality test






    # test all udim variations and return number of found tiles
    def udimFileDetector(self, sourcePathList):
        amount = 0

        cmds.progressWindow(	title='checking Udim Tiles',
					progress=amount,
					status='Progress: ',
					isInterruptable=True )
        fileCount = 0
        num = 0
        for v in range(10):
            if cmds.progressWindow( query=True, isCancelled=True ) :
                break
            for u in range(10):
                if u > 0:
                    if (os.path.isfile(sourcePathList[0] + '.' + str('10') + str(v) + str(u) + '.' + sourcePathList[2])):
                        num += 1
            cmds.progressWindow(edit=True,progress=v*10)
        cmds.progressWindow(endProgress=1)
        return num
    def frameBufferDetector(self,sourcePathList):

        num = 0
        # test each frame in render range
        for frame in range(int(cmds.getAttr('defaultRenderGlobals.startFrame')),int(cmds.getAttr('defaultRenderGlobals.endFrame'))):
                framebuffer = str(10000 + frame)
                if (os.path.isfile(sourcePathList[0] + '.' + framebuffer[1:5] + '.' + sourcePathList[2])):
                        num += 1
        if num == (int(cmds.getAttr('defaultRenderGlobals.endFrame')) - int(cmds.getAttr('defaultRenderGlobals.startFrame'))):
            return True
        else:
            return False



