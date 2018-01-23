#!/usr/bin/python
""" SHell RECipes module """

import subprocess
import os
import sys
import shutil
import platform
import re
import argparse

from time import time
from time import ctime

from datetime import datetime
import random
import string
import inspect
import tempfile
import zlib
import hashlib
import base64

__author__ = 'dmitry.obukhov'
__all__ = ['TextProcessor', 'Batch']



class TextProcessor(object):
    """  Text manipulation functions """

    @staticmethod
    def quoted_string(string_value):
        """ 'abc' --> '"abc"' """
        return "\"%s\"" % string_value
    #--- end of method

    @staticmethod
    def time_stamp(format_str = '%Y_%m_%d_%H%M%S%f'):
        """  --> '2018_01_01_1234569999' """
        return datetime.now().strftime(format_str)
    #--- end of method

    @staticmethod
    def random_string(length, charset=''):
        """  --> 'lsdahfl897klj' """
        if charset=='':
            charset = string.ascii_uppercase + string.digits
        return ''.join(random.choice(charset) for _ in range(length))
    #--- end of method


    @staticmethod
    def parse_shell_output(command, args=''):
        """  --> 'lsdahfl897klj' """
        retVal = []
        outputInOneStr = subprocess.check_output([command, args])
        retVal = re.split('[\r\n]+', outputInOneStr)
        for idx in range(0,len(retVal)):
            retVal[idx] = retVal[idx].rstrip()
        #---
        return retVal
    #--- end of method


    @staticmethod
    def debug_info(message_str):
        """  --> Debug info """
        frame = sys._getframe(1)
        funName = frame.f_code.co_name
        line_number = frame.f_lineno
        filename = frame.f_code.co_filename
        return ( "%s : %s (%s:%04d) : %s" % (self.TimeString('%H.%M.%S.%f'), funName,filename,line_number,message_str))
    #--- end of method


    @staticmethod
    def Read(file_name_str, cleanUp=True):
        """  <FILE> --> [str,str,str] """
        retVal = []
        try:
            f = open(file_name_str)
        except IOError:
            return None
        else:
            retVal = f.readlines()
            f.close()
            if cleanUp == True:
                retVal = TextProcessor.rstrip_all(retVal)
                retVal = TextProcessor.remove_empty_lines(retVal)
        return retVal
    #---------------------



    @staticmethod
    def unify_length(s, maxlen=-1, minlen=-1, spacer=' '):
        """  Cut string or add spacers to keep length for all lines """
        retStr = s
        curLen = len(retStr)
        # if maxLen defined, keep the left portion
        if maxlen>0 and (curLen > maxlen):
            retStr = retStr[:maxlen]

        # if min len is defined, space trail string
        curLen = len(retStr)
        if minlen>0 and (curLen < minlen):
            retStr = retStr + spacer*(minlen-curLen)

        return retStr
    #--

    @staticmethod
    def fold(long_str, width):
        """  longStr --> [str1,str2,str3] """
        retVal = []
        tmp = long_str
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
    def format(t, indent="", header="", footer="", maxlen=-1, minlen=-1, line_numbering_start=-1):
        """  [str1,str2] --> [header, offset + str1, offset + str2, footer]"""
        retTxt = []
        line_number_str = ""
        line_number_placeholder = ''
        if line_numbering_start>-1:
            line_number = line_numbering_start
            line_number_width = len("%d" % len(t))
            line_number_template = "%%%dd: " % line_number_width
            line_number_placeholder = ' '*(line_number_width+2)

        # if the header is defined, add header after indent
        if (len(header))>0:
            retTxt.append("%s%s%s" % (indent, line_number_placeholder, header))

        for i in range(0,len(t)):
            # prepare line numbering
            if line_numbering_start>-1:
                line_number_str = line_number_template % line_number
                line_number += 1
            # prepare line in format [indent][lineNumber][actualString]
            cur_line = "%s%s%s" % (indent,line_number_str,t[i])
            cur_line = TextProcessor.unify_length(cur_line,maxlen,minlen)
            # add to the output
            retTxt.append(cur_line)
        #----------------------------- end for

        if (len(footer))>0:
            retTxt.append("%s%s%s" % (indent, line_number_placeholder, footer))

        return retTxt
    #---------------------

    @staticmethod
    def Print(t, indent="", header="", footer="", maxlen=-1, minlen=-1, line_numbering_start=-1):
        """  print the list of strings """
        if len(t)>0:
            tmp = TextProcessor.format(t,indent,header,footer,maxlen,minlen,line_numbering_start)
            for i in range(0,len(tmp)):
                print (tmp[i])
            #---
        #---
    #---


    @staticmethod
    def save(text, file_name):
        """  save text to file """
        fileToSave = open(file_name, 'w')
        for item in text:
            fileToSave.write("%s\n" % item)
        #---
        fileToSave.flush()
        fileToSave.close()
    #---

    @staticmethod
    def append(text, file_name):
        """  append text to file """
        fileToSave = open(file_name, 'a')
        for item in text:
            fileToSave.write("%s\n" % item)
        #---
        fileToSave.flush()
        fileToSave.close()
    #---



    @staticmethod
    def replace_all(t, pattern, replacement):
        """  replace pattern in all strings """
        retVal = []
        for i in range(0,len(t)):
            cur = t[i]
            while re.match(pattern,cur):
                cur = re.sub(pattern, replacement, cur)
            #---
            retVal.append(cur)
        #---
        return retVal
    #---------------------

    @staticmethod
    def each_line(txt, function_str):
        """ for each line ret[x] = functionStr(inp[x]) """
        retVal = []
        for i in range(0,len(txt)):
            x = txt[i]
            y = eval(function_str)
            retVal.append(y)
        #---
        return retVal
    #--

    @staticmethod
    def rstrip_all(txt):
        """ for each y = rstrip(x) """
        retVal = []
        for i in range(0,len(txt)):
            retVal.append(txt[i].rstrip())
        #---
        return retVal
    #---------------------

    @staticmethod
    def remove_empty_lines(txt):
        """ RemoveEmptyLines """
        retVal = []
        for i in range(0,len(txt)):
            if len(txt[i])>0:
                retVal.append(txt[i])
            #---
        #---
        return retVal
    #---------------------

    @staticmethod
    def remove_duplicates(txt):
        output = []
        for x in txt:
            if x not in output:
                output.append(x)
            #--
        #--
        return output
    #---------------------


    @staticmethod
    def add(txt, something, delimiter='[\n|\r]+'):
        if type( something ) == str :
            tmp = re.split(delimiter, something)
            txt.extend(tmp)
        elif type( something ) == list :
            txt.extend(something)
        return txt
    #---------------------

    @staticmethod
    def dedent(txt, offset_pos=0):
        output = []
        for x in txt:
            output.append(x[offset_pos:])
        #--
        return output
    #---------------------

    @staticmethod
    def maxlen(txt):
        maxLen = len(txt[0])
        for x in txt:
            if len(x)>maxLen:
                maxLen = len(x)
            #---
        #---
        return maxLen
    #---------------------

    @staticmethod
    def minlen(txt):
        minLen = len(txt[0])
        for x in txt:
            if len(x)<minLen:
                minLen = len(x)
            #---
        #---
        return minLen
    #---------------------


    @staticmethod
    def to_string (txt, delimiter=' '):
        retStr = ""
        maxidx = len(txt)
        for i in range(0,maxidx):
            retStr += txt[i]
            if i<(maxidx-1):
                retStr += delimiter
            #---
        #---
        return retStr
    #---------------------

    @staticmethod
    def add_right_column(txt,trailer=' '):
        output = []
        for x in txt:
            output.append(x + trailer)
        #--
        return output
    #---------------------

    @staticmethod
    def vertical_cut(txt,left_col=0,right_col=-1):
        output = []
        for x in txt:
            if len(x)<left_col:
                output.append('')
            elif len(x)<right_col:
                output.append(x[left_col:])
            else:
                output.append(x[left_col:right_col])
        #--
        return output
    #---------------------

    @staticmethod
    def filter(txt, pattern):
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
    def filter_not(txt, pattern):
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
    def search_forward(txt, pattern, start=0):
        for i in range(start,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                return i
        return -1
    #---------------------

    @staticmethod
    def search_backward(txt, pattern, start=-1):
        if start<0:
            start = len(txt)-1
        for i in range(start,-1,-1):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                return i
        return -1
    #---------------------


    @staticmethod
    def count_matches(txt,pattern):
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
    def cut_fragment(txt, start, stop):
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
    def insert_fragment(txt,position,fragment):
        """ insert fragment at given position """
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
    """ Shell interface """

    def __init__(self, debug=False, quiet=True, log_file=""):
        """ Class Constructor """
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
        self.logList = []           # debug log
        self.text = []
        self.output = []        # copy of print
        self.replay = []        # replay buffer
        self.token = []

        self.cout = []
        self.parsed = []
        self.cerr = []
        self.cret = 0
        self.command = ''
        self.starttime = None
        self.endtime = None
        self.elapsed = 0
        self.process   = None
        self.rawOutput = ''
        self.rawError  = ''



        self.LogFile = log_file
        if len(self.LogFile)>0:
            if self.LogFile == "auto":
                (d,f,e) = self.split_file_name(callerScript)
                self.LogFile = os.path.normpath(tempfile.gettempdir() + '/' + f + '__' + TextProcessor.time_stamp() + '.tmp')
            #--
        #---
        self.supressRunOutput = False
        self.lastWrittenFile = ''
        self.lastBackupFile = ''
        self.caller = callerScript
        self.logBaseline = 3
        self.logOffsetStr = '    '
        self.log('caller=%s' % callerScript)
        self.log('self=%s' % __file__)
        if self.debug:
            self.log('==== System information')
            self.log("platform.system=%s" % self.system)
            self.log("platform.platform=%s" % platform.platform())
            (x,y) = platform.architecture()
            self.log("platform.architecture=%s" % x)
            self.log("platform.python_version=%s" % platform.python_version())
            self.log("platform.system=%s" % platform.system())
            if 'Linux' == self.system:
                (distName,distVer,distID) = platform.linux_distribution()
                self.log("Linux.Distro=%s" % distName)
                self.log("Linux.Version=%s" % distVer)
                self.log("Linux.DistID=%s" % distID)
            #---
            self.log('===========================')
        #--
    #---

    def _call_stack_depth (self):
        """ Hidden Method for stack depth """
        stack = inspect.stack()
        return len(stack)
    #---

    def log(self, message):
        """ Save message in execution history """
        stack = inspect.stack()
        offset = self.logOffsetStr * (len(stack) - self.logBaseline)
        if self.debug:
            print (offset + message)
        #---
        self.logList.append(offset + message)
        if len(self.LogFile)>0:
            with open(self.LogFile, "a") as myLogFile:
                myLogFile.write("%s\n" % (offset + message))
            #---
        #---
        return True
    #---

    def ask_to_continue(self, message=''):
        """ Ask for user input to continue or stop """
        # pylint: disable=W0212
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        # pylint: enable=W0212
        if len(message)>0:
            self.prn(message)
        else:
            self.prn("Continue execution?")
        #---
        var = raw_input('')
        if var == 'n':
            self.log('User terminated')
            self.exit(0)
        #---
        self.log('User choose to continue...')
        return True
    #---


    def log_caller_function(self):
        """ LogCallerFunction """
        # pylint: disable=W0212
        self.log('--> %s' % (sys._getframe(1)).f_code.co_name)
        # pylint: enable=W0212
        return True
    #---


    def log_extend(self, array_of_strings):
        """ Log a list of strings """
        stack = inspect.stack()
        offset = self.logOffsetStr * (len(stack) - self.logBaseline)
        for eachStr in array_of_strings:
            self.log(offset + eachStr)
        return True
    #---



    def _run_silent (self, command_str, working_directory=''):
        """ Run shall command without log messages """
        actualDirectory = os.getcwd()
        if (len(working_directory)>0):
            os.chdir(working_directory)
        #--
        process = subprocess.Popen(command_str, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        pid = process.pid
        rawOutput, rawError = process.communicate()
        if (len(working_directory)>0):
            os.chdir(actualDirectory)
        #--
        return process.returncode
    #---


    def run (self, command_str, working_directory='', silent=False):
        """ Run shall command """
        if len(command_str)==0:
            return True
        #---
        self.log('--> %s     %s' % ((sys._getframe(0)).f_code.co_name,command_str))
        self.cout = []
        self.parsed = []
        self.cerr = []
        self.cret = 0
        self.command = command_str
        self.starttime = time()

        self.log("Executing %s at %s" % (self.command, os.getcwd()))
        self.log("Started %s" % ctime(self.starttime))

        actualDirectory = os.getcwd()
        if (len(working_directory)>0):
            self.log("Changing directory %s --> %s" % (actualDirectory,working_directory))
            os.chdir(working_directory)
        #--

        self.log("Continue in %s" % (os.getcwd()))

        self.process = subprocess.Popen(self.command, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        pid = self.process.pid

        self.log('PID = %d' % pid)

        if self.supressRunOutput or silent:
            (self.rawOutput, self.rawError) = self.process.communicate()
            self.cout = TextProcessor.parse_shell_output(self.rawOutput)
            self.cerr = TextProcessor.parse_shell_output(self.rawError)
            self.cret = self.process.returncode
        else:
            self.cout = []
            self.rawOutput = ""

            for line in iter(self.process.stdout.readline, ''):
                line = line.rstrip()
                self.prn ("%s" % line)
                self.cout.append(line)
            #---
            self.rawError = self.process.stderr.readlines()
            self.process.stdout.close()
            self.process.stderr.close()
            self.cret = self.process.wait()

            self.rawOutput = "\n".join(self.cout)
        #---

        self.log('Thread finished with return code %d' % self.cret)

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
            self.log_extend(TextProcessor.format(self.cout, offset, header, footer))
        #--
        if len(self.cerr)>0:
            header = '--- stderr of %s ---' % self.command
            footer = '-'*len(header)
            self.log_extend(TextProcessor.format(self.cerr, offset, header, footer))
        #--

        if (len(working_directory)>0):
            self.log("Changing directory %s --> %s" % (working_directory,actualDirectory))
            os.chdir(actualDirectory)
            self.log("Continue in %s" % (os.getcwd()))
        #--


        self.endtime = time()
        self.elapsed = (self.endtime - self.starttime)
        self.log("Completed %s" % ctime(self.endtime))
        self.log("Elapsed %f seconds" % self.elapsed)

        return (self.cret == 0)



    def run_and_parse(self, command, work_dir, pattern, delimiter=' '):
        """ Run shall command and parse output """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        self.token = []
        res = self.run(command,work_dir)
        pos = TextProcessor.search_forward(self.cout,pattern)
        if pos>=0:
            self.log('Pattern %s found at position %d of stdout' % (pattern,pos))
            self.token = re.split(delimiter,self.cout[pos])
            self.log('Extracted %d tokens' % (len(self.token)))
        else:
            self.log('Pattern %s is not found in stdout capture' % (pattern))
            pos = TextProcessor.search_forward(self.cerr,pattern)
            if pos>=0:
                self.log('Pattern %s found at position %d in stderr' % (pattern,pos))
                self.token = re.split(delimiter,self.cerr[pos])
                self.log('Extracted %d tokens' % (len(self.token)))
            else:
                self.log('Pattern %s is not found in stderr capture' % (pattern))
            #---
        return pos
    #---


    def run_as_user(self, command, work_dir, user=''):
        """ Run shall command as specific user """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name + " user=%s" % user)
        if len(user)>0:
            # Run it as different user
            command = ("sudo -H -u %s bash -c " % user) + "'" + command + "'"
        #---
        return self.run(command)
    #---

    def _read_new_buffer (self, file_name):
        """ Read file """
        retBuf = []
        self.errcode = 0
        if not os.path.isfile(file_name):
            self.errcode = -1
            self.errmsg = "ERROR (%d): Cannot find file %s" % (self.errcode, file_name)
            self.log(self.errmsg)
            return (False,[])
        #-- end if

        try:
            f = open(file_name)
        except IOError:
            self.errcode = -2
            self.errmsg = "ERROR (%d): Cannot open %s" % (self.errcode, file_name)
            self.log(self.errmsg)
            return (False,[])
        #---

        try:
            retBuf = f.readlines()
        except:
            self.errcode = -3
            self.errmsg = "ERROR (%d): Cannot read from %s" % (self.errcode, file_name)
            self.log(self.errmsg)
            return (False,[])
        #---

        f.close()

        retBuf = TextProcessor.rstrip_all(retBuf)
        #retBuf = TextProcessor.RemoveEmptyLines(retBuf)

        if len(retBuf)<1:
            warning = "Warning: empty file %s" % (file_name)
            self.log(self.errmsg)
        #-- end if

        return (True,retBuf)
    #---

    def read_file (self, file_name):
        """ Read file """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        (res,self.text) = self._read_new_buffer(file_name)
        return res
    #---

    def write_file (self, file_name, str_array=None):
        """ Write file """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        self.errcode = 0
        self.lastWrittenFile = file_name
        self.lastBackupFile = ''
        if os.path.isfile(file_name):
            self.lastBackupFile = file_name + '.bak'
            self.log('Saving backup %s' % self.lastBackupFile)
            shutil.copy(file_name, self.lastBackupFile)
        #-- end if

        try:
            fileToSave = open(file_name, 'w')
            bufferToSave = []
            if str_array == None:
                bufferToSave = self.text
            else:
                bufferToSave = str_array

            for item in bufferToSave:
                fileToSave.write("%s\n" % item)
            #--
            fileToSave.flush()
            fileToSave.close()
            self.log("Saved %d lines to %s" % (len(bufferToSave),file_name))
            return True
        except:
            self.errcode = -2
            self.errmsg = "ERROR (%d): Cannot write to %s" % (self.errcode, file_name)
            self.log(self.errmsg)
            return False
        return False
    #---

    def _diff_last_file_write (self):
        """ Diff last written file """
        if os.path.isfile(self.lastWrittenFile) and os.path.isfile(self.lastBackupFile):

            with tempfile.NamedTemporaryFile(dir=tempfile._get_default_tempdir(), delete=False) as tmpfile:
                diffName = tmpfile.name

            self._run_silent('diff %s %s > %s' % (self.lastBackupFile,self.lastWrittenFile,diffName))
            (res,diffBuffer) = self._read_new_buffer(diffName)
            if res:
                offset = '    '
                header = '====== DIFF in %s ======' % self.lastWrittenFile
                footer = '='*len(header)
                self.log_extend(TextProcessor.format(diffBuffer, offset, header,footer))
            #---
            try:
                os.remove(diffName)
            except:
                self.log("Warning: Cannot delete temp file in Diff function")
            #---
        #-- end if
        return True
    #---

    def append_to_file(self, file_name, lines):
        """ append text to file """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.read_file(file_name):
            return False

        tempName = TextProcessor.random_string(8) + '.tmp'
        if self.debug:
            shutil.copyfile(file_name,tempName)

        self.text.extend(lines)
        if self.debug:
            self.log("Added %d lines to %s" % (len(lines),file_name))

        if not self.write_file(file_name):
            return False

        if self.debug:
            self._diff_last_file_write()

        return True
    #---------------------

    def replace_line_in_file(self, file_name, pattern, replacement, use_regex=False):
        """ open file, replace line, save """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.read_file(file_name):
            return False

        pos = TextProcessor.search_forward(self.text,pattern)             # Find the configuration line
        if (pos<0):                                                     # if line not found
            self.errcode = -3
            self.errmsg = "WARNING (%d): Cannot find %s in %s" % (self.errcode,pattern, file_name)
            self.log(self.errmsg)
            return False

        if use_regex:
            self.text[pos] = re.sub(self.text[pos],pattern,replacement)
        else:
            self.text[pos] = replacement

        if not self.write_file(file_name):
            return False

        if self.debug:
            self._diff_last_file_write()

        return True
    #---------------------


    def insert_fragment_at_pos(self, file_name, pos, fragment):
        """ open file, insert fragment at position, save """
        retVal = False
        myName = (sys._getframe(0)).f_code.co_name
        self.log('--> %s' % myName)

        while True: # Single exit point function
            if not self.read_file(file_name):
                break
            #---
            self.text = TextProcessor.insert_fragment(self.text,pos,fragment)

            if not self.write_file(file_name):
                break
            #---

            if self.debug:
                self._diff_last_file_write()
            #---

            retVal = True
            break # Single exit point function must break at the end
        #---

        self.log('<-- %s' % myName)
        return retVal
    #---------------------


    def insert_fragment_at_marker(self, file_name, pattern, fragment):
        """ open file, insert fragment at marker, save """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.read_file(file_name):
            return False

        pos = TextProcessor.search_forward(self.text,pattern)
        if pos>0:
            return self.insert_fragment_at_pos(file_name, pos+1, fragment)

        return False
    #---------------------


    def delete_fragment_between_markers(self, file_name, start_pattern, end_pattern, inclusive=False):
        """ open file, delete fragment between markers, save """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.read_file(file_name):
            return False

        posStart = TextProcessor.search_forward(self.text,start_pattern)
        if posStart<0:
            self.log("Cannot find start pattern %s" % start_pattern)
            return False

        self.log("Found start pattern %s at %d" % (start_pattern,posStart))
        # start search from the position of start pattern
        posEnd = TextProcessor.search_forward(self.text,end_pattern,posStart)
        if posEnd<0:
            self.log("Cannot find end pattern %s" % end_pattern)
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

        if not self.write_file(file_name):
            return False

        if self.debug:
            self._diff_last_file_write()

        return True
    #---------------------


    def delete_lines_from_file(self, file_name, pattern):
        """ open file, delete lines matching pattern, save """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.read_file(file_name):
            return False

        self.text = TextProcessor.filter_not(self.text,pattern)

        self.text = TextProcessor.insert_fragment(self.text,pos,fragment)

        if not self.write_file(file_name):
            return False

        if self.debug:
            self._diff_last_file_write()

        return True
    #---------------------


    def prn(self, str_message):
        """ print and save log """
        self.log(str_message)
        if not self.quiet:
            print (str_message)
        return True
    #--


    def exit(self, ret_code=0, message='', log=''):
        """ exit script """
        # pylint: disable=W0212
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        # pylint: enable=W0212
        if message!='':
            self.logList.append(strMessage)
            print (message)
        #---
        self.log('Exit script with code %d' % ret_code)
        exit(ret_code)
    #--

    def fatal_error(self, message):
        """ Fatal Error: save log and terminate """
        # pylint: disable=W0212
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        # pylint: enable=W0212
        retCode = -1
        self.logList.append(strMessage)
        sys.stderr.write("%s\n" % message)
        self.log('Exit script with code %d' % retCode)
        exit(retCode)
    #--


    def check_condition(self, condition):
        """ Assert """
        if not condition:
            frame = sys._getframe(1)
            funName = frame.f_code.co_name
            filename = frame.f_code.co_filename
            message = 'Fatal exit on assert in %s (%s:%d)' % (funName, filename, filename)
            self.fatal_error(message)
        return True
    #--


    def find_files(self, mask='*.*', work_dir=''):
        """ Find files mathing a mask """
        # pylint: disable=W0212
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        # pylint: enable=W0212
        if work_dir=='':
            work_dir = os.getcwd()
        #---
        self.log('Mask = %s, Path=%s' % (mask, work_dir))
        matches = []
        for root, dirnames, filenames in os.walk(work_dir):
          for filename in fnmatch.filter(filenames, mask):
              matches.append(os.path.join(root, filename).replace("\\", "/"))
        self.log("<-- Found %d files" % len(matches))
        return matches
    #---

    def find_set_of_files(self, masks=['*.*'], work_dir=''):
        """ Find files by set of masks """
        # pylint: disable=W0212
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        # pylint: enable=W0212
        matches = []
        for mask in masks:
            extMatches = self.find_files(mask,work_dir)
            if len(extMatches)>0:
                matches.extend(extMatches)
            #---
        #---
        self.log("<-- Found %d files" % len(matches))
        return matches
    #---

    def split_file_name(self, file_name):
        """ Split file name into path, name, and extension """
        rPath = os.path.dirname(file_name)
        (rName, rExt) = os.path.splitext( os.path.basename(file_name))
        return (rPath,rName,rExt)
    #---

    def run_clean(self, command, work_dir='', error_pattern=''):
        """ Run command and ensure that it went w/o issues """
        # pylint: disable=W0212
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        # pylint: enable=W0212
        self.run(command, work_dir)
        if (self.cret!=0):

            self.log("Terminating of RunClean, return code is not 0")
            header = '--- stdout of %s (%d) ---' % (command, self.cret)
            footer = '-'*len(header)
            offset = '    '
            self.log_extend(TextProcessor.format(self.cout, offset, header, footer))

            header = '--- stderr of %s (%d) ---' % (command, self.cret)
            footer = '-'*len(header)
            self.log_extend(TextProcessor.format(self.cerr, offset, header, footer))

            self.exit(-1)
        #---

        if len(error_pattern)>0:
            # pattern is given
            if TextProcessor.search_forward(self.cout, error_pattern)>-1:
                self.log('Pattern %s is found in stdout' % error_pattern)
                TextProcessor.Print(self.cout, '    ', '---- stdout of %s (%s) ----' % (command, self.cret), '------\n')
                TextProcessor.Print(self.cerr, '    ', '---- stderr of %s (%s) ----' % (command, self.cret), '------\n')
                self.exit(-1)
            #---

            if TextProcessor.search_forward(self.cerr, error_pattern)>-1:
                self.log('Pattern %s is found in stderr' % error_pattern)
                TextProcessor.Print(self.cout, '    ', '---- stdout of %s (%s) ----' % (command, self.cret), '------\n')
                TextProcessor.Print(self.cerr, '    ', '---- stderr of %s (%s) ----' % (command, self.cret), '------\n')
                self.exit(-1)
            #---
        #---
        return
    #---

    def one_dir_up(self,dir_name):
        """ One directory up tree """
        oneDirUp = re.sub('/[^/]+$', '', dir_name)
        return oneDirUp
    #---

    def get_mac_address(self, delimiter=':'):
        """ Get MAC address of the current system """
        # pylint: disable=W0212
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        # pylint: enable=W0212
        retVal = ''
        while True:
            self.run('ifconfig -a | grep HWaddr', silent=True)
            if self.cret != 0:
                self.log("ERROR: Command execution error.")
                break # execution error
            #---

            if len(self.cout) < 1:
                self.log("ERROR: Command returned no output. Is pattern HWaddr missing?")
                break
            #---

            parts = re.split('\s+',self.cout[0])
            if len(parts) < 1:
                self.log("ERROR: Command output format. Is output format  differ from expected?")
                break
            #---

            rawStr = parts[4]
            byteStr = re.split(':',rawStr)
            if len(byteStr) < 6:
                self.log("ERROR: Parsing error. Is output format  differ from expected?")
                break
            #---

            # Success
            retVal = delimiter.join(byteStr)

            break
        #----------------------
        return retVal
    #---


    def _gen_pybin(self, export_data, obj_name, default_file_name):
        """ Generate script to restore binary file """
        f = open(obj_name+'.py', 'wt')
        f.write("#!/usr/bin/python\n")
        f.write("\n")
        f.write("__all__ = ['Export']\n")
        f.write("\n")
        f.write("# This is automatically generated file. Do not edit!\n")
        f.write("# Usage:\n")
        f.write("#     import %s\n" % obj_name)
        f.write("#     %s.Extract()\n" % obj_name)
        f.write("# or in command line\n")
        f.write("#     python %s.py [fileName]\n" % obj_name)
        f.write("\n")
        f.write("import zlib\n")
        f.write("import binascii\n")
        f.write("import hashlib\n")
        f.write("import base64\n")
        f.write("import sys\n")
        f.write("\n")
        f.write("def Extract(fileName='%s'):\n" % default_file_name)
        f.write("    binObject=''\n")

        dataArray = TextProcessor.fold(export_data, 100)

        for blk in dataArray:
            f.write("    binObject+='%s'\n" % blk)
        #---


        f.write("    decoded = base64.b64decode(binObject)\n")
        f.write("    decompressed = zlib.decompress(decoded)\n")
        f.write("    f = open(fileName, 'wb')\n")
        f.write("    f.write(decompressed)\n")
        f.write("    f.flush()\n")
        f.write("    f.close()\n")
        f.write("#---\n")
        f.write("\n")
        f.write("if __name__ == '__main__':\n")
        f.write("    import argparse\n")
        f.write("    parser = argparse.ArgumentParser()\n")
        f.write("    parser.add_argument('--file', action='store', default='%s', help='Export file name')\n" % default_file_name)
        f.write("    args = parser.parse_args()\n")
        f.write("    Extract(args.file)\n")
        f.write("#---\n")
        f.write("\n")
    #---



    def bin2py(self, bin_file_name, py_object_name):
        """ Generate Python script to restore binary file """
        # pylint: disable=W0212
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        # pylint: enable=W0212
        try:
            self.log('Converting %s to %s.py' % (bin_file_name, py_object_name))

            original_data = open(bin_file_name, 'rb').read()
            self.log('Original   %8d bytes (%s)' % (len(original_data), hashlib.sha256(original_data).hexdigest()))

            compressed = zlib.compress(original_data)
            self.log('Compressed %8d bytes (%s)' % (len(compressed), hashlib.sha256(compressed).hexdigest()))

            encoded = base64.b64encode(compressed)
            self.log('Encoded    %8d bytes (%s)' % (len(encoded), hashlib.sha256(encoded).hexdigest()))

            self._gen_pybin(encoded, py_object_name, bin_file_name)
        except:
            self.log("Warning: something went wrong")
        #---
        # pylint: disable=W0212
        self.log('<-- %s' % (sys._getframe(0)).f_code.co_name)
        # pylint: enable=W0212
    #---

#-- end of class



if __name__ == "__main__":
    exit_code = -1
    parser = argparse.ArgumentParser(description="Shell Receipes Engine", \
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    # Global arguments
    parser.add_argument('--debug', action='store_true', default=False, help='Debug execution mode')
    parser.add_argument('--quiet', action='store_true', default=False, help='Quiet execution mode')

    subparsers = parser.add_subparsers(help='Supported commands', dest='command')

    SETUP_PRS = subparsers.add_parser('setup', help='Setup Python module')
    INSTALL_PRS = subparsers.add_parser('install', help='Install shrec as system utility')
    UTEST_PRS = subparsers.add_parser('unittest', help='Unit test the module')
    DEBUG_PRS = subparsers.add_parser('debug', help='Debug new code')

    RECIPE_PRS = subparsers.add_parser('recipe', help='System configuration recipes')
    RSP = RECIPE_PRS.add_subparsers(help='Recipes', dest='recipe')

    R001 = RSP.add_parser('enablerootssh', \
        description="Enable or disable SSH access for root", \
        help='Enable root ssh')
    R001.add_argument('--no', action='store_true', default=False, help='Opposite operation')

    R002 = RSP.add_parser('enablepm', \
        description="Enable or disable kernel power managemennt functions", \
        help='Enable power management')
    R002.add_argument('--no', action='store_true', default=False, help='Opposite operation')

    R003 = RSP.add_parser('enableip6', \
        description="Enable or disable IP V.6 support", \
        help='Enable support of IP v.6')
    R003.add_argument('--no', action='store_true', default=False, help='Opposite operation')

    R004 = RSP.add_parser('enabletcg', \
        description="Enable or disable TCG SED support", \
        help='Enable support of TCG storage')
    R004.add_argument('--no', action='store_true', default=False, help='Opposite operation')

    R005 = RSP.add_parser('sethostname', \
        "Set hostname", \
        help='Set hostname from MAC or Random')
    R005.add_argument('--naming', action='store', default='mac', help='Naming: {mac,rnd}')

    args = parser.parse_args()

    if (args.command == 'setup'):
        batch = Batch(args.debug, args.quiet, "auto")
        setupScript = [ \
                "#!/usr/bin/env python", \
                "from distutils.core import setup", \
                "setup(name='shrec',version='0.2',", \
                "      description='Script Helper',", \
                "      py_modules=['shrec'])", \
                "" \
            ]
        #---
        TextProcessor.save(setupScript, 'temp_setup.py')
        batch.run('python temp_setup.py install')
        os.remove('temp_setup.py')
        TextProcessor.Print(batch.cout,'','-- installation log --')
        batch.exit(0)
    #--

    if (args.command == 'unittest'):
        errorCount = 0

        actRes = TextProcessor.quoted_string('abc')
        if (actRes != '"abc"'):
            print ("FAIL -- QuotedString")
            errorCount += 1
        #---

        actRes1 = TextProcessor.time_stamp()
        actRes2 = TextProcessor.time_stamp()
        if (actRes1 == actRes2):
            print ("FAIL -- TimeStamp %s VS %s" % (actRes1,actRes2))
            errorCount += 1
        #---

        actRes = TextProcessor.random_string(3,'a')
        if (actRes != 'aaa'):
            print ("FAIL -- random_string charset limitation")
            errorCount += 1
        #---

        actRes1 = TextProcessor.random_string(16,'0123456789')
        actRes2 = TextProcessor.random_string(16,'0123456789')
        if (actRes1 == actRes2):
            print ("FAIL -- random_string, not really random")
            errorCount += 1
        #---


        exit(errorCount)
    #--

    if (args.command == 'recipe'):

        if (args.recipe == 'enablerootssh'):
            batch = Batch(args.debug, args.quiet, "auto")
            if batch.system != 'Linux': # Check the current platform
                batch.prn("Current platform is %s" % batch.system)
                batch.prn("Command is supported only for Linux platforms, terminating")
                batch.prn("See details in %s" % batch.LogFile)
                batch.exit(0)
            #---
            if args.no is False:
                # Normal operation
                batch.replace_line_in_file('/etc/ssh/sshd_config', 'PermitRootLogin', 'PermitRootLogin yes')
            else:
                batch.replace_line_in_file('/etc/ssh/sshd_config', 'PermitRootLogin', 'PermitRootLogin without-password')
            #---
            batch.run('service sshd restart')
            batch.exit(0)
        #---

        if (args.recipe == 'enabletcg'):
            batch = Batch(args.debug, args.quiet, "auto")
            if batch.system != 'Linux': # Check the current platform
                batch.prn("Current platform is %s" % batch.system)
                batch.prn("Command is supported only for Linux platforms, terminating")
                batch.prn("See details in %s" % batch.LogFile)
                batch.exit(0)
            #---
            print(batch.get_mac_address('').upper())
            if args.no is False:
                batch.prn("Enabling support of TCG storage")
                # Normal operation
                # /etc/default/grub
                # GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
                # Change to GRUB_CMDLINE_LINUX_DEFAULT="quiet splash libata.allow_tpm=1"
                # run update-grub
                #
            else:
                batch.prn("Disabling support of TCG storage")
                # Reverse operation
                # /etc/default/grub
                # GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
                # Change to GRUB_CMDLINE_LINUX_DEFAULT="quiet splash libata.allow_tpm=1"
                # run update-grub
                #
            #---
            batch.exit(0)
        #---

        if (args.recipe == 'sethostname'):
            # https://www.linuxquestions.org/questions/linux-networking-3/mac-address-based-hostname-333067/
            batch = Batch(args.debug, args.quiet, "auto")
            if batch.system != 'Linux': # Check the current platform
                batch.prn("Current platform is %s" % batch.system)
                batch.prn("Command is supported only for Linux platforms, terminating")
                batch.prn("See details in %s" % batch.LogFile)
                batch.exit(0)
            #---
            while True:
                new_host_name = ''
                if args.naming == 'mac':
                    new_host_name = batch.get_mac_address('').upper()
                elif args.naming == 'rnd':
                    new_host_name = TextProcessor.random_string(8)
                else:
                    batch.prn("ERROR: Unsupported naming scheme %s" % args.naming)
                    break
                #---

                if not (new_host_name == ''):
                    batch.prn("ERROR: Cannot get new hostname.")
                    break
                #---

                batch.run('hostname %s' % new_host_name, silent=True)
                if batch.cret != 0:
                    batch.prn("ERROR: Command execution error.")
                    break
                #---


                if not batch.write_file('/etc/hostname', [new_host_name]):
                    batch.prn("ERROR: writing /etc/hostname")
                    break
                #---


                #-------------------- SUCCESS
                exit_code = 0
                break
            #---
            batch.exit(exit_code)
        #---


    #--




    if (args.command == 'debug'):
        BATCH = Batch(args.debug, args.quiet, "auto")
        BATCH.prn("Put your code here")
        BATCH.prn(batch.LogFile)
        BATCH.run("ping -c 3 127.0.0.1")
        print (BATCH.cret)
        BATCH.exit(0)
    #--



    print ("Unhandled command %s" % args.command)

    exit(0)

