import sys
import socket
import select
import struct
import errno

import platform
import optparse
import datetime
import getpass

import os
import maya.cmds as cmds
import maya.utils
import maya.mel
from time import gmtime, strftime

TrFileRevisionDate = "$DateTime: 2009/04/23 17:17:43 $"

tractorMayaWindow = ''
tractorEngineNameGrp = '' 
tractorEnginePortGrp = '' 
doCleanUpGrp = ''
rendererMenuGrp = ''
localRemoteGrp = ''
framesPerServerGrp = '' 
jobPriorityGrp = '' 
jobServerAttributesGrp = '' 
jobCmdTagsGrp = '' 
envkeyGrp = '' 
rendererArgsGrp = '' 
jobDoneCmdGrp = '' 
jobErrorCmdGrp = '' 
crewsGrp = '' 
extraJobOptionsGrp = ''
doJobPauseGrp = ''
otherRendererGrp = ''

tractorEngineName = '147.197.217.242'
tractorEnginePort = '80'
renderer = ''
distribMode = 'Local'
framesPerServer = 1

jobPriority = 1
jobServerAttrs = ''
jobCmdTags = ''
envKey = '';
rendererArgs = ''
jobDoneCmd = ''
jobErrorCmd = ''
crews = ''
extraJobOptions = ''
scriptCleanUp = 0
tmpSceneCleanUp = 0
doJobPause = 0
sceneName = ''
# added for test frames
startFrame = 0
stopFrame = 0

## ------------------------------------------------------------- ##
class TrHttpRPC(object):

    def __init__(self, host, port=80, logger=None, apphdrs={}):
        self.host = host
        self.port = port
        self.logger = logger
        self.appheaders = apphdrs

        if port <= 0:
            h,c,p = host.partition(':')
            if p:
                self.host = h
                self.port = int(p)

        # embrace and extend errno values
        if not hasattr(errno, "WSAECONNRESET"):
            errno.WSAECONNRESET = 10054
        if not hasattr(errno, "WSAECONNREFUSED"):
            errno.WSAECONNREFUSED = 10061


    def Transaction (self, tractorverb, formdata, parseCtxName=None,
                        xheaders={}, analyzer=None):
        """
        Make an HTTP request and retrieve the reply from the server.
        An implementation using a few high-level methods from the
        urllib2 module is also possible, however it is many times
        slower than this implementation, and pulls in modules that
        are not always available (e.g. when running in maya's python).
        """
        outdata = None
        errcode = 0
        s = None

        try:
            # like:  http://tractor-engine:80/Tractor/task?q=nextcmd&...
            t = "/Tractor/" + tractorverb

            # we use POST when making changes to the destination (REST)
            req = "POST " + t + " HTTP/1.0\r\n"
            for h in self.appheaders:
                req += h + ": " + self.appheaders[h] + "\r\n"
            for h in xheaders:
                req += h + ": " + xheaders[h] + "\r\n"

            if formdata:
                t = formdata.strip()
                req += "Content-Type: application/x-www-form-urlencoded\r\n"
                req += "Content-Length: %d\r\n" % len(t)
                req += "\r\n"  # end of http headers
                req += t
            else:
                req += "\r\n"  # end of http headers

            # error checking?  why be a pessimist?
            # that's why we have exceptions

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect( (self.host, self.port) )
            s.sendall(req)

            mustTimeWait = False

            t = ""  # build up the reply text
            while 1:
                r,w,x = select.select([s], [], [], 30.0)
                if r:
                    if 0 == len(r):
                        self.Debug("time-out waiting for http reply")
                        mustTimeWait = True
                        break
                    else:
                        r = s.recv(4096)
                if not r:
                    break
                else:
                    t += r

            # Attempt to reduce descriptors held in TIME_WAIT on the
            # engine by dismantling this request socket immediately
            # if we've received an answer.  Usually the close() call
            # returns immediately (no lingering close), but the socket
            # persists in TIME_WAIT in the background for some seconds.
            # Instead, we force it to dismantle early by turning ON
            # linger-on-close() but setting the timeout to zero seconds.
            #
            if not mustTimeWait:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                                 struct.pack('ii', 1, 0))
            s.close()

            if t and len(t):
                n = t.find("\r\n\r\n")
                h = t[0:n] # headers

                n += 4
                outdata = t[n:].strip()  # body, or error msg, no CRLF

                n = h.find(' ') + 1
                e = h.find(' ', n)
                errcode = int( h[n:e] )

                if errcode == 200:
                    errcode = 0

                    # expecting a json dict?  parse it
                    if outdata and parseCtxName:
                        try:
                            outdata = self.parseJSON(outdata)

                        except Exception:
                            errcode = -1
                            self.Debug("json parse:\n" + outdata)
                            outdata = "parse %s: %s" % \
                                        (parseCtxName, self.Xmsg())

                if analyzer:
                    analyzer( h )

            else:
                outdata = "no data received"
                errcode = -1

        except Exception, e:
            if e[0] in (errno.ECONNREFUSED, errno.WSAECONNREFUSED):
                outdata = "connection refused"
                errcode = e[0]
            elif e[0] in (errno.ECONNRESET, errno.WSAECONNRESET):
                outdata = "connection dropped"
                errcode = e[0]
            else:
                errcode = -1
                outdata = "http transaction: " + self.Xmsg()

        return (errcode, outdata)


    def parseJSON(self, json):
        #
        # A simpleminded "converter" from inbound json to python dicts.
        #
        # Expect a JSON object, which of course also happens to be the
        # same format as a python dictionary:
        #  { "user": "yoda", "jid": 123, ..., "cmdline": "prman ..." }
        #
        # NOTE: python eval() will *fail* on strings ending in CRLF (\r\n),
        # they must be stripped!  (by our caller, if necessary)
        #
        # We add local variables to stand in for the three JSON
        # "native" types that aren't available in python, however
        # these types aren't expected to appear in tractor data.
        #
        null = None
        true = True
        false = False

        return eval( json )


    def Debug (self, txt):
        if self.logger:
            self.logger.debug(txt)

    def Xmsg (self):
        if self.logger and hasattr(self.logger, 'Xcpt'):
            return self.logger.Xcpt()
        else:
            errclass, excobj = sys.exc_info()[:2]
            return "%s - %s" % (errclass.__name__, str(excobj))
