#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function


class Numbers(object):
    """  Numbers manipulation class """
    @staticmethod
    def is_a_number(x_str):
        """This function determines if its argument, x, is in the format of a
        number. It can be number can be in integer, floating point, scientific, or
        engineering format. The function returns '1' if the argument is formattted
        like a number, and '0' otherwise.
        https://github.com/ActiveState/code/blob/master/recipes/Python/67084_Assuring_that_entry_valid/recipe-67084.py
        """
        import re
        num_re = re.compile(r'^[-+]?([0-9]+\.?[0-9]*|\.[0-9]+)([eE][-+]?[0-9]+)?$')
        return str(re.match(num_re, x_str)) != 'None'
    #---
#---


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
