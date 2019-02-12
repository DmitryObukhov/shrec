#!/usr/bin/python
"""
    Universal code module
"""

from __future__ import print_function
import re
import collections
from datetime import datetime
import subprocess
import os
import json
from time import time
import pprint
import inspect
import platform


__all__ = ['Debug', 'Strings', 'Text', 'Shell']
__version__ = '0.0.1'

class Debug(object):
    """ Debug functions """
    @staticmethod
    def lineno():
        """Returns the current line number in our program."""
        return inspect.currentframe().f_back.f_lineno
    #---
#-----------


class Numbers(object):
    """  Numbers manipulation class """
    @staticmethod
    def is_a_number(x):
        """This function determines if its argument, x, is in the format of a
        number. It can be number can be in integer, floating point, scientific, or
        engineering format. The function returns '1' if the argument is formattted
        like a number, and '0' otherwise.
        https://github.com/ActiveState/code/blob/master/recipes/Python/67084_Assuring_that_entry_valid/recipe-67084.py
        """
        import re
        num_re = re.compile(r'^[-+]?([0-9]+\.?[0-9]*|\.[0-9]+)([eE][-+]?[0-9]+)?$')
        return str(re.match(num_re, x)) != 'None'
    #---
#---



class Strings(object):
    """  Strings manipulation class """
    @staticmethod
    def enquote(string_value, quote_mark=r'"'):
        """ 'abc' --> '"abc"' """
        return "%s%s%s" % (quote_mark, string_value, quote_mark)
    #--- end of enquote

    @staticmethod
    def lorem(maxlen=-1):
        """  generates random text to mockup web layout  """
        lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
                incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
                exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute
                irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat
                nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa
                qui officia deserunt mollit anim id est laborum. Sint occaecat cupidatat non
                proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""
        lorem = re.sub(r'\s\s+', ' ', lorem)
        if maxlen > 0:
            lorem = lorem[:maxlen]
        #---
        return lorem
    #---

    @staticmethod
    def timestamp(format_str='%Y_%m_%d_%H%M%S%f'):
        """  --> '2018_01_01_1234569999' """
        return datetime.now().strftime(format_str)
    #--- end of timestamp


    @staticmethod
    def randomstr(length, charset=''):
        """  --> 'lsdahfl897klj' """
        import string
        import random
        if charset == '':
            charset = string.ascii_uppercase + string.digits
        return ''.join(random.choice(charset) for _ in range(length))
    #--- end of random_string


    @staticmethod
    def is_url(url):
        """ Returns True is string is valid URL """
        try:
            from urllib.parse import urlparse
        except ImportError:
            from urlparse import urlparse
        #---

        try:
            res = urlparse(url)
            return res.scheme != ""
        except BaseException:
            return False
        #---
        return False
    #---


    @staticmethod
    def is_email(strval):
        """ Returns True is string is valid email """
        regexp = re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}', re.IGNORECASE)
        email = regexp.findall(strval)
        if email:
            return True
        #---
        return False
    #---


    @staticmethod
    def extract_email(strval):
        """ Returns True is string is valid email """
        regexp = re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}', re.IGNORECASE)
        email = regexp.findall(strval)
        if email:
            return email[0]
        #---
        return ''
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
            ret_str = ret_str + spacer * (minlen - cur_len)
        #---
        return ret_str
    #---




#--- end of class Strings



