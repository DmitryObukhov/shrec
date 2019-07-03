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
            cur_line = Text.unify_length(cur_line, maxlen, minlen)
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
            cur_line = Text.unify_length(cur_line, maxlen, minlen)
            # add to the output
            ret_val.append(cur_line)
        #-- pylint: disable=consider-using-enumerate

        if footer != '':
            cur_line = "%s%s" % (offset, footer)
            cur_line = Text.unify_length(cur_line, maxlen, minlen)
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

    @staticmethod
    def bin2hexdump(buf, linelen=32, middlecol='', fourdivider='', bytedivider='', address=False):
        ret = []
        if linelen<0:
            linelen = len(buf)
        #---

        if address:
            curstr = '%08X: ' % 0
        else:
            curstr = ''
        #---
        for i in range(len(buf)):
            if (i > 0):
                if (i % linelen == 0):
                    ret.append(curstr.rstrip())
                    if address:
                        curstr = '%08X: ' % i
                    else:
                        curstr = ''
                    #---
                else:
                    if ((i % (linelen/2)) == 0):
                        curstr += middlecol
                    elif (i % 4) == 0:
                        curstr += fourdivider
                    #---
                #---
            #---
            curstr = curstr + '%02X%s' % (buf[i], bytedivider)
        #---
        ret.append(curstr.rstrip())
        return ret
    #---

    @staticmethod
    def hexdump2bin(dump):
        dump_str = ''
        for line in dump:
            line = line.strip()
            line = re.sub('^[0-9a-fA-F]+\:\s+', '', line) # Remove header address
            line = re.sub('[^0-9a-fA-F\s]+', ' ', line)   # Remove non-hexdigit characters
            line = re.sub('\s+', '', line)   # Remove non-hexdigit characters
            dump_str += line
        #---
        s=binascii.unhexlify(dump_str)
        ret=[ord(x) for x in s]
        return ret
    #---


#--- end of class Text
