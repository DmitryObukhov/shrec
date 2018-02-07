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
import getpass

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
        caller_script = frame.f_code.co_filename
        self.error_count = 0
        self.debug = debug      # enable debug features and save extended log
        self.quiet = quiet
        self.context = 5        # context size for diffs
        self.system = platform.system()
        self.sysver = platform.release()
        self.platform = sys.platform
        self.dist = platform.dist()
        self.errcode = 0        # error code of the last command
        self.errmsg = ''        # diagnostic message
        self.log_list = []           # debug log
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
        self.process = None
        self.raw_output = ''
        self.raw_error = ''



        self.log_file_name = log_file
        if self.log_file_name != '':
            if self.log_file_name == "auto":
                script_name = self.fname_name(caller_script)
                self.log_file_name = os.path.normpath(tempfile.gettempdir() +
                                                      '/' +
                                                      script_name +
                                                      '__' +
                                                      self.timestamp() +
                                                      '.tmp')
            #--
        #---
        self.supress_run_output = False
        self.last_written_file = ''
        self.last_backup_file = ''
        self.caller = caller_script

        stack = inspect.stack()
        self.log_baseline = len(stack)
        self.log_offset_str = ' '*4
        self.log('caller=%s' % caller_script)
        self.log('self=%s' % __file__)
        self.log('user=%s' % getpass.getuser())

        if self.debug:
            self.log('==== System information')
            self.log("platform.system=%s" % self.system)
            self.log("platform.platform=%s" % platform.platform())
            (bits, linkage) = platform.architecture()
            self.log("platform.architecture=%s" % bits)
            self.log("platform.linkage=%s" % linkage)
            self.log("platform.python_version=%s" % platform.python_version())
            self.log("platform.system=%s" % platform.system())
            if self.system == 'Linux':
                (dist_name, dist_ver, dist_id) = platform.linux_distribution()
                self.log("Linux.Distro=%s" % dist_name)
                self.log("Linux.Version=%s" % dist_ver)
                self.log("Linux.DistID=%s" % dist_id)
            #---
            self.log('===========================')
        #--
    #---

    @staticmethod
    def quoted_string(string_value):
        """ 'abc' --> '"abc"' """
        return "\"%s\"" % string_value
    #--- end of method

    @staticmethod
    def timestamp(format_str='%Y_%m_%d_%H%M%S%f'):
        """  --> '2018_01_01_1234569999' """
        return datetime.now().strftime(format_str)
    #--- end of method

    @staticmethod
    def random_string(length, charset=''):
        """  --> 'lsdahfl897klj' """
        if charset == '':
            charset = string.ascii_uppercase + string.digits
        return ''.join(random.choice(charset) for _ in range(length))
    #--- end of method

    @staticmethod
    def rstrip_all(txt):
        """ for each y = rstrip(x) """
        ret_val = []
        for idx in range(0, len(txt)):
            ret_val.append(txt[idx].rstrip())
        #---
        return ret_val
    #---------------------

    @staticmethod
    def remove_empty_lines(txt):
        """ RemoveEmptyLines """
        ret_val = []
        for idx in range(0, len(txt)):
            if txt[idx] != '':
                ret_val.append(txt[idx])
            #---
        #---
        return ret_val
    #---------------------

    @staticmethod
    def save(text, file_name):
        """  save text to file """
        file_to_save = open(file_name, 'w')
        for item in text:
            file_to_save.write("%s\n" % item)
        #---
        file_to_save.flush()
        file_to_save.close()
    #---

    @staticmethod
    def append(text, file_name):
        """  append text to file """
        file_to_save = open(file_name, 'a')
        for item in text:
            file_to_save.write("%s\n" % item)
        #---
        file_to_save.flush()
        file_to_save.close()
    #---

    @staticmethod
    def read(file_name_str, clean=True):
        """  <FILE> --> [str,str,str] """
        ret_val = []
        try:
            input_file = open(file_name_str)
        except IOError:
            return None
        else:
            ret_val = input_file.readlines()
            input_file.close()
            if clean:
                ret_val = ShellWrapper.rstrip_all(ret_val)
                ret_val = ShellWrapper.remove_empty_lines(ret_val)
        return ret_val
    #---------------------

    @staticmethod
    def fold(long_str, width=80):
        """  longStr --> [str1,str2,str3] """
        ret_val = []
        tmp = long_str
        while tmp != '':
            cur = ''
            if len(tmp) > width:
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

    @staticmethod
    def replace_all(text, pattern, replacement):
        """  replace pattern in all strings """
        ret_val = []
        for idx in range(0, len(text)):
            cur = re.sub(pattern, replacement, text[idx])
            ret_val.append(cur)
        #---
        return ret_val
    #---------------------

    @staticmethod
    def remove_duplicates(txt):
        """ Remove duplicated lines """
        output = []
        for cur_str in txt:
            if cur_str not in output:
                output.append(cur_str)
            #--
        #--
        return output
    #---------------------

    @staticmethod
    def each_line(txt, function_name):
        """ for each line ret[x] = functionStr(inp[x]) """
        ret_val = []
        for idx in range(0, len(txt)):
            cur_str = txt[idx]
            new_str = function_name(cur_str)
            ret_val.append(new_str)
        #---
        return ret_val
    #--

    @staticmethod
    def maxlen(txt):
        """ Max length of a line in text """
        max_len = len(txt[0])
        for cur_str in txt:
            if len(cur_str) > max_len:
                max_len = len(cur_str)
            #---
        #---
        return max_len
    #---------------------

    @staticmethod
    def longest_line(txt):
        """ Max length of a line in text """
        max_len = len(txt[0])
        longest = txt[0]
        for cur_str in txt:
            if len(cur_str) > max_len:
                max_len = len(cur_str)
                longest = cur_str
            #---
        #---
        return longest
    #---------------------



    @staticmethod
    def minlen(txt):
        """ Min length of a line in text """
        min_len = len(txt[0])
        for cur_str in txt:
            if len(cur_str) < min_len:
                min_len = len(cur_str)
            #---
        #---
        return min_len
    #---------------------

    @staticmethod
    def shortest_line(txt):
        """ Min length of a line in text """
        min_len = len(txt[0])
        shortest = txt[0]
        for cur_str in txt:
            if len(cur_str) < min_len:
                min_len = len(cur_str)
                shortest = cur_str
            #---
        #---
        return shortest
    #---------------------

    @staticmethod
    def filter(txt, pattern):
        """ returns matching lines as new list """
        filtered = []
        for idx in range(0, len(txt)):
            matches = re.findall(pattern, txt[idx])
            if matches:
                filtered.append(txt[idx])
            #--
        #--
        return filtered
    #---------------------

    @staticmethod
    def filter_not(txt, pattern):
        """ returns not matching lines as new list """
        filtered = []
        for idx in range(0, len(txt)):
            matches = re.findall(pattern, txt[idx])
            if matches:
                pass #
            else:
                filtered.append(txt[idx])
            #--
        #--
        return filtered
    #---------------------

    @staticmethod
    def search_forward(txt, pattern, start=0):
        """ starting from start_idx searching forward for pattern.
            Returns index or -1 if not found
        """
        for idx in range(start, len(txt)):
            matches = re.findall(pattern, txt[idx])
            if matches:
                return idx
            #---
        #---
        return -1
    #---------------------

    @staticmethod
    def search_backward(txt, pattern, start=-1):
        """ starting from start_idx searching backward for pattern.
            Returns index or -1 if not found
        """
        if start < 0:
            start = len(txt)-1
        #---
        for idx in range(start, -1, -1):
            matches = re.findall(pattern, txt[idx])
            if matches:
                return idx
            #---
        #---
        return -1
    #---------------------

    @staticmethod
    def count_matches(txt, pattern):
        """ Returns number of lines matching the pattern """
        ret_val = 0
        for i in range(0, len(txt)):
            matches = re.findall(pattern, txt[i])
            if matches:
                ret_val += 1    # if pattern found, count in
            #--
        #--
        return ret_val
    #---------------------

    @staticmethod
    def to_string(txt, delimiter=' '):
        """ text to string """
        ret_val = ""
        maxidx = len(txt)
        for i in range(0, maxidx):
            ret_val += txt[i]
            if i < (maxidx-1):
                ret_val += delimiter
            #---
        #---
        return ret_val
    #---------------------

    @staticmethod
    def get_fragment(txt, start, stop):
        """ cut fragment of text and return it as new text """
        filtered = []
        if start < 0:
            start = 0
        if stop > len(txt):
            stop = len(txt)
        for i in range(start, stop):
            filtered.append(txt[i])
        #---
        return filtered
    #---------------------

    @staticmethod
    def cut_fragment(txt, start, stop):
        """ cut fragment of text and return it as new text """
        filtered = []
        if start < 0:
            start = 0
        if stop > len(txt):
            stop = len(txt)
        for i in range(0, start):
            filtered.append(txt[i])
        #---
        for i in range(stop, len(txt)):
            filtered.append(txt[i])
        #---
        return filtered
    #---------------------

    @staticmethod
    def insert_fragment(txt, position, fragment):
        """ insert fragment at given position """
        output = []
        if position < len(txt):
            # before
            for i in range(0, position):
                output.append(txt[i])
            #---
            output.extend(fragment)
            for i in range(position, len(txt)):
                output.append(txt[i])
            #---
            # after
        else:
            output.extend(fragment)
        #---
        return output
    #---------------------


    @staticmethod
    def indent(txt, lead=' '*4):
        """ Indent text """
        output = []
        for cur_str in txt:
            output.append(lead + cur_str)
        #--
        return output
    #---------------------

    @staticmethod
    def trail(txt, trailer):
        """ Add trailers """
        output = []
        for cur_str in txt:
            output.append(cur_str + trailer)
        #--
        return output
    #---------------------

    @staticmethod
    def dedent(txt, offset_pos=0):
        """ Dedent text """
        output = []
        for cur_str in txt:
            output.append(cur_str[offset_pos:])
        #--
        return output
    #---------------------

    @staticmethod
    def cut_vertical(txt, left_col=0, right_col=-1):
        """ Cut vertical block from the text and return text """
        output = []
        # todo: implementation
        for cur_str in txt:
            if len(cur_str) < left_col:
                output.append('')
            elif len(cur_str) < right_col:
                output.append(cur_str[0:left_col])
            else:
                output.append(cur_str[0:left_col] + cur_str[right_col:])
        #--
        return output
    #---------------------

    @staticmethod
    def get_vertical(txt, left_col=0, right_col=-1):
        """ Cut vertical block from the text and return the block """
        output = []
        if left_col < 0:
            left_col = 0
        #---
        for cur_str in txt:
            if len(cur_str) < left_col:
                output.append('')
            elif len(cur_str) < right_col:
                output.append(cur_str[left_col:])
            else:
                output.append(cur_str[left_col:right_col])
        #--
        return output
    #---------------------

    @staticmethod
    def one_dir_up(dir_name):
        """ One directory up tree """
        one_dir_up = re.sub('/[^/]+$', '', dir_name)
        return one_dir_up
    #---

    @staticmethod
    def _split_file_name(file_name):
        """ Split file name into path, name, and extension """
        r_path = os.path.dirname(file_name)
        (r_name, r_ext) = os.path.splitext(os.path.basename(file_name))
        ret_val = {}
        ret_val['path'] = r_path
        ret_val['name'] = r_name
        ret_val['ext'] = r_ext
        return ret_val
    #---

    @staticmethod
    def fname_path(file_name):
        """ Split file name into path, name, and extension """
        parts = ShellWrapper._split_file_name(file_name)
        return parts['path']
    #---

    @staticmethod
    def fname_name(file_name):
        """ Split file name into path, name, and extension """
        r_path = os.path.dirname(file_name)
        (r_name, r_ext) = os.path.splitext(os.path.basename(file_name))
        return r_name
    #---

    @staticmethod
    def fname_ext(file_name):
        """ Split file name into path, name, and extension """
        r_path = os.path.dirname(file_name)
        (r_name, r_ext) = os.path.splitext(os.path.basename(file_name))
        # return everything except starting dot (.ext --> ext)
        return r_ext[1:]
    #---
    @staticmethod
    def unify_length(input_str, maxlen=-1, minlen=-1, spacer=' '):
        """  Cut string or add spacers to keep length for all lines """
        # todo: unittest
        ret_str = input_str
        cur_len = len(ret_str)
        # if maxLen defined, keep the left portion
        if (maxlen > 0) and (cur_len > maxlen):
            ret_str = ret_str[:maxlen]
        #---

        # if min len is defined, space trail string
        cur_len = len(ret_str)
        if (minlen > 0) and (cur_len < minlen):
            ret_str = ret_str + spacer*(minlen-cur_len)
        #---

        return ret_str
    #--


    @staticmethod
    def fmttxt(txt,
               indent="",
               header="",
               footer="",
               maxlen=-1,
               minlen=-1,
               line_numbering_start=-1):
        """  [str1,str2] --> [header, offset + str1, offset + str2, footer]"""
        # todo: unittest
        ret_val = []
        line_number_str = ""
        line_number_placeholder = ''
        if line_numbering_start > -1:
            line_number = line_numbering_start
            line_number_width = len("%d" % len(txt))
            line_number_template = "%%%dd: " % line_number_width
            line_number_placeholder = ' '*(line_number_width+2)
        #---

        # if the header is defined, add header after indent
        if header != '':
            cur_line = "%s%s" % (indent,header)
            cur_line = ShellWrapper.unify_length(cur_line, maxlen, minlen)
            ret_val.append(cur_line)
        #---

        for line_idx in range(0, len(txt)):
            # prepare line numbering
            if line_numbering_start > -1:
                line_number_str = line_number_template % line_number
                line_number += 1
            # prepare line in format [indent][lineNumber][actualString]
            cur_line = "%s%s%s" % (indent, line_number_str, txt[line_idx])
            cur_line = ShellWrapper.unify_length(cur_line, maxlen, minlen)
            # add to the output
            ret_val.append(cur_line)
        #----------------------------- end for

        if footer != '':
            cur_line = "%s%s" % (indent,footer)
            cur_line = ShellWrapper.unify_length(cur_line, maxlen, minlen)
            ret_val.append(cur_line)
        #---

        return ret_val
    #---------------------

    @staticmethod
    def prntxt(txt,
               indent="",
               header="",
               footer="",
               maxlen=-1,
               minlen=-1,
               line_numbering_start=-1):
        """  print the list of strings """
        # todo: unittest
        if txt != '':
            tmp = ShellWrapper.fmttxt(txt,
                                      indent,
                                      header,
                                      footer,
                                      maxlen,
                                      minlen,
                                      line_numbering_start)
            #---------------------------------------------
            for i in range(0, len(tmp)):
                print (tmp[i])
            #---
        #---
    #---

    @staticmethod
    def debug_string(message_str):
        """  --> Debug string for use with log """
        # todo: unittest
        frame = sys._getframe(1)
        fun_name = frame.f_code.co_name
        line_number = frame.f_lineno
        file_name = frame.f_code.co_filename

        ret_str = "%s : %s (%s:%04d) : %s" % (
            ShellWrapper.timestamp('%H.%M.%S.%f'),
            fun_name,
            file_name,
            line_number,
            message_str)

        return ret_str
    #--- end of method

    @staticmethod
    def debug_info(message_str):
        """  --> Debug info """
        callerframerecord = inspect.stack()[1]    # 0 represents this line, 1 represents line at caller
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        ret_val = {}
        ret_val['filename'] = info.filename     # __FILE__
        ret_val['function'] = info.function     # __FUNCTION__
        ret_val['lineno'] = info.lineno         # __LINE__
        return ret_val
    #--- end of method



    @staticmethod
    def parse_shell_output(shell_output_str):
        """  --> 'lsdahfl897klj' """
        # todo: unittest
        ret_val = []
        ret_val = re.split('[\r\n]+', shell_output_str)
        for idx in range(0, len(ret_val)):
            ret_val[idx] = ret_val[idx].rstrip()
        #---
        ret_val = ShellWrapper.remove_empty_lines(ret_val)
        return ret_val
    #--- end of method

    @staticmethod
    def _call_stack_depth():
        """ Hidden Method for stack depth """
        stack = inspect.stack()
        return len(stack)
    #---


    def log(self, message, offset_correction=0):
        """ Save message in execution history """
        stack = inspect.stack()
        offset = self.log_offset_str * (len(stack) - self.log_baseline + offset_correction)
        if self.debug:
            print (offset + message)
        #---
        self.log_list.append(offset + message)
        if self.log_file_name != '':
            with open(self.log_file_name, "a") as logfile:
                logfile.write("%s\n" % (offset + message))
            #---
        #---
        return True
    #---


    def _log_func(self, entry=True, message=''):
        callerframerecord = inspect.stack()[1]    # 0 represents this line, 1 represents line at caller
        frame = callerframerecord[0]
        info1 = inspect.getframeinfo(frame)

        callerframerecord = inspect.stack()[2]    # 0 represents this line, 1 represents line at caller
        frame = callerframerecord[0]
        info2 = inspect.getframeinfo(frame)

        if entry:
            self.log('---> %s (%s:%d, %s) %s' % (info1.function, info2.filename, info2.lineno, info2.function, message), -2)
        else:
            self.log('<--- %s %s' % (info1.function, message), -2)
        #---
    #---

    def log_extend(self, array_of_strings, offset_correction=-1):
        """ Log a list of strings """
        for cur_str in array_of_strings:
            self.log(cur_str, offset_correction)
        #---
        return True
    #---

    def _logtest2(self):
        self._log_func(True)
        self.log('body of test 2')
        self._log_func(False)
    #---


    def _logtest(self):
        self._log_func(True)
        self.log('body of test 1')
        self._logtest2()
        self.log_extend(['a', 'b', 'c'])
        self._log_func(False)
    #---


    def run(self, command_str, working_directory='', silent=False):
        """ Run shell command """
        self._log_func(True)
        if command_str == '':
            self._log_func(False, 'command str is empty')
            return True
        #---
        self.cout = []
        self.parsed = []
        self.cerr = []
        self.cret = 0
        self.command = command_str
        self.starttime = time()

        self.log("Executing %s at %s" % (self.command, os.getcwd()))
        self.log("Started %s" % ctime(self.starttime))

        actual_directory = os.getcwd()
        if working_directory:
            self.log("Changing directory %s --> %s" % (actual_directory, working_directory))
            os.chdir(working_directory)
        #--

        self.log("Continue in %s" % (os.getcwd()))

        self.process = subprocess.Popen(self.command, shell=True, 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)

        pid = self.process.pid

        self.log('PID = %d' % pid)

        if self.supress_run_output or silent:
            (self.raw_output, self.raw_error) = self.process.communicate()
            self.cout = self.parse_shell_output(self.raw_output)
            self.cerr = self.parse_shell_output(self.raw_error)
            self.cret = self.process.returncode
        else:
            self.cout = []
            self.raw_output = ""

            empty_count = 0
            empty_count_treshold = 10
            for line in iter(self.process.stdout.readline, ''):
                line = line.decode('utf-8')
                line = line.rstrip()
                if line == '':
                    empty_count += 1
                else:
                    empty_count = 0
                    self.prn("%s" % line)
                    self.cout.append(line)
                #---
                if empty_count > empty_count_treshold:
                    break
                #---
            #---
            self.raw_error = self.process.stderr.readlines()
            self.process.stdout.close()
            self.process.stderr.close()
            self.cret = self.process.wait()

            self.raw_output = "\n".join(self.cout)
        #---

        self.log('Process finished with return code %d' % self.cret)

        offset = ' '*4

        if self.cret != 0:
            if (self.cout) and (self.supress_run_output or silent):
                self.prntxt(self.cout, ' '*4, '------- stdout output -------------')
            #---
            if self.cerr:
                self.prntxt(self.cerr, ' '*4, '------- stderr output -------------')
            #---
        #---

        if self.cout:
            header = '--- stdout of %s ---' % self.command
            footer = '-'*len(header)
            self.log_extend(self.fmttxt(self.cout, offset, header, footer))
        #--

        if self.cerr:
            header = '--- stderr of %s ---' % self.command
            footer = '-'*len(header)
            self.log_extend(self.fmttxt(self.cerr, offset, header, footer))
        #--

        if working_directory:
            self.log("Changing directory %s --> %s" % (working_directory, actual_directory))
            os.chdir(actual_directory)
            self.log("Continue in %s" % (os.getcwd()))
        #--


        self.endtime = time()
        self.elapsed = (self.endtime - self.starttime)
        self.log("Completed %s" % ctime(self.endtime))
        self.log("Elapsed %f seconds" % self.elapsed)

        if self.cret != 0:
            self.error_count += 1
        #---

        self._log_func(False)
        return self.cret == 0
    #---

    def _run_silent(self, command_str, working_directory=''):
        """ Run shall command without log messages """
        self._log_func(True)
        self.log(command_str)
        actual_directory = os.getcwd()
        if working_directory:
            os.chdir(working_directory)
        #--
        process = subprocess.Popen(command_str,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        self.raw_output, self.raw_error = process.communicate()
        if working_directory:
            os.chdir(actual_directory)
        #--
        self._log_func(False)
        return process.returncode
    #---

    def run_as_user(self, command, work_dir, user=''):
        """ Run shall command as specific user """
        self._log_func(True)
        self.log('command %s' % command)
        self.log('user    %s' % user)
        self.log('dir     %s' % work_dir)
        if user:
            # Run it as different user
            sudo_cmd = "sudo -H -u %s bash -c " % user
            cd_cmd = ''
            if work_dir:
                cd_cmd = 'cd %s; ' % work_dir
            #---
            command = sudo_cmd + "'" + cd_cmd + command + "'"
        #---
        self._log_func(False)
        return self.run(command)
    #---


    def write_file(self, file_name, str_array=None):
        """ Write file """
        self._log_func(True)
        self.errcode = 0
        self.last_written_file = file_name
        self.last_backup_file = ''
        if os.path.isfile(file_name):
            self.last_backup_file = file_name + '.bak'
            self.log('Saving backup %s' % self.last_backup_file)
            shutil.copy(file_name, self.last_backup_file)
        #-- end if

        try:
            file_to_save = open(file_name, 'w')
            buffer_to_save = []
            if str_array is None:
                buffer_to_save = self.text
            else:
                buffer_to_save = str_array

            for item in buffer_to_save:
                file_to_save.write("%s\n" % item)
            #--
            file_to_save.flush()
            file_to_save.close()
            self.log("Saved %d lines to %s" % (len(buffer_to_save), file_name))
            return True
        except IOError:
            self.errcode = -2
            self.errmsg = "ERROR (%d): Cannot write to %s" % (self.errcode, file_name)
            self.log(self.errmsg)
            return False
        #---
        self._log_func(False)
        return False
    #---

    def prn(self, str_message):
        """ print message and save log """
        self.log(str_message)
        if not self.quiet:
            print(str_message)
        return True
    #--

    def find_files(self, mask='*.*', work_dir=''):
        """ Find files mathing a mask """
        self._log_func(True)
        if work_dir == '':
            work_dir = os.getcwd()
        #---
        self.log('Mask = %s, Path=%s' % (mask, work_dir))
        matches = []
        for root, dirnames, filenames in os.walk(work_dir):
            #self.log("    %d files" % len(filenames))
            #self.log("    %d dirs" % len(dirnames))
            for filename in fnmatch.filter(filenames, mask):
                fname = os.path.join(root, filename)
                fname = os.path.abspath(fname)
                matches.append(fname)
            #---
        #---
        self._log_func(False,"Found %d files" % len(matches))
        return matches
    #---

    ###############################################################################################
    #     ____  ____    _   _ _   _ ___ _____ _____ _____ ____ _____ _____ ____
    #    |___ \| __ )  | | | | \ | |_ _|_   _|_   _| ____/ ___|_   _| ____|  _ \
    #      __) |  _ \  | | | |  \| || |  | |   | | |  _| \___ \ | | |  _| | | | |
    #     / __/| |_) | | |_| | |\  || |  | |   | | | |___ ___) || | | |___| |_| |
    #    |_____|____/   \___/|_| \_|___| |_|   |_| |_____|____/ |_| |_____|____/
    #
    ###############################################################################################

    def match_os(self, required_os):
        """ Enable root login to SSH server """
        if self.system != required_os: # Check the current platform
            self.prn("Current platform is %s" % batch.system)
            self.prn("Command is supported only for %s platforms, terminating" % required_os)
            self.prn("See details in %s" % batch.LogFile)
            return False
        #---
        return True
    #---


    def env_read(self, var_name):
        """ Read environment variable """
        self._log_func(True)
        ret_val = ''
        # todo: implementation
        self._log_func(False)
        return ret_val
    #---

    def env_write(self, var_name, val, persistent=False):
        """ Write environment variable """
        self._log_func(True)
        # todo: implementation
        self._log_func(False)
        return True
    #---


    def ask_to_continue(self, message=''):
        """ Ask for user input to continue or stop """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if message != '':
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









    def run_and_parse(self, command, work_dir, pattern, delimiter=' '):
        """ Run shall command and parse output """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        self.token = []
        self.run(command, work_dir)
        if self.cret != 0:
            self.error_count += 1
        #---
        pos = self.search_forward(self.cout, pattern)
        if pos >= 0:
            self.log('Pattern %s found at position %d of stdout' % (pattern, pos))
            self.token = re.split(delimiter, self.cout[pos])
            self.log('Extracted %d tokens' % (len(self.token)))
        else:
            self.log('Pattern %s is not found in stdout capture' % (pattern))
            pos = self.search_forward(self.cerr, pattern)
            if pos >= 0:
                self.log('Pattern %s found at position %d in stderr' % (pattern, pos))
                self.token = re.split(delimiter, self.cerr[pos])
                self.log('Extracted %d tokens' % (len(self.token)))
            else:
                self.log('Pattern %s is not found in stderr capture' % (pattern))
            #---
        return pos
    #---



    def _read_new_buffer(self, file_name):
        """ Read file """
        ret_buf = []
        self.errcode = 0
        if not os.path.isfile(file_name):
            self.errcode = -1
            self.errmsg = "ERROR (%d): Cannot find file %s" % (self.errcode, file_name)
            self.log(self.errmsg)
            return (False, [])
        #-- end if

        try:
            input_file = open(file_name)
        except IOError:
            self.errcode = -2
            self.errmsg = "ERROR (%d): Cannot open %s" % (self.errcode, file_name)
            self.log(self.errmsg)
            return (False, [])
        #---

        try:
            ret_buf = input_file.readlines()
        except IOError:
            self.errcode = -3
            self.errmsg = "Error (%d): Cannot read from %s" % (self.errcode, file_name)
            self.log(self.errmsg)
            return (False, [])
        else:
            input_file.close()
        #---


        ret_buf = self.rstrip_all(ret_buf)
        #retBuf = self.RemoveEmptyLines(retBuf)

        if len(ret_buf) < 1:
            self.log("Warning: empty file %s" % (file_name))
        #-- end if

        return (True, ret_buf)
    #---

    def read_file(self, file_name):
        """ Read file """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        (res, self.text) = self._read_new_buffer(file_name)
        return res
    #---


    def _diff_last_file_write(self):
        """ Diff last written file """
        if os.path.isfile(self.last_written_file) and os.path.isfile(self.last_backup_file):
            dir_name = tempfile._get_default_tempdir()
            with tempfile.NamedTemporaryFile(dir_name, delete=False) as tmpfile:
                diff_name = tmpfile.name
            #---

            self._run_silent('diff %s %s > %s' % (self.last_backup_file,
                                                  self.last_written_file,
                                                  diff_name))

            (res, diff_buffer) = self._read_new_buffer(diff_name)
            if res:
                offset = '    '
                header = '====== DIFF in %s ======' % self.last_written_file
                footer = '='*len(header)
                self.log_extend(self.fmttxt(diff_buffer, offset, header, footer))
            #---
            try:
                os.remove(diff_name)
            except OSError:
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

        temp_name = self.random_string(8) + '.tmp'
        if self.debug:
            shutil.copyfile(file_name, temp_name)

        self.text.extend(lines)
        if self.debug:
            self.log("Added %d lines to %s" % (len(lines), file_name))

        if not self.write_file(file_name):
            return False
        #---

        if self.debug:
            self._diff_last_file_write()
        #---

        return True
    #---------------------

    def replace_line_in_file(self, file_name, pattern, replacement, use_regex=False):
        """ open file, replace line, save """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.read_file(file_name):
            return False
        #---

        pos = self.search_forward(self.text, pattern)             # Find the configuration line
        if pos < 0:                                                     # if line not found
            self.errcode = -3
            self.errmsg = "WARNING (%d): Cannot find %s in %s" % (self.errcode, pattern, file_name)
            self.log(self.errmsg)
            return False
        #---

        if use_regex:
            self.text[pos] = re.sub(self.text[pos], pattern, replacement)
        else:
            self.text[pos] = replacement
        #---

        if not self.write_file(file_name):
            return False
        #---

        if self.debug:
            self._diff_last_file_write()
        #---

        return True
    #---------------------


    def insert_fragment_at_pos(self, file_name, pos, fragment):
        """ open file, insert fragment at position, save """
        ret_val = False
        name_of_function = (sys._getframe(0)).f_code.co_name
        self.log('--> %s' % name_of_function)

        while True: # Single exit point function
            if not self.read_file(file_name):
                break
            #---
            self.text = self.insert_fragment(self.text, pos, fragment)

            if not self.write_file(file_name):
                break
            #---

            if self.debug:
                self._diff_last_file_write()
            #---

            ret_val = True
            break # Single exit point function must break at the end
        #---

        self.log('<-- %s' % name_of_function)
        return ret_val
    #---------------------


    def insert_fragment_at_marker(self, file_name, pattern, fragment):
        """ open file, insert fragment at marker, save """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.read_file(file_name):
            return False
        #---
        pos = self.search_forward(self.text, pattern)
        if pos > 0:
            return self.insert_fragment_at_pos(file_name, pos+1, fragment)
        #---
        return False
    #---------------------


    def delete_fragment_between_markers(self,
                                        file_name,
                                        start_pattern,
                                        end_pattern,
                                        inclusive=False):
        """ open file, delete fragment between markers, save """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if not self.read_file(file_name):
            return False

        pos_start = self.search_forward(self.text, start_pattern)
        if pos_start < 0:
            self.log("Cannot find start pattern %s" % start_pattern)
            return False
        #---

        self.log("Found start pattern %s at %d" % (start_pattern, pos_start))
        # start search from the position of start pattern
        pos_end = self.search_forward(self.text, end_pattern, pos_start)
        if pos_end < 0:
            self.log("Cannot find end pattern %s" % end_pattern)
            return False
        #---

        new_text = []
        start_offset = 1
        end_offset = 0
        if inclusive:
            start_offset = 0
            end_offset = 1
        #---

        for idx in range(0, pos_start+start_offset):
            new_text.append(self.text[idx])
        #---

        for idx in range(pos_end-end_offset, len(self.text)):
            new_text.append(self.text[idx])
        #---

        self.text = new_text

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

        self.text = self.filter_not(self.text, pattern)

        if not self.write_file(file_name):
            return False

        if self.debug:
            self._diff_last_file_write()

        return True
    #---------------------




    def exit(self, ret_code=-666, message=''):
        """ exit script """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        if message != '':
            self.log_list.append(message)
            print(message)
        #---
        if ret_code == -666:
            ret_code = self.cret
        #---
        if message == '':
            self.log('Exit script with code %d' % ret_code)
        else:
            self.log('Exit %d (%s)' % (ret_code, message))
        #---
        exit(ret_code)
    #--

    def fatal_error(self, message):
        """ Fatal Error: save log and terminate """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        ret_code = -1
        self.log_list.append(message)
        sys.stderr.write("%s\n" % message)
        self.log('Exit script with code %d' % ret_code)
        exit(ret_code)
    #--


    def check_condition(self, condition):
        """ Assert """
        if not condition:
            frame = sys._getframe(1)
            fun_name = frame.f_code.co_name
            file_name = frame.f_code.co_filename
            message = 'Fatal exit on assert in %s (%s:%d)' % (fun_name, file_name, file_name)
            self.fatal_error(message)
        return True
    #--




    def run_clean(self, command, work_dir='', error_pattern=''):
        """ Run command and ensure that it went w/o issues """
        self.log('--> %s' % (sys._getframe(0)).f_code.co_name)
        self.run(command, work_dir)
        if self.cret != 0:
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

        if error_pattern:
            # pattern is given
            out_hdr = '---- stdout of %s (%s) ----' % (command, self.cret)
            err_hdr = '---- stderr of %s (%s) ----' % (command, self.cret)
            footer = '------\n'
            offset = ' '*4
            if self.search_forward(self.cout, error_pattern) > -1:
                self.log('Pattern %s is found in stdout' % error_pattern)
                self.prntxt(self.cout, offset, out_hdr, footer)
                self.prntxt(self.cerr, offset, err_hdr, footer)
                self.exit(-1)
            #---

            if self.search_forward(self.cerr, error_pattern) > -1:
                self.log('Pattern %s is found in stderr' % error_pattern)
                self.prntxt(self.cout, offset, out_hdr, footer)
                self.prntxt(self.cerr, offset, err_hdr, footer)
                self.exit(-1)
            #---
        #---
        return
    #---

    def remove(self, dir_or_file_name):
        """ Delete file or directory """
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

            parts = re.split(r'\s+', self.cout[0])
            if len(parts) < 1:
                self.log("ERROR: Command output format. Is output format  differ from expected?")
                break
            #---

            raw_str = parts[4]
            byte_str = re.split(':', raw_str)
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

#-- end of class
