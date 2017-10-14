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

from ngSkinTools.ui.basedialog import BaseDialog
from ngSkinTools.ui.uiWrappers import FormLayout
from maya import cmds
from ngSkinTools.ui import basedialog
from ngSkinTools import license
from ngSkinTools.utils import Utils
from ngSkinTools.ui.events import LayerEvents

class LicenseDialog(BaseDialog):
    BUTTON_SAVE = basedialog.Button("Save", "save")
    
    def __init__(self):
        BaseDialog.__init__(self)
        self.title = "ngSkinTools license"
        self.buttons = [self.BUTTON_SAVE, self.BUTTON_CANCEL]

    def createInnerUi(self, parent):
        layout = FormLayout(parent=parent, width=400, height=180)
        
        description = "If you've purchased ngSkinTools already, you should have received email with a license key. " + \
            "Enter that key into the field below. Contact support@ngskintools.com if you're having any issues " + \
            "getting the key authorized.\n\n" + \
            "Note: the license will be locked to this computer on first use.\n\n" + \
            "For more information, visit www.ngskintools.com."  
        
        cmds.setParent(layout)
        labelDescription = cmds.scrollField(editable=False, wordWrap=True, text=description, font='obliqueLabelFont') 
        labelTitle = cmds.text(label="License key:", font='boldLabelFont')
        editLicenseKey = self.controls.editLicenseKey = cmds.textField(alwaysInvokeEnterCommandOnReturn=True,enterCommand=lambda *args:self.closeDialogWithResult(self.BUTTON_SAVE))
        

        layout.attachForm(labelDescription, 0, 10, None, 10)
        layout.attachForm(editLicenseKey, None, 10, 10, 10)
        layout.attachForm(labelTitle, None, None, None, 10)
        
        
        layout.attachControl(labelTitle, editLicenseKey, None, None, 5, None)
        layout.attachControl(labelDescription, labelTitle, None, None, 15, None)
        
        return layout
        
    def closeDialogWithResult(self, button):
        if button == self.BUTTON_SAVE:
            key = cmds.textField(self.controls.editLicenseKey, q=True, text=True)
            raise Exception("unfinished here")
            result = license.validateLicense()
            if result==0:
                LayerEvents.layerAvailabilityChanged.emit()
                Utils.confirmDialog(title='Key accepted', message="License key was accepted. Thank you.", button=['Ok'], defaultButton='Ok')
            else:
                Utils.confirmDialog(title='Key not accepted', message="Error: license key was not accepted.", button=['Ok'], defaultButton='Ok')
                return

        BaseDialog.closeDialogWithResult(self, button)
