#!/usr/bin/python
__author__ = 'dmitry.obukhov'
__all__ = ['TextProcessor', 'Batch']

import subprocess, threading
import os, sys, shutil, signal, platform
import re
import argparse
import stat
from time import time, strftime, ctime, sleep
from datetime import datetime
from datetime import timedelta
import ctypes
import random
import string
import logging, inspect
import tempfile
import zlib
import binascii
import hashlib
import base64
import sys

class TextProcessor(object):
    @staticmethod
    def QuotedString(stringValue):
        return "\"%s\"" % stringValue
    #--- end of method

    @staticmethod
    def TimeStamp(formatStr = '%Y_%m_%d_%H%M%S%f'):
        return datetime.now().strftime(formatStr)
    #--- end of method

    @staticmethod
    def RandomString(length, charset=''):
        if charset=='':
            charset = string.ascii_uppercase + string.digits
        return ''.join(random.choice(charset) for _ in range(length))
    #--- end of method


    @staticmethod
    def GetCommandOutput(command, args=''):
        retVal = []
        outputInOneStr = subprocess.check_output([command, args])
        retVal = re.split('[\r\n]+', outputInOneStr)
        for idx in range(0,len(retVal)):
            retVal[idx] = retVal[idx].rstrip()
        #---
        return retVal
    #--- end of method


    @staticmethod
    def DebugInfo(messageStr):
        frame = sys._getframe(1)
        funName = frame.f_code.co_name
        line_number = frame.f_lineno
        filename = frame.f_code.co_filename
        return ( "%s : %s (%s:%04d) : %s" % (self.TimeString('%H.%M.%S.%f'), funName,filename,line_number,messageStr))
    #--- end of method


    @staticmethod
    def Read(fileNameStr, cleanUp=True):
        retVal = []
        try:
            f = open(fileNameStr)
        except IOError:
            return None
        else:
            retVal = f.readlines()
            f.close()
            if cleanUp == True:
                retVal = TextProcessor.RStrip(retVal)
                retVal = TextProcessor.RemoveEmptyLines(retVal)
        return retVal
    #---------------------



    @staticmethod
    def UnifyLength(s, maxLen=-1, minLen=-1, spacer=' '):
        retStr = s
        curLen = len(retStr)
        # if maxLen defined, keep the left portion
        if maxLen>0 and (curLen > maxLen):
            retStr = retStr[:maxLen]

        # if min len is defined, space trail string
        curLen = len(retStr)
        if minLen>0 and (curLen < minLen):
            retStr = retStr + spacer*(minLen-curLen)

        return retStr
    #--

    @staticmethod
    def Fold(longStr, width):
        retVal = []
        tmp = longStr
        while len(tmp)>0:
            cur = ''
            if len(tmp)>width:
                cur = tmp[0:width]
                tmp = tmp[width:]
            else:
                cur = tmp
                tmp = ''
            #---
            retVal.append(cur)
        #---
        return retVal
    #---

    @staticmethod
    def Format(t, indent="", header="", footer="", maxLen=-1, minLen=-1, lineNumberingStart=-1):
        retTxt = []
        lineNumberStr = ""
        lineNumberPlaceholder = ''
        if lineNumberingStart>-1:
            lineNumber = lineNumberingStart
            lineNumberWidth = len("%d" % len(t))
            lineNumberTemplate = "%%%dd: " % lineNumberWidth
            lineNumberPlaceholder = ' '*(lineNumberWidth+2)

        # if the header is defined, add header after indent
        if (len(header))>0:
            retTxt.append("%s%s%s" % (indent, lineNumberPlaceholder, header))

        for i in range(0,len(t)):
            # prepare line numbering
            if lineNumberingStart>-1:
                lineNumberStr = lineNumberTemplate % lineNumber
                lineNumber += 1
            # prepare line in format [indent][lineNumber][actualString]
            curLine = "%s%s%s" % (indent,lineNumberStr,t[i])
            curLine = TextProcessor.UnifyLength(curLine,maxLen,minLen)
            # add to the output
            retTxt.append(curLine)
        #----------------------------- end for

        if (len(footer))>0:
            retTxt.append("%s%s%s" % (indent, lineNumberPlaceholder, footer))

        return retTxt
    #---------------------

    @staticmethod
    def Print(t, indent="",header="",footer="",maxLen=-1,minLen=-1,lineNumberingStart=-1):
        if len(t)>0:
            tmp = TextProcessor.Format(t,indent,header,footer,maxLen,minLen,lineNumberingStart)
            for i in range(0,len(tmp)):
                print (tmp[i])
            #--
        #--
    #---------------------


    @staticmethod
    def Save(theList,fName):
        fileToSave = open(fName, 'w')
        for item in theList:
            fileToSave.write("%s\n" % item)
        #--
        fileToSave.flush()
        fileToSave.close()
    #---------------------

    @staticmethod
    def Append(theList,fName):
        fileToSave = open(fName, 'a')
        for item in theList:
            fileToSave.write("%s\n" % item)
        fileToSave.flush()
        fileToSave.close()
    #---------------------



    @staticmethod
    def Replace(t,pattern,replacement):
        retVal = []
        for i in range(0,len(t)):
            cur = t[i]
            while re.match(pattern,cur):
                cur = re.sub(pattern, replacement, cur)
            retVal.append(cur)
        return retVal
    #---------------------

    @staticmethod
    def EachLine(txt, functionStr):
        retVal = []
        for i in range(0,len(txt)):
            x = txt[i]
            y = eval(functionStr)
            retVal.append(y)
        return retVal
    #--

    @staticmethod
    def RStrip(txt):
        retVal = []
        for i in range(0,len(txt)):
            retVal.append(txt[i].rstrip())
        return retVal
    #---------------------

    @staticmethod
    def RemoveEmptyLines(txt):
        retVal = []
        for i in range(0,len(txt)):
            if len(txt[i])>0:
                retVal.append(txt[i])
        return retVal
    #---------------------

    @staticmethod
    def CommandOutput(rawOutput):
        txt = re.split('[\r\n]*', rawOutput)
        retVal = []
        for i in range(0,len(txt)):
            if len(txt[i])>0:
                retVal.append(txt[i].rstrip())
        return retVal
    #---------------------


    @staticmethod
    def RemoveDuplicates(txt):
        output = []
        for x in txt:
            if x not in output:
                output.append(x)
            #--
        #--
        return output
    #---------------------


    @staticmethod
    def Add(txt, something, delimiter='[\n|\r]+'):
        if type( something ) == str :
            tmp = re.split(delimiter, something)
            txt.extend(tmp)
        elif type( something ) == list :
            txt.extend(something)
        return txt
    #---------------------

    @staticmethod
    def Dedent(txt, offsetPos=0):
        output = []
        for x in txt:
            output.append(x[offsetPos:])
        #--
        return output
    #---------------------

    @staticmethod
    def MaxLen(txt):
        maxLen = len(txt[0])
        for x in txt:
            if len(x)>maxLen:
                maxLen = len(x)
        return maxLen
    #---------------------

    @staticmethod
    def MinLen(txt):
        minLen = len(txt[0])
        for x in txt:
            if len(x)<minLen:
                minLen = len(x)
        return minLen
    #---------------------


    @staticmethod
    def ToString (txt, delimiter=' '):
        retStr = ""
        maxidx = len(txt)
        for i in range(0,maxidx):
            retStr += txt[i]
            if i<(maxidx-1):
                retStr += delimiter
        return retStr
    #---------------------

    @staticmethod
    def AddRightColumn(txt,trailer=' '):
        output = []
        for x in txt:
            output.append(x + trailer)
        #--
        return output
    #---------------------

    @staticmethod
    def VerticalCut(txt,leftCol=0,rightCol=-1):
        output = []
        for x in txt:
            if len(x)<leftCol:
                output.append('')
            elif len(x)<rightCol:
                output.append(x[leftCol:])
            else:
                output.append(x[leftCol:rightCol])
        #--
        return output
    #---------------------

    @staticmethod
    def Filter(txt, pattern):
        filtered = []
        for i in range(0,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                filtered.append(txt[i])
            #--
        #--
        return filtered
    #---------------------

    @staticmethod
    def FilterNot(txt, pattern):
        filtered = []
        for i in range(0,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)==0:
                filtered.append(txt[i])
            #--
        #--
        return filtered
    #---------------------


    @staticmethod
    def SearchForward(txt, pattern, start=0):
        for i in range(start,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                return i
        return -1
    #---------------------

    @staticmethod
    def SearchBackward(txt, pattern, start=-1):
        if start<0:
            start = len(txt)-1
        for i in range(start,-1,-1):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                return i
        return -1
    #---------------------


    @staticmethod
    def Count(txt,pattern):
        retVal = 0
        for i in range(0,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                retVal += 1    # if pattern found, count in
            #--
        #--
        return retVal
    #---------------------


    @staticmethod
    def Fragment(txt, start, stop):
        filtered = []
        if start<0:
            start = 0
        if stop>len(txt):
            stop = len(txt)

        for i in range(start,stop):
            filtered.append(txt[i])

        return filtered
    #---------------------


    @staticmethod
    def Replace(txt,compiledRegEx,replacement):
        output = []
        for i in range(0,len(txt)):
            (s,x) = compiledRegEx.subn(replacement,txt[i])
            output.append(s)
        return output
    #---------------------

    @staticmethod
    def Insert(txt,position,fragment):
        output = []
        if position<len(txt):
            # before
            for i in range(0,position):
                output.append(txt[i])
            output.extend(fragment)
            for i in range(position,len(txt)):
                output.append(txt[i])
            # after
        else:
            output.extend(fragment)
        #---
        return output
    #---------------------
#-- end of TextProcessor




class Batch(object):
    def __init__(self, debug=False, quiet=True, LogFile=""):
        frame = sys._getframe(1)
        callerScript = frame.f_code.co_filename
        self.debug = debug      # enable debug features and save extended log
        self.quiet = quiet
        self.context = 5        # context size for diffs
        self.system     = platform.system()
        self.sysver     = platform.release()
        self.platform   = sys.platform
        self.dist       = platform.dist()
        self.errcode = 0        # error code of the last command
        self.errmsg = ''        # diagnostic message
        self.log = []           # debug log
        self.text = []
        self.output = []        # copy of print
        self.replay = []        # replay buffer
        self.token = []
        self.LogFile = LogFile
        if len(self.LogFile)>0:
            if self.LogFile == "auto":
                (d,f,e) = self.SplitFileName(callerScript)
                self.LogFile = os.path.normpath(tempfile.gettempdir() + '/' + f + '__' + TextProcessor.TimeStamp() + '.tmp')
            #--
        #---
        self.supressRunOutput = False
        self.lastWrittenFile = ''
        self.lastBackupFile = ''
        self.caller = callerScript
        self.logBaseline = 3
        self.logOffsetStr = '    '
        self.Log('caller=%s' % callerScript)
        self.Log('self=%s' % __file__)
        if self.debug:
            self.Log('==== System information')
            self.Log("platform.system=%s" % self.system)
            self.Log("platform.platform=%s" % platform.platform())
            (x,y) = platform.architecture()
            self.Log("platform.architecture=%s" % x)
            self.Log("platform.python_version=%s" % platform.python_version())
            self.Log("platform.system=%s" % platform.system())
            if 'Linux' == self.system:
                (distName,distVer,distID) = platform.linux_distribution()
                self.Log("Linux.Distro=%s" % distName)
                self.Log("Linux.Version=%s" % distVer)
                self.Log("Linux.DistID=%s" % distID)
            #---
            self.Log('===========================')
        #--
    #---

    def _callStackDepth (self):
        stack = inspect.stack()
        return len(stack)
    #---

    def Log(self, message):
        stack = inspect.stack()
        offset = self.logOffsetStr * (len(stack) - self.logBaseline)
        if self.debug:
            print (offset + message)
        #---
        self.log.append(offset + message)
        if len(self.LogFile)>0:
            with open(self.LogFile, "a") as myLogFile:
                myLogFile.write("%s\n" % (offset + message))
            #---
        #---
        return True
    #---

    def AskToContinue(self, message=''):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if len(message)>0:
            self.Print(message)
        else:
            self.Print("Continue execution?")
        #---
        var = raw_input('')
        if var == 'n':
            self.Log('User terminated')
            self.Exit(0)
        #---
        self.Log('User choose to continue...')
        return True
    #---


    def LogCallerFunction(self):
        self.Log('--> %s' % (sys._getframe(1)).f_code.co_name)
        return True
    #---


    def LogExtend(self, arrayOfStrings):
        stack = inspect.stack()
        offset = self.logOffsetStr * (len(stack) - self.logBaseline)
        for eachStr in arrayOfStrings:
            self.Log(offset + eachStr)
        return True
    #---



    def _HiddenRun (self, commandStr, workingDirectory=''):
        actualDirectory = os.getcwd()
        if (len(workingDirectory)>0):
            os.chdir(workingDirectory)
        #--
        process = subprocess.Popen(commandStr, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        pid = process.pid
        rawOutput, rawError = process.communicate()
        if (len(workingDirectory)>0):
            os.chdir(actualDirectory)
        #--
        return process.returncode
    #---


    def Run (self, commandStr, workingDirectory='', silent=False):
        if len(commandStr)==0:
            return True
        #---
        self.Log('--> %s     %s' % ((sys._getframe(0)).f_code.co_name,commandStr))
        self.cout = []
        self.parsed = []
        self.cerr = []
        self.cret = 0
        self.command = commandStr
        self.starttime = time()

        self.Log("Executing %s at %s" % (self.command, os.getcwd()))
        self.Log("Started %s" % ctime(self.starttime))

        actualDirectory = os.getcwd()
        if (len(workingDirectory)>0):
            self.Log("Changing directory %s --> %s" % (actualDirectory,workingDirectory))
            os.chdir(workingDirectory)
        #--

        self.Log("Continue in %s" % (os.getcwd()))

        self.process = subprocess.Popen(self.command, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        pid = self.process.pid

        self.Log('PID = %d' % pid)

        if self.supressRunOutput or silent:
            (self.rawOutput, self.rawError) = self.process.communicate()
            self.cout = TextProcessor.CommandOutput(self.rawOutput)
            self.cerr = TextProcessor.CommandOutput(self.rawError)
            self.cret = self.process.returncode
        else:
            self.cout = []
            self.rawOutput = ""

            for line in iter(self.process.stdout.readline, ''):
                line = line.rstrip()
                self.Print ("%s" % line)
                self.cout.append(line)
            #---
            self.rawError = self.process.stderr.readlines()
            self.process.stdout.close()
            self.process.stderr.close()
            self.cret = self.process.wait()

            self.rawOutput = "\n".join(self.cout)
        #---

        self.Log('Thread finished with return code %d' % self.cret)

        offset = ' '*4
        spacer = '\n'*2

        if self.cret!=0:
            if len(self.cout)>0 and (self.supressRunOutput or silent):
                TextProcessor.Print(self.cout, ' '*4, '------- stdout output -------------')
            #---
            if len(self.cerr)>0:
                TextProcessor.Print(self.cerr, ' '*4, '------- stderr output -------------')
            #---

        if len(self.cout)>0:
            header = '--- stdout of %s ---' % self.command
            footer = '-'*len(header)
            self.LogExtend(TextProcessor.Format(self.cout, offset, header, footer))
        #--
        if len(self.cerr)>0:
            header = '--- stderr of %s ---' % self.command
            footer = '-'*len(header)
            self.LogExtend(TextProcessor.Format(self.cerr, offset, header, footer))
        #--

        if (len(workingDirectory)>0):
            self.Log("Changing directory %s --> %s" % (workingDirectory,actualDirectory))
            os.chdir(actualDirectory)
            self.Log("Continue in %s" % (os.getcwd()))
        #--


        self.endtime = time()
        self.elapsed = (self.endtime - self.starttime)
        self.Log("Completed %s" % ctime(self.endtime))
        self.Log("Elapsed %f seconds" % self.elapsed)

        return (self.cret == 0)



    def RunAndParse(self, command, workDir, pattern, delimiter=' '):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        self.token = []
        res = self.Run(command,workDir)
        pos = TextProcessor.SearchForward(self.cout,pattern)
        if pos>=0:
            self.Log('Pattern %s found at position %d of stdout' % (pattern,pos))
            self.token = re.split(delimiter,self.cout[pos])
            self.Log('Extracted %d tokens' % (len(self.token)))
        else:
            self.Log('Pattern %s is not found in stdout capture' % (pattern))
            pos = TextProcessor.SearchForward(self.cerr,pattern)
            if pos>=0:
                self.Log('Pattern %s found at position %d in stderr' % (pattern,pos))
                self.token = re.split(delimiter,self.cerr[pos])
                self.Log('Extracted %d tokens' % (len(self.token)))
            else:
                self.Log('Pattern %s is not found in stderr capture' % (pattern))
            #---
        return pos
    #---


    def RunAsUser(self, command, workDir, user=''):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name + " user=%s" % user)
        if len(user)>0:
            # Run it as different user
            command = ("sudo -H -u %s bash -c " % user) + "'" + command + "'"
        #---
        return self.Run(command)
    #---

    def _ReadNewBuffer (self, fileName):
        #self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        retBuf = []
        self.errcode = 0
        if not os.path.isfile(fileName):
            self.errcode = -1
            self.errmsg = "ERROR (%d): Cannot find file %s" % (self.errcode, fileName)
            self.Log(self.errmsg)
            return (False,[])
        #-- end if

        try:
            f = open(fileName)
        except IOError:
            self.errcode = -2
            self.errmsg = "ERROR (%d): Cannot open %s" % (self.errcode, fileName)
            self.Log(self.errmsg)
            return (False,[])
        #---

        try:
            retBuf = f.readlines()
        except:
            self.errcode = -3
            self.errmsg = "ERROR (%d): Cannot read from %s" % (self.errcode, fileName)
            self.Log(self.errmsg)
            return (False,[])
        #---

        f.close()

        retBuf = TextProcessor.RStrip(retBuf)
        #retBuf = TextProcessor.RemoveEmptyLines(retBuf)

        if len(retBuf)<1:
            warning = "Warning: empty file %s" % (fileName)
            self.Log(self.errmsg)
        #-- end if

        return (True,retBuf)
    #---

    def ReadFile (self, fileName):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        (res,self.text) = self._ReadNewBuffer(fileName)
        return res
    #---

    def WriteFile (self, fileName, strArray=None):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        self.errcode = 0
        self.lastWrittenFile = fileName
        self.lastBackupFile = ''
        if os.path.isfile(fileName):
            self.lastBackupFile = fileName + '.bak'
            self.Log('Saving backup %s' % self.lastBackupFile)
            shutil.copy(fileName, self.lastBackupFile)
        #-- end if

        try:
            fileToSave = open(fileName, 'w')
            bufferToSave = []
            if strArray == None:
                bufferToSave = self.text
            else:
                bufferToSave = strArray

            for item in bufferToSave:
                fileToSave.write("%s\n" % item)
            #--
            fileToSave.flush()
            fileToSave.close()
            self.Log("Saved %d lines to %s" % (len(bufferToSave),fileName))
            return True
        except:
            self.errcode = -2
            self.errmsg = "ERROR (%d): Cannot write to %s" % (self.errcode, fileName)
            self.Log(self.errmsg)
            return False
        return False
    #---

    def DiffLastFileWrite (self):
        import tempfile
        #self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if os.path.isfile(self.lastWrittenFile) and os.path.isfile(self.lastBackupFile):

            with tempfile.NamedTemporaryFile(dir=tempfile._get_default_tempdir(), delete=False) as tmpfile:
                diffName = tmpfile.name

            self._HiddenRun('diff %s %s > %s' % (self.lastBackupFile,self.lastWrittenFile,diffName))
            (res,diffBuffer) = self._ReadNewBuffer(diffName)
            if res:
                offset = '    '
                header = '====== DIFF in %s ======' % self.lastWrittenFile
                footer = '='*len(header)
                self.LogExtend(TextProcessor.Format(diffBuffer, offset, header,footer))
            #---
            try:
                os.remove(diffName)
            except:
                self.Log("Warning: Cannot delete temp file in Diff function")
            #---
        #-- end if
        return True
    #---

    def AddLinesToFile(self, fileName, lines):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.ReadFile(fileName):
            return False

        tempName = TextProcessor.RandomString(8) + '.tmp'
        if self.debug:
            shutil.copyfile(fileName,tempName)

        self.text.extend(lines)
        if self.debug:
            self.Log("Added %d lines to %s" % (len(lines),fileName))

        if not self.WriteFile(fileName):
            return False

        if self.debug:
            self.DiffLastFileWrite()

        return True
    #---------------------

    def ReplaceLineInFile(self, fileName, pattern, replacement, useRegEx=False):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.ReadFile(fileName):
            return False

        pos = TextProcessor.SearchForward(self.text,pattern)             # Find the configuration line
        if (pos<0):                                                     # if line not found
            self.errcode = -3
            self.errmsg = "WARNING (%d): Cannot find %s in %s" % (self.errcode,pattern, fileName)
            self.Log(self.errmsg)
            return False

        if useRegEx:
            self.text[pos] = re.sub(self.text[pos],pattern,replacement)
        else:
            self.text[pos] = replacement

        if not self.WriteFile(fileName):
            return False

        if self.debug:
            self.DiffLastFileWrite()

        return True
    #---------------------


    def InsertFragmentAtPos(self, fileName, pos, fragment):
        retVal = False
        myName = (sys._getframe(0)).f_code.co_name
        self.Log('--> %s' % myName)

        while True: # Single exit point function
            if not self.ReadFile(fileName):
                break
            #---
            self.text = TextProcessor.Insert(self.text,pos,fragment)

            if not self.WriteFile(fileName):
                break
            #---

            if self.debug:
                self.DiffLastFileWrite()
            #---

            retVal = True
            break # Single exit point function must break at the end
        #---

        self.Log('<-- %s' % myName)
        return retVal
    #---------------------


    def InsertFragmentAfterLine(self, fileName, pattern, fragment):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.ReadFile(fileName):
            return False

        pos = TextProcessor.SearchForward(self.text,pattern)
        if pos>0:
            return self.InsertFragmentAtPos(fileName, pos+1, fragment)

        return False
    #---------------------


    def DeleteFragmentBetween(self, fileName, startPattern, endPattern, inclusive=False):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.ReadFile(fileName):
            return False

        posStart = TextProcessor.SearchForward(self.text,startPattern)
        if posStart<0:
            self.Log("Cannot find start pattern %s" % startPattern)
            return False

        self.Log("Found start pattern %s at %d" % (startPattern,posStart))
        # start search from the position of start pattern
        posEnd = TextProcessor.SearchForward(self.text,endPattern,posStart)
        if posEnd<0:
            self.Log("Cannot find end pattern %s" % endPattern)
            return False

        newText = []
        startOffset = 1
        endOffset = 0
        if inclusive:
            startOffset = 0
            endOffset = 1

        for idx in range(0, posStart+startOffset):
            newText.append(self.text[idx])

        for idx in range(posEnd-endOffset, len(self.text)):
            newText.append(self.text[idx])

        self.text = newText

        if not self.WriteFile(fileName):
            return False

        if self.debug:
            self.DiffLastFileWrite()

        return True
    #---------------------


    def DeleteLinesFromFile(self, fileName, pattern):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.ReadFile(fileName):
            return False

        self.text = TextProcessor.FilterNot(self.text,pattern)

        self.text = TextProcessor.Insert(self.text,pos,fragment)

        if not self.WriteFile(fileName):
            return False

        if self.debug:
            self.DiffLastFileWrite()

        return True
    #---------------------


    def Print(self, strMessage):
        self.Log(strMessage)
        if not self.quiet:
            print (strMessage)
        return True
    #--


    def Exit(self, retCode=0, message='', log=''):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if message!='':
            self.log.append(strMessage)
            print (message)
        #---
        self.Log('Exit script with code %d' % retCode)
        exit(retCode)
    #--

    def FatalError(self, message):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        retCode = -1
        self.log.append(strMessage)
        sys.stderr.write("%s\n" % message)
        self.Log('Exit script with code %d' % retCode)
        exit(retCode)
    #--


    def Assert(self, condition, retCode, message, log=''):
        if not condition:
            frame = sys._getframe(1)
            funName = frame.f_code.co_name
            line_number = frame.f_lineno
            filename = frame.f_code.co_filename
            message = 'Fatal exit on assert in %s (%s:%d)' % (funName, filename, filename)
            self.FatalError(message)
        return True
    #--


    def FindFiles(self, mask='*.*', workDir=''):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if workDir=='':
            workDir = os.getcwd()
        #---
        self.Log('Mask = %s, Path=%s' % (mask, workDir))
        matches = []
        for root, dirnames, filenames in os.walk(workDir):
          for filename in fnmatch.filter(filenames, mask):
              matches.append(os.path.join(root, filename).replace("\\", "/"))
        self.Log("<-- Found %d files" % len(matches))
        return matches
    #---

    def FindSetOfFiles(self, masks=['*.*'], workDir=''):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        matches = []
        for mask in masks:
            extMatches = self.FindFiles(mask,workDir)
            if len(extMatches)>0:
                matches.extend(extMatches)
            #---
        #---
        self.Log("<-- Found %d files" % len(matches))
        return matches
    #---

    def SplitFileName(self, fname):
        rPath = os.path.dirname(fname)
        (rName, rExt) = os.path.splitext( os.path.basename(fname))
        return (rPath,rName,rExt)
    #---

    def RunClean(self, command, workDir='', errorPattern=''):
        self.Run(command, workDir)
        if (self.cret!=0):
            self.Log("Terminating of RunClean, return code is not 0")
            header = '--- stdout of %s (%d) ---' % (command, self.cret)
            footer = '-'*len(header)
            self.LogExtend(TextProcessor.Format(self.cout, offset, header, footer))

            header = '--- stderr of %s (%d) ---' % (command, self.cret)
            footer = '-'*len(header)
            self.LogExtend(TextProcessor.Format(self.cerr, offset, header, footer))

            self.Exit(-1)
        #---

        if len(errorPattern)>0:
            # pattern is given
            if TextProcessor.SearchForward(self.cout, errorPattern)>-1:
                print 'Pattern %s is found in stdout' % errorPattern
                TextProcessor.Print(self.cout,'    ','---- stdout of %s (%s) ----' % (command, self.cret), '------\n')
                TextProcessor.Print(self.cerr,'    ','---- stderr of %s (%s) ----' % (command, self.cret), '------\n')
                self.Exit(-1)
            #---

            if TextProcessor.SearchForward(self.cerr, errorPattern)>-1:
                print 'Pattern %s is found in stderr' % errorPattern
                TextProcessor.Print(self.cout,'    ','---- stdout of %s (%s) ----' % (command, self.cret), '------\n')
                TextProcessor.Print(self.cerr,'    ','---- stderr of %s (%s) ----' % (command, self.cret), '------\n')
                self.Exit(-1)
            #---
        #---
        return
    #---

    def OneDirUp(self,dirName):
        oneDirUp = re.sub('/[^/]+$','',dirName)
        return oneDirUp
    #---

    def GetMACAddress(self, delimiter=':'):
        retVal = ''
        while True:
            self.Run('ifconfig -a | grep HWaddr', silent=True)
            if self.cret != 0:
                self.Log("ERROR: Command execution error.")
                break # execution error
            #---

            if len(self.cout) < 1:
                self.Log("ERROR: Command returned no output. Is pattern HWaddr missing?")
                break
            #---

            parts = re.split('\s+',self.cout[0])
            if len(parts) < 1:
                self.Log("ERROR: Command output format. Is output format  differ from expected?")
                break
            #---

            rawStr = parts[4]
            byteStr = re.split(':',rawStr)
            if len(byteStr) < 6:
                self.Log("ERROR: Parsing error. Is output format  differ from expected?")
                break
            #---

            # Success
            retVal = delimiter.join(byteStr)

            break
        #----------------------
        return retVal
    #---


    def GenPyBin(self, exportData, objName, defaultFileLocation):
        f = open(objName+'.py', 'wt')
        f.write( "#!/usr/bin/python\n")
        f.write( "\n")
        f.write( "__all__ = ['Export']\n")
        f.write( "\n")
        f.write( "# This is automatically generated file. Do not edit!\n")
        f.write( "# Usage:\n")
        f.write( "#     import %s\n" % objName)
        f.write( "#     %s.Extract()\n" % objName)
        f.write( "# or in command line\n")
        f.write( "#     python %s.py [fileName]\n" % objName)
        f.write( "\n")
        f.write( "import zlib\n")
        f.write( "import binascii\n")
        f.write( "import hashlib\n")
        f.write( "import base64\n")
        f.write( "import sys\n")
        f.write( "\n")
        f.write( "def Extract(fileName='%s'):\n" % defaultFileLocation)
        f.write( "    binObject=''\n")

        dataArray = TextProcessor.Fold(exportData, 100)

        for blk in dataArray:
            f.write( "    binObject+='%s'\n" % blk)
        #---


        f.write( "    decoded = base64.b64decode(binObject)\n")
        f.write( "    decompressed = zlib.decompress(decoded)\n")
        f.write( "    f = open(fileName, 'wb')\n")
        f.write( "    f.write(decompressed)\n")
        f.write( "    f.flush()\n")
        f.write( "    f.close()\n")
        f.write( "#---\n")
        f.write( "\n")
        f.write( "if __name__ == '__main__':\n")
        f.write( "    import argparse\n")
        f.write( "    parser = argparse.ArgumentParser()\n")
        f.write( "    parser.add_argument('--file', action='store', default='%s', help='Export file name')\n" % defaultFileLocation)
        f.write( "    args = parser.parse_args()\n")
        f.write( "    Extract(args.file)\n")
        f.write( "#---\n")
        f.write( "\n")
    #---



    def bin2py(self, binFileName, pyObjectName):
        self.Log('--> %s' % (sys._getframe(0)).f_code.co_name)
        try:
            self.Log('Converting %s to %s.py' % (binFileName, pyObjectName))

            original_data = open(binFileName, 'rb').read()
            self.Log('Original   %8d bytes (%s)' % (len(original_data), hashlib.sha256(original_data).hexdigest()))

            compressed = zlib.compress(original_data)
            self.Log('Compressed %8d bytes (%s)' % (len(compressed), hashlib.sha256(compressed).hexdigest()))

            encoded = base64.b64encode(compressed)
            self.Log('Encoded    %8d bytes (%s)' % (len(encoded), hashlib.sha256(encoded).hexdigest()))

            self.GenPyBin(encoded, pyObjectName, binFileName)
        except:
            self.Log("Warning: something went wrong")
        #---
        self.Log('<-- %s' % (sys._getframe(0)).f_code.co_name)
    #---

#-- end of class



if __name__ == "__main__":
    import argparse
    head_description = "Shell Receipes Engine"
    parser = argparse.ArgumentParser(description        =   head_description,
                                     formatter_class    =   argparse.RawDescriptionHelpFormatter)
    # Global arguments
    parser.add_argument('--debug',   action='store_true', default=False,        help='Debug execution mode')
    parser.add_argument('--quiet',   action='store_true', default=False,        help='Quiet execution mode')

    subparsers = parser.add_subparsers(help='Supported commands', dest='command')

    setup_parser = subparsers.add_parser('setup',                  help='Setup Python module')
    setup_parser = subparsers.add_parser('install',                help='Install shrec as system utility')
    unitt_parser = subparsers.add_parser('unittest',               help='Unit test the module')
    debug_parser = subparsers.add_parser('debug',                  help='Debug new code')

    recipe_parser = subparsers.add_parser('recipe',                  help='System configuration recipes')
    rsp = recipe_parser.add_subparsers(help='Recipes', dest='recipe')

    description = "Enable or disable SSH access for root"
    r001_parser = rsp.add_parser('enablerootssh',  description=description,     help='Enable root ssh')
    r001_parser.add_argument('--no',  action='store_true', default=False,       help='Opposite operation')

    description = "Enable or disable kernel power managemennt functions"
    r002_parser = rsp.add_parser('enablepm',  description=description,          help='Enable power management')
    r002_parser.add_argument('--no',  action='store_true', default=False,       help='Opposite operation')

    description = "Enable or disable IP V.6 support"
    r003_parser = rsp.add_parser('enableip6',  description=description,         help='Enable support of IP v.6')
    r003_parser.add_argument('--no',  action='store_true', default=False,       help='Opposite operation')

    description = "Enable or disable TCG SED support"
    r003_parser = rsp.add_parser('enabletcg',  description=description,         help='Enable support of TCG storage')
    r003_parser.add_argument('--no',  action='store_true', default=False,       help='Opposite operation')

    description = "Set hostname"
    r003_parser = rsp.add_parser('sethostname',  description=description,       help='Set hostname from MAC or Random')
    r003_parser.add_argument('--naming',  action='store', default='mac',          help='Naming: {mac,rnd}')


    args = parser.parse_args()

    if (args.command == 'setup'):
        setupScript = [
                "#!/usr/bin/env python",
                "from distutils.core import setup",
                "setup(name='shrec',version='0.2',",
                "      description='Script Helper',",
                "      py_modules=['shrec'])",
                ""
            ]
        #---
        TextProcessor.Save(setupScript, 'temp_setup.py')
        batch.Run('python temp_setup.py install')
        os.remove('temp_setup.py')
        TextProcessor.Print(batch.cout,'','-- installation log --')
        batch.Exit(0)
    #--

    if (args.command == 'unittest'):
        errorCount = 0

        actRes = TextProcessor.QuotedString('abc')
        if (actRes != '"abc"'):
            print ("FAIL -- QuotedString")
            errorCount += 1
        #---

        actRes1 = TextProcessor.TimeStamp()
        actRes2 = TextProcessor.TimeStamp()
        if (actRes1 == actRes2):
            print ("FAIL -- TimeStamp %s VS %s" % (actRes1,actRes2))
            errorCount += 1
        #---

        actRes = TextProcessor.RandomString(3,'a')
        if (actRes != 'aaa'):
            print ("FAIL -- RandomString charset limitation")
            errorCount += 1
        #---

        actRes1 = TextProcessor.RandomString(16,'0123456789')
        actRes2 = TextProcessor.RandomString(16,'0123456789')
        if (actRes1 == actRes2):
            print ("FAIL -- RandomString, not really random")
            errorCount += 1
        #---


        exit(errorCount)
    #--

    if (args.command == 'recipe'):

        if (args.recipe == 'enablerootssh'):
            batch = Batch(args.debug, args.quiet, "auto")
            if batch.system != 'Linux': # Check the current platform
                batch.Print("Current platform is %s" % batch.system)
                batch.Print("Command is supported only for Linux platforms, terminating")
                batch.Print("See details in %s" % batch.LogFile)
                batch.Exit(0)
            #---
            if (args.no == False):
                # Normal operation
                batch.ReplaceLineInFile('/etc/ssh/sshd_config', 'PermitRootLogin', 'PermitRootLogin yes')
            else:
                batch.ReplaceLineInFile('/etc/ssh/sshd_config', 'PermitRootLogin', 'PermitRootLogin without-password')
            #---
            batch.Run('service sshd restart')
            batch.Exit(0)
        #---

        if (args.recipe == 'enabletcg'):
            batch = Batch(args.debug, args.quiet, "auto")
            if batch.system != 'Linux': # Check the current platform
                batch.Print("Current platform is %s" % batch.system)
                batch.Print("Command is supported only for Linux platforms, terminating")
                batch.Print("See details in %s" % batch.LogFile)
                batch.Exit(0)
            #---
            print( batch.GetMACAddress('').upper() )
            if (args.no == False):
                batch.Print("Enabling support of TCG storage")
                # Normal operation
                # /etc/default/grub
                # GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
                # Change to GRUB_CMDLINE_LINUX_DEFAULT="quiet splash libata.allow_tpm=1"
                # run update-grub
                #
            else:
                batch.Print("Disabling support of TCG storage")
                # Reverse operation
                # /etc/default/grub
                # GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
                # Change to GRUB_CMDLINE_LINUX_DEFAULT="quiet splash libata.allow_tpm=1"
                # run update-grub
                #
            #---
            batch.Exit(0)
        #---

        if (args.recipe == 'sethostname'):
            # https://www.linuxquestions.org/questions/linux-networking-3/mac-address-based-hostname-333067/
            batch = Batch(args.debug, args.quiet, "auto")
            if batch.system != 'Linux': # Check the current platform
                batch.Print("Current platform is %s" % batch.system)
                batch.Print("Command is supported only for Linux platforms, terminating")
                batch.Print("See details in %s" % batch.LogFile)
                batch.Exit(0)
            #---
            exitCode = -1
            while True:
                if args.naming == 'mac':
                    newHostName = batch.GetMACAddress('').upper()
                elif args.naming == 'rnd':
                    newHostName = TextProcessor.RandomString(8)
                else:
                    batch.Print("ERROR: Unsupported naming scheme %s" % args.naming)
                    break
                #---

                if len(newHostName)==0:
                    batch.Print("ERROR: Cannot get new hostname.")
                    break
                #---

                batch.Run('hostname %s' % newHostName, silent=True)
                if batch.cret != 0:
                    batch.Print("ERROR: Command execution error.")
                    break
                #---


                if not batch.WriteFile('/etc/hostname', [newHostName]):
                    batch.Print("ERROR: writing /etc/hostname")
                    break
                #---


                #-------------------- SUCCESS
                exitCode = 0
                break
            #---
            batch.Exit(exitCode)
        #---


    #--




    if (args.command == 'debug'):
        batch = Batch(args.debug, args.quiet, "auto")
        batch.Print("Put your code here")
        batch.Print(batch.LogFile)
        batch.Run("ping -c 3 127.0.0.1")
        print (batch.cret)
        batch.Exit(0)
    #--



    print ("Unhandled command %s" % args.command)

    exit(0)




