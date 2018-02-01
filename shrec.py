#!/usr/bin/python
""" SHell RECipes module """
from __future__ import print_function
import argparse
from shellwrapper import ShellWrapper
#import subprocess
#import os
#import sys
#import shutil
#import platform
#import re
#from datetime import datetime
#import random
#import string
#import inspect
#import tempfile
#import zlib
#import hashlib
#import base64
#from time import time
#from time import ctime

__author__ = 'dmitry.obukhov'

'''
#!/usr/bin/python
""" SHell RECipes module """
from __future__ import print_function
from textprocessor import TextProcessor
from batchprocessor import BatchProcessor

class ShellRecipes(object):
    """ Shell interface """

    def __init__(self, debug=False, quiet=True, log_file=""):
        """ Class Constructor """
        self.debug = debug
        self.quiet = quiet
        self.batch = BatchProcessor(self.debug, self.quiet, "auto")
    #--

    def match_os(self, required_os):
        """ Enable root login to SSH server """
        if self.batch.system != required_os: # Check the current platform
            self.batch.prn("Current platform is %s" % batch.system)
            self.batch.prn("Command is supported only for %s platforms, terminating" % required_os)
            self.batch.prn("See details in %s" % batch.LogFile)
            self.batch.exit(0)
        #---
        return True
    #---

    def enable_root_ssh():
        """ Enable root login to SSH server """
        if not self.match_os('Linux'): # Check the current platform
            return -1
        #---
        batch.replace_line_in_file('/etc/ssh/sshd_config', \
            'PermitRootLogin', \
            'PermitRootLogin yes')
        batch.run('service sshd restart')
        return batch.error_count
    #---

    def disable_root_ssh():
        """ Disable root login to SSH server """
        if not self.match_os('Linux'): # Check the current platform
            return -1
        #---
        batch.replace_line_in_file('/etc/ssh/sshd_config', \
            'PermitRootLogin', \
            'PermitRootLogin without-password')
        #---
        batch.run('service sshd restart')
        return batch.error_count
    #---

    def enable_tcg():
        """ Enable access to SED (TCG) storage """
        if not self.match_os('Linux'): # Check the current platform
            return -1
        #---

        # Normal operation
        # /etc/default/grub
        # GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
        # Change to GRUB_CMDLINE_LINUX_DEFAULT="quiet splash libata.allow_tpm=1"
        # run update-grub

        return batch.error_count
    #---

    def set_hostname():
        """ Disable root login to SSH server """
        if not self.match_os('Linux'): # Check the current platform
            return -1
        #---

        # Normal operation
        # /etc/default/grub
        # GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
        # Change to GRUB_CMDLINE_LINUX_DEFAULT="quiet splash libata.allow_tpm=1"
        # run update-grub
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

            if new_host_name == '':
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

        return batch.error_count
    #---

#--- end of class ShellRecipes


'''


def main():
    """ main function to parse arguments """
    exit_code = -1
    parser = argparse.ArgumentParser(description="Shell Receipes Engine", \
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    # Global arguments
    parser.add_argument('--debug', action='store_true', default=False, help='Debug execution mode')
    parser.add_argument('--quiet', action='store_true', default=False, help='Quiet execution mode')

    subparsers = parser.add_subparsers(help='Supported commands', dest='command')

    setup_parser = subparsers.add_parser('setup', help='Setup Python module')
    install_parser = subparsers.add_parser('install', help='Install shrec as system utility')
    utest_parser = subparsers.add_parser('unittest', help='Unit test the module')

    #r001d = recipe_subparser.add_parser('enablerootssh',    help='Enable root ssh')
    #r001n = recipe_subparser.add_parser('disablerootssh',   help='Disable root ssh')
    #r002d = recipe_subparser.add_parser('enablepm',         help='Enable power management')
    #r002n = recipe_subparser.add_parser('disablepm',        help='Disable power management')
    #r003d = recipe_subparser.add_parser('enableip6',        help='Enable support of IP v.6')
    #r003n = recipe_subparser.add_parser('disableip6',       help='Disable support of IP v.6')
    #r004d = recipe_subparser.add_parser('enabletcg',        help='Enable support of TCG storage')
    #r004n = recipe_subparser.add_parser('disabletcg',       help='Disable support of TCG storage')

    #r005  = recipe_subparser.add_parser('sethostname',      help='Set hostname from MAC or Random')
    #r005.add_argument('--naming', action='store', default='mac', help='Naming: {mac,rnd}')

    args = parser.parse_args()

    if args.command == 'setup':
        batch = ShellWrapper(args.debug, args.quiet, "auto")
        setup_script = [ \
                "#!/usr/bin/env python", \
                "from distutils.core import setup", \
                "setup(name='shrellwrapper',version='0.3',", \
                "      description='Script Helper',", \
                "      py_modules=['shrellwrapper'])", \
                "" \
            ]
        #---
        batch.save(setup_script, 'temp_setup.py')
        batch.run('python temp_setup.py install')
        batch.remove('temp_setup.py')
        batch.prntxt(batch.cout, '', '-- installation log --')
        batch.exit(0)
    #--

    print("Unhandled command %s" % args.command)
    return -1
#---


if __name__ == "__main__":
    exit(main())
#---
