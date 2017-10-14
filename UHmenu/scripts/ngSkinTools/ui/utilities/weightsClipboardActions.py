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

from ngSkinTools.ui.actions import BaseLayerAction
from ngSkinTools.utils import Utils
from ngSkinTools.ui.layerDataModel import LayerDataModel

class CopyWeights(BaseLayerAction):
    @Utils.visualErrorHandling
    @Utils.undoable
    @Utils.preserveSelection
    def execute(self):
        LayerDataModel.getInstance().clipboard.withCurrentLayerAndInfluence().copy()


class CutWeights(BaseLayerAction):
    
    @Utils.visualErrorHandling
    @Utils.undoable
    @Utils.preserveSelection
    def execute(self):
        LayerDataModel.getInstance().clipboard.withCurrentLayerAndInfluence().cut()

class PasteWeightsAdd(BaseLayerAction):
    
    @Utils.visualErrorHandling
    @Utils.undoable
    @Utils.preserveSelection
    def execute(self):
        LayerDataModel.getInstance().clipboard.withCurrentLayerAndInfluence().pasteAdd()

class PasteWeightsSubstract(BaseLayerAction):
    
    @Utils.visualErrorHandling
    @Utils.undoable
    @Utils.preserveSelection
    def execute(self):
        LayerDataModel.getInstance().clipboard.withCurrentLayerAndInfluence().pasteSubstract()

class PasteWeightsReplace(BaseLayerAction):
    
    @Utils.visualErrorHandling
    @Utils.undoable
    @Utils.preserveSelection
    def execute(self):
        LayerDataModel.getInstance().clipboard.withCurrentLayerAndInfluence().pasteReplace()
