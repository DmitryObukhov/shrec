#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Universal code module
"""

from __future__ import print_function
from .shell import Shell
from .text import Text



class Shrec(object):
    def __init__(self, args_dict):
        self.args = args_dict   # Arguments from command line
        self.textfile = []      # Last read text file as list of strings
        self.log_file_name = self.args['logfile']
        self.log_store = []     # Store for log records
        self.text = Text()
        self.shell = Shell()
    #---
#---





if __name__ == "__main__":
    pass
#---
