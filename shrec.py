#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" ShRec stands for Shell Recipes. It implements functions frequently used
    for Linux system administration scripts.

Longer description of this module.

Below is an example of usage:

        import shrec
        class Worker(shrec.Shrec):
            def __init__(self, arg_list):
                super(Worker,self).__init__(arg_list)
                # Add child-specific code
                self.xxx = True
                self.yyy = True
                self.zzz = None

            def create_parser(self):
                # Add child-specific code
                self.parser = argparse.ArgumentParser(description='xxx')
                self.parser.add_argument("foo", action="store", help="Foo")
            # parse_parameters

            def validate_parameters(self):
                super(Worker,self).validate_parameters()
                # Add child-specific code
                if self.xxx:
                    self.zzz = 'abcd'

            def job(self):
                # Add child-specific code
                return 0

        if __name__ == "__main__":
            arglist = sys.argv.copy()  # Get list of command line arguments
            del arglist[0]  # Item 0 is the script name, it must be deleted
            worker = Worker(arglist)
            exit(worker.job())


This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__module__ = "shrec"
__version__ = "0.1.0"
__author__ = "Dmitry Obukhov"
__contact__ = "dmitry.obukhov@gmail.com"
__authors__ = [__author__]
__copyright__ = "Copyright (C) 2020, World"
__credits__ = [__author__]
__deprecated__ = False
__email__ = __contact__
__license__ = "GPLv3"
__maintainer__ = __author__
__status__ = "Production"
__date__ = "2020/02/02"


import os
import datetime
import inspect
import fnmatch
import string
import random
import sys
import re
import time
import platform
import json
import traceback
import runpy
import collections
import argparse
import pandas as pd
import xlsxwriter
import shlex
import atexit
import pprint
import binascii
import importlib
import types
import subprocess