class Text(object):
    """ Text (list of strings) manipulation class """

    @staticmethod
    def rstrip(txt):
        """ for each y = rstrip(x) """
        ret_val = []
        for line in txt:
            ret_val.append(line.rstrip())
        #---
        return ret_val
    #---------------------


    @staticmethod
    def decode(txt):
        """ for each y = rstrip(x) """
        ret_val = []
        for line in txt:
            try:
                res = line.decode('utf-8')
            except AttributeError:
                res = line
            #---
            ret_val.append(res)
        #---
        return ret_val
    #---------------------


    @staticmethod
    def remove_empty_lines(txt):
        """ RemoveEmptyLines """
        ret_val = []
        for line in txt:
            if line != '':
                ret_val.append(line)
            #---
        #---
        return ret_val
    #---------------------


    @staticmethod
    def clean(txt):
        """ for each y = rstrip(x) """
        ret_val = []
        for line in txt:
            clean_str = str(line)
            clean_str = clean_str.rstrip()
            if clean_str != '':
                ret_val.append(clean_str)
            #---
        #---
        return ret_val
    #---------------------


    @staticmethod
    def save(text, file_name):
        """  save text to file """
        file_to_save = open(file_name, 'w')
        for line in text:
            file_to_save.write("%s\n" % line)
        #---
        file_to_save.flush()
        file_to_save.close()
    #---


    @staticmethod
    def append(text, file_name):
        """  append text to file """
        file_to_save = open(file_name, 'a')
        for line in text:
            file_to_save.write("%s\n" % line)
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
                ret_val = Text.rstrip(ret_val)
                ret_val = Text.remove_empty_lines(ret_val)
            #---
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
    def replace(txt, pattern, replacement):
        """  replace pattern in all strings """
        ret_val = []
        for line in txt:
            cur = re.sub(pattern, replacement, line)
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
    def longest(txt):
        """ Max length of a line in text """
        max_len = len(txt[0])
        retval = 0
        # pylint: disable=consider-using-enumerate
        #         indexation is used for return value
        for idx in range(0, len(txt)):
            if len(txt[idx]) > max_len:
                max_len = len(txt[idx])
                retval = idx
            #---
        #-- pylint: enable=consider-using-enumerate
        return retval
    #---------------------


    @staticmethod
    def shortest(txt):
        """ Min length of a line in text """
        min_len = len(txt[0])
        retval = 0
        # pylint: disable=consider-using-enumerate
        #         indexation is used for return value
        for idx in range(0, len(txt)):
            if len(txt[idx]) < min_len:
                min_len = len(txt[idx])
                retval = idx
            #---
        #-- pylint: enable=consider-using-enumerate
        return retval
    #---------------------

    @staticmethod
    def filter(txt, pattern):
        """ returns matching lines as new list """
        filtered = []
        for line in txt:
            matches = re.findall(pattern, line)
            if matches:
                filtered.append(line)
            #--
        #--
        return filtered
    #---------------------


    @staticmethod
    def filter_not(txt, pattern):
        """ returns not matching lines as new list """
        filtered = []
        for line in txt:
            matches = re.findall(pattern, line)
            if matches:
                pass
            else:
                filtered.append(line)
            #--
        #--
        return filtered
    #---------------------


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
            #---
        #-- pylint: enable=consider-using-enumerate
        return -1
    #---------------------


    @staticmethod
    def search_backward(txt, pattern, start=-1):
        """ starting from start_idx searching backward for pattern.
            Returns index or -1 if not found
        """
        if start < 0:
            start = len(txt) - 1
        #---
        # pylint: disable=consider-using-enumerate
        #         indexation is used for return value
        for idx in range(start, -1, -1):
            matches = re.findall(pattern, txt[idx])
            if matches:
                return idx
            #---
        #-- pylint: enable=consider-using-enumerate
        return -1
    #---------------------


    @staticmethod
    def find(txt, pattern):
        """ Returns number of lines matching the pattern """
        ret_val = []
        idx = 0
        for line in txt:
            matches = re.findall(pattern, line)
            if matches:
                ret_val.append(idx)
            #--
            idx += 1
        #--
        return ret_val
    #---------------------

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
            #--
            idx += 1
        #--
        return ret_val
    #---------------------


    @staticmethod
    def get_fragment(txt, start, stop):
        """ cut fragment of text and return it as new text """
        filtered = []
        if start < 0:
            start = 0
        #---
        if stop > len(txt):
            stop = len(txt)-1
        #---
        for i in range(start, (stop+1)):
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
            stop = len(txt) -1
        for i in range(0, start):
            filtered.append(txt[i])
        #---
        for i in range((stop+1), len(txt)):
            filtered.append(txt[i])
        #---
        return filtered
    #---------------------


    @staticmethod
    def insert_fragment(txt, position, fragment):
        """ insert fragment at given position """
        output = []
        if position < 0:
            output.extend(fragment)
            output.extend(txt)
        elif position < len(txt):
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
            output.extend(txt)
            output.extend(fragment)
        #---
        return output
    #---------------------


    @staticmethod
    def indent(txt, lead=' ' * 4):
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
        if left_col < 0:
            return Text.cut_vertical(txt, 0, right_col)
        #---
        output = []
        for cur_str in txt:
            if len(cur_str) < right_col:
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
    def format(txt, offset="", header="", footer="", maxlen=-1, minlen=-1, line_numbering_start=-1):
        """  [str1,str2] --> [header, offset + str1, offset + str2, footer]"""
        # todo: unittest
        ret_val = []
        line_number_str = ""
        if line_numbering_start > -1:
            line_number = line_numbering_start
            line_number_width = len("%d" % len(txt))
            line_number_template = "%%%dd: " % line_number_width
        #---

        # if the header is defined, add header after indent
        if header != '':
            cur_line = "%s%s" % (offset, header)
            cur_line = Strings.unify_length(cur_line, maxlen, minlen)
            ret_val.append(cur_line)
        #---

        # pylint: disable=consider-using-enumerate
        #         indexation is used for line nuimbering
        for line_idx in range(0, len(txt)):
            # prepare line numbering
            if line_numbering_start > -1:
                line_number_str = line_number_template % line_number
                line_number += 1
            # prepare line in format [indent][lineNumber][actualString]
            cur_line = "%s%s%s" % (offset, line_number_str, txt[line_idx])
            cur_line = Strings.unify_length(cur_line, maxlen, minlen)
            # add to the output
            ret_val.append(cur_line)
        #-- pylint: disable=consider-using-enumerate

        if footer != '':
            cur_line = "%s%s" % (offset, footer)
            cur_line = Strings.unify_length(cur_line, maxlen, minlen)
            ret_val.append(cur_line)
        #---

        return ret_val
    #---------------------


    @staticmethod
    def print(txt, offset="", header="", footer="", maxlen=-1, minlen=-1, line_numbering_start=-1):
        """  print the list of strings """


        if not isinstance(txt, list):
            txt = Text.from_struct(txt)
        #---

        if txt != '':
            tmp = Text.format(txt, offset, header, footer, maxlen, minlen, line_numbering_start)
            for line in tmp:
                print(line)
            #---
        #---
    #---


    @staticmethod
    def from_struct(struct, header='', footer='', _indent=4):
        """ Creates printable text from struct using JSON or PPRINT """
        retval = []
        if header != '':
            retval.append(header)
        #---
        try:
            temp_str = json.dumps(struct, indent=_indent, ensure_ascii=True)
            txt = re.split(r'[\r\n]+', temp_str)
            retval.extend(txt)
        except TypeError:
            temp_str = pprint.pformat(struct, indent=_indent, width=1)
            txt = re.split(r'[\r\n]+', temp_str)
            retval.extend(txt)
        #---
        if footer != '':
            retval.append(footer)
        #---
        return retval
    #---


