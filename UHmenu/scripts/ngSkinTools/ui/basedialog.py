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
from ngSkinTools.ui.uiWrappers import FormLayout
from ngSkinTools.ui.constants import Constants
from ngSkinTools.log import LoggerFactory

log = LoggerFactory.getLogger("base dialog")


class Button:
    def __init__(self,title,buttonId):
        self.title = title
        self.buttonId = buttonId
        
    def __str__(self):
        return self.buttonId
        
class BaseDialog:
    currentDialog = None
    
    BUTTON_OK = Button("Ok","ok")
    BUTTON_CANCEL = Button("Cancel","cancel")
    BUTTON_CLOSE =  Button("Close","close")
    
    def __init__(self):
        self.title = "Untitled"
        self.buttons = []
        class Controls:
            pass
        self.controls = Controls()
        
    def createInnerUi(self,parent):
        pass
    
    
    def closeDialogWithResult(self,button):
        '''
        called when button is clicked. buttonID is one of BUTTON_* constants,
        representing which dialog button was clicked
        '''
        cmds.layoutDialog(dismiss=button.buttonId)
        
    
    def createUi(self):
        def getButtonClickHandler(button):
            'helper function to create separate instances of button click handler for each button'
            def handler(*args):
                self.closeDialogWithResult(button)
                
            return handler

        form = FormLayout(useExisting=cmds.setParent(q=True))
        
        
        innerUi = self.createInnerUi(form)
        buttonsForm = FormLayout(parent=form,height=Constants.BUTTON_HEIGHT+Constants.MARGIN_SPACING_VERTICAL*2)
        prevBtn = None
        for button in reversed(self.buttons):
            
            btn = cmds.button(label=button.title,height=Constants.BUTTON_HEIGHT,width=Constants.BUTTON_WIDTH,
                              command=getButtonClickHandler(button));
            
            buttonsForm.attachForm(btn, 0, None if prevBtn is not None else Constants.MARGIN_SPACING_HORIZONTAL*2, None, None)
            if prevBtn is not None:
                buttonsForm.attachControl(btn, prevBtn, None, Constants.MARGIN_SPACING_HORIZONTAL, None, None)
            prevBtn = btn
            
            
        form.attachForm(innerUi, Constants.MARGIN_SPACING_VERTICAL, Constants.MARGIN_SPACING_HORIZONTAL, None, Constants.MARGIN_SPACING_HORIZONTAL)
        form.attachForm(buttonsForm, None, True, True, True)
        form.attachControl(innerUi, buttonsForm, None, None, Constants.MARGIN_SPACING_VERTICAL, None)
        
        
    def execute(self,parentWindow=None):
        BaseDialog.currentDialog = self
        log.debug("executing a dialog")
        
        options = {'ui':self.createUi,'title':self.title}
        if parentWindow is not None:
            options["parent"] = parentWindow
        result = cmds.layoutDialog(**options)
        BaseDialog.currentDialog = None
        log.debug("dialog ended")
        for i in self.buttons:
            if i.buttonId==result:
                return i
        return None
        return result
        