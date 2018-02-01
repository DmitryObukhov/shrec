#!/usr/bin/python
""" SHell RECipes module """
from __future__ import print_function
import subprocess
import os
import sys
import shutil
import platform
import re
import fnmatch
from datetime import datetime
import random
import string
import inspect
import tempfile
import zlib
import hashlib
import base64
from time import time
from time import ctime

# Logging violates class protection to extract name of the calling function. Disable the warning
# pylint: disable=W0212


__all__ = ['ShellWrapper']
__author__ = 'dmitry.obukhov'

class ShellWrapper(object):
    """ Shell interface """

    def __init__(self, debug=False, quiet=True, log_file=""):
        """ Class Constructor """
        frame = sys._getframe(1)
        callerScript = frame.f_code.co_filename
        self.error_count = 0
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
                fn_split = self.split_file_name(callerScript)
                self.LogFile = os.path.normpath(tempfile.gettempdir() + '/' + fn_split['name'] + '__' + self.time_stamp() + '.tmp')
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
            (bits, linkage) = platform.architecture()
            self.log("platform.architecture=%s" % bits)
            self.log("platform.linkage=%s" % linkage)
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

    @staticmethod
    def quoted_string(string_value):
        """ 'abc' --> '"abc"' """
        return "\"%s\"" % string_value
    #--- end of method

    def time_stamp(self, format_str = '%Y_%m_%d_%H%M%S%f'):
        """  --> '2018_01_01_1234569999' """
        return datetime.now().strftime(format_str)
    #--- end of method

    def random_string(self, length, charset=''):
        """  --> 'lsdahfl897klj' """
        if charset=='':
            charset = string.ascii_uppercase + string.digits
        return ''.join(random.choice(charset) for _ in range(length))
    #--- end of method


    def parse_shell_output(self, shell_output_str):
        """  --> 'lsdahfl897klj' """
        ret_val = []
        ret_val = re.split('[\r\n]+', shell_output_str)
        for idx in range(0,len(ret_val)):
            ret_val[idx] = ret_val[idx].rstrip()
        #---
        return ret_val
    #--- end of method


    def debug_info(self, message_str):
        """  --> Debug info """
        frame = sys._getframe(1)
        funName = frame.f_code.co_name
        line_number = frame.f_lineno
        filename = frame.f_code.co_filename
        return ( "%s : %s (%s:%04d) : %s" % (self.time_stamp('%H.%M.%S.%f'), funName, filename, line_number, message_str))
    #--- end of method


    def read(self, file_name_str, cleanUp=True):
        """  <FILE> --> [str,str,str] """
        ret_val = []
        try:
            f = open(file_name_str)
        except IOError:
            return None
        else:
            ret_val = f.readlines()
            f.close()
            if cleanUp == True:
                ret_val = self.rstrip_all(ret_val)
                ret_val = self.remove_empty_lines(ret_val)
        return ret_val
    #---------------------

    def unify_length(self, s, maxlen=-1, minlen=-1, spacer=' '):
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

    def fold(self, long_str, width):
        """  longStr --> [str1,str2,str3] """
        ret_val = []
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
            ret_val.append(cur)
        #---
        return ret_val
    #---

    def fmttxt(self, t, indent="", header="", footer="", maxlen=-1, minlen=-1, line_numbering_start=-1):
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
            cur_line = self.unify_length(cur_line,maxlen,minlen)
            # add to the output
            retTxt.append(cur_line)
        #----------------------------- end for

        if (len(footer))>0:
            retTxt.append("%s%s%s" % (indent, line_number_placeholder, footer))

        return retTxt
    #---------------------

    def prntxt(self, t, indent="", header="", footer="", maxlen=-1, minlen=-1, line_numbering_start=-1):
        """  print the list of strings """
        if len(t)>0:
            tmp = self.fmttxt(t, indent, header, footer, maxlen, minlen, line_numbering_start)
            for i in range(0,len(tmp)):
                print (tmp[i])
            #---
        #---
    #---


    def save(self, text, file_name):
        """  save text to file """
        fileToSave = open(file_name, 'w')
        for item in text:
            fileToSave.write("%s\n" % item)
        #---
        fileToSave.flush()
        fileToSave.close()
    #---

    def append(self, text, file_name):
        """  append text to file """
        fileToSave = open(file_name, 'a')
        for item in text:
            fileToSave.write("%s\n" % item)
        #---
        fileToSave.flush()
        fileToSave.close()
    #---



    def replace_all(self, t, pattern, replacement):
        """  replace pattern in all strings """
        ret_val = []
        for i in range(0,len(t)):
            cur = t[i]
            while re.match(pattern,cur):
                cur = re.sub(pattern, replacement, cur)
            #---
            ret_val.append(cur)
        #---
        return ret_val
    #---------------------

    def each_line(self, txt, function_name):
        """ for each line ret[x] = functionStr(inp[x]) """
        ret_val = []
        for i in range(0,len(txt)):
            x = txt[i]
            y = function_name(x)
            ret_val.append(y)
        #---
        return ret_val
    #--

    def rstrip_all(self, txt):
        """ for each y = rstrip(x) """
        ret_val = []
        for i in range(0,len(txt)):
            ret_val.append(txt[i].rstrip())
        #---
        return ret_val
    #---------------------

    def remove_empty_lines(self, txt):
        """ RemoveEmptyLines """
        ret_val = []
        for i in range(0,len(txt)):
            if len(txt[i])>0:
                ret_val.append(txt[i])
            #---
        #---
        return ret_val
    #---------------------

    def remove_duplicates(self, txt):
        output = []
        for x in txt:
            if x not in output:
                output.append(x)
            #--
        #--
        return output
    #---------------------


    def dedent(self, txt, offset_pos=0):
        output = []
        for x in txt:
            output.append(x[offset_pos:])
        #--
        return output
    #---------------------

    def maxlen(self, txt):
        maxLen = len(txt[0])
        for x in txt:
            if len(x)>maxLen:
                maxLen = len(x)
            #---
        #---
        return maxLen
    #---------------------

    def minlen(self, txt):
        minLen = len(txt[0])
        for x in txt:
            if len(x)<minLen:
                minLen = len(x)
            #---
        #---
        return minLen
    #---------------------


    def to_string (self, txt, delimiter=' '):
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

    def add_right_column(self, txt,trailer=' '):
        output = []
        for x in txt:
            output.append(x + trailer)
        #--
        return output
    #---------------------

    def vertical_cut(self, txt,left_col=0,right_col=-1):
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

    def filter(self, txt, pattern):
        filtered = []
        for i in range(0,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                filtered.append(txt[i])
            #--
        #--
        return filtered
    #---------------------

    def filter_not(self, txt, pattern):
        filtered = []
        for i in range(0,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)==0:
                filtered.append(txt[i])
            #--
        #--
        return filtered
    #---------------------


    def search_forward(self, txt, pattern, start=0):
        for i in range(start,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                return i
        return -1
    #---------------------

    def search_backward(self, txt, pattern, start=-1):
        if start<0:
            start = len(txt)-1
        for i in range(start,-1,-1):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                return i
        return -1
    #---------------------


    def count_matches(self, txt, pattern):
        ret_val = 0
        for i in range(0,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                ret_val += 1    # if pattern found, count in
            #--
        #--
        return ret_val
    #---------------------


    def cut_fragment(self, txt, start, stop):
        filtered = []
        if start<0:
            start = 0
        if stop>len(txt):
            stop = len(txt)

        for i in range(start,stop):
            filtered.append(txt[i])

        return filtered
    #---------------------


    def insert_fragment(self, txt, position, fragment):
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
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
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
        self.log('--> %s' % (sys._getframe(1)).f_code.co_name)
        return True
    #---


    def log_extend(self, array_of_strings):
        """ Log a list of strings """
        stack = inspect.stack()
        offset = self.logOffsetStr * (len(stack) - self.logBaseline)
        for eachStr in array_of_strings:
            self.log(offset + eachStr)
        #---
        return True
    #---



    def _run_silent (self, command_str, working_directory=''):
        """ Run shall command without log messages """
        actualDirectory = os.getcwd()
        if (len(working_directory)>0):
            os.chdir(working_directory)
        #--
        process = subprocess.Popen(command_str, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        self.rawOutput, self.rawError = process.communicate()
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
            self.cout = self.parse_shell_output(self.rawOutput)
            self.cerr = self.parse_shell_output(self.rawError)
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

        if self.cret!=0:
            if len(self.cout)>0 and (self.supressRunOutput or silent):
                self.prntxt(self.cout, ' '*4, '------- stdout output -------------')
            #---
            if len(self.cerr)>0:
                self.prntxt(self.cerr, ' '*4, '------- stderr output -------------')
            #---

        if len(self.cout)>0:
            header = '--- stdout of %s ---' % self.command
            footer = '-'*len(header)
            self.log_extend(self.fmttxt(self.cout, offset, header, footer))
        #--
        if len(self.cerr)>0:
            header = '--- stderr of %s ---' % self.command
            footer = '-'*len(header)
            self.log_extend(self.fmttxt(self.cerr, offset, header, footer))
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

        if self.cret != 0:
            self.error_count += 1
        #---

        return (self.cret == 0)



    def run_and_parse(self, command, work_dir, pattern, delimiter=' '):
        """ Run shall command and parse output """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        self.token = []
        self.run(command,work_dir)
        if self.cret != 0:
            self.error_count += 1
        #---
        pos = self.search_forward(self.cout,pattern)
        if pos>=0:
            self.log('Pattern %s found at position %d of stdout' % (pattern,pos))
            self.token = re.split(delimiter,self.cout[pos])
            self.log('Extracted %d tokens' % (len(self.token)))
        else:
            self.log('Pattern %s is not found in stdout capture' % (pattern))
            pos = self.search_forward(self.cerr,pattern)
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

        retBuf = self.rstrip_all(retBuf)
        #retBuf = self.RemoveEmptyLines(retBuf)

        if len(retBuf)<1:
            self.log("Warning: empty file %s" % (file_name))
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
                self.log_extend(self.fmttxt(diffBuffer, offset, header,footer))
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

        tempName = self.random_string(8) + '.tmp'
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

        pos = self.search_forward(self.text,pattern)             # Find the configuration line
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
        ret_val = False
        myName = (sys._getframe(0)).f_code.co_name
        self.log('--> %s' % myName)

        while True: # Single exit point function
            if not self.read_file(file_name):
                break
            #---
            self.text = self.insert_fragment(self.text,pos,fragment)

            if not self.write_file(file_name):
                break
            #---

            if self.debug:
                self._diff_last_file_write()
            #---

            ret_val = True
            break # Single exit point function must break at the end
        #---

        self.log('<-- %s' % myName)
        return ret_val
    #---------------------


    def insert_fragment_at_marker(self, file_name, pattern, fragment):
        """ open file, insert fragment at marker, save """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.read_file(file_name):
            return False

        pos = self.search_forward(self.text,pattern)
        if pos>0:
            return self.insert_fragment_at_pos(file_name, pos+1, fragment)

        return False
    #---------------------


    def delete_fragment_between_markers(self, file_name, start_pattern, end_pattern, inclusive=False):
        """ open file, delete fragment between markers, save """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.read_file(file_name):
            return False

        posStart = self.search_forward(self.text,start_pattern)
        if posStart<0:
            self.log("Cannot find start pattern %s" % start_pattern)
            return False

        self.log("Found start pattern %s at %d" % (start_pattern,posStart))
        # start search from the position of start pattern
        posEnd = self.search_forward(self.text,end_pattern,posStart)
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

        self.text = self.filter_not(self.text,pattern)

        if not self.write_file(file_name):
            return False

        if self.debug:
            self._diff_last_file_write()

        return True
    #---------------------


    def prn(self, str_message):
        """ print message and save log """
        self.log(str_message)
        if not self.quiet:
            print (str_message)
        return True
    #--


    def exit(self, ret_code=0, message=''):
        """ exit script """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if message!='':
            self.logList.append(message)
            print (message)
        #---
        self.log('Exit script with code %d' % ret_code)
        exit(ret_code)
    #--

    def fatal_error(self, message):
        """ Fatal Error: save log and terminate """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        retCode = -1
        self.logList.append(message)
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
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if work_dir=='':
            work_dir = os.getcwd()
        #---
        self.log('Mask = %s, Path=%s' % (mask, work_dir))
        matches = []
        for root, dirnames, filenames in os.walk(work_dir):
            for filename in fnmatch.filter(filenames, mask):
                matches.append(os.path.join(root, filename).replace("\\", "/"))
            #---
        #---
        self.log("<-- Found %d files" % len(matches))
        return matches
    #---

    def split_file_name(self, file_name):
        """ Split file name into path, name, and extension """
        r_path = os.path.dirname(file_name)
        (r_name, r_ext) = os.path.splitext( os.path.basename(file_name))
        ret_val = {}
        ret_val['path'] = r_path
        ret_val['name'] = r_name
        ret_val['ext']  = r_ext
        return ret_val
    #---

    def run_clean(self, command, work_dir='', error_pattern=''):
        """ Run command and ensure that it went w/o issues """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        self.run(command, work_dir)
        if (self.cret!=0):

            self.log("Terminating of RunClean, return code is not 0")
            header = '--- stdout of %s (%d) ---' % (command, self.cret)
            footer = '-'*len(header)
            offset = '    '
            self.log_extend(self.fmttxt(self.cout, offset, header, footer))

            header = '--- stderr of %s (%d) ---' % (command, self.cret)
            footer = '-'*len(header)
            self.log_extend(self.fmttxt(self.cerr, offset, header, footer))

            self.exit(-1)
        #---

        if len(error_pattern)>0:
            # pattern is given
            if self.search_forward(self.cout, error_pattern)>-1:
                self.log('Pattern %s is found in stdout' % error_pattern)
                self.prntxt(self.cout, '    ', '---- stdout of %s (%s) ----' % (command, self.cret), '------\n')
                self.prntxt(self.cerr, '    ', '---- stderr of %s (%s) ----' % (command, self.cret), '------\n')
                self.exit(-1)
            #---

            if self.search_forward(self.cerr, error_pattern)>-1:
                self.log('Pattern %s is found in stderr' % error_pattern)
                self.prntxt(self.cout, '    ', '---- stdout of %s (%s) ----' % (command, self.cret), '------\n')
                self.prntxt(self.cerr, '    ', '---- stderr of %s (%s) ----' % (command, self.cret), '------\n')
                self.exit(-1)
            #---
        #---
        return
    #---

    def one_dir_up(self,dir_name):
        """ One directory up tree """
        one_dir_up = re.sub('/[^/]+$', '', dir_name)
        return one_dir_up
    #---

    def remove(self,dir_or_file_name):
        """ Delete file """
        self.log('--> %s %s' % ((sys._getframe(0)).f_code.co_name, dir_or_file_name))
        if os.path.isdir(dir_or_file_name):
            self.log('%s is directory' % dir_or_file_name)
            os.rmdir(dir_or_file_name)
        else:
            self.log('%s is file' % dir_or_file_name)
            os.remove(dir_or_file_name)
        #---
        self.log('<-- %s %s' % ((sys._getframe(0)).f_code.co_name, dir_or_file_name))
        return
    #---


    def get_mac_address(self, delimiter=':'):
        """ Get MAC address of the current system """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        ret_val = ''
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

            parts = re.split(r'\s+',self.cout[0])
            if len(parts) < 1:
                self.log("ERROR: Command output format. Is output format  differ from expected?")
                break
            #---

            raw_str = parts[4]
            byte_str = re.split(':',raw_str)
            if len(byte_str) < 6:
                self.log("ERROR: Parsing error. Is output format  differ from expected?")
                break
            #---

            # Success
            ret_val = delimiter.join(byte_str)

            break
        #----------------------
        return ret_val
    #---


    def _gen_pybin(self, export_data, obj_name, default_file_name):
        """ Generate script to restore binary file """
        script_file = open(obj_name+'.py', 'wt')
        script_file.write("#!/usr/bin/python\n")
        script_file.write("\n")
        script_file.write("__all__ = ['Export']\n")
        script_file.write("\n")
        script_file.write("# This is automatically generated file. Do not edit!\n")
        script_file.write("# Usage:\n")
        script_file.write("#     import %s\n" % obj_name)
        script_file.write("#     %s.Extract()\n" % obj_name)
        script_file.write("# or in command line\n")
        script_file.write("#     python %s.py [fileName]\n" % obj_name)
        script_file.write("\n")
        script_file.write("import zlib\n")
        script_file.write("import binascii\n")
        script_file.write("import hashlib\n")
        script_file.write("import base64\n")
        script_file.write("import sys\n")
        script_file.write("\n")
        script_file.write("def Extract(fileName='%s'):\n" % default_file_name)
        script_file.write("    binObject=''\n")

        data_array = self.fold(export_data, 100)

        for blk in data_array:
            script_file.write("    binObject+='%s'\n" % blk)
        #---


        script_file.write("    decoded = base64.b64decode(binObject)\n")
        script_file.write("    decompressed = zlib.decompress(decoded)\n")
        script_file.write("    f = open(fileName, 'wb')\n")
        script_file.write("    f.write(decompressed)\n")
        script_file.write("    f.flush()\n")
        script_file.write("    f.close()\n")
        script_file.write("#---\n")
        script_file.write("\n")
        script_file.write("if __name__ == '__main__':\n")
        script_file.write("    import argparse\n")
        script_file.write("    parser = argparse.ArgumentParser()\n")
        script_file.write("    parser.add_argument('--file', action='store', default='%s', help='Export file name')\n" % default_file_name)
        script_file.write("    args = parser.parse_args()\n")
        script_file.write("    Extract(args.file)\n")
        script_file.write("#---\n")
        script_file.write("\n")
    #---



    def bin2py(self, bin_file_name, py_object_name):
        """ Generate Python script to restore binary file """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
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
        self.log('<-- %s' % (sys._getframe(0)).f_code.co_name)
    #---

#-- end of class