## ------------------------------------------------------------- ##
sys.path.insert(1, os.path.join(sys.path[0], "blade-modules"))
## --------------------------------------------------- ##
def Spool (argv):
    '''
    tractor-spool - main - examine options, connect to engine, transfer job
    '''
    appName =        "tractor-spool"
    appVersion =     "TRACTOR_VERSION"
    appProductDate = "TRACTOR_BUILD_DATE"
    appDir = os.path.dirname( os.path.realpath( __file__ ) )

    defaultMtd  = "tractor-engine:80"

    spoolhost = socket.gethostname().split('.')[0] # options can override
    user = getpass.getuser()

    # ------ # 

    if not appProductDate[0].isdigit():
        appProductDate = " ".join(TrFileRevisionDate.split()[1:3])
        appVersion = "dev"

    appBuild = "%s %s (%s)" % (appName, appVersion, appProductDate)

    optparser = optparse.OptionParser(version=appBuild,
                                      usage="%prog [options] JOBFILE...\n"
                                        "%prog [options] --rib RIBFILE...\n"
                                        "%prog [options] --jdelete JOB_ID" )

    optparser.add_option("--priority", dest="priority",
            type="float", default=1.0,
            help="priority of the new job")

    optparser.add_option("--engine", dest="mtdhost",
            type="string", default=defaultMtd,
            help="hostname[:port] of the master tractor daemon, "
                 "default is '"+defaultMtd+"' - usually a DNS alias")

    optparser.add_option("--hname", dest="hname",
            type="string", default=spoolhost,
            help="the origin hostname for this job, used to find the "
                 "'home blade' that will run 'local' Cmds; default is "
                 "the locally-derived hostname")

    optparser.add_option("--user", dest="uname",
            type="string", default=user,
            help="alternate job owner, default is user spooling the job")

    optparser.add_option("--jobcwd", dest="jobcwd",
            type="string", default=trAbsPath(os.getcwd()),
            help="blades will attempt to chdir to the specified directory "
                 "when launching commands from this job; default is simply "
                 "the cwd at time when tractor-spool is run")

    optparser.set_defaults(ribspool=None)
    optparser.add_option("--rib", "-r", dest="ribspool",
            action="store_const", const="rcmd",
            help="treat the flename arguments as RIB files to be rendered; "
                 "a single task tractor job is automatically created to handle "
                 "the rendering (using prman on remote blade)")

    optparser.add_option("--ribs", dest="ribspool",
            action="store_const", const="rcmds",
            help="treat the flename arguments as RIB files to be rendered; "
                 "a  multi-task tractor job is automatically created to handle "
                 "the rendering (using prman on remote blade)")

    optparser.add_option("--nrm", dest="ribspool",
            action="store_const", const="nrm",
            help="a variant of --rib, above, that causes the generated "
                 "tractor job to use netrender on the local blade rather "
                 "than direct rendering with prman on a blade; used when "
                 "the named RIBfile is not accessible from the remote "
                 "blades directly")

    optparser.add_option("--skey", dest="ribservice",
            type="string", default="pixarRender",
            help="used with --rib to change the service key used to "
                 "select matching blades, default: pixarRender")

    #optparser.add_option("--jdelete", dest="jdel_id",
    #        type="string", default=None,
    #        help="delete the requested job from the queue")

    optparser.set_defaults(loglevel=1)
    optparser.add_option("-v",
            action="store_const", const=2, dest="loglevel",
            help="verbose status")
    optparser.add_option("-q",
            action="store_const", const=0, dest="loglevel",
            help="quiet, no status")

    optparser.add_option("--paused", dest="paused",
            action="store_true", default=False,
            help="submit job in paused mode")

    rc = 0
    xcpt = None

    try:
        options, jobfiles = optparser.parse_args( argv )

        #if options.jdel_id:
        #    if len(jobfiles) > 0:
        #        optparser.error("too many arguments for jdelete")
        #        return 1
        #    else:
        #        return jobDelete(options)

        if 0 == len(jobfiles):
            optparser.error("no job script specified")
            return 1

        if options.loglevel > 1:
            print "%s\nCopyright (c) 2007-%d Pixar. All rights reserved." \
                    % (appBuild, datetime.datetime.now().year)

        if options.mtdhost != defaultMtd:
            h,n,p = options.mtdhost.partition(":")
            if not p:
                options.mtdhost = h + ':80'

        # paused starting is represented by a negative priority
        # decremented by one. This allows a zero priority to pause
        if options.paused:
            try:
                options.priority = str( -float( options.priority ) -1 )
            except Exception:
                options.priority = "-2"

        # apply --rib handler by default if all files end in ".rib"
        if not options.ribspool and \
            reduce(lambda x, y: x and y,
                    [f.endswith('.rib') for f in jobfiles]):
            options.ribspool = 'rcmds'

        #
        # now spool new jobs
        #
        if options.ribspool:
            rc = createRibRenderJob(jobfiles, options)
            if rc == 0:
                rc, xcpt = jobSpool(jobfiles[0], options)
        else:
            for filename in jobfiles:
                rc, xcpt = jobSpool(filename, options)
                if rc:
                    break

    except KeyboardInterrupt:
        xcpt = "received keyboard interrupt"

    except SystemExit, e:
        rc = e

    except:
        errclass, excobj = sys.exc_info()[:2]
        xcpt = "job spool: %s - %s" % (errclass.__name__, str(excobj))
        rc = 1

    if xcpt:
        print >>sys.stderr,xcpt

    return rc
