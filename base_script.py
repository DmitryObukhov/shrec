#!/usr/bin/env python3
#from __future__ import print_function
import inspect
import sys
import unittest
import os
import re

from swissknife import Debug    as debug
from swissknife import Text     as tx
from swissknife import Shell    as sh


# global structure for arguments
args = {}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug",  action="store_true", default=False)
    parser.add_argument("olddir", action="store")
    parser.add_argument("newdir", action="store")
    args = vars(parser.parse_args())
    if args['debug']:
        tx.print(args, '    ', 'Arguments')
    #---

    for name in args['files']:
        pass
    #---
#-----------------------------------------------
