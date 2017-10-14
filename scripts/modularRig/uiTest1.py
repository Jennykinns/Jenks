import maya.cmds as cmds
import uiTest1_UI as customUI
import maya.OpenMayaUI as omUi
from functools import partial

try:
    from PySide import QtGui, QtCore
    import PySide.QtGui as QtWidgets
    from shiboken import wrapInstance
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets
    from shiboken2 import wrapInstance

reload(customUI)

## remove global variables from previous runs
deleteVars=[]
var = None
val = None
for var, val in globals().iteritems():
    if 'limb' in var:
        deleteVars.append(var)
for x in deleteVars:
    del globals()[x]

limbBoxNum = 0
currentLimbBoxes = []
mode = False
spineJntsNum = 7
locScaleSpnBoxVal = 1
ctrlScaleSpnBoxVal = 1
butt = None
rigName = None

iconDir=cmds.internalVar(uad=True)+"scripts/Jenks/scripts/curveCreator/icons/"

def maya_main_window():
    main_window_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def main():
    global myWindow

    try:
        myWindow.close()
    except: pass
    myWindow = myTool(parent=maya_main_window())
    myWindow.show()


class myTool(QtWidgets.QDialog):
    def __init__(self,parent = None):

        reload(customUI)
        print("loaded")

        super(myTool, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui =  customUI.Ui_Form()

        self.ui.setupUi(self)

        ## connect inputs to functions
        self.ui.newEntry.clicked.connect(self.add)
        self.ui.clearEntries.clicked.connect(self.clear)
        self.ui.biRad.clicked.connect(partial(self.updateModeRad, False))
        self.ui.quadRad.clicked.connect(partial(self.updateModeRad, True))
        self.ui.nameEdit.textChanged.connect(self.updateName)
        self.ui.spineSpnBox.valueChanged.connect(self.updateSpineSpnBox)
        self.ui.main1SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'main1'))
        self.ui.main2SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'main2'))
        self.ui.main3SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'main3'))
        self.ui.left1SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'left1'))
        self.ui.left2SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'left2'))
        self.ui.left3SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'left3'))
        self.ui.right1SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'right1'))
        self.ui.right2SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'right2'))
        self.ui.right3SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'right3'))
        self.ui.settings1SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'settings1'))
        self.ui.settings2SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'settings2'))
        self.ui.settings3SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'settings3'))
        self.ui.misc1SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'misc1'))
        self.ui.misc2SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'misc2'))
        self.ui.misc3SpnBox.valueChanged.connect(partial(self.updateColSpnBox, 'misc3'))
        self.ui.locScaleSpnBox.valueChanged.connect(self.updateLocScaleSpnBox)
        self.ui.ctrlScaleSpnBox.valueChanged.connect(self.updateCtrlScaleSpnBox)
        self.ui.locsBtn.pressed.connect(self.updateLocsBtn)
        self.ui.mirrorBtn.pressed.connect(self.updateMirrorBtn)
        self.ui.createBtn.pressed.connect(self.updateCreateBtn)

        self.updateColSpnBox('main1', '11')
        self.updateColSpnBox('main2', '23')
        self.updateColSpnBox('main3', '24')
        self.updateColSpnBox('left1', '16')
        self.updateColSpnBox('left2', '29')
        self.updateColSpnBox('left3', '30')
        self.updateColSpnBox('right1', '13')
        self.updateColSpnBox('right2', '25')
        self.updateColSpnBox('right3', '22')
        self.updateColSpnBox('settings1', '27')
        self.updateColSpnBox('settings2', '32')
        self.updateColSpnBox('settings3', '8')
        self.updateColSpnBox('misc1', '31')
        self.updateColSpnBox('misc2', '1')
        self.updateColSpnBox('misc3', '1')

        for i in range(3):
            if i > 1:
                self.add(typ=1)
            elif i > 0:
                self.add(typ=0)
            else:
                self.add(typ=3)


    def add(self, typ=0, *args):
        global limbBoxNum
        global currentLimbBoxes
        limbBoxNum += 1
        num = str(limbBoxNum)
        currentLimbBoxes.append(num)
        ## set default mirror
        if typ == 0 or typ == 1:
            mir = True
        else:
            mir = False
        ## create limb entry
        exec('self.limbBox_'+num+' = QtWidgets.QWidget(self.ui.scrollAreaWidgetContents)')
        exec('self.limbBox_'+num+'.setMinimumSize(QtCore.QSize(400, 60))')
        exec('self.limbBox_'+num+'.setMaximumSize(QtCore.QSize(400, 60))')
        exec('self.limbBox_'+num+'.setObjectName("limbBox_'+num+'")')
        exec('self.limbBoxGrid = QtWidgets.QGridLayout(self.limbBox_'+num+')')
        self.limbBoxGrid.setContentsMargins(0, 0, 0, 0)
        self.limbBoxGrid.setSpacing(0)
        self.limbBoxGrid.setContentsMargins(0, 0, 0, 0)
        self.limbBoxGrid.setObjectName("limbBoxGrid")
        exec('self.limbBoxInside = QtWidgets.QGroupBox(self.limbBox_'+num+')')
        self.limbBoxInside.setTitle("")
        self.limbBoxInside.setObjectName("limbBoxInside")
        self.limbBoxInsideGrid = QtWidgets.QGridLayout(self.limbBoxInside)
        self.limbBoxInsideGrid.setContentsMargins(0, 0, 0, 0)
        self.limbBoxInsideGrid.setHorizontalSpacing(2)
        self.limbBoxInsideGrid.setVerticalSpacing(0)
        self.limbBoxInsideGrid.setObjectName("limbBoxInsideGrid")
        exec('self.limbMinus_'+num+' = QtWidgets.QPushButton(self.limbBoxInside)')
        exec('self.limbMinus_'+num+'.setMaximumSize(QtCore.QSize(10, 10))')
        exec('self.limbMinus_'+num+'.setObjectName("limbMinus_'+num+'")')
        exec('self.limbBoxInsideGrid.addWidget(self.limbMinus_'+num+', 0, 0, 1, 1)')
        exec('self.limbType_'+num+' = QtWidgets.QComboBox(self.limbBoxInside)')
        exec('self.limbType_'+num+'.setMaximumSize(QtCore.QSize(60, 50))')
        exec('self.limbType_'+num+'.setObjectName("limbType_'+num+'")')
        exec('self.limbType_'+num+'.addItem("")')
        exec('self.limbType_'+num+'.addItem("")')
        exec('self.limbType_'+num+'.addItem("")')
        exec('self.limbType_'+num+'.addItem("")')
        exec('self.limbBoxInsideGrid.addWidget(self.limbType_'+num+', 0, 1, 1, 1)')
        exec('self.limbSide_'+num+' = QtWidgets.QLineEdit(self.limbBoxInside)')
        exec('self.limbSide_'+num+'.setObjectName("limbSide_'+num+'")')
        exec('self.limbBoxInsideGrid.addWidget(self.limbSide_'+num+', 0, 2, 1, 1)')
        exec('self.limbMir_'+num+' = QtWidgets.QLineEdit(self.limbBoxInside)')
        exec('self.limbMir_'+num+'.setObjectName("limbMir_'+num+'")')
        exec('self.limbBoxInsideGrid.addWidget(self.limbMir_'+num+', 0, 3, 1, 1)')
        exec('self.limbName_'+num+' = QtWidgets.QLineEdit(self.limbBoxInside)')
        exec('self.limbName_'+num+'.setObjectName("limbName_'+num+'")')
        exec('self.limbBoxInsideGrid.addWidget(self.limbName_'+num+', 0, 4, 1, 1)')
        exec('self.limbParent_'+num+' = QtWidgets.QLineEdit(self.limbBoxInside)')
        exec('self.limbParent_'+num+'.setObjectName("limbParent_'+num+'")')
        exec('self.limbBoxInsideGrid.addWidget(self.limbParent_'+num+', 0, 5, 1, 1)')
        self.limbOptions = QtWidgets.QGridLayout()
        self.limbOptions.setSpacing(0)
        self.limbOptions.setObjectName("limbOptions")
        exec('self.limbOpt1_'+num+' = QtWidgets.QCheckBox(self.limbBoxInside)')
        exec('self.limbOpt1_'+num+'.setObjectName("limbOpt1_'+num+'")')
        exec('self.limbOptions.addWidget(self.limbOpt1_'+num+', 0, 0, 1, 1)')
        exec('self.limbOpt2_'+num+' = QtWidgets.QCheckBox(self.limbBoxInside)')
        exec('self.limbOpt2_'+num+'.setObjectName("limbOpt2_'+num+'")')
        exec('self.limbOptions.addWidget(self.limbOpt2_'+num+', 0, 1, 1, 1)')
        exec('self.limbOpt3_'+num+' = QtWidgets.QCheckBox(self.limbBoxInside)')
        exec('self.limbOpt3_'+num+'.setObjectName("limbOpt3_'+num+'")')
        exec('self.limbOptions.addWidget(self.limbOpt3_'+num+', 0, 2, 1, 1)')
        exec('self.limbOpt4_'+num+' = QtWidgets.QCheckBox(self.limbBoxInside)')
        exec('self.limbOpt4_'+num+'.setObjectName("limbOpt4_'+num+'")')
        exec('self.limbOptions.addWidget(self.limbOpt4_'+num+', 1, 0, 1, 1)')
        exec('self.limbOpt5_'+num+' = QtWidgets.QCheckBox(self.limbBoxInside)')
        exec('self.limbOpt5_'+num+'.setObjectName("limbOpt5_'+num+'")')
        exec('self.limbOptions.addWidget(self.limbOpt5_'+num+', 1, 1, 1, 1)')
        exec('self.limbOpt6_'+num+' = QtWidgets.QCheckBox(self.limbBoxInside)')
        exec('self.limbOpt6_'+num+'.setObjectName("limbOpt6_'+num+'")')
        exec('self.limbOptions.addWidget(self.limbOpt6_'+num+', 1, 2, 1, 1)')
        exec('self.limbMirTog_'+num+' = QtWidgets.QCheckBox(self.limbBoxInside)')
        exec('self.limbMirTog_'+num+'.setMaximumSize(QtCore.QSize(15, 15))')
        exec('self.limbMirTog_'+num+'.setText("")')
        exec('self.limbMirTog_'+num+'.setObjectName("limbMirTog_'+num+'")')
        exec('self.limbOptions.addWidget(self.limbMirTog_'+num+', 0, 3, 2, 1)')
        exec('self.limbMirBtn_'+num+' = QtWidgets.QPushButton(self.limbBoxInside)')
        exec('self.limbMirBtn_'+num+'.setMinimumSize(QtCore.QSize(40, 25))')
        exec('self.limbMirBtn_'+num+'.setMaximumSize(QtCore.QSize(40, 25))')
        exec('self.limbMirBtn_'+num+'.setObjectName("limbMirBtn_'+num+'")')
        exec('self.limbOptions.addWidget(self.limbMirBtn_'+num+', 0, 5, 2, 1)')
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.limbOptions.addItem(spacerItem, 0, 6, 2, 1)
        spacerItem1 = QtWidgets.QSpacerItem(7, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.limbOptions.addItem(spacerItem1, 0, 4, 2, 1)
        self.limbBoxInsideGrid.addLayout(self.limbOptions, 2, 0, 1, 6)
        self.limbSep = QtWidgets.QFrame(self.limbBoxInside)
        self.limbSep.setFrameShape(QtWidgets.QFrame.HLine)
        self.limbSep.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.limbSep.setObjectName("limbSep")
        self.limbBoxInsideGrid.addWidget(self.limbSep, 1, 0, 1, 6)
        self.limbBoxGrid.addWidget(self.limbBoxInside, 0, 0, 1, 1)
        exec('self.ui.formLayout.setWidget('+str(limbBoxNum-1)+', QtWidgets.QFormLayout.LabelRole, self.limbBox_'+num+')')

        ## limb type click down index
        exec('self.limbType_'+num+'.setCurrentIndex('+str(typ)+')')

        ## labels
        exec('self.limbType_'+num+'.setItemText(0, QtWidgets.QApplication.translate("Form", "Arm", None, -1))')
        exec('self.limbType_'+num+'.setItemText(1, QtWidgets.QApplication.translate("Form", "Leg", None, -1))')
        exec('self.limbType_'+num+'.setItemText(2, QtWidgets.QApplication.translate("Form", "Tail", None, -1))')
        exec('self.limbType_'+num+'.setItemText(3, QtWidgets.QApplication.translate("Form", "Head", None, -1))')
        exec('self.limbMinus_'+num+'.setText(QtWidgets.QApplication.translate("Form", "-", None, -1))')
        exec('self.limbSide_'+num+'.setPlaceholderText(QtWidgets.QApplication.translate("Form", "Side (Opt)", None, -1))')
        exec('self.limbMir_'+num+'.setPlaceholderText(QtWidgets.QApplication.translate("Form", "Mirror Side", None, -1))')
        exec('self.limbName_'+num+'.setPlaceholderText(QtWidgets.QApplication.translate("Form", "Name (Opt)", None, -1))')
        exec('self.limbParent_'+num+'.setPlaceholderText(QtWidgets.QApplication.translate("Form", "Parent Joint", None, -1))')
        exec('self.limbOpt3_'+num+'.setText(QtWidgets.QApplication.translate("Form", "Stretchy", None, -1))')
        exec('self.limbOpt1_'+num+'.setText(QtWidgets.QApplication.translate("Form", "Fingers/Toes", None, -1))')
        exec('self.limbOpt2_'+num+'.setText(QtWidgets.QApplication.translate("Form", "FK/IK Switch", None, -1))')
        exec('self.limbOpt4_'+num+'.setText(QtWidgets.QApplication.translate("Form", "Soft IK", None, -1))')
        exec('self.limbOpt5_'+num+'.setText(QtWidgets.QApplication.translate("Form", "Ribbon", None, -1))')
        exec('self.limbOpt6_'+num+'.setText(QtWidgets.QApplication.translate("Form", "Auto Clav", None, -1))')
        exec('self.limbMirBtn_'+num+'.setText(QtWidgets.QApplication.translate("Form", "Mirror", None, -1))')

        ## force initial updates
        self.updateLimbType(num, typ)
        if mir:
            self.updateLimbMirTog(num, 2)
        else:
            self.updateLimbMirTog(num, 0)


        ## connect limb inputs to functions
        exec('self.limbMinus_'+num+'.clicked.connect(partial(self.updateLimbMinus, num))')
        exec('self.limbSide_'+num+'.textChanged.connect(partial(self.updateLimbSide, num))')
        exec('self.limbName_'+num+'.textChanged.connect(partial(self.updateLimbName, num))')
        exec('self.limbParent_'+num+'.textChanged.connect(partial(self.updateLimbParent, num))')
        exec('self.limbType_'+num+'.currentIndexChanged.connect(partial(self.updateLimbType, num))')
        exec('self.limbOpt1_'+num+'.stateChanged.connect(partial(self.updateLimbOpt, num, "1"))')
        exec('self.limbOpt2_'+num+'.stateChanged.connect(partial(self.updateLimbOpt, num, "2"))')
        exec('self.limbOpt3_'+num+'.stateChanged.connect(partial(self.updateLimbOpt, num, "3"))')
        exec('self.limbOpt4_'+num+'.stateChanged.connect(partial(self.updateLimbOpt, num, "4"))')
        exec('self.limbOpt5_'+num+'.stateChanged.connect(partial(self.updateLimbOpt, num, "5"))')
        exec('self.limbOpt6_'+num+'.stateChanged.connect(partial(self.updateLimbOpt, num, "6"))')
        exec('self.limbMir_'+num+'.textChanged.connect(partial(self.updateLimbMirName, num))')
        exec('self.limbMirTog_'+num+'.stateChanged.connect(partial(self.updateLimbMirTog, num))')
        exec('self.limbMirBtn_'+num+'.clicked.connect(partial(self.updateLimbMirBtn, num))')

        ## set text edit vars to Blank
        self.updateLimbName(num, '')
        self.updateLimbSide(num, '')
        self.updateLimbMirName(num, '')


    def clear(self, *args):
        global limbBoxNum
        global currentLimbBoxes
        # for i in range(limbBoxNum):
        #     i = str(i+1)
        #     try:
        #         exec('self.ui.formLayout.removeWidget(self.limbBox_'+i+')')
        #         exec('self.limbBox_'+i+'.deleteLater()')
        #         exec('self.limbBox_'+i+' = None')
        #     except AttributeError:
        #         continue
        for i in currentLimbBoxes:
            try:
                exec('self.ui.formLayout.removeWidget(self.limbBox_'+i+')')
                exec('self.limbBox_'+i+'.deleteLater()')
                exec('self.limbBox_'+i+' = None')
            except AttributeError:
                continue
        currentLimbBoxes = []


    def updateModeRad(self, val, *args):
        global mode
        mode = val


    def updateName(self, val, *args):
        global rigName
        rigName = val


    def updateSpineSpnBox(self, val, *args):
        global spineJntsNum
        spineJntsNum = val
        armLimbBoxes = []
        for x in currentLimbBoxes:
            if eval('limbType_'+x+'Val') == 0:
                armLimbBoxes.append(x)
        for x in armLimbBoxes:
            self.setParentText(x, 0)


    def updateColSpnBox(self, box, val, *args):
        exec(box+'SpnBoxVal = '+str(val), globals())
        exec('self.ui.'+box+'ImgBtn.setIcon(QtGui.QIcon(iconDir+"Colour"+str(val).zfill(2)+".png"))')


    def updateLocScaleSpnBox(self, val, *args):
        global locScaleSpnBoxVal
        locScaleSpnBoxVal = val


    def updateCtrlScaleSpnBox(self, val, *args):
        global ctrlScaleSpnBoxVal
        ctrlScaleSpnBoxVal = val


    def updateLocsBtn(self, *args):
        if not rigName:
            if mode:
                name = 'Quadruped'
            else:
                name = 'Biped'
        print '-----'
        print ''
        print 'Name: '+str(name)
        print 'Scale: '+str(locScaleSpnBoxVal)+', '+str(ctrlScaleSpnBoxVal)
        if mode:
            print 'Mode: Quadruped'
        else:
            print 'Mode: Biped'
        print 'Spine Joints: '+str(spineJntsNum)
        for x in currentLimbBoxes:
            self.getLimbOptions(str(x))


    def updateMirrorBtn(self, *args):
        print 'Mirror Locators Btn Pressed'
        for k,v in globals().iteritems():
            if str(k).startswith('limb'):
                print str(k)+' : '+str(v)


    def updateCreateBtn(self, *args):
        print 'Create Rig Btn Pressed'
        print currentLimbBoxes


    def updateLimbName(self, num, val, *args):
        exec('limbName_'+num+'Val = "'+str(val)+'"', globals())


    def updateLimbSide(self, num, val, *args):
        exec('limbSide_'+num+'Val = "'+str(val)+'"', globals())


    def updateLimbParent(self, num, val, *args):
        exec('limbParent_'+num+'Val = "'+str(val)+'"', globals())


    def updateLimbMinus(self, num, *args):
        global currentLimbBoxes
        exec('self.ui.formLayout.removeWidget(self.limbBox_'+num+')')
        exec('self.limbBox_'+num+'.deleteLater()')
        exec('self.limbBox_'+num+' = None')
        currentLimbBoxes.remove(num)


    def updateLimbType(self, num, val, *args):
        exec('limbType_'+num+'Val = '+str(val), globals())
        ## set parent text
        self.setParentText(num, val)
        ## default options by type
        if val == 0: ## arm
            exec('self.limbOpt1_'+num+'.setText("Fingers")')
            exec('self.limbOpt1_'+num+'.setEnabled(True)')
            exec('limbOpt1Checked = self.limbOpt1_'+num+'.isChecked()')
            if not limbOpt1Checked:
                exec('self.limbOpt1_'+num+'.toggle()')
            self.updateLimbOpt(num, '1', 2)
            exec('self.limbOpt2_'+num+'.setText("FK/IK Switch")')
            exec('self.limbOpt2_'+num+'.setEnabled(True)')
            exec('limbOpt2Checked = self.limbOpt2_'+num+'.isChecked()')
            if not limbOpt2Checked:
                exec('self.limbOpt2_'+num+'.toggle()')
            self.updateLimbOpt(num, '2', 2)
            exec('self.limbOpt3_'+num+'.setText("Stretchy [NI]")')
            exec('self.limbOpt3_'+num+'.setEnabled(True)')
            exec('limbOpt3Checked = self.limbOpt3_'+num+'.isChecked()')
            if not limbOpt3Checked:
                exec('self.limbOpt3_'+num+'.toggle()')
            self.updateLimbOpt(num, '3', 2)
            exec('self.limbOpt4_'+num+'.setText("Soft IK [NI]")')
            exec('self.limbOpt4_'+num+'.setEnabled(True)')
            exec('limbOpt4Checked = self.limbOpt4_'+num+'.isChecked()')
            if not limbOpt4Checked:
                exec('self.limbOpt4_'+num+'.toggle()')
            self.updateLimbOpt(num, '4', 2)
            exec('self.limbOpt5_'+num+'.setText("Ribbon [NI]")')
            exec('self.limbOpt5_'+num+'.setEnabled(True)')
            exec('limbOpt5Checked = self.limbOpt5_'+num+'.isChecked()')
            if limbOpt5Checked:
                exec('self.limbOpt5_'+num+'.toggle()')
            self.updateLimbOpt(num, '5', 0)
            exec('self.limbOpt6_'+num+'.setText("Auto Clav [NI]")')
            exec('self.limbOpt6_'+num+'.setEnabled(True)')
            exec('limbOpt6Checked = self.limbOpt6_'+num+'.isChecked()')
            if not limbOpt6Checked:
                exec('self.limbOpt6_'+num+'.toggle()')
            self.updateLimbOpt(num, '6', 2)
            exec('limbMirTogChecked = self.limbMirTog_'+num+'.isChecked()')
            if not limbMirTogChecked:
                exec('self.limbMirTog_'+num+'.toggle()')
            self.updateLimbMirTog(num, 2)
        elif val == 1: ## leg
            exec('self.limbOpt1_'+num+'.setText("Toes")')
            exec('self.limbOpt1_'+num+'.setEnabled(True)')
            exec('limbOpt1Checked = self.limbOpt1_'+num+'.isChecked()')
            if limbOpt1Checked:
                exec('self.limbOpt1_'+num+'.toggle()')
            self.updateLimbOpt(num, '1', 0)
            exec('self.limbOpt2_'+num+'.setText("FK/IK Switch")')
            exec('self.limbOpt2_'+num+'.setEnabled(True)')
            exec('limbOpt2Checked = self.limbOpt2_'+num+'.isChecked()')
            if not limbOpt2Checked:
                exec('self.limbOpt2_'+num+'.toggle()')
            self.updateLimbOpt(num, '2', 2)
            exec('self.limbOpt3_'+num+'.setText("Stretchy [NI]")')
            exec('self.limbOpt3_'+num+'.setEnabled(True)')
            exec('limbOpt3Checked = self.limbOpt3_'+num+'.isChecked()')
            if not limbOpt3Checked:
                exec('self.limbOpt3_'+num+'.toggle()')
            self.updateLimbOpt(num, '3', 2)
            exec('self.limbOpt4_'+num+'.setText("Soft IK [NI]")')
            exec('self.limbOpt4_'+num+'.setEnabled(True)')
            exec('limbOpt4Checked = self.limbOpt4_'+num+'.isChecked()')
            if not limbOpt4Checked:
                exec('self.limbOpt4_'+num+'.toggle()')
            self.updateLimbOpt(num, '4', 2)
            exec('self.limbOpt5_'+num+'.setText("Ribbon [NI]")')
            exec('self.limbOpt5_'+num+'.setEnabled(True)')
            exec('limbOpt5Checked = self.limbOpt5_'+num+'.isChecked()')
            if limbOpt5Checked:
                exec('self.limbOpt5_'+num+'.toggle()')
            self.updateLimbOpt(num, '5', 0)
            exec('self.limbOpt6_'+num+'.setText("-")')
            exec('self.limbOpt6_'+num+'.setEnabled(False)')
            exec('limbOpt6Checked = self.limbOpt6_'+num+'.isChecked()')
            if limbOpt6Checked:
                exec('self.limbOpt6_'+num+'.toggle()')
            self.updateLimbOpt(num, '6', 0)
            exec('limbMirTogChecked = self.limbMirTog_'+num+'.isChecked()')
            if not limbMirTogChecked:
                exec('self.limbMirTog_'+num+'.toggle()')
            self.updateLimbMirTog(num, 2)
        elif val == 2: ## tail
            exec('self.limbOpt1_'+num+'.setText("IK Spline")')
            exec('self.limbOpt1_'+num+'.setEnabled(True)')
            exec('limbOpt1Checked = self.limbOpt1_'+num+'.isChecked()')
            if not limbOpt1Checked:
                exec('self.limbOpt1_'+num+'.toggle()')
            self.updateLimbOpt(num, '1', 2)
            exec('self.limbOpt2_'+num+'.setText("Dynamics [NI]")')
            exec('self.limbOpt2_'+num+'.setEnabled(True)')
            exec('limbOpt2Checked = self.limbOpt2_'+num+'.isChecked()')
            if limbOpt2Checked:
                exec('self.limbOpt2_'+num+'.toggle()')
            self.updateLimbOpt(num, '2', 0)
            exec('self.limbOpt3_'+num+'.setText("-")')
            exec('self.limbOpt3_'+num+'.setEnabled(False)')
            exec('limbOpt3Checked = self.limbOpt3_'+num+'.isChecked()')
            if limbOpt3Checked:
                exec('self.limbOpt3_'+num+'.toggle()')
            self.updateLimbOpt(num, '3', 0)
            exec('self.limbOpt4_'+num+'.setText("-")')
            exec('self.limbOpt4_'+num+'.setEnabled(False)')
            exec('limbOpt4Checked = self.limbOpt4_'+num+'.isChecked()')
            if limbOpt4Checked:
                exec('self.limbOpt4_'+num+'.toggle()')
            self.updateLimbOpt(num, '4', 0)
            exec('self.limbOpt5_'+num+'.setText("-")')
            exec('self.limbOpt5_'+num+'.setEnabled(False)')
            exec('limbOpt5Checked = self.limbOpt5_'+num+'.isChecked()')
            if limbOpt5Checked:
                exec('self.limbOpt5_'+num+'.toggle()')
            self.updateLimbOpt(num, '5', 0)
            exec('self.limbOpt6_'+num+'.setText("-")')
            exec('self.limbOpt6_'+num+'.setEnabled(False)')
            exec('limbOpt6Checked = self.limbOpt6_'+num+'.isChecked()')
            if limbOpt6Checked:
                exec('self.limbOpt6_'+num+'.toggle()')
            self.updateLimbOpt(num, '6', 0)
            exec('limbMirTogChecked = self.limbMirTog_'+num+'.isChecked()')
            if limbMirTogChecked:
                exec('self.limbMirTog_'+num+'.toggle()')
            self.updateLimbMirTog(num, 0)
        else: ## head
            exec('self.limbOpt1_'+num+'.setText("IK")')
            exec('self.limbOpt1_'+num+'.setEnabled(True)')
            exec('limbOpt1Checked = self.limbOpt1_'+num+'.isChecked()')
            if not limbOpt1Checked:
                exec('self.limbOpt1_'+num+'.toggle()')
            self.updateLimbOpt(num, '1', 2)
            exec('self.limbOpt2_'+num+'.setText("-")')
            exec('self.limbOpt2_'+num+'.setEnabled(False)')
            exec('limbOpt2Checked = self.limbOpt2_'+num+'.isChecked()')
            if limbOpt2Checked:
                exec('self.limbOpt2_'+num+'.toggle()')
            self.updateLimbOpt(num, '2', 0)
            exec('self.limbOpt3_'+num+'.setText("-")')
            exec('self.limbOpt3_'+num+'.setEnabled(False)')
            exec('limbOpt3Checked = self.limbOpt3_'+num+'.isChecked()')
            if limbOpt3Checked:
                exec('self.limbOpt3_'+num+'.toggle()')
            self.updateLimbOpt(num, '3', 0)
            exec('self.limbOpt4_'+num+'.setText("-")')
            exec('self.limbOpt4_'+num+'.setEnabled(False)')
            exec('limbOpt4Checked = self.limbOpt4_'+num+'.isChecked()')
            if limbOpt4Checked:
                exec('self.limbOpt4_'+num+'.toggle()')
            self.updateLimbOpt(num, '4', 0)
            exec('self.limbOpt5_'+num+'.setText("-")')
            exec('self.limbOpt5_'+num+'.setEnabled(False)')
            exec('limbOpt5Checked = self.limbOpt5_'+num+'.isChecked()')
            if limbOpt5Checked:
                exec('self.limbOpt5_'+num+'.toggle()')
            self.updateLimbOpt(num, '5', 0)
            exec('self.limbOpt6_'+num+'.setText("-")')
            exec('self.limbOpt6_'+num+'.setEnabled(False)')
            exec('limbOpt6Checked = self.limbOpt6_'+num+'.isChecked()')
            if limbOpt6Checked:
                exec('self.limbOpt6_'+num+'.toggle()')
            self.updateLimbOpt(num, '6', 0)
            exec('limbMirTogChecked = self.limbMirTog_'+num+'.isChecked()')
            if limbMirTogChecked:
                exec('self.limbMirTog_'+num+'.toggle()')
            self.updateLimbMirTog(num, 0)


    def updateLimbOpt(self, num, optNum, val, *args):
        exec('limbOpt'+optNum+'_'+num+'Val = '+str(val), globals())


    def updateLimbMirName(self, num, val, *args):
        exec('limbMirName_'+num+'Val = "'+str(val)+'"', globals())


    def updateLimbMirTog(self, num, val, *args):
        exec('limbMirTog_'+num+'Val = '+str(val), globals())
        exec('self.limbMirBtn_'+num+'.setEnabled('+str(val)+')')
        exec('self.limbMir_'+num+'.setEnabled('+str(val)+')')
        if val:
            exec('self.limbSide_'+num+'.setPlaceholderText(QtWidgets.QApplication.translate("Form", "Side", None, -1))')
        else:
            exec('self.limbSide_'+num+'.setPlaceholderText(QtWidgets.QApplication.translate("Form", "Side (Opt)", None, -1))')


    def updateLimbMirBtn(self, num, *args):
        print 'Mirror Btn '+num+' Pressed'


    def setParentText(self, num, type, *args):
        if type == 0:   ## arm
            parName = int(spineJntsNum / 1.5 + (spineJntsNum % 1.5 > 0)-1)
            if spineJntsNum < 12:
                parentTxt = 'spine_'+str(parName).zfill(2)
            elif spineJntsNum < 102:
                parentTxt = 'spine_'+str(parName).zfill(3)
        elif type == 1: ## leg
            parentTxt = 'spine_base'
        elif type == 2: ## tail
            parentTxt = 'spine_base'
        else:   ## head
            parentTxt = 'spine_end'

        exec('self.limbParent_'+num+'.setText(parentTxt)')
        self.updateLimbParent(num, parentTxt)


    def getLimbOptions(self, num, *args):
        print ''
        print '--- Limb '+num+' Options: '
        exec('print "Limb Name: "+str(limbName_'+num+'Val)')
        exec('print "Limb Side: "+str(limbSide_'+num+'Val)')
        exec('print "Limb Mirror Side: "+str(limbMirName_'+num+'Val)')
        exec('print "Limb Parent: "+str(limbParent_'+num+'Val)')
        exec('print "Mirror: "+str(limbMirTog_'+num+'Val)')
        print '--'
        if eval('limbType_'+num+'Val') == 0:
            exec('print "Fingers: "+str(limbOpt1_'+num+'Val)')
            exec('print "FK/IK: "+str(limbOpt2_'+num+'Val)')
            exec('print "Stretchy: "+str(limbOpt3_'+num+'Val)')
            exec('print "Soft IK: "+str(limbOpt4_'+num+'Val)')
            exec('print "Ribbon: "+str(limbOpt5_'+num+'Val)')
            exec('print "Auto Clav: "+str(limbOpt6_'+num+'Val)')
        elif eval('limbType_'+num+'Val') == 1:
            exec('print "Toes: "+str(limbOpt1_'+num+'Val)')
            exec('print "FK/IK: "+str(limbOpt2_'+num+'Val)')
            exec('print "Stretchy: "+str(limbOpt3_'+num+'Val)')
            exec('print "Soft IK: "+str(limbOpt4_'+num+'Val)')
            exec('print "Ribbon: "+str(limbOpt5_'+num+'Val)')
        elif eval('limbType_'+num+'Val') == 2:
            exec('print "IK Spline: "+str(limbOpt1_'+num+'Val)')
            exec('print "Dynamics: "+str(limbOpt2_'+num+'Val)')
        else:
            exec('print "IK: "+str(limbOpt1_'+num+'Val)')



main()
