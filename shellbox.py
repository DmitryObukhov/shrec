#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" ShRec stands for Shell Recipes. It implements functions frequently used
    for Linux system administration scripts.

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

__module__ = "shellbox"
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
__date__ = "2022/02/02"

import datetime
import json
import pprint
import random
import re
import string
import sys
import time
import os
import inspect
import traceback
import subprocess
#import glob
import shutil


class TextEditor:
    """ Collection of text (list of strings) operations
    """
    @staticmethod
    def read(file_name_str, clean=True):
        """Read file to the list(str)"""
        text = []
        # pylint: disable=consider-using-with
        try:
            input_file = open(file_name_str, encoding='UTF-8', errors="ignore")
        except IOError:
            return []
        # pylint: enable=consider-using-with

        text = input_file.readlines()
        input_file.close()
        if clean:
            text = TextEditor.rstrip(text)
        return text

    @staticmethod
    def write(text, file_name, append=False):
        """Save text to file"""
        # pylint: disable=consider-using-with
        if append:
            file_to_save = open(file_name, "a", encoding='UTF-8')
        else:
            file_to_save = open(file_name, "w", encoding='UTF-8')
        # pylint: enable=consider-using-with

        for line in text:
            file_to_save.write(f"{line}\n")
        file_to_save.flush()
        file_to_save.close()

    @staticmethod
    def timestamp(format_str="%Y_%m_%d_%H%M%S%f"):
        """--> '2018_01_01_1234569999'"""
        return datetime.datetime.now().strftime(format_str)

    @staticmethod
    def randomstr(length, charset=""):
        """--> 'lsdahfl897klj'"""
        if charset == "":
            charset = string.ascii_uppercase + string.digits
        return "".join(random.choice(charset) for _ in range(length))

    @staticmethod
    def rstrip(input_text):
        """for each y = rstrip(x)"""
        text = []
        for line in input_text:
            text.append(line.rstrip())
        return text

    @staticmethod
    def search_forward(txt, pattern, start=0):
        """starting from start_idx searching forward for pattern.
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
        """starting from start_idx searching backward for pattern.
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
        """Returns array of line numbers matching the pattern"""
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
        """Returns array of line numbers not matching the pattern"""
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

    @staticmethod
    def get_fragment(txt, start, stop):
        """cut fragment of text and return it as new text"""
        filtered = []
        start = max(start, 0)
        stop = min(stop, len(txt)-1)
        for idx in range(start, (stop + 1)):
            filtered.append(txt[idx])
        return filtered

    @staticmethod
    # pylint: disable=too-many-arguments
    def format(
        txt,
        offset="",
        header="",
        footer="",
        maxlen=-1,
        minlen=-1,
        line_numbering_start=-1,
    ):
        """[str1,str2] --> [header, offset + str1, offset + str2, footer]"""
        # pylint: enable=too-many-arguments
        ret_val = []
        line_number_str = ""
        if line_numbering_start > -1:
            line_number = line_numbering_start
            line_number_width = len(f"{len(txt)}")
            line_number_template = f"%{line_number_width}d: "

        # if the header is defined, add header after indent
        if header != "":
            cur_line = f"{offset}{header}"
            ret_val.append(cur_line)

        # pylint: disable=consider-using-enumerate
        #         indexation is used for line nuimbering
        for line_idx in range(len(txt)):
            # prepare line numbering
            if line_numbering_start > -1:
                line_number_str = line_number_template % line_number
                line_number += 1
            # prepare line in format [indent][lineNumber][actualString]
            cur_line = f"{offset}{line_number_str}{txt[line_idx]}"
            # add to the output
            if maxlen>0:
                cur_line = cur_line[:maxlen]
            if minlen>0:
                missing = minlen - len(cur_line)
                if missing > 0:
                    cur_line += ' '*missing

            ret_val.append(cur_line)
        # pylint: disable=consider-using-enumerate

        if footer != "":
            cur_line = f"{offset}{footer}"
            ret_val.append(cur_line)
        return ret_val

    @staticmethod
    # pylint: disable=too-many-arguments
    def print(
        txt,
        offset="",
        header="",
        footer="",
        maxlen=-1,
        minlen=-1,
        line_numbering_start=-1,
    ):
        """print the list of strings"""
        # pylint: enable=too-many-arguments
        if not isinstance(txt, list):
            txt = TextEditor.from_struct(txt)

        if txt != "":
            tmp = TextEditor.format(
                txt, offset, header, footer, maxlen, minlen, line_numbering_start
            )
            for line in tmp:
                print(line)

    @staticmethod
    def from_struct(struct):
        """Creates printable text from struct using JSON or PPRINT"""
        retval = []
        if isinstance(struct, str):
            retval.append(str(struct))
            return retval

        if isinstance(struct,(int, float)):
            retval.append(str(struct))
            return retval

        try:
            temp_str = json.dumps(struct, indent=4, ensure_ascii=True)
            txt = re.split(r"[\r\n]+", temp_str)
            retval.extend(txt)
        except TypeError:
            temp_str = pprint.pformat(struct, indent=4, width=1)
            txt = re.split(r"[\r\n]+", temp_str)
            retval.extend(txt)
        return retval

    @staticmethod
    def enquote(string_value, quote_mark=r'"'):
        """'abc' --> '"abc"'"""
        return f"{quote_mark}{string_value}{quote_mark}"

    @staticmethod
    def replace(txt, pattern, replacement):
        """replace pattern in all strings"""
        ret_val = []
        for line in txt:
            cur = re.sub(pattern, replacement, line)
            ret_val.append(cur)
        return ret_val

    @staticmethod
    def remove_duplicates(txt):
        """Remove duplicated lines"""
        output = []
        for cur_str in txt:
            if cur_str not in output:
                output.append(cur_str)
        return output

    @staticmethod
    def is_text(val):
        """Returns True is val is a list of strings"""
        if not isinstance(val, list):
            return False
        if len(val) < 1:
            return False
        if not isinstance(val[0], str):
            return False
        return True