## ------------------------------------------------------------- ##
#Creates absolute path 
def trAbsPath (path):
    '''
    Generate a canonical path for tractor.  This is an absolute path
    with backslashes flipped forward.  Backslashes have been known to
    cause problems as they flow through system, especially in the 
    Safari javascript interpreter.
    '''
    return os.path.abspath( path ).replace('\\', '/')
## ------------------------------------------------------------- ##
def jobSpool (jobfile, options):
    '''
    Transfer the given job (alfred script) to the central job queue.
    '''

    if options.ribspool:
        alfdata = options.ribjobtxt
    else:
        # usual case, read the alfred jobfile
        f = open(jobfile, "rb")
        alfdata = f.read()
        f.close()

    hdrs = {
        'Content-Type':         'application/tractor-spool',
        'X-Tractor-User':       options.uname,
        'X-Tractor-Spoolhost':  options.hname,
        'X-Tractor-Dir':        options.jobcwd,
        'X-Tractor-Jobfile':    trAbsPath(jobfile),
        'X-Tractor-Priority':   str(options.priority)
    }

    return TrHttpRPC(options.mtdhost,0).Transaction("spool",alfdata,None,hdrs)
## ------------------------------------------------------------- ##
def createRibTask (ribfiles, options):
    single = True if  type(ribfiles) == type ("") else False 

    jtxt = "  Task -title {"
    if single:
        jtxt += ribfiles
    else:
        jtxt += " ".join( [os.path.basename(f) for f in ribfiles] )
    jtxt += "} -cmds {\n"

    if 'nrm' == options.ribspool:
        jtxt += "    Cmd {netrender %H -f -Progress"
    else:
        jtxt += "    RemoteCmd {prman -Progress"

    if single:
        jtxt += ' "' + ribfiles + '"'
    else:
        jtxt += ' "' + '" "'.join(ribfiles) + '"'
    jtxt += '} -service {' + options.ribservice + '} -tags {prman}'
    jtxt += "\n  }\n"  # end of cmds
    return jtxt
