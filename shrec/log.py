#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import datetime
import json
import inspect
import sys


class Log(object):
    """ Log and Debug functions """
    def __init__(self, args_dict):
        """ Constructor """
        self.verbose   = _verbose
        self.debug     = _debug
        self.logname   = _logname
        self.treshhold = _treshhold
        self.store   = []
        self.print("Created log object", -666)
    #---

    @staticmethod
    def debug_info(depth=1):
        """Returns the debug info tuple (file, lineNum, funcName)."""
        frame = sys._getframe(depth)
        funName = frame.f_code.co_name
        line_number = frame.f_lineno
        filename = frame.f_code.co_filename
        return (filename, line_number, funName)
    #---

    def print(self, msg, level=0):
        """ """
        log_record = {}
        log_record['time'] = str(datetime.now())
        log_record['level'] = level
        (scriptname, line_number, funName) = self.debug_info(2)
        log_record['script'] = scriptname
        log_record['line'] = line_number
        log_record['function'] = funName
        log_record['depth'] = len(inspect.stack())
        log_record['message'] = msg
        #------------------------------------------------------------------
        self.store.append(log_record)
        if self.debug:
            Text.print(log_record)
        #---

        if level>=self.treshhold:
            if self.verbose:
                print(msg)
            #---
            if self.logname:
                with open(self.logname, "a") as log_file:
                    log_file.write("%s\n" % msg)
                #---
            #---
        #---
    #---

    def dump(self, logname=''):
        store_str = json.dumps(self.store, ensure_ascii=True, indent=4)
        if self.verbose:
            print(store_str)
        #---
        if logname:
            with open(logname, "w") as log_file:
                log_file.write("%s\n" % store_str)
            #---
        #---
    #---



#-----------
