#!/usr/bin/env python3

import os
#from swissknife import Shell as sh
from swissknife import Text as tx

# global structure for arguments
args = {}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug",  action="store_true", default=False)
    parser.add_argument("--dryrun", action="store_true", default=False)
    parser.add_argument("files", action="store", default=".", nargs='*')
    args = vars(parser.parse_args())
    if args['debug']:
        tx.print(args, '    ', 'Arguments')
    #---

    for name in args['files']:
        pass
    #---
#-----------------------------------------------
