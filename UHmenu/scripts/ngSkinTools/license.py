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
from ngSkinTools.ui.options import PersistentValueModel
import os
from ngSkinTools.ui.events import LayerEvents
from ngSkinTools.utils import Utils
from os.path import isdir

savedLicensePath = PersistentValueModel("ngSkinToolsOption_licensePath")

def validateLicense(licensePath=None):
    '''
    validates RLM license, looking for it on the given path
    '''
    
    if licensePath is None:
        licensePath=getLicensePath()
    LayerEvents.licenseStatusChanged.emitDeferred()
    return cmds.ngSkinToolsLicense(validateLicense=True, licensePath=licensePath)

def licenseStatus():
    '''
    returns RLM code for license status. 0 means activated, negative values map to errors
    '''
    
    #repeat two times
    for i in range(2):
        result = cmds.ngSkinToolsLicense(licenseStatus=True)
        if result is None:
            validateLicense()
    return result

def getHostId():
    '''
    executes RLM host id and returns the result
    '''
    import subprocess
    import os.path as path
    toolsPath = path.abspath(path.join(path.dirname(__file__),"tools"))
    
    operatingSystem = Utils.getOs()

    isLinux = operatingSystem=="linux"
    isOsx = operatingSystem=='mac'
    useTemporaryExecutable = isLinux or isOsx
    
    rlmHostId = "rlmhostid.exe"
    if isLinux:
        rlmHostId = "rlmhostid-linux"
    if isOsx:
        rlmHostId = "rlmhostid-osx"
    
    executeCommand = [path.join(toolsPath,rlmHostId)]
    executeCommand.append("-q")
    
    if useTemporaryExecutable:
        # some instalation methods (extracting a zip) might not set the executable flags,
        # and we are probably better of just making a temporary executable with proper flags
        # ...and we've just discovered that the executable needs to be called exactly "rlmhostid"
        import tempfile, shutil, os
        temporaryDirectory = tempfile.mkdtemp()
        temporaryExecutable = os.path.join(temporaryDirectory,"rlmhostid")
        
        
        shutil.copy2(executeCommand[0], temporaryExecutable)
        executeCommand[0] = temporaryExecutable
        os.chmod(executeCommand[0], 0777)
    
    
    
    try:
        result = subprocess.check_output(executeCommand).strip()
    finally:
        if useTemporaryExecutable:
            os.unlink(temporaryExecutable)
            os.rmdir(temporaryDirectory)
        
    # rlmhostid returns zero even in case of errors; rely on the output to detect execution errors
    if "rlmhostid" in result: # probably some kind of errors showing tool usage
        raise Exception("rlmhostid failed to execute.")
    return result

def getLicensePath():
    '''
    returns license path, checking configuration in priority:
        Maya's optionVar 'ngSkinToolsOption_licensePath'
        environment variable NGSKINTOOLS_LICENSE_PATH
        environment variable RLM_LICENSE
        Maya's user app dir 
    '''
    def parsePathFromRlmLicense(licensePath):
        '''
        take a value in form of:
            
            license_spec1:license_spec2:license_spec3: .... :license_specN (UNIX)
            license_spec1;license_spec2;license_spec3; .... ;license_specN (Windows)
        
        ...and return first entry that is an existing directory.
        '''
        paths = licensePath.split(os.path.pathsep)
        for p in paths:
            if os.path.isdir(p):
                return p
            
        return None
    
    licensePath = savedLicensePath.get()
    if licensePath is None:
        licensePath = os.getenv("NGSKINTOOLS_LICENSE_PATH", None)
    if licensePath is None:
        licensePath = os.getenv("RLM_LICENSE", None)
        if licensePath is not None:
            licensePath = parsePathFromRlmLicense(licensePath)
             
    if licensePath is None:
        licensePath = cmds.internalVar(userAppDir=True)
        
    licensePath = os.path.normpath(licensePath)
    
    return licensePath
    
def setLicensePath(licensePath):
    savedLicensePath.set(licensePath)
    validateLicense()
    
    
def downloadLicenseFile(licenseKey,hostId=None,fileLocation=None):
    '''
    exchanges licenseKey+hostId for a licenseFile online.
    Operation will fail if license file already exists (won't overwrite)
    '''
    
    # check if the license file already exists
    if fileLocation is None:
        fileLocation = os.path.join(getLicensePath(),"ngskintools.lic")
        
    if os.path.exists(fileLocation):
        raise Exception("License file '{0}' already exists".format(fileLocation))
    
    if hostId is None:
        hostId = getHostId()
         
    # download now
    import urllib2
    import json
    try:
        req = urllib2.Request('http://licensing.ngskintools.com/api/projects/ngskintools/licenses/'+licenseKey)
        resp = urllib2.urlopen(req,json.dumps({"hostId":hostId}))
        result = json.load(resp)
        contents = result['licenseFile']
    except urllib2.HTTPError, err:
        result = json.load(err)
        raise Exception("Failed downloading license file ({0}): {1}".format(err.getcode(),result['message']))
    except Exception, err:
        raise Exception("Failed downloading license file: unknown error ({0})".format(str(err)))     
    
    # save to file
    with open(fileLocation,"w") as f:
        f.write(contents)

    # force license revalidation
    validateLicense()
        
    