## ------------------------------------------------------------- ##
def createRibRenderJob (ribfiles, options):
    rc = 0
    jtxt = "##AlfredToDo 3.0\n"
    jtxt += "Job -title {" + os.path.basename(ribfiles[0])
    if len(ribfiles) > 1:
        jtxt += " ..."
    jtxt += "} -subtasks {\n"
    if options.ribspool=="rcmds":
        for f in ribfiles:
            jtxt += createRibTask(f, options)
    else:
        jtxt += createRibTask(ribfiles, options)

    jtxt += "}\n"    # end of job

    options.ribjobtxt = jtxt

    return rc
## ------------------------------------------------------------- ##
def getSceneFilename():
    result = maya.mel.eval('file -q -sceneName')
    if result == '':
        dir = maya.mel.eval('workspace -q -rootDirectory')
        dir += maya.mel.eval('workspace -q -fre "scene"')
        result = dir + '/untitled.ma'
    return result
## ------------------------------------------------------------- ##
def stashScene():

    global sceneName

    # generate an id - a combinitaion of maya's pid and random number
    scenefile = getSceneFilename()
    sceneName = os.path.splitext( os.path.basename(scenefile))[0]

    id = maya.mel.eval('getpid')
    rn = maya.mel.eval('rand 1000')
    id += maya.mel.eval('floor ' + str(rn))
    id = int(id)
    scenedir = maya.mel.eval('workspace -q -fre renderScenes')
    if  scenedir == None:
        scenedir = maya.mel.eval('workspace -q -rte renderScenes')
    
    rootDir = maya.mel.eval('workspace -q -rootDirectory')
    scenedir = rootDir + '/' + scenedir
    maya.mel.eval('sysFile -makeDir "' + scenedir + '"')
    # insert an underscore so maya doesn't automatically delete the file on us
    tmpFileName = scenedir + '/' + '_' + sceneName + "_" + str(id)
    filetype = maya.mel.eval('file -q -type')
    tmpFileName = maya.mel.eval('file -type "' + filetype[0] + '" -ea "' + tmpFileName + '"')

    return tmpFileName;