class Shrec(object):
    description = "todo: Update me"

    ###########################################################################
    # Python-native interface to the object
    ###########################################################################

    def __init__(self, arg_list=None):
        """ Initialization """
        # Log files
        self.log_records = []
        self.shell_script = []

        self.parser = None
        if arg_list != None:
            self.create_parser()  # This method shall be redefined in child class
            arg_list = self.expand_parameters(arg_list)
            self.args = vars(self.parser.parse_args(arg_list))
            self.validate_parameters()  # method shall be redefined in child class
            self.logname = self.args['logname']
            if self.logname != '':
                atexit.register(self.__close_log)
                self.__open_log()
        else:
            self.args = {}
            self.logname = ''
            self.args['quiet'] = False
            self.args['debug'] = False


        # Run parameters
        self.stage = ''
        self.bypass_error = False
        self.add_allout = True

        self.shell_script.append('#!/bin/bash')
        self.shell_script.append('#########################################')
        self.shell_script.append('# This script is automatically generated')
        self.shell_script.append('#########################################')
        self.shell_script.append('')
    # __init__

    def __enter__(self):
        """ Entry point for 'with sh as Shrec(args)' """
        return self

    def __exit__(self, type, value, traceback):
        """ Exit point """
        pass

    ###########################################################################
    # Methods to be mandatory redefined in the child class
    ###########################################################################

    def create_parser(self):
        raise Exception('create_parser shall be defined in the child class')
    # parse_parameters

    def job(args):
        raise Exception('Method job shall be re-defined in the child class')
    # end of job

    def validate_parameters(self):
        ''' Validate common parameters here. Method shall be defined in child
            to validate child-specific params
        '''
        if 'debug' not in self.args.keys():
            self.args['debug'] = False
        if 'quiet' not in self.args.keys():
            self.args['quiet'] = False
        if self.args['logname'] == 'auto':
            self.args['logname'] = self.timestamp() + '.log'

        # The rest of parameter validation is child-specific and shall be
        # defined in the child class
    # end of Validate

    ###########################################################################
    # Utility methods
    ###########################################################################

    @staticmethod
    def expand_parameters(args_list):
        """ Expand parameter files --xx @yy.txt --zz  ==>  --xx --yy1=12 --yy2=34 --zz
            This mechanism allows to use files with credentials
        """
        if len(args_list) == 0:
            return args_list
        arg_processing_complete = False
        while not arg_processing_complete:
            complete_arguments = ''
            for idx, val in enumerate(args_list):
                arg_processing_complete = True
                if val[0] == '@':
                    arg_processing_complete = False
                    param_file = val[1:]
                    with open(param_file, 'r') as parameters_file:
                        param_str = parameters_file.read()
                    params = re.split(r'[\r\n]', param_str)
                    params_processed = []
                    for p in params:
                        params_processed.append(re.sub(r'#.*$', '', p))
                    complete_arguments += ' %s ' % ' '.join(params_processed)
                else:
                    complete_arguments += ' %s ' % val
            args_list = shlex.split(complete_arguments)
        return args_list
    # expand_parameters

    @staticmethod
    def timestamp(format_str='%Y_%m_%d_%H%M%S%f'):
        """  --> '2018_01_01_1234569999' """
        return datetime.datetime.now().strftime(format_str)

    @staticmethod
    def randomstr(length, charset=''):
        """  --> 'lsdahfl897klj' """
        if charset == '':
            charset = string.ascii_uppercase + string.digits
        return ''.join(random.choice(charset) for _ in range(length))

    @staticmethod
    def rstrip(input_text):
        """ for each y = rstrip(x) """
        text = []
        for line in input_text:
            text.append(line.rstrip())
        return text

    ###########################################################################
    # Logging infrastructure
    ###########################################################################

    def __open_log(self):
        if self.logname != '':
            log_record = self.__create_log_struct()
            log_record['time'] = str(datetime.datetime.now())
            log_record['message'] = 'Open log file'
            with open(self.logname, "w") as log_file:
                log_file.write("[%s\n" % json.dumps(log_record))

    def __close_log(self):
        if self.logname != '':
            log_record = {}
            log_record['function'] = inspect.currentframe().f_code.co_name
            log_record['seconds'] = time.time()
            log_record['time'] = str(datetime.datetime.now())
            log_record['message'] = 'All done'

            with open(self.logname, "a") as log_file:
                log_file.write("%s]\n" % json.dumps(log_record))

            # if len(self.shell_script) > 4:
            #     scrpit_name = self.logname.replace('.log', '.sh')
            #     self.save_file(self.shell_script, scrpit_name)

    def __raw_log(self, log_record):
        self.log_records.append(log_record)
        if self.logname:
            with open(self.logname, "a") as log_file:
                log_file.write("%s,\n" % json.dumps(log_record,
                                                    indent=4,
                                                    ensure_ascii=True))

    def log(self, msg):
        """ """
        log_record = self.__create_log_struct()
        log_record['message'] = msg
        log_record['stage'] = self.stage
        log_record['time'] = str(datetime.datetime.now())
        stack = traceback.format_list(traceback.extract_stack())
        del stack[len(stack) - 1]
        log_record['stack'] = stack
        self.__raw_log(log_record)

    def __create_log_struct(self):
        """ """
        log_record = {}
        called = sys._getframe(1)
        caller = sys._getframe(2)
        log_record['function'] = called.f_code.co_name
        log_record['seconds'] = time.time()
        caller = "%s:%d (%s)" % (caller.f_code.co_filename,
                                 caller.f_lineno,
                                 caller.f_code.co_name)
        log_record['caller'] = caller

        return log_record

    ###########################################################################
    # File operations: read, write, append
    ###########################################################################

    def read_file(self, file_name_str, clean=True):
        """  Read file to the list(str) """
        text = []
        try:
            input_file = open(file_name_str, encoding='ascii', errors='ignore')
        except IOError:
            return None
        else:
            text = input_file.readlines()
            input_file.close()
            if clean:
                text = self.rstrip(text)
        return text

    @staticmethod
    def save_file(text, file_name):
        """  Save text to file """
        file_to_save = open(file_name, 'w')
        for line in text:
            file_to_save.write("%s\n" % line)
        file_to_save.flush()
        file_to_save.close()

    @staticmethod
    def append_file(text, file_name):
        """  Append text to file """
        file_to_save = open(file_name, 'a')
        for line in text:
            file_to_save.write("%s\n" % line)
        file_to_save.flush()
        file_to_save.close()

    ##########################################################################
    # Filesystem operations: find
    ##########################################################################

    def find_files(self, mask='*.*', work_dir='', recursive=True, short=False):
        """ Find files matching a mask. Mask can be a string or
            list of strings
        """
        if type(mask) is list:
            flist = []
            for m in mask:
                mlist = self.find_files(m, work_dir, recursive)
                flist.extend(mlist)
            return sorted(flist)

        if work_dir == '':
            work_dir = os.getcwd()

        matches = []
        if recursive:
            # disable warning for unused variable dirnames
            # pylint: disable=W0612
            for root, dirnames, filenames in os.walk(work_dir):
                for filename in fnmatch.filter(filenames, mask):
                    fname = os.path.join(root, filename)
                    if short:
                        matches.append(fname)
                    else:
                        fname = os.path.abspath(fname)
                        matches.append(fname)
            # pylint: enable=W0612
        else:
            for file_name in os.listdir(work_dir):
                if fnmatch.fnmatch(file_name, mask):
                    fname = os.path.join(work_dir, file_name)
                    fname = os.path.abspath(fname)
                    matches.append(fname)
        return sorted(matches)

    def git_root(starting_point=''):
        start_dir = os.getcwd()
        if starting_point:
            os.chdir(starting_point)
        while True:
            cur_dir = os.getcwd()
            if os.path.exists('.git'):
                git_root = os.getcwd()
                os.chdir(start_dir)
                return git_root
            os.chdir('..')
            new_dir = os.getcwd()
            if new_dir == cur_dir:
                # Device top level directory. Stop search, no .git found
                os.chdir(start_dir)
                return ''
    # git_root

    def current_platform(self):
        """ checks the current platform and returns a string
            windows -- for any windows system
            redhat  -- for RedHat (RPM) based Linux distros (RedHat, Fedora)
            debian  -- for Debian (DEB) based Linux distros (Debian, Ubuntu)
            linux   -- for unknown Linux distros
            unknown -- for unknown platforms
            todo:
            darwin  -- for MAC systems
        """
        my_system = platform.system()
        if my_system == 'Windows':
            return 'windows'
        elif my_system == 'Linux':
            if os.path.isfile('/etc/debian_version'):
                return 'debian'
            elif os.path.isfile('/etc/redhat-release'):
                return 'redhat'
            return 'linux'
        return 'unknown'

    def is_linux_system(self):
        """ returns True if platform is recognized Linux system """
        _linux_systems = ['debian', 'redhat', 'linux']
        return self.current_platform() in _linux_systems

    def which(self, name):
        """ find executor """
        for path in os.getenv("PATH").split(os.path.pathsep):
            full_path = path + os.sep + name
            if os.path.exists(full_path):
                return full_path
        # Return a UNIX-style exit code so it can be checked by
        # calling scripts.
        # Programming shortcut to toggle the value of found: 1 => 0, 0 => 1.
        return None

    def dump(self, array, comment=''):
        log_record = self.__create_log_struct()
        dump = Editor.bin2hexdump(array, bytedivider=' ', address=True)
        if comment != '':
            dump.insert(0, comment)
        if len(dump) == 1:
            log_record['message'] = dump[0]
        else:
            log_record['message'] = dump
        self.__raw_log(log_record)
        self.print(dump)

    @staticmethod
    def search_forward(txt, pattern, start=0):
        """ starting from start_idx searching forward for pattern.
            Returns index or -1 if not found
        """
        # pylint: disable=consider-using-enumerate
        #         indexation is used for return value
        for idx in range(start, len(txt)):
            matches = re.findall(pattern, txt[idx])
            if matches:
                return idx
        # pylint: enable=consider-using-enumerate
        return -1

    @staticmethod
    def search_backward(txt, pattern, start=-1):
        """ starting from start_idx searching backward for pattern.
            Returns index or -1 if not found
        """
        if start < 0:
            start = len(txt) - 1
        # pylint: disable=consider-using-enumerate
        #         indexation is used for return value
        for idx in range(start, -1, -1):
            matches = re.findall(pattern, txt[idx])
            if matches:
                return idx
        # pylint: enable=consider-using-enumerate
        return -1

    @staticmethod
    def find(txt, pattern):
        """ Returns number of lines matching the pattern """
        ret_val = []
        idx = 0
        for line in txt:
            matches = re.findall(pattern, line)
            if matches:
                ret_val.append(idx)
            idx += 1
        return ret_val

    @staticmethod
    def find_not(txt, pattern):
        """ Returns number of lines matching the pattern """
        ret_val = []
        idx = 0
        for line in txt:
            matches = re.findall(pattern, line)
            if matches:
                pass
            else:
                ret_val.append(idx)
            idx += 1
        return ret_val

    def get_fragment(self, txt, start, stop):
        """ cut fragment of text and return it as new text """
        filtered = []
        if start < 0:
            start = 0
        if stop > len(txt):
            stop = len(txt) - 1
        for i in range(start, (stop + 1)):
            filtered.append(txt[i])
        return filtered

    @staticmethod
    def format(txt, offset="", header="", footer="",
               maxlen=-1, minlen=-1, line_numbering_start=-1):
        """  [str1,str2] --> [header, offset + str1, offset + str2, footer]"""
        # todo: unittest
        ret_val = []
        line_number_str = ""
        if line_numbering_start > -1:
            line_number = line_numbering_start
            line_number_width = len("%d" % len(txt))
            line_number_template = "%%%dd: " % line_number_width

        # if the header is defined, add header after indent
        if header != '':
            cur_line = "%s%s" % (offset, header)
            ret_val.append(cur_line)

        # pylint: disable=consider-using-enumerate
        #         indexation is used for line nuimbering
        for line_idx in range(len(txt)):
            # prepare line numbering
            if line_numbering_start > -1:
                line_number_str = line_number_template % line_number
                line_number += 1
            # prepare line in format [indent][lineNumber][actualString]
            cur_line = "%s%s%s" % (offset, line_number_str, txt[line_idx])
            # add to the output
            ret_val.append(cur_line)
        # pylint: disable=consider-using-enumerate

        if footer != '':
            cur_line = "%s%s" % (offset, footer)
            ret_val.append(cur_line)
        return ret_val

    def print(self, txt, offset="", header="", footer="",
              maxlen=-1, minlen=-1, line_numbering_start=-1):
        """  print the list of strings """
        if not isinstance(txt, list):
            txt = self.from_struct(txt)

        if txt != '':
            tmp = self.format(txt, offset, header, footer,
                              maxlen, minlen, line_numbering_start)
            for line in tmp:
                print(line)

    @staticmethod
    def from_struct(struct):
        """ Creates printable text from struct using JSON or PPRINT """
        retval = []
        if type(struct) is str:
            retval.append(str(struct))
            return retval
        elif (type(struct) is int) or (type(struct) is float):
            retval.append(str(struct))
            return retval

        try:
            temp_str = json.dumps(struct, indent=4, ensure_ascii=True)
            txt = re.split(r'[\r\n]+', temp_str)
            retval.extend(txt)
        except TypeError:
            temp_str = pprint.pformat(struct, indent=4, width=1)
            txt = re.split(r'[\r\n]+', temp_str)
            retval.extend(txt)
        return retval

    @staticmethod
    def enquote(string_value, quote_mark=r'"'):
        """ 'abc' --> '"abc"' """
        return "%s%s%s" % (quote_mark, string_value, quote_mark)

    @staticmethod
    def bin2hexdump(buf, linelen=32,
                    middlecol='', fourdivider='', bytedivider='',
                    address=False):
        ret = []
        if linelen < 0:
            linelen = len(buf)

        if address:
            curstr = '%08X: ' % 0
        else:
            curstr = ''
        for i in range(len(buf)):
            if (i > 0):
                if (i % linelen == 0):
                    ret.append(curstr.rstrip())
                    if address:
                        curstr = '%08X: ' % i
                    else:
                        curstr = ''
                else:
                    if ((i % (linelen / 2)) == 0):
                        curstr += middlecol
                    elif (i % 4) == 0:
                        curstr += fourdivider
            curstr = curstr + '%02X%s' % (buf[i], bytedivider)
        ret.append(curstr.rstrip())
        return ret

    @staticmethod
    def hexdump2bin(dump):
        dump_str = ''
        for line in dump:
            line = line.strip()
            # Remove header address, non-hexdigit characters
            line = re.sub('^[0-9a-fA-F]+\:\s+', '', line)
            line = re.sub('[^0-9a-fA-F\s]+', ' ', line)
            line = re.sub('\s+', '', line)
            dump_str += line
        s = binascii.unhexlify(dump_str)
        ret = [ord(x) for x in s]
        return ret

    @staticmethod
    def fname_split(file_name):
        """ Split file name into path, name, and extension """
        r_path = os.path.dirname(file_name)
        (r_name, r_ext) = os.path.splitext(os.path.basename(file_name))
        return (r_path, r_name, r_ext)

    @staticmethod
    def replace(txt, pattern, replacement):
        """  replace pattern in all strings """
        ret_val = []
        for line in txt:
            cur = re.sub(pattern, replacement, line)
            ret_val.append(cur)
        return ret_val

    @staticmethod
    def remove_duplicates(txt):
        """ Remove duplicated lines """
        output = []
        for cur_str in txt:
            if cur_str not in output:
                output.append(cur_str)
        return output

    @staticmethod
    def is_text(val):
        """ Returns True is val is a list of strings """
        if not type(val) is list:
            return False
        if len(val) < 1:
            return False
        if not type(val[0]) is str:
            return False
        return True

    @staticmethod
    def is_email(strval):
        """ Returns True is string is valid email """
        regexp = re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}',
                            re.IGNORECASE)
        email = regexp.findall(strval)
        if email:
            return True
        return False

    @staticmethod
    def extract_email(strval):
        """ Returns True is string is valid email """
        regexp = re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}',
                            re.IGNORECASE)
        email = regexp.findall(strval)
        if email:
            return email[0]
        return ''

    @staticmethod
    def bin2hexdump(buf, linelen=32,
                    middlecol='', fourdivider='', bytedivider='',
                    address=False):
        ret = []
        if linelen < 0:
            linelen = len(buf)

        if address:
            curstr = '%08X: ' % 0
        else:
            curstr = ''
        for i in range(len(buf)):
            if (i > 0):
                if (i % linelen == 0):
                    ret.append(curstr.rstrip())
                    if address:
                        curstr = '%08X: ' % i
                    else:
                        curstr = ''
                else:
                    if ((i % (linelen / 2)) == 0):
                        curstr += middlecol
                    elif (i % 4) == 0:
                        curstr += fourdivider
            curstr = curstr + '%02X%s' % (buf[i], bytedivider)
        ret.append(curstr.rstrip())
        return ret

    @staticmethod
    def hexdump2bin(dump):
        dump_str = ''
        for line in dump:
            line = line.strip()
            # Remove header address, non-hexdigit characters
            line = re.sub('^[0-9a-fA-F]+\:\s+', '', line)
            line = re.sub('[^0-9a-fA-F\s]+', ' ', line)
            line = re.sub('\s+', '', line)
            dump_str += line
        s = binascii.unhexlify(dump_str)
        ret = [ord(x) for x in s]
        return ret

    def run(self, command_str, working_directory='',
            comment='', quiet=None, bypass_error=None):
        """ Run shell command """

        def __parse_shell_output(shell_output_str):
            """  Parse string received from process to list of
            strings AKA text """
            ret_val = []
            parsed = re.split('[\r\n]+', shell_output_str)
            for line in parsed:
                line = line.rstrip()
                if line != '':
                    ret_val.append(line)
            return ret_val

        retval = collections.OrderedDict()
        retval['function'] = inspect.currentframe().f_code.co_name
        retval['seconds'] = time.time()
        retval['command'] = command_str
        retval['comment'] = comment
        retval['stage'] = self.stage
        retval['status'] = -666
        retval['dir'] = os.getcwd()
        retval['diagnostics'] = ''
        retval['stdout'] = []
        retval['stderr'] = []
        retval['flags'] = {}
        retval['flags']['silent'] = False
        retval['flags']['terminate_on_error'] = False
        retval['process'] = {}
        retval['process']['pid'] = -666
        retval['process']['time'] = str(datetime.datetime.now())
        retval['process']['started'] = time.time()
        retval['process']['finished'] = retval['process']['started']
        retval['process']['elapsed'] = -666.0
        stack = traceback.format_list(traceback.extract_stack())
        del stack[len(stack) - 1]
        retval['stack'] = stack

        if quiet is None:
            quiet = self.args['quiet']
        retval['flags']['quiet'] = quiet

        if bypass_error is None:
            bypass_error = self.bypass_error
        retval['flags']['bypass_error'] = bypass_error

        retval['command'] = command_str
        retval['comment'] = comment

        if command_str == '':
            retval['diagnostics'] = 'Command line is empty'
            retval['status'] = 0
            return retval

        actual_directory = os.getcwd()
        if working_directory:
            os.chdir(working_directory)
        retval['dir'] = os.getcwd()

        process = subprocess.Popen(command_str, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        retval['process']['pid'] = process.pid

        if quiet:
            (raw_output, raw_error) = process.communicate()
            retval['stdout'] = __parse_shell_output(raw_output.decode('utf-8'))
            retval['stderr'] = __parse_shell_output(raw_error.decode('utf-8'))
            retval['status'] = process.returncode
        else:
            retval['stdout'] = []
            empty_count = 0
            empty_count_treshold = 10
            for line in iter(process.stdout.readline, ''):
                line = (line.decode('utf-8')).rstrip()
                if line == '':
                    empty_count += 1
                else:
                    empty_count = 0
                    print("%s" % line)
                    retval['stdout'].append(line)
                if empty_count > empty_count_treshold:
                    break

            raw_error_list = process.stderr.readlines()
            retval['stderr'] = []
            for errline in raw_error_list:
                line = errline.decode('utf-8')
                line = line.rstrip()
                if line != '':
                    retval['stderr'].append(line)
            process.stdout.close()
            process.stderr.close()
            retval['status'] = process.wait()

        if working_directory:
            os.chdir(actual_directory)

        retval['process']['finished'] = time.time()
        retval['process']['elapsed'] = (retval['process']['finished'] -
                                        retval['process']['started'])

        self.__raw_log(retval)

        # Allout is a helper and not need to be added to the log
        if self.add_allout:
            all_stdout = ' '.join(retval['stdout'])
            all_stderr = ' '.join(retval['stderr'])
            retval['allout'] = (all_stdout + ' ' + all_stderr).strip()

        if comment:
            self.shell_script.append('# %s' % comment)
        self.shell_script.append('# Status: %d, Ignore error: %s' %
                                 (retval['status'], bypass_error))
        self.shell_script.append('%s' % command_str)
        self.shell_script.append('')

        if not bypass_error and (retval['status'] != 0):
            print(json.dumps(retval, indent=4, ensure_ascii=True))
            exit(retval['status'])
        return retval

    def module_from_file(self, module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
# end of class Shrec

class Runner(Shrec):
    """ Dummy, but quick child to perform simple operations """
    def __init__(self):
        """ Rely on the inherited, no arguments, all to defaults """
        super(Runner,self).__init__()

    def create_parser(self):
        pass

    def validate_parameters(self):
        pass
# end of class Runner


if __name__ == "__main__":
    arglist = sys.argv.copy()  # Get list of command line arguments
    del arglist[0]  # Item 0 is the script name, it must be deleted
    if len(arglist) == 0:
        print('Empty list of arguments')
        exit(-1)
    if arglist[0] == 'install':
        print('Installing the module')
        install_script = []
        install_script.append('from distutils.core import setup')
        install_script.append('setup(name="%s",version="%s",' % (__module__, __version__))
        install_script.append('      author="%s",' % __author__)
        install_script.append('      author_email="%s",' % __email__)
        install_script.append('      py_modules=["shrec"])')
        runner = Runner()
        runner.save_file(install_script, 'temp_setup.py')
        runner.run('python   temp_setup.py install')
        runner.run('rm -f temp_setup.py')
        exit(0)
    # end of install
    print('Unsupported argument "%s"' % arglist[0])
    exit(-1)
