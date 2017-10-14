#
#    ngSkinTools
#    Copyright (c) 2009-2016 Viktoras Makauskas. 
#    All rights reserved.
#    
#    Get more information at 
#        http://www.ngskintools.com
#    
#    --------------------------------------------------------------------------
#
#    The coded instructions, statements, computer programs, and/or related
#    material (collectively the "Data") in these files are subject to the terms 
#    and conditions defined by EULA.
#         
#    A copy of EULA can be found in file 'LICENSE.txt', which is part 
#    of this source code package.
#    

from maya import cmds
from ngSkinTools.ui.uiWrappers import CheckBoxField
from ngSkinTools.ui.options import Options
from ngSkinTools.ui.constants import Constants
from ngSkinTools.ui.basetoolwindow import BaseToolWindow
from datetime import datetime
from ngSkinTools.log import LoggerFactory


class UpdateCheckWindow(BaseToolWindow):
    '''
    An interface for Check-For-Updates feature.
    '''
    
    UPDATE_THREAD = None
    
    def __init__(self,windowName):
        BaseToolWindow.__init__(self,windowName)
        self.updateAvailable = False
        self.windowTitle = 'NgSkinTools Update'
        self.defaultWidth = 500
        self.defaultHeight = 400
        self.sizeable = True
        self.useUserPrefSize = False
    
    def createWindow(self):
        BaseToolWindow.createWindow(self)
        margin1 = 5 
        margin2 = 10

        form = cmds.formLayout(parent=self.windowName)
        self.topLabel = cmds.text(label='',font='boldLabelFont')
        self.customUIContainer = cmds.columnLayout(adjustableColumn=1,rowSpacing=margin2)
        cmds.separator()
        cmds.setParent('..')
        
        lowerRow = cmds.formLayout(height=Constants.BUTTON_HEIGHT)
        checkBox = CheckBoxField(Options.OPTION_CHECKFORUPDATES,label='Automatically check for updates',
                      annotation='Check for updates automatically when ngSkinTools window is opened (once per Maya application session)')
        closeButton = cmds.button(label='Close',align='center',width=80,command=lambda *args:self.closeWindow())

        cmds.formLayout(lowerRow,e=True,attachForm=[(closeButton,'top',0)])
        cmds.formLayout(lowerRow,e=True,attachNone=[(closeButton,'left')])
        cmds.formLayout(lowerRow,e=True,attachForm=[(closeButton,'right',margin1)])
        cmds.formLayout(lowerRow,e=True,attachForm=[(closeButton,'bottom',0)])

        cmds.formLayout(lowerRow,e=True,attachForm=[(checkBox.field,'top',0)])
        cmds.formLayout(lowerRow,e=True,attachForm=[(checkBox.field,'left',margin1)])
        cmds.formLayout(lowerRow,e=True,attachControl=[(checkBox.field,'right',margin1,closeButton)])
        cmds.formLayout(lowerRow,e=True,attachForm=[(checkBox.field,'bottom',0)])

        
        
        cmds.formLayout(form,e=True,attachForm=[(self.topLabel,'top',margin2)])
        cmds.formLayout(form,e=True,attachForm=[(self.topLabel,'left',margin1)])
        cmds.formLayout(form,e=True,attachNone=[(self.topLabel,'right')])
        cmds.formLayout(form,e=True,attachNone=[(self.topLabel,'bottom')])

        cmds.formLayout(form,e=True,attachNone=[(lowerRow,'top')])
        cmds.formLayout(form,e=True,attachForm=[(lowerRow,'left',margin1)])
        cmds.formLayout(form,e=True,attachForm=[(lowerRow,'right',margin1)])
        cmds.formLayout(form,e=True,attachForm=[(lowerRow,'bottom',margin1)])
        
        cmds.formLayout(form,e=True,attachControl=[(self.customUIContainer,'top',margin2,self.topLabel)])
        cmds.formLayout(form,e=True,attachForm=[(self.customUIContainer,'left',margin1)])
        cmds.formLayout(form,e=True,attachForm=[(self.customUIContainer,'right',margin1)])
        cmds.formLayout(form,e=True,attachControl=[(self.customUIContainer,'bottom',margin2,lowerRow)])
        
    def setTopLabel(self,message):
        cmds.text(self.topLabel,e=True, label=message)
        
    def addMessage(self,message):
        cmds.text(label=message,parent=self.customUIContainer,wordWrap=True,width=300,align='left')
        
    def addButton(self,title,command):
        cmds.button(label=title,parent=self.customUIContainer,command=lambda *args:command())
    
        
class ResultsData:
    def __init__(self):
        self.updateAvailable = False
        self.versionAvailable = "1.0"
        self.updateDate = datetime.now()

class ResultsDisplay:        
    WINDOW_NAME='ngSkinToolsUpdateCheckWindow'
    
    def showInfoWindow(self,title,message):
        BaseToolWindow.destroyWindow(self.WINDOW_NAME)
        w = BaseToolWindow.getWindowInstance(self.WINDOW_NAME, UpdateCheckWindow)
        w.setTopLabel(title)
        w.addMessage(message)
        w.showWindow()

    def showResultsWindow(self,data):
        '''
        :param ResultsData data: data to show for results window 
        '''
        BaseToolWindow.destroyWindow(self.WINDOW_NAME)
        w = BaseToolWindow.getWindowInstance(self.WINDOW_NAME, UpdateCheckWindow)
        w.setTopLabel('Update Available' if data.updateAvailable else 'No Updates Found')
        
        if data.updateAvailable:
            w.addMessage("New plugin version available: {0}".format(data.versionAvailable))
        else:
            w.addMessage("Plugin is up to date")

        w.addMessage("Released date: %s"%data.updateDate.strftime("%d %B, %Y"))
        
        
        def linkOpener(url):
            def result(*args):
                import webbrowser
                webbrowser.open(url)
            return result
        
        w.addButton("ngskintools.com",linkOpener("http://www.ngskintools.com"))
        w.showWindow()