## ------------------------------------------------------------- ##
def createJobScript():
    global renderer
    global distribMode
    global framesPerServer
    global jobPriority
    global jobServerAttrs
    global jobCmdTags
    global envKey
    global rendererArgs
    global jobDoneCmd
    global jobErrorCmd
    global crews
    global extraJobOptions
    global scriptCleanUp
    global tmpSceneCleanUp
    global sceneName
    # added start and stop frames for testRenders
    global startFrame
    global stopFrame

    # fixed variables UH
    cmdType = 'RemoteCmd'

    # add testframe option here
    print(type(startFrame))
    print(type(stopFrame))
    #REMOVED And moved to UHRFTOOLS
    #startFrame = int(cmds.getAttr('defaultRenderGlobals.startFrame') )
    #stopFrame = int(cmds.getAttr('defaultRenderGlobals.endFrame') )
    byFrame = int(cmds.getAttr('defaultRenderGlobals.byFrame'))
    #animation = int(cmds.getAttr('defaultRenderGlobals.animation'))
    #if animation == 0:
    #    stopFrame = startFrame

    print(str(startFrame) + "  :  " + str(stopFrame))
    
    serviceKey = '' + jobServerAttrs
    sceneFile = stashScene()
    currentTime = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime())
    projDir = maya.mel.eval('workspace -q -rootDirectory')
    id = maya.mel.eval('getpid')
    rn = maya.mel.eval('rand 1000')
    id += maya.mel.eval('floor ' + str(rn))
    id = int(id)
    fnm = ''
    fnm = projDir + '/tmpMaya_' + str(id) + '.alf'
    print('TS: Renderer: '+ renderer)
    renderCmd = 'Render -r ' + renderer
    options = ' -im ' + sceneName + ' -proj %D(' + projDir  + ') ' + rendererArgs

    jobFile = open(fnm, 'w')

    cmdtail = '-service { RfMRender } -envkey { ' #maya' +  cmds.about(p=True).split(' ')[1]
    cmdtail = cmdtail + ' ' + envKey + '}'

    jobFile.write('##AlfredToDo 3.0\n')
    jobFile.write('##\n')
    jobFile.write('## Generated: ' + str(currentTime) +'\n')
    jobFile.write('## Maya file: ' + os.path.basename(sceneFile) + '\n')
    jobFile.write('##\n\n')

    title = getSceneFilename()
    title = os.path.basename(title)

    jobFile.write('Job -title {' + title + '}')
    jobFile.write(' -dirmaps { { {R:/} {/mnt/RenderStore/} NFS}}')
    jobFile.write(' -pbias ' + str(jobPriority) + '')
    jobFile.write(' -tags { Render ' + jobCmdTags + '}')
    jobFile.write(' -service {' + jobServerAttrs + '}')
    jobFile.write(' -crews {' + crews + '}')
    jobFile.write(' -envkey {' + envKey + '}')
    jobFile.write(' -whendone {' + jobDoneCmd + '}')
    jobFile.write(' -whenerror {' + jobErrorCmd + '}')
    jobFile.write(' ' + extraJobOptions + ' ')
    jobFile.write('-subtasks {\n')

    jobFile.write('Task -title {Job} -serialsubtasks 0 -subtasks {\n')


    for frame in range(startFrame, stopFrame+1, framesPerServer):

        e = frame + framesPerServer - byFrame
        title = ''

        if byFrame == 1:
            title = 'Frame ' + str(frame)
        else:
            title = 'Frames ' + str(frame) + ' to ' + str(e) + ' by ' + str(byFrame)
            

        jobFile.write('   Task -title {' + title + '} -cmds {\n')
        cmd = ''
        e = frame + framesPerServer - byFrame
        if e > stopFrame:
            e = stopFrame
		
        cmd += renderCmd + ' -s ' + str(frame) + ' -e ' + str(e) + ' -b ' + str(byFrame)
        cmd += options
        cmd += ' %D(' + sceneFile + ') '
        jobFile.write( '        ' + cmdType + ' {' + cmd + '} ' + cmdtail + '\n')
        jobFile.write('   }\n')

    jobFile.write('} -cleanup {\n')
    if scriptCleanUp:
        jobFile.write('     File delete "' + fnm + '"\n')
    if tmpSceneCleanUp:
        jobFile.write('     File delete "' + sceneFile + '"\n')
    jobFile.write('}\n')
    jobFile.write('}\n')
    jobFile.close()
    return fnm

def spoolJob(args):
    global tractorEngineName
    global tractorEnginePort
    global doJobPause
    tractorEngine = '' + tractorEngineName + ':' + str(tractorEnginePort)
    jobScript = createJobScript()

    #prioritySetting = 100.0
    prioritySetting = args
    print args
    #empty arguements
    args = []

    #if (int(priority) > 0) or (int(priority) < 100):
    args.append('--priority=' + str(prioritySetting)  )

    # set the engine
    args.append('--engine=' + tractorEngine)

    if doJobPause:
        args.append('--paused')
    
    args.append(jobScript)

    print(args)    

    Spool(args)
