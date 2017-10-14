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

'''
    information about toolkit version
'''
from ngSkinTools.ui.options import Options, PersistentValueModel
from maya import cmds


RELEASE_NAME = "ngSkinTools %(version)s"
COPYRIGHT = "Copyright 2009-2016 Viktoras Makauskas"
PRODUCT_URL = "http://www.ngskintools.com"

   
def getReleaseName():
    '''
    returns release name with version information
    '''
    return RELEASE_NAME % {'version':pluginVersion()}

def pluginVersion():
    '''
    Unique version of plugin, e.g. "1.0beta.680". Also represents 
    required version of mll plugin. Automatically set at build time
    '''
    pluginVersion_doNotEdit = "1.1.0"  
    return pluginVersion_doNotEdit;  

def buildWatermark():
    '''
    returns a unique ID of this build. 
    will be set by a build system and stored in the plugin binary
    '''
    
    return cmds.ngSkinToolsLicense(q=True,watermark=True)

def uniqueClientId():
    '''
    returns a unique ID for this installation. randomly generated at first run.
    '''
    model = PersistentValueModel(Options.VAR_OPTION_PREFIX+"updateCheckUniqueClientId", None)
    if model.get() is None:
        model.set(generateUniqueClientId())
    return model.get()


# returns random hexadecimal 40-long string    
def generateUniqueClientId():
    import random
    result = ""
    for i in range(10):
        result += "%0.4x" % random.randrange(0xFFFF)
        
    return result
    


class SemanticVersion:
    def __init__(self,stringVersion):
        self.major = 0
        self.minor = 0
        self.patch = 0
        self.preRelease = None
        self.parse(stringVersion)
        
    def parse(self,stringVersion):
        import re
        pattern = re.compile(r"(\d+)(\.(\d+)((\.)(\d+))?)?(-([a-zA-Z0-9]+))?")
        
        def toInt(s):
            try:
                return int(s)
            except:
                return 0
             
        
        result = pattern.match(stringVersion)
        if result is None:
            raise Exception("Invalid version string: '{0}'".format(stringVersion))
            
        self.major = toInt(result.group(1))
        self.minor = toInt(result.group(3))
        self.patch = toInt(result.group(6))
        self.preRelease = result.group(8)

def compareSemVer(currentVersion,candidateVersion):
    '''
    returns negative if current version is bigger, 0 if versions are equal and positive if candidateVersion is higher.
    
    e.g.
    
    1.0, 1.1 -> 1
    1.0, 1.0-beta -> -1
    
    '''
    currentVersion = SemanticVersion(currentVersion)
    candidateVersion = SemanticVersion(candidateVersion)
    
    if currentVersion.major!=candidateVersion.major:
        return candidateVersion.major-currentVersion.major
    if currentVersion.minor!=candidateVersion.minor:
        return candidateVersion.minor-currentVersion.minor
    if currentVersion.patch!=candidateVersion.patch:
        return candidateVersion.patch-currentVersion.patch
    if currentVersion.preRelease!=candidateVersion.preRelease:
        if currentVersion.preRelease is None:
            return -1
        if candidateVersion.preRelease is None:
            return 1
        return 1 if candidateVersion.preRelease>currentVersion.preRelease else -1
    
    
    return 0


    