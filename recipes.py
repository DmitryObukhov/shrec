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


#--- end of class ShellRecipes

