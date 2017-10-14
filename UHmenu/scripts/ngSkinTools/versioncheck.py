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

from ngSkinTools import version
from ngSkinTools.utils import Utils
from ngSkinTools.ui.updateCheckWindow import ResultsDisplay, ResultsData
import datetime

class VersionChecker:
    
    def __init__(self):
        self.watermark=None
        self.uniqueClientId=None
        
        self.transport = None
        
        self.links = []
        self.resultsDisplay = ResultsDisplay()
        
    def downloadInfo(self,successCallback,failureCallback):
        '''
        executes version info download in separate thread, 
        then runs callback in main thread when download completes or fails
        '''

        import maya.utils
        import urllib2
        import urllib
        import json
        import threading

        resource = "ngSkinTools-v1-"+Utils.getOs()+"-maya"+str(Utils.getMayaVersion())
        endpoint = "http://versiondb.ngskintools.com/releases/"+resource+"?"+urllib.urlencode({
                'currentVersion': version.pluginVersion(),
                'buildWatermark': version.buildWatermark(),
                'uniqueClientId': version.uniqueClientId(),
        })
        def runnerFunc():
            try:
                result = urllib2.urlopen(endpoint).read()
                maya.utils.executeDeferred(successCallback, json.loads(result))
            except Exception, err:
                maya.utils.executeDeferred(failureCallback, str(err))
                
        threading.Thread(target=runnerFunc).start()
        
        
    def execute(self,silent=True):
        '''
        silent: don't show anything to the user unless there's update really available. no progress and 
        no notification about errors.
        '''
        
        
        if not silent:
            self.resultsDisplay.showInfoWindow('Please wait...','Downloading update information')

        def successHandler(response):
            try:
                updateInfo = ResultsData()
                updateInfo.updateDate = datetime.datetime.strptime(response['dateReleased'],"%Y-%m-%d")
                updateInfo.versionAvailable = response['latestVersion']
                updateInfo.updateAvailable = version.compareSemVer(version.pluginVersion(), updateInfo.versionAvailable)>0
                
                if not silent or updateInfo.updateAvailable:
                    self.resultsDisplay.showResultsWindow(updateInfo)
            except Exception,err:
                if not silent:
                    self.resultsDisplay.showInfoWindow('Error',"Version check failed ({0})".format(str(err)))
                
        def errorHandler(errorMessage):
            if not silent:
                self.resultsDisplay.showInfoWindow('Error',"Version check failed ({0})".format(errorMessage))
        self.downloadInfo(successHandler,errorHandler)
            
checker = VersionChecker()        
        
