#!/usr/bin/python
# -*- coding: utf-8 -*-
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
import sys
import binascii


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

    def run_as_user(self, command, work_dir, user=''):
        """ Run shall command as specific user """
        #self._log_func(True)
        #self.log('command %s' % command)
        #self.log('user    %s' % user)
        #self.log('dir     %s' % work_dir)
        if user:
            # Run it as different user
            sudo_cmd = "sudo -H -u %s bash -c " % user
            cd_cmd = ''
            if work_dir:
                cd_cmd = 'cd %s; ' % work_dir
            #---
            command = sudo_cmd + "'" + cd_cmd + command + "'"
        #---
        #self._log_func(False)
        return self.run(command)
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
    def fname_split(file_name, ret_tuple=False):
        """ Split file name into path, name, and extension """
        r_path = os.path.dirname(file_name)
        (r_name, r_ext) = os.path.splitext(os.path.basename(file_name))
        ret_val = {}
        ret_val['path'] = r_path
        ret_val['name'] = r_name
        ret_val['ext'] = r_ext[1:]
        if ret_tuple:
            return (r_path, r_name, r_ext)
        #---
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
    def find_files(mask='*.*', work_dir='', recursive=True, short=False):
        """ Find files mathing a mask. Masj can be a string or list of strings """
        import fnmatch

        if type(mask) is list:
            flist = []
            for m in mask:
                mlist = Shell.find_files(m, work_dir, recursive)
                flist.extend(mlist)
            #---
            return sorted(flist)
        #---

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
                    if short:
                        matches.append(fname)
                    else:
                        fname = os.path.abspath(fname)
                        matches.append(fname)
                    #
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
    def flat_folder(workDir, separator='_'):
        if (not os.path.exists(workDir)):
            sys.stderr.write('ERROR: %s doesn`t exists\n' % workDir)
            return -1
        #---

        if (not os.path.isdir(workDir)):
            sys.stderr.write('ERROR: %s is not a directory\n' % workDir)
            return -1
        #---

        curDir = os.getcwd()
        os.chdir(workDir)

        pathRemover = re.compile('/')
        fList = Shell.find_files("*.*", '.', short=True)

        for x in range(0,len(fList)):
            newName1 = str(fList[x][2:])
            (newName2,n) = pathRemover.subn(separator, newName1)
            os.renames(fList[x], newName2)
        #---

        os.chdir(curDir)
        return len(fList)
    #---

    @staticmethod
    def transliterate_folder(workDir):
        from unidecode import unidecode

        if (not os.path.exists(workDir)):
            sys.stderr.write('ERROR: %s doesn`t exists\n' % workDir)
            return -1
        #---

        if (not os.path.isdir(workDir)):
            sys.stderr.write('ERROR: %s is not a directory\n' % workDir)
            return -1
        #---

        curDir = os.getcwd()
        os.chdir(workDir)

        fList = Shell.find_files("*.*", '.', short=True)

        for x in fList:
            newName  = unidecode(x)
            if (x != newName):
                os.renames(x, newName)
            #---
        #---

        os.chdir(curDir)
        return len(fList)

    #---


    @staticmethod
    def merge(fileList, mergeFileName):
        fout = open(mergeFileName,'wb')
        for n in fileList:
            fin  = open(n,'rb')
            while True:
                data = fin.read(65536)
                if not data:
                    break
                #---
                fout.write(data)
            #---
            fin.close()
        #---
        fout.flush()
        fout.close()
        return 0
    #------------------------------------------------


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
    def dir_contains_dirs(name):
        retval = []
        list_dir = os.listdir(name)
        #Text.print(list_dir)
        for f in list_dir:
            if os.path.isdir(name + '/' + f):
                retval.append(f)
            #---
        #---
        return retval
    #---

    @staticmethod
    def dir_contains_files(name):
        retval = []
        list_dir = os.listdir(name)
        for f in list_dir:
            if os.path.isfile(os.path.join('.', f)):
                retval.append(f)
            #---
        #---
        return retval
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
    def detrack_folder(mask, workdir=''):
        flist = Shell.find_files(mask, workdir)
        for name in flist:
            newname = re.sub('^[\d\.\s]+','',name)
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
    def makedir(dirname, temp=False):
        """ Make directory with error handling
        """
        import errno
        import tempfile

        if temp:
            dirpath = tempfile.mkdtemp(prefix=dirname)
            return dirpath
        #---

        if os.path.isdir(dirname):
            return dirname
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
        return dirname
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
