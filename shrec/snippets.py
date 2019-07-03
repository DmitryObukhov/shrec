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

class Snippets(object):
    """ Class to hold various snippets """
    def __init__(self):
        """ Constructor """
        pass
    #---

    @staticmethod
    def dict_increment(dct, field, val=1):
        """ Increment field in dictionary """
        if not field in dct.keys():
            dct[field] = 0
        #---
        dct[field] += val
    #---

    @staticmethod
    def dict_merge(dctA, dctB):
        """ merge two dicts """
        dctC = {**dctA, **dctB}
        return dctC
    #---

#--- end of Utils

