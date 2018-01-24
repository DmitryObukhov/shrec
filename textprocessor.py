#!/usr/bin/python
""" SHell RECipes module """
from __future__ import print_function

import subprocess
import os
import sys
import shutil
import platform
import re
import argparse

from time import time
from time import ctime

from datetime import datetime
import random
import string
import inspect
import tempfile
import zlib
import hashlib
import base64

__author__ = 'dmitry.obukhov'
__all__ = ['TextProcessor']


class TextProcessor(object):
    """  Text manipulation functions """

    @staticmethod
    def quoted_string(string_value):
        """ 'abc' --> '"abc"' """
        return "\"%s\"" % string_value
    #--- end of method

    @staticmethod
    def time_stamp(format_str = '%Y_%m_%d_%H%M%S%f'):
        """  --> '2018_01_01_1234569999' """
        return datetime.now().strftime(format_str)
    #--- end of method

    @staticmethod
    def random_string(length, charset=''):
        """  --> 'lsdahfl897klj' """
        if charset=='':
            charset = string.ascii_uppercase + string.digits
        return ''.join(random.choice(charset) for _ in range(length))
    #--- end of method


    @staticmethod
    def parse_shell_output(shell_output_str):
        """  --> 'lsdahfl897klj' """
        retVal = []
        retVal = re.split('[\r\n]+', shell_output_str)
        for idx in range(0,len(retVal)):
            retVal[idx] = retVal[idx].rstrip()
        #---
        return retVal
    #--- end of method


    @staticmethod
    def debug_info(message_str):
        """  --> Debug info """
        frame = sys._getframe(1)
        funName = frame.f_code.co_name
        line_number = frame.f_lineno
        filename = frame.f_code.co_filename
        return ( "%s : %s (%s:%04d) : %s" % (self.TimeString('%H.%M.%S.%f'), funName,filename,line_number,message_str))
    #--- end of method


    @staticmethod
    def read(file_name_str, cleanUp=True):
        """  <FILE> --> [str,str,str] """
        retVal = []
        try:
            f = open(file_name_str)
        except IOError:
            return None
        else:
            retVal = f.readlines()
            f.close()
            if cleanUp == True:
                retVal = TextProcessor.rstrip_all(retVal)
                retVal = TextProcessor.remove_empty_lines(retVal)
        return retVal
    #---------------------



    @staticmethod
    def unify_length(s, maxlen=-1, minlen=-1, spacer=' '):
        """  Cut string or add spacers to keep length for all lines """
        retStr = s
        curLen = len(retStr)
        # if maxLen defined, keep the left portion
        if maxlen>0 and (curLen > maxlen):
            retStr = retStr[:maxlen]

        # if min len is defined, space trail string
        curLen = len(retStr)
        if minlen>0 and (curLen < minlen):
            retStr = retStr + spacer*(minlen-curLen)

        return retStr
    #--

    @staticmethod
    def fold(long_str, width):
        """  longStr --> [str1,str2,str3] """
        retVal = []
        tmp = long_str
        while len(tmp)>0:
            cur = ''
            if len(tmp)>width:
                cur = tmp[0:width]
                tmp = tmp[width:]
            else:
                cur = tmp
                tmp = ''
            #---
            retVal.append(cur)
        #---
        return retVal
    #---

    @staticmethod
    def format(t, indent="", header="", footer="", maxlen=-1, minlen=-1, line_numbering_start=-1):
        """  [str1,str2] --> [header, offset + str1, offset + str2, footer]"""
        retTxt = []
        line_number_str = ""
        line_number_placeholder = ''
        if line_numbering_start>-1:
            line_number = line_numbering_start
            line_number_width = len("%d" % len(t))
            line_number_template = "%%%dd: " % line_number_width
            line_number_placeholder = ' '*(line_number_width+2)

        # if the header is defined, add header after indent
        if (len(header))>0:
            retTxt.append("%s%s%s" % (indent, line_number_placeholder, header))

        for i in range(0,len(t)):
            # prepare line numbering
            if line_numbering_start>-1:
                line_number_str = line_number_template % line_number
                line_number += 1
            # prepare line in format [indent][lineNumber][actualString]
            cur_line = "%s%s%s" % (indent,line_number_str,t[i])
            cur_line = TextProcessor.unify_length(cur_line,maxlen,minlen)
            # add to the output
            retTxt.append(cur_line)
        #----------------------------- end for

        if (len(footer))>0:
            retTxt.append("%s%s%s" % (indent, line_number_placeholder, footer))

        return retTxt
    #---------------------

    @staticmethod
    def Print(t, indent="", header="", footer="", maxlen=-1, minlen=-1, line_numbering_start=-1):
        """  print the list of strings """
        if len(t)>0:
            tmp = TextProcessor.format(t, indent, header, footer, maxlen, minlen, line_numbering_start)
            for i in range(0,len(tmp)):
                print (tmp[i])
            #---
        #---
    #---


    @staticmethod
    def save(text, file_name):
        """  save text to file """
        fileToSave = open(file_name, 'w')
        for item in text:
            fileToSave.write("%s\n" % item)
        #---
        fileToSave.flush()
        fileToSave.close()
    #---

    @staticmethod
    def append(text, file_name):
        """  append text to file """
        fileToSave = open(file_name, 'a')
        for item in text:
            fileToSave.write("%s\n" % item)
        #---
        fileToSave.flush()
        fileToSave.close()
    #---



    @staticmethod
    def replace_all(t, pattern, replacement):
        """  replace pattern in all strings """
        retVal = []
        for i in range(0,len(t)):
            cur = t[i]
            while re.match(pattern,cur):
                cur = re.sub(pattern, replacement, cur)
            #---
            retVal.append(cur)
        #---
        return retVal
    #---------------------

    @staticmethod
    def each_line(txt, function_str):
        """ for each line ret[x] = functionStr(inp[x]) """
        retVal = []
        for i in range(0,len(txt)):
            x = txt[i]
            y = eval(function_str)
            retVal.append(y)
        #---
        return retVal
    #--

    @staticmethod
    def rstrip_all(txt):
        """ for each y = rstrip(x) """
        retVal = []
        for i in range(0,len(txt)):
            retVal.append(txt[i].rstrip())
        #---
        return retVal
    #---------------------

    @staticmethod
    def remove_empty_lines(txt):
        """ RemoveEmptyLines """
        retVal = []
        for i in range(0,len(txt)):
            if len(txt[i])>0:
                retVal.append(txt[i])
            #---
        #---
        return retVal
    #---------------------

    @staticmethod
    def remove_duplicates(txt):
        output = []
        for x in txt:
            if x not in output:
                output.append(x)
            #--
        #--
        return output
    #---------------------


    @staticmethod
    def add(txt, something, delimiter='[\n|\r]+'):
        if type( something ) == str :
            tmp = re.split(delimiter, something)
            txt.extend(tmp)
        elif type( something ) == list :
            txt.extend(something)
        return txt
    #---------------------

    @staticmethod
    def dedent(txt, offset_pos=0):
        output = []
        for x in txt:
            output.append(x[offset_pos:])
        #--
        return output
    #---------------------

    @staticmethod
    def maxlen(txt):
        maxLen = len(txt[0])
        for x in txt:
            if len(x)>maxLen:
                maxLen = len(x)
            #---
        #---
        return maxLen
    #---------------------

    @staticmethod
    def minlen(txt):
        minLen = len(txt[0])
        for x in txt:
            if len(x)<minLen:
                minLen = len(x)
            #---
        #---
        return minLen
    #---------------------


    @staticmethod
    def to_string (txt, delimiter=' '):
        retStr = ""
        maxidx = len(txt)
        for i in range(0,maxidx):
            retStr += txt[i]
            if i<(maxidx-1):
                retStr += delimiter
            #---
        #---
        return retStr
    #---------------------

    @staticmethod
    def add_right_column(txt,trailer=' '):
        output = []
        for x in txt:
            output.append(x + trailer)
        #--
        return output
    #---------------------

    @staticmethod
    def vertical_cut(txt,left_col=0,right_col=-1):
        output = []
        for x in txt:
            if len(x)<left_col:
                output.append('')
            elif len(x)<right_col:
                output.append(x[left_col:])
            else:
                output.append(x[left_col:right_col])
        #--
        return output
    #---------------------

    @staticmethod
    def filter(txt, pattern):
        filtered = []
        for i in range(0,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                filtered.append(txt[i])
            #--
        #--
        return filtered
    #---------------------

    @staticmethod
    def filter_not(txt, pattern):
        filtered = []
        for i in range(0,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)==0:
                filtered.append(txt[i])
            #--
        #--
        return filtered
    #---------------------


    @staticmethod
    def search_forward(txt, pattern, start=0):
        for i in range(start,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                return i
        return -1
    #---------------------

    @staticmethod
    def search_backward(txt, pattern, start=-1):
        if start<0:
            start = len(txt)-1
        for i in range(start,-1,-1):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                return i
        return -1
    #---------------------


    @staticmethod
    def count_matches(txt,pattern):
        retVal = 0
        for i in range(0,len(txt)):
            x = re.findall(pattern, txt[i])
            if len(x)>0:
                retVal += 1    # if pattern found, count in
            #--
        #--
        return retVal
    #---------------------


    @staticmethod
    def cut_fragment(txt, start, stop):
        filtered = []
        if start<0:
            start = 0
        if stop>len(txt):
            stop = len(txt)

        for i in range(start,stop):
            filtered.append(txt[i])

        return filtered
    #---------------------


    @staticmethod
    def insert_fragment(txt,position,fragment):
        """ insert fragment at given position """
        output = []
        if position<len(txt):
            # before
            for i in range(0,position):
                output.append(txt[i])
            output.extend(fragment)
            for i in range(position,len(txt)):
                output.append(txt[i])
            # after
        else:
            output.extend(fragment)
        #---
        return output
    #---------------------
#-- end of TextProcessor