#--- end of class Text






class Shell(object):
    """  Executing external tools """
    @staticmethod
    def __create_default_return_structure():
        """ Create return structure """
        retval = collections.OrderedDict()
        retval['command'] = 'n/i'
        retval['dir'] = 'n/i'
        retval['silent'] = False
        retval['terminate_on_error'] = False
        retval['pid'] = -666
        retval['started'] = time()
        retval['finished'] = retval['started']
        retval['elapsed'] = -666.0
        retval['status'] = -666
        retval['diagnostics'] = 'n/i'
        retval['stdout'] = []
        retval['stderr'] = []
        return retval
    #---

    @staticmethod
    def __parse_shell_output(shell_output_str):
        """  Parse string received from process to list of strings AKA text """
        ret_val = []
        parsed = re.split('[\r\n]+', shell_output_str)
        for line in parsed:
            line = line.rstrip()
            if line != '':
                ret_val.append(line)
            #---
        #---
        return ret_val
    #--- end of parse_shell_output


    @staticmethod
    def run(command_str, working_directory='', silent=False, terminate_on_error=False):
        """ Run shell command """

        retval = Shell.__create_default_return_structure()
        retval['silent'] = silent
        retval['terminate_on_error'] = terminate_on_error
        retval['command'] = command_str

        if command_str == '':
            retval['diagnostics'] = 'Command line is empty'
            retval['status'] = 0
            return retval
        #---

        actual_directory = os.getcwd()
        if working_directory:
            os.chdir(working_directory)
        #--
        retval['dir'] = os.getcwd()

        process = subprocess.Popen(command_str, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        retval['pid'] = process.pid

        if silent:
            (raw_output, raw_error) = process.communicate()
            retval['stdout'] = Shell.__parse_shell_output(raw_output.decode('utf-8'))
            retval['stderr'] = Shell.__parse_shell_output(raw_error.decode('utf-8'))
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
                #---
                if empty_count > empty_count_treshold:
                    break
                #---
            #---

            raw_error_list = process.stderr.readlines()
            retval['stderr'] = []
            for errline in raw_error_list:
                line = errline.decode('utf-8')
                line = line.rstrip()
                if line != '':
                    retval['stderr'].append(line)
                #---
            #---
            process.stdout.close()
            process.stderr.close()
            retval['status'] = process.wait()
        #---

        if working_directory:
            os.chdir(actual_directory)
        #--

        retval['finished'] = time()
        retval['elapsed'] = (retval['finished'] - retval['started'])

        if terminate_on_error and (retval['status'] != 0):
            print(json.dumps(retval, indent=4, ensure_ascii=True))
            exit(retval['status'])
        #---

        return retval
    #---

    @staticmethod
    def batch(cmd_list, silent=False):
        """ Executes a list of commands. Record format:
            (tag, command, directory, break_on_error, silent, description)
        """
        execution = collections.OrderedDict()
        execution['started'] = time()
        execution['started_str'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        execution['status'] = 0
        execution['errorcount'] = 0
        execution['executions'] = collections.OrderedDict()

        err_count = 0
        fatal_error_count = 0
        for command_tuple in cmd_list:
            tag = command_tuple[0]
            command = command_tuple[1]
            directory = command_tuple[2]
            break_on_error = command_tuple[3]
            cmd_silent = command_tuple[4]
            description = command_tuple[5]
            if not silent:
                print('    %s' % command)
            #---

            op_res = Shell.run(command, directory, cmd_silent)


            op_res['description'] = description
            if not silent:
                print('    %d' % op_res['status'])
            #---

            execution['executions'][tag] = op_res
            if op_res['status'] != 0:
                err_count += 1
                if break_on_error:
                    fatal_error_count += 1
                    break
                #---
            #---
        #---

        execution['errorcount'] = err_count
        if fatal_error_count > 0:
            execution['status'] = err_count
        #---

        execution['finished'] = time()
        execution['elapsed'] = (execution['finished'] - execution['started'])
        return execution
    #---

    @staticmethod
    def fname_split(file_name):
        """ Split file name into path, name, and extension """
        r_path = os.path.dirname(file_name)
        (r_name, r_ext) = os.path.splitext(os.path.basename(file_name))
        ret_val = {}
        ret_val['path'] = r_path
        ret_val['name'] = r_name
        ret_val['ext'] = r_ext[1:]
        return ret_val
    #---

    @staticmethod
    def fname_path(file_name):
        """ Split file name into path, name, and extension """
        parts = Shell.fname_split(file_name)
        return parts['path']
    #---

    @staticmethod
    def fname_name(file_name):
        """ Split file name into path, name, and extension """
        parts = Shell.fname_split(file_name)
        return parts['name']
    #---

    @staticmethod
    def fname_ext(file_name):
        """ Split file name into path, name, and extension """
        parts = Shell.fname_split(file_name)
        return parts['ext']
    #---

    @staticmethod
    def find_files(mask='*.*', work_dir='', recursive=True):
        """ Find files mathing a mask """
        import fnmatch
        if work_dir == '':
            work_dir = os.getcwd()
        #---
        matches = []
        if recursive:
            # disable warning for unused variable dirnames
            # pylint: disable=W0612
            for root, dirnames, filenames in os.walk(work_dir):
                for filename in fnmatch.filter(filenames, mask):
                    fname = os.path.join(root, filename)
                    fname = os.path.abspath(fname)
                    matches.append(fname)
                #---
            #---
            # pylint: enable=W0612
        else:
            for file_name in os.listdir(work_dir):
                if fnmatch.fnmatch(file_name, mask):
                    fname = os.path.join(work_dir, file_name)
                    fname = os.path.abspath(fname)
                    matches.append(fname)
                #---
            #---
        #---
        return sorted(matches)
    #---

    @staticmethod
    def normalize_file_name(name):
        newname = name
        # append underscores as placeholders
        newname = re.sub(r'([\^\D]{1})(\d\d\d)(\D)', r'\1_\2\3', newname)
        newname = re.sub(r'([\^\D]{1})(\d\d)(\D)', r'\1__\2\3', newname)
        newname = re.sub(r'([\^\D]{1})(\d)(\D)', r'\1___\2\3', newname)
        # convert underscores to leading zeroes
        newname = re.sub(r'(___)(\d)(\D)', r'000\2\3', newname)
        newname = re.sub(r'(__)(\d\d)(\D)', r'00\2\3', newname)
        newname = re.sub(r'(_)(\d\d\d)(\D)', r'0\2\3', newname)
        return newname
    #---



    @staticmethod
    def normalize_names(mask, workdir=''):
        flist = Shell.find_files(mask, workdir)
        newnames = []
        for name in flist:
            newname = Shell.normalize_file_name(name)
            if name != newname:
                os.rename(name,newname)
            #---
        #---
    #---


    @staticmethod
    def remove(dir_or_file_name):
        """ Delete file or directory
            Guaranteed destruction
        """
        import shutil
        import stat
        if os.path.isdir(dir_or_file_name):
            os.chmod(dir_or_file_name, stat.S_IWRITE)
            try:
                shutil.rmtree(dir_or_file_name)
            except OSError:
                Shell.run('rm -rf %s' % dir_or_file_name)
            #---
        elif os.path.isfile(dir_or_file_name):
            os.chmod(dir_or_file_name, stat.S_IWRITE)
            os.remove(dir_or_file_name)
        #---
        return
    #---

    @staticmethod
    def makedir(dirname):
        """ Make directory with error handling
        """
        import errno
        if os.path.isdir(dirname):
            return 0
        #---
        if os.path.isfile(dirname):
            raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
        #---
        try:
            os.makedirs(os.path.normpath(dirname))
        except OSError as cur_exception:
            if cur_exception.errno != errno.EEXIST:
                raise
            #---
        #---
        return 0
    #---

    @staticmethod
    def touch(filename, times=None):
        """ Make directory with error handling
        """
        with open(filename, 'a'):
            os.utime(filename, times)
        return 0
    #---


    @staticmethod
    def current_platform():
        """ checks the current platform and returns a string
            windows -- for any windows system
            redhat  -- for RedHat (RPM) based Linux distros (RedHat, Fedora)
            debian  -- for Debian (DEB) based Linux distros (Debian, Ubuntu)
            linux   -- for unknown Linux distros
            unknown -- for unknown platforms

            todo:
            darwin  -- for MAC systems
                       No mac, no ability to experiment with script installations
                       Meanwhile it is 'unknown' for safety reasons
        """

        my_system = platform.system()
        if my_system == 'Windows':
            return 'windows'
        elif my_system == 'Linux':
            if os.path.isfile('/etc/debian_version'):
                return 'debian'
            elif os.path.isfile('/etc/redhat-release'):
                return 'redhat'
            #---
            return 'linux'
        #---
        return 'unknown'
    #---

    @staticmethod
    def mktempdir(_prefix=''):
        import tempfile
        dirpath = tempfile.mkdtemp(prefix=_prefix)
        return dirpath
    #---



    @staticmethod
    def is_known_system():
        """ returns True if platform is recognized """
        _known_systems = ['debian', 'redhat', 'linux', 'windows']
        return Shell.current_platform() in _known_systems
    #---


    @staticmethod
    def is_linux_system():
        """ returns True if platform is recognized Linux system """
        _linux_systems = ['debian', 'redhat', 'linux']
        return Shell.current_platform() in _linux_systems
    #---


    @staticmethod
    def is_windows_system():
        """ platform is Windows """
        return Shell.current_platform() == 'windows'
    #---


    @staticmethod
    def is_admin():
        """ https://stackoverflow.com/questions/130763/
            request-uac-elevation-from-within-a-python-script
        """
        if Shell.is_windows_system():
            import ctypes
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except BaseException:
                return False
            #---
        elif Shell.is_linux_system():
            # pylint: disable=no-member
            #         if pylinted on windows, this line creates an error, because Python for Windows
            #         doesn't have the member getuid or geteuid
            return os.geteuid() == 0
            # pylint: enable=no-member
        else:
            return False
        #---
    #---


    @staticmethod
    def which(name):
        """ https://github.com/ActiveState/code/blob/master/recipes/Python/579035_UNIXlike_which/recipe-579035.py """
        found = 0
        for path in os.getenv("PATH").split(os.path.pathsep):
            full_path = path + os.sep + name
            if os.path.exists(full_path):
                found = 1
                return full_path
            #---
        #---
        # Return a UNIX-style exit code so it can be checked by calling scripts.
        # Programming shortcut to toggle the value of found: 1 => 0, 0 => 1.
        return None
    #---



#--- end of class Shell


class NumberBag(object):
    """ Class to give out a sequence in a specific order """
    modes = ['fifo', 'lifo', 'rand']
    def __init__(self, mode):
        """ Constructor """
        self.content = []
        if mode in self.modes:
            self.mode = mode
        else:
            self.mode = 'fail'
        #---
    #---

    def put(self, var):
        """ Put an element into a sequence, always at the end """
        self.content.append(var)
    #---

    def get(self):
        """ Get an element """
        import random
        if not self.content:
            return None
        #---

        if self.mode == 'lifo':
            retval = self.content[len(self.content) - 1]
            del self.content[-1]
            return retval
        elif self.mode == 'fifo':
            retval = self.content[0]
            del self.content[0]
            return retval
        elif self.mode == 'rand':
            idx = random.randint(0, (len(self.content) - 1))
            retval = self.content[idx]
            del self.content[idx]
            return retval
        else:
            return None
        #---
    #---

    def count(self):
        """ How many elements available """
        return len(self.content)
    #---
#---

if __name__ == "__main__":
    print('---')
#---