class ShellBox:
    """Perform shell operations"""

    def __init__(self):
        pass

    @staticmethod
    # pylint: disable=too-many-arguments, too-many-locals, too-many-branches, too-many-statements, consider-using-with
    def run(
        command_str,
        working_directory="",
        comment="",
        quiet=None,
        bypass_error=None,
        terminate_pattern=None
    ):
        """Run Shell command"""
        def __parse_shell_output(shell_output_str):
            """Parse string received from process to list of
            strings AKA text"""
            ret_val = []
            parsed = re.split("[\r\n]+", shell_output_str)
            for line in parsed:
                line = line.rstrip()
                if line != "":
                    ret_val.append(line)
            return ret_val

        retval = {}
        retval["function"] = inspect.currentframe().f_code.co_name
        retval["seconds"] = time.time()
        retval["command"] = command_str
        retval["comment"] = comment
        retval["status"] = -666
        retval["dir"] = os.getcwd()
        retval["diagnostics"] = ""
        retval["stdout"] = []
        retval["stderr"] = []
        retval["flags"] = {}
        retval["process"] = {}
        retval["process"]["pid"] = -666
        retval["process"]["time"] = str(datetime.datetime.now())
        retval["process"]["started"] = time.time()
        retval["process"]["finished"] = retval["process"]["started"]
        retval["process"]["elapsed"] = -666.0

        stack = traceback.format_list(traceback.extract_stack())
        del stack[len(stack) - 1]
        retval["stack"] = stack

        if quiet is None:
            quiet = False
        retval["flags"]["quiet"] = quiet

        if bypass_error is None:
            bypass_error = False
        retval["flags"]["bypass_error"] = bypass_error

        retval["command"] = command_str
        retval["comment"] = comment

        if command_str == "":
            retval["diagnostics"] = "Command line is empty"
            retval["status"] = 0
            return retval

        actual_directory = os.getcwd()
        if working_directory:
            os.chdir(working_directory)
        retval["dir"] = os.getcwd()

        process = subprocess.Popen(
            command_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        retval["process"]["pid"] = process.pid

        if quiet:
            (raw_output, raw_error) = process.communicate()
            retval["stdout"] = __parse_shell_output(raw_output.decode("utf-8"))
            retval["stderr"] = __parse_shell_output(raw_error.decode("utf-8"))
            retval["status"] = process.returncode
        else:
            retval["stdout"] = []
            empty_count = 0
            empty_count_threshold = 10
            for line in iter(process.stdout.readline, ""):
                line = (line.decode("utf-8")).rstrip()
                if line == "":
                    empty_count += 1
                else:
                    empty_count = 0
                    print(f"{line}")
                    retval["stdout"].append(line)

                if terminate_pattern is not None:
                    matches = re.findall(terminate_pattern, line)
                    if matches:
                        process.terminate()
                        break

                if empty_count > empty_count_threshold:
                    break

            raw_error_list = process.stderr.readlines()
            retval["stderr"] = []
            for errline in raw_error_list:
                line = errline.decode("utf-8")
                line = line.rstrip()
                if line != "":
                    retval["stderr"].append(line)
            process.stdout.close()
            process.stderr.close()
            retval["status"] = process.wait()

        if working_directory:
            os.chdir(actual_directory)

        retval["process"]["finished"] = time.time()
        retval["process"]["elapsed"] = (
            retval["process"]["finished"] - retval["process"]["started"]
        )

        # Allout is a helper and not need to be added to the log
        all_stdout = " ".join(retval["stdout"])
        all_stderr = " ".join(retval["stderr"])
        retval["allout"] = (all_stdout + " " + all_stderr).strip()

        if not bypass_error and (retval["status"] != 0):
            print(json.dumps(retval, indent=4, ensure_ascii=True))
            sys.exit(retval["status"])
        return retval
    # pylint: enable=too-many-arguments, too-many-locals, too-many-branches,
    # pylint: enable=too-many-statements, consider-using-with

    @staticmethod
    def find_files(path, mask='*.*'):
        """ Recursively find files """
        res = ShellBox.run(f"find {path} -iname '{mask}'", quiet=True)
        return res['stdout']

    @staticmethod
    def for_each(flist, command_template, working_directory="", dryrun=False, quiet=None, bypass_error=None):
        """ Execute command for each file in the list """
        log = []
        all_good = True

        if quiet is None:
            quiet = False

        if bypass_error is None:
            bypass_error = False

        for fname in flist:
            command = command_template % fname
            if not quiet:
                print(command)
            if not dryrun:
                res = ShellBox.run(command, working_directory, quiet=True, bypass_error=True)
                log.append(res)
            if res['status'] != 0:
                all_good = False
        return all_good, log

    @staticmethod
    def merge_files(f_list, f_output):
        "Binary merge set of files"
        with open(f_output, 'wb') as outfile:
            for filename in f_list:
                if filename == f_output: # don't copy the output into the output
                    continue
                with open(filename, 'rb') as readfile:
                    shutil.copyfileobj(readfile, outfile)
            #---
        #---


class SnippetCollection:
    @staticmethod
    def snippet_csvinout():
        # https://realpython.com/python-csv/
        import csv
        with open('employee_birthday.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                    line_count += 1
            print(f'Processed {line_count} lines.')

    def snipet_json():
        pass
        # https://realpython.com/python-json/


class LinuxAdmin:
    """Perform Linux administrative operations"""
    @staticmethod
    def enable_access_to_usb_device(usbdev):
        "Enable access to USB device without sudo"
        rules_file = "/etc/udev/rules.d/51-myusb.rules"
        tokens = re.split(':', usbdev)

        usbdev_hi = tokens[0]
        usbdev_lo = tokens[1]
        # pylint: disable=consider-using-f-string
        spell  = 'SUBSYSTEMS=="usb", '
        spell += 'ATTRS{idVendor}=="%s", ' % usbdev_hi
        spell += 'ATTRS{idProduct}=="%s", ' % usbdev_lo
        spell += 'GROUP="users", '
        spell += 'MODE="0666"'
        # pylint: enable=consider-using-f-string
        content = TextEditor.read(rules_file)               # Open configuration file
        content.append(spell)                               # Add config line
        content = TextEditor.remove_duplicates(content)     # Clean up
        TextEditor.write(content, rules_file)               # Save configuration
        ShellBox.run('udevadm control --reload')            # Kick the new rules up

    @staticmethod
    def am_i_root():
        "Returns True if script is running with elevated privilegies"
        return os.getuid() == 0

    @staticmethod
    def sudo_run(command_str, working_directory="", quiet=True):
        res = ShellBox.run(f'sshpass -f ~/.local/sudopwd.txt sudo "{command_str}"', working_directory, quiet)
        return res['stdout']


    @staticmethod
    def binary_merge_files(pathname="."):
        "Find mp3 files in directory 'pathname' and merge them into one"
        if pathname == '.':
            pathname = os.getcwd()
        flist = ShellBox.find_files(pathname, mask='*.obj')
        for fname in flist:
            print(fname[88:])
        return len(flist)

    @staticmethod
    def save_sudo_pswd(password, default_file_name="~/.local/sudopwd.txt"):
        default_file_name = os.path.expanduser(default_file_name)
        with open(default_file_name, "w") as file_writer:
            file_writer.write("%s\n" % password)

    @staticmethod
    def read_sudo_pswd(default_file_name="~/.local/sudopwd.txt"):
        default_file_name = os.path.expanduser(default_file_name)
        print(default_file_name)
        with open(default_file_name, "r") as file_reader:
            pwd = file_reader.readline()
        return pwd


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
        install_script.append('      py_modules=["%s"])'% (__module__))
        TextEditor.write(install_script, 'temp_setup.py')

        ShellBox.run('python   temp_setup.py install')
        ShellBox.run('rm -f temp_setup.py')
        exit(0)
    # end of install
    print('Unsupported argument "%s"' % arglist[0])
    exit(-1)
