#!/usr/bin/env python3
from __future__ import print_function
import inspect
import sys
import unittest
import os
import re

from shrec import Debug    as debug
from shrec import Text     as tx
from shrec import Shell    as sh

# global structure for arguments
args = {}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug",  action="store_true", default=False)
    subparsers = parser.add_subparsers(help='Supported operations', dest='operation')
    a_parser = subparsers.add_parser("add")
    a_parser.add_argument("-c", "--comment", action="store", default='', help="Key's comments")
    a_parser.add_argument("filename",  action="store", default='key_P10_O0_T2_FASK_1.pub', nargs='*', help='File name, i.e. id_rsa.pub')

    args = vars(parser.parse_args())
    if args['debug']:
        tx.print(args, '    ', 'Arguments')
    #---
#-----------------------------------------------
